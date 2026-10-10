"""
Cookbook 02 - Task Assignment to Specialized Teams
====================================================

Problem type : Assignment
Industry     : Media
Scenario     : Marketing agency projects

Uses the same Nexus AssignmentModel that powers every assignment scenario.
Same math, different data.

Run: python cookbooks/02_task_assignment_teams.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.assignment import AssignmentModel
from cookbooks._common import load_json, banner, print_narrative


def main():
    banner("Cookbook 02 - Task Assignment to Specialized Teams")

    # 1. Load a real-world instance: 5 projects, 3 teams
    data = load_json("data/assignment/proyectos_equipos.json")

    # 2. Build and solve with the same engine used by every assignment scenario
    model = AssignmentModel()
    model.cargar_datos(data_dict=data)
    model.build()
    model.solve()

    # 3. Print the narrative result
    results = model.get_results()
    print_narrative(results)

    # 4. Print the assignments
    print("  Assignments:")
    for a in results.get("asignaciones", []):
        print("    " + a["proyecto"] + " -> " + a["equipo"]
              + " · " + str(a["horas"]) + "h · "
              + str(a["valor"]) + " EUR")
    print()


if __name__ == "__main__":
    main()
