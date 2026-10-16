from ortools.math_opt.python import mathopt
import json


def _normalize_data(data):
    """Accept both English and Spanish field names.
    Returns a dict with Spanish keys (internal canonical format)."""
    def pick(d, *keys):
        for k in keys:
            if k in d:
                return d[k]
        raise KeyError("None of " + str(keys) + " found in " + str(list(d.keys())))

    def norm_asset(a):
        return {
            "id": a.get("id"),
            "nombre": pick(a, "name", "nombre"),
            "rentabilidad": pick(a, "expected_return", "rentabilidad"),
            "riesgo": pick(a, "risk", "riesgo"),
            "limite_max": pick(a, "max_weight", "limite_max"),
            "limite_min": a.get("min_weight", 0.0),
        }

    return {
        "activos": [norm_asset(a) for a in pick(data, "assets", "activos")],
        "capital_total": pick(data, "total_capital", "capital_total"),
        "aversion_riesgo": data.get("risk_aversion", data.get("aversion_riesgo", 2.0)),
        "covarianzas": pick(data, "covariances", "covarianzas"),
        "narrative_domain": data.get("narrative_domain", "finance"),
        "subject": data.get("subject", ""),
        "target_audience": data.get("target_audience", ""),
        "return_unit": data.get("return_unit", "%"),
        "aversion_scale": data.get("aversion_scale", 1.0),
    }


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

        # Normalizar nombres de campos (ES o EN)
        data = _normalize_data(data)

        self.activos = data["activos"]
        self.num_activos = len(self.activos)
        self.capital_total = data.get("capital_total", 100000)
        self.aversion_base = data.get("aversion_riesgo", 2.0)
        self.covarianzas = data["covarianzas"]
        self.narrative_domain = data.get("narrative_domain", "finance")
        self.subject = data.get("subject", "")
        self.target_audience = data.get("target_audience", "")
        self.return_unit = data.get("return_unit", "%")
        self.aversion_scale = data.get("aversion_scale", 1.0)
        print(f"Datos cargados: {self.num_activos} activos")

    def build(self):
        print("Construyendo modelo de Markowitz (cuadratico)...")

        aversion = self.aversion_base
        if self.params and "aversion_riesgo" in self.params:
            aversion = float(self.params["aversion_riesgo"])
            print(f"Aversion al riesgo: {aversion}")

        rentabilidades = [a["rentabilidad"] for a in self.activos]

        if self.params and "content_seo_override" in self.params:
            pct = float(self.params["content_seo_override"]) / 100.0
            for i, a in enumerate(self.activos):
                if a["nombre"] == "Content & SEO":
                    rentabilidades[i] = rentabilidades[i] * (1 + pct)
                    print(f"Content & SEO override: {pct*100:+.1f}%")
                    break

        if self.params and "rentabilidad_tech" in self.params:
            nueva = float(self.params["rentabilidad_tech"]) / 100.0
            for i, a in enumerate(self.activos):
                if a["id"] == "A001":
                    rentabilidades[i] = nueva
                    print(f"Rentabilidad Tech: {nueva}")
                    break

        self.model = mathopt.Model(name="markowitz")

        max_exp = None
        if self.params and "max_exposure" in self.params:
            max_exp = float(self.params["max_exposure"]) / 100.0
            print(f"Max exposure per block: {max_exp*100:.0f}%")

        # Minimo global (override del slider) o min_weight por activo
        global_min = None
        if self.params and "min_per_channel" in self.params:
            global_min = float(self.params["min_per_channel"]) / 100.0
            print(f"Minimo global por canal: {global_min*100:.1f}%")

        self.w = []
        for i in range(self.num_activos):
            ub = self.activos[i]["limite_max"]
            if max_exp is not None:
                ub = min(ub, max_exp)

            lb = self.activos[i].get("limite_min", 0.0)
            if global_min is not None:
                lb = max(lb, global_min)

            self.w.append(self.model.add_variable(
                lb=lb,
                ub=ub,
                name=f"w_{i}"
            ))

        capital_constraint = self.model.add_linear_constraint(
            mathopt.fast_sum(self.w) == 1.0,
            name="capital_total"
        )

        if self.params and "diversification_floor" in self.params:
            div_floor = float(self.params["diversification_floor"]) / 100.0
            if div_floor > 0:
                print(f"Diversification floor: {div_floor*100:.1f}%")
                for i in range(self.num_activos):
                    self.model.add_linear_constraint(
                        self.w[i] >= div_floor,
                        name=f"div_floor_{i}"
                    )

        rendimiento = mathopt.fast_sum(
            self.w[i] * rentabilidades[i] for i in range(self.num_activos)
        )

        varianza = mathopt.fast_sum(
            self.w[i] * self.w[j] * self.covarianzas[i][j]
            for i in range(self.num_activos)
            for j in range(self.num_activos)
        )

        self.rentabilidades_efectivas = rentabilidades
        self.model.maximize(rendimiento - aversion * self.aversion_scale * varianza)

        print(f"Modelo construido con aversion {aversion}")
        return True

    def solve(self):
        print("Resolviendo modelo de Markowitz...")
        params = mathopt.SolveParameters(enable_output=False)
        try:
            self.result = mathopt.solve(self.model, mathopt.SolverType.GSCIP, params=params)
        except Exception as e:
            print(f"No se encontro solucion: {e}")
            self.result = None
            return False

        if self.result.termination.reason == mathopt.TerminationReason.OPTIMAL:
            print("Solucion optima!")
            return True
        else:
            print(f"No se encontro solucion: {self.result.termination}")
            return False

    def get_infeasible_narrative(self):
        """Explain why no feasible solution was found."""
        # Calcular minimos y maximos efectivos
        global_min = None
        if self.params and "min_per_channel" in self.params:
            global_min = float(self.params["min_per_channel"]) / 100.0

        max_exp = None
        if self.params and "max_exposure" in self.params:
            max_exp = float(self.params["max_exposure"]) / 100.0

        total_min = 0.0
        total_max = 0.0
        conflicts = []
        for a in self.activos:
            lb = a.get("limite_min", 0.0)
            if global_min is not None:
                lb = max(lb, global_min)
            ub = a["limite_max"]
            if max_exp is not None:
                ub = min(ub, max_exp)
            if lb > ub:
                conflicts.append(a["nombre"])
            total_min += lb
            total_max += ub

        if conflicts:
            insight = f"Some channels have minimum > maximum: {', '.join(conflicts)}. Reduce the minimum or raise the channel cap."
            warning = f"\u26A0 {len(conflicts)} channel(s) with conflicting bounds."
        elif total_min > 1.0:
            insight = f"Sum of minimums ({round(total_min*100, 0)}%) exceeds 100%. Lower the minimum per channel or reduce the number of channels."
            warning = f"\u26A0 Minimum allocation exceeds total budget by {round((total_min - 1.0)*100, 0)} points."
        elif total_max < 1.0:
            insight = f"Sum of maximums ({round(total_max*100, 0)}%) is below 100%. Raise the channel caps."
            warning = f"\u26A0 Maximum allocation is {round((1.0 - total_max)*100, 0)} points short of 100%."
        else:
            insight = "The model could not find a feasible allocation with the current constraints."
            warning = None

        return {
            "status": "infeasible",
            "narrative": {
                "titular": f"No feasible allocation<br><span class=\'hero-metrics\'>{len(self.activos)} channels \u00B7 check the constraints</span>",
                "comparacion": f"Total minimum required: {round(total_min*100, 0)}%. Total maximum allowed: {round(total_max*100, 0)}%.",
                "insight": insight,
                "warning": warning,
            }
        }

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
                    "rentabilidad_pct": round(self.rentabilidades_efectivas[i] * 100, 2),
                    "riesgo_pct": round(activo["riesgo"] * 100, 2)
                })
                rentabilidad_total += pesos[i] * self.rentabilidades_efectivas[i]

        for i in range(self.num_activos):
            for j in range(self.num_activos):
                varianza_total += pesos[i] * pesos[j] * self.covarianzas[i][j]

        riesgo_portfolio = varianza_total ** 0.5

        # Formato de la metrica de retorno segun el return_unit
        if self.return_unit == "%":
            metric = f"{round(rentabilidad_total*100, 2)}% return"
        else:
            metric = f"{round(rentabilidad_total, 2)} {self.return_unit}"

        # Identificar top asset
        top = max(cartera, key=lambda x: x["peso_pct"]) if cartera else None
        top_str = f"{top['activo']} ({top['peso_pct']}%)" if top else "n/a"

        # Narrativa por dominio
        if self.narrative_domain == "media_planning":
            parts = ["Media mix"]
            if self.subject:
                parts.append(self.subject)
            if self.target_audience:
                parts.append(self.target_audience)
            context_line = " \u00B7 ".join(parts)
            if self.return_unit == "GRP":
                total_reach = round(rentabilidad_total * self.capital_total / 1000, 0)
                metric_value = f"{int(total_reach)} GRP"
            else:
                metric_value = f"{round(rentabilidad_total, 2)} {self.return_unit}"
            metric_line = f"{metric_value} \u00B7 {round(riesgo_portfolio*100, 2)}% volatility"
            titular = f"{context_line}<br><span class='hero-metrics'>{metric_line}</span>"

            narrative = {
                "titular": titular,
                "comparacion": f"Concentrated in the {len(cartera)} most efficient media. Raising risk aversion would diversify further but reduce total reach.",
                "insight": f"Largest allocation: {top_str}.",
            }
        elif self.narrative_domain == "marketing":
            parts = ["Annual marketing budget"]
            if self.subject:
                parts.append(self.subject)
            context_line = " \u00B7 ".join(parts)
            metric_line = f"{metric} \u00B7 {round(riesgo_portfolio*100, 2)}% volatility"
            titular = f"{context_line}<br><span class='hero-metrics'>{metric_line}</span>"

            narrative = {
                "titular": titular,
                "comparacion": "Quadratic optimization accounts for correlations between blocks \u2014 a more diversified mix than a flat allocation. Optimal results may deviate from the standard 70-20-10 framework when ROI differences are strong.",
                "insight": f"Top pick: {top_str}.",
            }
        else:  # finance (default)
            parts = ["Portfolio"]
            if self.subject:
                parts.append(self.subject)
            context_line = " \u00B7 ".join(parts)
            metric_line = f"{metric} \u00B7 {round(riesgo_portfolio*100, 2)}% volatility"
            titular = f"{context_line}<br><span class='hero-metrics'>{metric_line}</span>"

            narrative = {
                "titular": titular,
                "comparacion": "Quadratic optimization accounts for correlations \u2014 a more diversified allocation than the linear model.",
                "insight": f"Markowitz (Nobel Prize, 1990). This portfolio holds {len(cartera)} assets.",
            }

        return {
            "status": "optimal",
            "objective_value": round(rentabilidad_total * 100, 2),
            "cartera": cartera,
            "rentabilidad_esperada_pct": round(rentabilidad_total * 100, 2),
            "riesgo_estimado_pct": round(riesgo_portfolio * 100, 2),
            "narrative": narrative
        }
