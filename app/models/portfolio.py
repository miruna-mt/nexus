from ortools.math_opt.python import mathopt
import json


class PortfolioModel:
    def __init__(self):
        self.name = "Portfolio - Markowitz"
        self.description = "Optimizacion de cartera con modelo de Markowitz (cuadratico)"
        self.params = None
        self.model = None

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

        self.activos = data["activos"]
        self.num_activos = len(self.activos)
        self.capital_total = data.get("capital_total", 100000)
        self.aversion_base = data.get("aversion_riesgo", 2.0)
        self.covarianzas = data["covarianzas"]
        print(f"Datos cargados: {self.num_activos} activos")

    def build(self):
        print("Construyendo modelo de Markowitz (cuadratico)...")

        aversion = self.aversion_base
        if self.params and "aversion_riesgo" in self.params:
            aversion = float(self.params["aversion_riesgo"])
            print(f"Aversion al riesgo: {aversion}")

        rentabilidades = [a["rentabilidad"] for a in self.activos]
        if self.params and "rentabilidad_tech" in self.params:
            nueva = float(self.params["rentabilidad_tech"]) / 100.0
            for i, a in enumerate(self.activos):
                if a["id"] == "A001":
                    rentabilidades[i] = nueva
                    print(f"Rentabilidad Tech: {nueva}")
                    break

        self.model = mathopt.Model(name="markowitz")

        self.w = []
        for i in range(self.num_activos):
            self.w.append(self.model.add_variable(
                lb=0.0,
                ub=self.activos[i]["limite_max"],
                name=f"w_{i}"
            ))

        capital_constraint = self.model.add_linear_constraint(
            mathopt.fast_sum(self.w) == 1.0,
            name="capital_total"
        )

        rendimiento = mathopt.fast_sum(
            self.w[i] * rentabilidades[i] for i in range(self.num_activos)
        )

        varianza = mathopt.fast_sum(
            self.w[i] * self.w[j] * self.covarianzas[i][j]
            for i in range(self.num_activos)
            for j in range(self.num_activos)
        )

        self.model.maximize(rendimiento - aversion * varianza)

        print(f"Modelo construido con aversion {aversion}")
        return True

    def solve(self):
        print("Resolviendo modelo de Markowitz...")
        params = mathopt.SolveParameters(enable_output=False)
        self.result = mathopt.solve(self.model, mathopt.SolverType.GSCIP, params=params)

        if self.result.termination.reason == mathopt.TerminationReason.OPTIMAL:
            print("Solucion optima!")
            return True
        else:
            print(f"No se encontro solucion: {self.result.termination}")
            return False

    def get_results(self):
        valores = self.result.variable_values()

        cartera = []
        rentabilidad_total = 0
        varianza_total = 0

        pesos = []
        for i in range(self.num_activos):
            peso = valores[self.w[i]]
            pesos.append(peso)

        for i in range(self.num_activos):
            if pesos[i] > 0.001:
                activo = self.activos[i]
                cartera.append({
                    "activo": activo["nombre"],
                    "peso_pct": round(pesos[i] * 100, 1),
                    "inversion": round(pesos[i] * self.capital_total, 0),
                    "rentabilidad_pct": round(activo["rentabilidad"] * 100, 2),
                    "riesgo_pct": round(activo["riesgo"] * 100, 2)
                })
                rentabilidad_total += pesos[i] * activo["rentabilidad"]

        for i in range(self.num_activos):
            for j in range(self.num_activos):
                varianza_total += pesos[i] * pesos[j] * self.covarianzas[i][j]

        riesgo_portfolio = varianza_total ** 0.5

        narrative = {
            "titular": f"Optimal portfolio \u00B7 {round(rentabilidad_total*100, 2)}% return \u00B7 {round(riesgo_portfolio*100, 2)}% volatility",
            "comparacion": "Quadratic optimization accounts for correlations \u2014 a more diversified allocation than the linear model.",
            "insight": f"Markowitz (Nobel Prize, 1990). This portfolio holds {len(cartera)} assets."
        }

        return {
            "status": "optimal",
            "objective_value": round(rentabilidad_total * 100, 2),
            "cartera": cartera,
            "rentabilidad_esperada_pct": round(rentabilidad_total * 100, 2),
            "riesgo_estimado_pct": round(riesgo_portfolio * 100, 2),
            "narrative": narrative
        }
