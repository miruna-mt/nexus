from ortools.linear_solver import pywraplp
import json


def _normalize_data(data):
    """Accept both English and Spanish field names.
    Returns a dict with Spanish keys (internal canonical format)."""
    def pick(d, *keys):
        for k in keys:
            if k in d:
                return d[k]
        raise KeyError("None of " + str(keys) + " found in " + str(list(d.keys())))

    def norm_product(p):
        return {
            "id": p.get("id"),
            "nombre": pick(p, "name", "nombre"),
            "coste_pedido": pick(p, "order_cost", "coste_pedido"),
            "coste_almacenaje": pick(p, "holding_cost", "coste_almacenaje"),
            "coste_rotura": pick(p, "stockout_cost", "coste_rotura"),
            "stock_inicial": pick(p, "initial_stock", "stock_inicial"),
            "demanda_semanal": pick(p, "weekly_demand", "demanda_semanal"),
        }

    return {
        "horizonte_semanas": pick(data, "horizon_weeks", "horizonte_semanas"),
        "capacidad_almacen": pick(data, "storage_capacity", "capacidad_almacen"),
        "productos": [norm_product(p) for p in pick(data, "products", "productos")],
        "unit_name": data.get("unit_name", "unit"),
        "narrative_domain": data.get("narrative_domain", "retail"),
        "subject": data.get("subject", ""),
        "service_level": data.get("service_level", 0.95),
    }


