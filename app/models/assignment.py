from ortools.linear_solver import pywraplp
import json

class AssignmentModel:
    def __init__(self):
        self.name = "Asignacion de Proyectos a Equipos"
        self.description = "Maximiza el valor de los proyectos asignados a equipos especializados"
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
        self.proyectos = data["proyectos"]
        self.equipos = data["equipos"]
        self.num_proyectos = len(self.proyectos)
        self.num_equipos = len(self.equipos)
        print(f"Datos cargados: {self.num_proyectos} proyectos, {self.num_equipos} equipos")

    def build(self):
        print("Construyendo modelo de asignacion...")

        multiplicador = 1.0
        bonus = 0.0
        if self.params:
            if "capacidad_equipos" in self.params:
                multiplicador = float(self.params["capacidad_equipos"]) / 100.0
                print(f"Multiplicador de capacidad: {multiplicador}")
            if "bonus_gran_empresa" in self.params:
                bonus = float(self.params["bonus_gran_empresa"])
                print(f"Bonus gran empresa: {bonus}")

        self.solver = pywraplp.Solver.CreateSolver("SCIP")
        if not self.solver:
            return False

        self.x = {}
        self.unassigned = {}
        for i in range(self.num_proyectos):
            self.unassigned[i] = self.solver.IntVar(0, 1, f"unassigned_{i}")
            for j in range(self.num_equipos):
                self.x[(i, j)] = self.solver.IntVar(0, 1, f"x_{i}_{j}")

        # Cada proyecto o se asigna a un equipo o queda sin asignar
        for i in range(self.num_proyectos):
            constraint = self.solver.Constraint(1, 1, f"un_equipo_o_sin_asignar_{i}")
            for j in range(self.num_equipos):
                constraint.SetCoefficient(self.x[(i, j)], 1)
            constraint.SetCoefficient(self.unassigned[i], 1)

        # Capacidad de cada equipo (con multiplicador)
        for j in range(self.num_equipos):
            horas_max = self.equipos[j]["horas_disponibles"] * multiplicador
            constraint = self.solver.Constraint(0, horas_max, f"capacidad_equipo_{j}")
            for i in range(self.num_proyectos):
                constraint.SetCoefficient(self.x[(i, j)], self.proyectos[i]["horas"])

        # Incompatibilidad de habilidades
        for i in range(self.num_proyectos):
            for j in range(self.num_equipos):
                habilidades_proyecto = set(self.proyectos[i]["habilidades_requeridas"])
                habilidades_equipo = set(self.equipos[j]["especialidades"])
                if not habilidades_proyecto.issubset(habilidades_equipo):
                    self.x[(i, j)].SetUb(0)

        # Funcion objetivo: maximizar valor asignado, penalizar no asignados
        PENALTY = 1.3
        objective = self.solver.Objective()
        objective.SetMaximization()
        for i in range(self.num_proyectos):
            valor = self.proyectos[i]["valor"]
            if bonus > 0 and self.proyectos[i]["id"] == 3:
                valor += bonus
                print(f"Bonus al proyecto: {self.proyectos[i]['nombre']}")
            for j in range(self.num_equipos):
                objective.SetCoefficient(self.x[(i, j)], valor)
            objective.SetCoefficient(self.unassigned[i], -valor * PENALTY)

        print(f"Modelo construido: {self.solver.NumVariables()} variables, {self.solver.NumConstraints()} restricciones")
        return True

    def solve(self):
        print("Resolviendo modelo de asignacion...")
        status = self.solver.Solve()
        if status == pywraplp.Solver.OPTIMAL:
            print(f"Solucion optima! Valor total: {self.solver.Objective().Value():.2f} EUR")
            return True
        elif status == pywraplp.Solver.FEASIBLE:
            print(f"Solucion factible. Valor: {self.solver.Objective().Value():.2f} EUR")
            return True
        else:
            print(f"No se encontro solucion. Status: {status}")
            return False

    def get_results(self):
        valor_total = 0
        asignados = []
        proyectos_asignados = set()

        for i in range(self.num_proyectos):
            for j in range(self.num_equipos):
                if self.x[(i, j)].solution_value() > 0.5:
                    asignados.append({
                        "proyecto": self.proyectos[i]["nombre"],
                        "equipo": self.equipos[j]["nombre"],
                        "horas": self.proyectos[i]["horas"],
                        "valor": self.proyectos[i]["valor"]
                    })
                    valor_total += self.proyectos[i]["valor"]
                    proyectos_asignados.add(i)

        proyectos_no_asignados = [
            self.proyectos[i]["nombre"]
            for i in range(self.num_proyectos)
            if i not in proyectos_asignados
        ]

        valor_total_posible = sum(p["valor"] for p in self.proyectos)
        porcentaje = round((valor_total / valor_total_posible) * 100, 1) if valor_total_posible > 0 else 0

        if proyectos_no_asignados:
            insight = f"Unassigned (capacity limit): {', '.join(proyectos_no_asignados)}."
        else:
            insight = "All projects assigned to a compatible team."

        narrative = {
            "titular": f"{len(asignados)} of {self.num_proyectos} projects assigned \u00B7 \u20AC{valor_total:,.0f} \u00B7 {porcentaje}% of maximum value",
            "comparacion": f"Total available value: \u20AC{valor_total_posible:,.0f}.",
            "insight": insight
        }

        return {
            "status": "optimal",
            "objective_value": valor_total,
            "asignaciones": asignados,
            "narrative": narrative
        }

