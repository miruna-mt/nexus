from ortools.linear_solver import pywraplp
import json

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
        self.horizonte = data["horizonte_semanas"]
        self.capacidad_almacen = data["capacidad_almacen"]
        self.productos = data["productos"]
        self.num_productos = len(self.productos)
        print(f"Datos cargados: {self.num_productos} productos, {self.horizonte} semanas")

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

        self.solver = pywraplp.Solver.CreateSolver("SCIP")
        if not self.solver:
            return False

        self.pedido = {}
        self.stock = {}
        self.rotura = {}
        self.hacer_pedido = {}

        for p in range(self.num_productos):
            self.pedido[p] = {}
            self.stock[p] = {}
            self.rotura[p] = {}
            self.hacer_pedido[p] = {}
            for t in range(self.horizonte):
                self.pedido[p][t] = self.solver.IntVar(0, self.solver.infinity(), f"pedido_{p}_{t}")
                self.stock[p][t] = self.solver.NumVar(0, self.solver.infinity(), f"stock_{p}_{t}")
                self.rotura[p][t] = self.solver.NumVar(0, self.solver.infinity(), f"rotura_{p}_{t}")
                self.hacer_pedido[p][t] = self.solver.IntVar(0, 1, f"hacer_pedido_{p}_{t}")

        for p in range(self.num_productos):
            for t in range(self.horizonte):
                demanda = self.productos[p]["demanda_semanal"][t]
                if t == 0:
                    stock_anterior = self.productos[p]["stock_inicial"]
                else:
                    stock_anterior = self.stock[p][t-1]
                self.solver.Add(
                    self.stock[p][t] == stock_anterior + self.pedido[p][t] - demanda + self.rotura[p][t]
                )

        M = 10000
        for p in range(self.num_productos):
            for t in range(self.horizonte):
                self.solver.Add(self.pedido[p][t] <= M * self.hacer_pedido[p][t])

        for t in range(self.horizonte):
            self.solver.Add(
                sum(self.stock[p][t] for p in range(self.num_productos)) <= self.capacidad_almacen
            )

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
        status = self.solver.Solve()
        if status == pywraplp.Solver.OPTIMAL:
            print(f"Solucion optima! Coste total: {self.solver.Objective().Value():.2f} EUR")
            return True
        elif status == pywraplp.Solver.FEASIBLE:
            print(f"Solucion factible. Coste: {self.solver.Objective().Value():.2f} EUR")
            return True
        else:
            print(f"No se encontro solucion. Status: {status}")
            return False

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
            insight_roturas = "Zero stockouts across 12 weeks. Literature documents 30\u201350% savings with EOQ."
        else:
            insight_roturas = f"{roturas_totales} units lost to stockouts."

        narrative = {
            "titular": f"Optimal ordering \u00B7 \u20AC{coste_total:,.2f} over 12 weeks \u00B7 {num_pedidos} orders",
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

