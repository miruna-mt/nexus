from ortools.linear_solver import pywraplp
import json


PRIORITY_WEIGHTS = {"high": 3, "medium": 2, "low": 1}
HOURS_PER_MEMBER_PER_DAY = 6.0


class AssignmentModel:
    def __init__(self):
        self.name = "Case Assignment to Specialized Teams"
        self.description = "Balances caseload across teams to minimize maximum backlog"
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

        self.teams = data["teams"]
        self.cases = data["cases"]
        self.num_teams = len(self.teams)
        self.num_cases = len(self.cases)
        self.unit_name = data.get("unit_name", "case")
        print(f"Datos cargados: {self.num_cases} casos, {self.num_teams} equipos")

    def build(self):
        print("Construyendo modelo de asignacion (minimax backlog)...")

        self.capacity_multiplier = 1.0
        if self.params and "capacity_multiplier" in self.params:
            self.capacity_multiplier = float(self.params["capacity_multiplier"]) / 100.0
            print(f"Multiplicador de capacidad: {self.capacity_multiplier}")

        self.solver = pywraplp.Solver.CreateSolver("SCIP")
        if not self.solver:
            return False

        # x[i][j] = 1 si el caso i va al equipo j
        self.x = {}
        for i in range(self.num_cases):
            for j in range(self.num_teams):
                self.x[(i, j)] = self.solver.IntVar(0, 1, f"x_{i}_{j}")

        # B = backlog maximo ponderado (variable auxiliar)
        self.B = self.solver.NumVar(0, self.solver.infinity(), "B")

        # Cada caso va a exactamente 1 equipo
        for i in range(self.num_cases):
            constraint = self.solver.Constraint(1, 1, f"one_team_{i}")
            for j in range(self.num_teams):
                constraint.SetCoefficient(self.x[(i, j)], 1)

        # Incompatibilidad de habilidades
        for i in range(self.num_cases):
            req = set(self.cases[i]["required_skills"])
            for j in range(self.num_teams):
                spec = set(self.teams[j]["specialties"])
                if not req.issubset(spec):
                    self.x[(i, j)].SetUb(0)

        # Backlog ponderado por equipo <= B
        for j in range(self.num_teams):
            constraint = self.solver.Constraint(-self.solver.infinity(), 0, f"backlog_team_{j}")
            constraint.SetCoefficient(self.B, -1)
            for i in range(self.num_cases):
                w = PRIORITY_WEIGHTS.get(self.cases[i]["priority"], 1)
                h = self.cases[i]["hours"]
                constraint.SetCoefficient(self.x[(i, j)], h * w)

        # Objetivo: minimizar B
        objective = self.solver.Objective()
        objective.SetCoefficient(self.B, 1)
        objective.SetMinimization()

        print(f"Modelo construido: {self.solver.NumVariables()} variables, {self.solver.NumConstraints()} restricciones")
        return True

    def solve(self):
        print("Resolviendo modelo de asignacion...")
        status = self.solver.Solve()
        if status == pywraplp.Solver.OPTIMAL:
            print(f"Solucion optima! Backlog maximo ponderado: {self.B.solution_value():.1f}")
            return True
        elif status == pywraplp.Solver.FEASIBLE:
            print(f"Mejor solucion encontrada en el tiempo limite: Backlog {self.B.solution_value():.1f}")
            return True
        else:
            print(f"No se encontro solucion. Status: {status}")
            return False

    def get_results(self):
        team_stats = []
        for j in range(self.num_teams):
            assigned = 0
            raw_hours = 0.0
            weighted_hours = 0.0
            for i in range(self.num_cases):
                if self.x[(i, j)].solution_value() > 0.5:
                    assigned += 1
                    h = self.cases[i]["hours"]
                    w = PRIORITY_WEIGHTS.get(self.cases[i]["priority"], 1)
                    raw_hours += h
                    weighted_hours += h * w

            members = self.teams[j]["members"]
            daily_capacity = members * HOURS_PER_MEMBER_PER_DAY * self.capacity_multiplier
            backlog_days = round(raw_hours / daily_capacity, 1) if daily_capacity > 0 else 0.0

            team_stats.append({
                "name": self.teams[j]["name"],
                "assigned": assigned,
                "raw_hours": round(raw_hours, 1),
                "weighted_hours": round(weighted_hours, 1),
                "backlog_days": backlog_days,
            })

        max_backlog = max((t["backlog_days"] for t in team_stats), default=0.0)
        avg_backlog = round(sum(t["backlog_days"] for t in team_stats) / len(team_stats), 1) if team_stats else 0.0
        busiest = max(team_stats, key=lambda t: t["backlog_days"]) if team_stats else None
        lightest = min(team_stats, key=lambda t: t["backlog_days"]) if team_stats else None

        insight = (
            f"Busiest: {busiest['name']} ({busiest['backlog_days']}d). "
            f"Lightest: {lightest['name']} ({lightest['backlog_days']}d)."
        ) if busiest and lightest else "No team data."

        warning = None
        if max_backlog > 5 and busiest:
            warning = f"\u26A0 {busiest['name']} is {busiest['backlog_days']} days behind. Consider rebalancing or adding capacity."

        narrative = {
            "titular": f"{self.num_cases} {self.unit_name if self.num_cases == 1 else self.unit_name + 's'} assigned \u00B7 max backlog {max_backlog} days ({busiest['name'] if busiest else 'n/a'})",
            "comparacion": f"Average backlog across teams: {avg_backlog} days.",
            "insight": insight,
            "warning": warning,
        }

        return {
            "status": "optimal",
            "objective_value": round(self.B.solution_value(), 1),
            "teams": team_stats,
            "narrative": narrative,
        }