class InventoryModel:
    def __init__(self):
        self.name = "Gestion de Inventario - Supermercado"
        self.description = "Optimiza pedidos y stock de productos perecederos"
        self.solver = None
        self.params = None

    def SetParams(self, params):
        self.params = params
        print(f"Parametros recibidos: {params}")

    def cargar_datos(self, filename=None, data_dict=None):
        if data_dict is not None:
            data = data_dict
        elif filename is not None:
            with open(filename, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
        else:
            raise ValueError("cargar_datos necesita 'filename' o 'data_dict'")

        # Normalizar nombres de campos (ES o EN)
        data = _normalize_data(data)

        self.horizonte = data["horizonte_semanas"]
        self.capacidad_almacen = data["capacidad_almacen"]
        self.capacity_multiplier = 1.0
        self.productos = data["productos"]
        self.num_productos = len(self.productos)
        print(f"Datos cargados: {self.num_productos} productos, {self.horizonte} semanas")
        self.unit_name = data.get("unit_name", "unit")
        self.narrative_domain = data.get("narrative_domain", "retail")
        self.subject = data.get("subject", "")
        self.service_level = data.get("service_level", 0.95)

    def build(self):
        print("Construyendo modelo de inventario...")

        coste_pedido = 50.0
        coste_almacenaje = 0.05
        coste_rotura = 2.0
        if self.params:
            if "coste_pedido" in self.params:
                coste_pedido = float(self.params["coste_pedido"])
                print(f"Coste pedido: {coste_pedido}")
            if "coste_almacenaje" in self.params:
                coste_almacenaje = float(self.params["coste_almacenaje"])
                print(f"Coste almacenaje: {coste_almacenaje}")
            if "coste_rotura" in self.params:
                coste_rotura = float(self.params["coste_rotura"])
                print(f"Coste rotura: {coste_rotura}")

        if self.params and "storage_capacity_multiplier" in self.params:
            self.capacity_multiplier = float(self.params["storage_capacity_multiplier"]) / 100.0
            print(f"Capacidad de almacen: {self.capacity_multiplier*100:.0f}%")

        if self.params and "service_level" in self.params:
            self.service_level = float(self.params["service_level"]) / 100.0
            print(f"Nivel de servicio: {self.service_level*100:.0f}%")

        self.solver = pywraplp.Solver.CreateSolver("SCIP")
        if not self.solver:
            return False

        self.pedido = {}
        self.llegada = {}
        self.stock = {}
        self.rotura = {}
        self.servida = {}
        self.hacer_pedido = {}

        for p in range(self.num_productos):
            self.pedido[p] = {}
            self.llegada[p] = {}
            self.stock[p] = {}
            self.rotura[p] = {}
            self.servida[p] = {}
            self.hacer_pedido[p] = {}
            for t in range(self.horizonte):
                self.pedido[p][t] = self.solver.IntVar(0, self.solver.infinity(), f"pedido_{p}_{t}")
                self.llegada[p][t] = self.solver.NumVar(0, self.solver.infinity(), f"llegada_{p}_{t}")
                self.stock[p][t] = self.solver.NumVar(0, self.solver.infinity(), f"stock_{p}_{t}")
                self.rotura[p][t] = self.solver.NumVar(0, self.solver.infinity(), f"rotura_{p}_{t}")
                self.servida[p][t] = self.solver.NumVar(0, self.solver.infinity(), f"servida_{p}_{t}")
                self.hacer_pedido[p][t] = self.solver.IntVar(0, 1, f"hacer_pedido_{p}_{t}")

        # Lead time: lo que pides en t llega en t+1. Semana 0 no hay pedido previo.
        for p in range(self.num_productos):
            for t in range(self.horizonte):
                if t == 0:
                    self.solver.Add(self.llegada[p][t] == 0)
                else:
                    self.solver.Add(self.llegada[p][t] == self.pedido[p][t-1])

        # Balance de stock con lead time
        for p in range(self.num_productos):
            for t in range(self.horizonte):
                demanda = self.productos[p]["demanda_semanal"][t]
                if t == 0:
                    stock_anterior = self.productos[p]["stock_inicial"]
                else:
                    stock_anterior = self.stock[p][t-1]

                # Stock disponible esta semana = lo que tenias + lo que llega
                disponible = stock_anterior + self.llegada[p][t]

                # No puedes servir mas de lo disponible
                self.solver.Add(self.servida[p][t] <= disponible)
                # No puedes servir mas de lo que piden
                self.solver.Add(self.servida[p][t] <= demanda)
                # Lo que no sirves, es rotura
                self.solver.Add(self.rotura[p][t] == demanda - self.servida[p][t])
                # El stock final es lo disponible menos lo servido
                self.solver.Add(self.stock[p][t] == disponible - self.servida[p][t])

        M = 10000
        for p in range(self.num_productos):
            for t in range(self.horizonte):
                self.solver.Add(self.pedido[p][t] <= M * self.hacer_pedido[p][t])

        capacidad_efectiva = int(self.capacidad_almacen * self.capacity_multiplier)
        # La capacidad limita el pico durante la semana: lo que ya tenias + lo que llega
        for t in range(self.horizonte):
            if t == 0:
                stock_anterior_expr = [self.productos[p]["stock_inicial"] for p in range(self.num_productos)]
            else:
                stock_anterior_expr = [self.stock[p][t-1] for p in range(self.num_productos)]
            self.solver.Add(
                sum(stock_anterior_expr[p] + self.llegada[p][t] for p in range(self.num_productos)) <= capacidad_efectiva
            )

        # Service level: roturas totales <= (1 - service_level) * demanda total
        total_demand = sum(
            self.productos[p]["demanda_semanal"][t]
            for p in range(self.num_productos)
            for t in range(self.horizonte)
        )
        max_stockout = int(total_demand * (1 - self.service_level))
        self.solver.Add(
            sum(self.rotura[p][t] for p in range(self.num_productos) for t in range(self.horizonte)) <= max_stockout
        )
        print(f"Max roturas permitidas: {max_stockout} (service level {self.service_level*100:.0f}%)")

        objective = self.solver.Objective()
        objective.SetMinimization()
        for p in range(self.num_productos):
            for t in range(self.horizonte):
                objective.SetCoefficient(self.hacer_pedido[p][t], coste_pedido)
                objective.SetCoefficient(self.stock[p][t], coste_almacenaje)
                objective.SetCoefficient(self.rotura[p][t], coste_rotura)

        print(f"Modelo construido: {self.solver.NumVariables()} variables, {self.solver.NumConstraints()} restricciones")
        return True

    def solve(self):
        print("Resolviendo modelo de inventario...")
        self.solver.SetTimeLimit(15000)  # 15 seconds
        status = self.solver.Solve()
        if status == pywraplp.Solver.OPTIMAL:
            print(f"Solucion optima! Coste total: {self.solver.Objective().Value():.2f} EUR")
            return True
        elif status == pywraplp.Solver.FEASIBLE:
            print(f"Mejor solucion encontrada en el tiempo limite: {self.solver.Objective().Value():.2f} EUR")
            return True
        else:
            print(f"No se encontro solucion. Status: {status}")
            return False

    def get_infeasible_narrative(self):
        """Explain why no feasible solution was found."""
        total_inicial = sum(p["stock_inicial"] for p in self.productos)
        capacidad_efectiva = int(self.capacidad_almacen * self.capacity_multiplier)
        total_demand = sum(
            self.productos[p]["demanda_semanal"][t]
            for p in range(self.num_productos)
            for t in range(self.horizonte)
        )
        max_stockout = int(total_demand * (1 - self.service_level))

        if total_inicial > capacidad_efectiva:
            insight = f"Initial stock ({total_inicial} {self.unit_name}s) exceeds warehouse capacity ({capacidad_efectiva}). Reduce initial stock or raise capacity."
            warning = f"\u26A0 Over capacity by {total_inicial - capacidad_efectiva} {self.unit_name}s at week 0."
        else:
            insight = f"Cannot meet {int(self.service_level*100)}% service level with the current capacity. Raise warehouse capacity or lower the service level target."
            warning = f"\u26A0 Max allowed stockouts: {max_stockout} {self.unit_name}s — not achievable with this capacity."

        return {
            "status": "infeasible",
            "narrative": {
                "titular": f"No feasible ordering plan<br><span class=\'hero-metrics\'>{self.num_productos} products \u00B7 {self.horizonte} weeks \u00B7 check capacity and service level</span>",
                "comparacion": f"Warehouse capacity: {capacidad_efectiva} {self.unit_name}s. Target service level: {int(self.service_level*100)}%.",
                "insight": insight,
                "warning": warning,
            }
        }

    def get_results(self):
        coste_total = self.solver.Objective().Value()

        coste_pedido = 50.0
        if self.params and "coste_pedido" in self.params:
            coste_pedido = float(self.params["coste_pedido"])

        coste_naive = 0
        for p in range(self.num_productos):
            for t in range(self.horizonte):
                coste_naive += coste_pedido

        ahorro = coste_naive - coste_total
        ahorro_pct = round((ahorro / coste_naive) * 100, 1) if coste_naive > 0 else 0

        # Cost breakdown (para la UI)
        coste_almacenaje = 0.05
        coste_rotura = 2.0
        if self.params:
            if "coste_almacenaje" in self.params:
                coste_almacenaje = float(self.params["coste_almacenaje"])
            if "coste_rotura" in self.params:
                coste_rotura = float(self.params["coste_rotura"])

        total_ordering = 0.0
        total_storage = 0.0
        total_stockout = 0.0
        for p in range(self.num_productos):
            for t in range(self.horizonte):
                total_ordering += self.hacer_pedido[p][t].solution_value() * coste_pedido
                total_storage += self.stock[p][t].solution_value() * coste_almacenaje
                total_stockout += self.rotura[p][t].solution_value() * coste_rotura

        cost_breakdown = {
            "ordering": round(total_ordering, 2),
            "storage": round(total_storage, 2),
            "stockout": round(total_stockout, 2)
        }

        pedidos_programados = []
        for p in range(self.num_productos):
            for t in range(self.horizonte):
                if self.pedido[p][t].solution_value() > 0.5:
                    pedidos_programados.append({
                        "producto": self.productos[p]["nombre"],
                        "semana": t + 1,
                        "cantidad": int(self.pedido[p][t].solution_value()),
                        "coste_pedido": coste_pedido
                    })

        resumen = []
        for p in range(self.num_productos):
            total_pedido = sum(self.pedido[p][t].solution_value() for t in range(self.horizonte))
            total_rotura = sum(self.rotura[p][t].solution_value() for t in range(self.horizonte))
            resumen.append({
                "producto": self.productos[p]["nombre"],
                "total_pedido": int(total_pedido),
                "total_rotura": int(total_rotura),
                "stock_final": int(self.stock[p][self.horizonte-1].solution_value())
            })

        num_pedidos = len(pedidos_programados)
        roturas_totales = sum(r["total_rotura"] for r in resumen)

        if roturas_totales == 0:
            insight_roturas = f"Zero stockouts across {self.horizonte} weeks. Literature documents 30\u201350% savings with EOQ."
        else:
            # Producto con mas roturas
            worst = max(resumen, key=lambda r: r["total_rotura"])
            worst_idx = next(p for p in range(self.num_productos)
                             if self.productos[p]["nombre"] == worst["producto"])
            # Semanas con rotura para ese producto (top 2)
            weeks = [(t + 1, int(self.rotura[worst_idx][t].solution_value()))
                     for t in range(self.horizonte)
                     if self.rotura[worst_idx][t].solution_value() > 0.5]
            weeks.sort(key=lambda x: x[1], reverse=True)
            top = [w for w, _ in weeks[:2]]
            if len(top) == 2:
                weeks_str = f"weeks {top[0]} and {top[1]}"
            elif len(top) == 1:
                weeks_str = f"week {top[0]}"
            else:
                weeks_str = "some weeks"

            if self.narrative_domain == "ad_sales":
                insight_roturas = f"{worst['producto']} turned away {worst['total_rotura']} buyers in {weeks_str} \u2014 demand exceeded available inventory."
            else:
                insight_roturas = f"{worst['producto']} had {worst['total_rotura']} unfilled {self.unit_name}s in {weeks_str} \u2014 demand exceeded stock."

        context_line = self.subject if self.subject else "Order plan"
        narrative = {
            "titular": f"{context_line}<br><span class='hero-metrics'>\u20AC{coste_total:,.2f} \u00B7 {num_pedidos} orders</span>",
            "comparacion": f"Ordering weekly on demand: \u20AC{coste_naive:,.2f}. Savings: \u20AC{ahorro:,.2f} ({ahorro_pct}%). EOQ model (MIT Sloan).",
            "insight": insight_roturas
        }

        return {
            "status": "optimal",
            "objective_value": coste_total,
            "cost_breakdown": cost_breakdown,
            "pedidos": pedidos_programados,
            "resumen": resumen,
            "narrative": narrative
        }

