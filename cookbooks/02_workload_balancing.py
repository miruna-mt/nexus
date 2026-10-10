"""
Cookbook 02 - Workload Balancing
=================================

Problem type : Assignment
Industry     : Media
Scenario     : Marketing agency project allocation

Same engine that powers every assignment scenario, now solving it as a
workload-balancing problem: distribute projects across teams so that the
busiest team is as unloaded as possible.

Run: python cookbooks/02_workload_balancing.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.assignment import AssignmentModel
from cookbooks._common import load_json, banner, print_narrative


def main():
    banner("Cookbook 02 - Workload Balancing")

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

    # 4. Print team stats
    unit = data.get("unit_name", "case")
    print("  Team load:")
    for t in results.get("teams", []):
        n = t["assigned"]
        label = unit if n == 1 else unit + "s"
        print("    " + t["name"].ljust(28)
              + " · " + str(n).rjust(2) + " " + label
              + " · " + str(t["raw_hours"]).rjust(6) + "h"
              + " · backlog " + str(t["backlog_days"]) + "d")
    print()


if __name__ == "__main__":
    main()
