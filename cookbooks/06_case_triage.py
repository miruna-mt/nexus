"""
Cookbook 06 - Case Triage in Banking
=====================================

Problem type : Assignment
Industry     : Banking
Scenario     : Investigations backlog at a mid-size bank

Same AssignmentModel that balances agency project workload, now applied
to banking operations: 200 pending cases across 6 specialized teams.
The model minimizes the busiest team's backlog.

Run: python cookbooks/06_case_triage.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.assignment import AssignmentModel
from cookbooks._common import load_json, banner, print_narrative


def main():
    banner("Cookbook 06 - Case Triage in Banking")

    # 1. Load a realistic backlog: 200 cases, 6 teams
    data = load_json("examples/assignment_case_triage.json")

    # 2. Build and solve with the SAME engine used by workload balancing
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
              + " · " + str(n).rjust(3) + " " + label
              + " · " + str(t["raw_hours"]).rjust(6) + "h"
              + " · backlog " + str(t["backlog_days"]) + "d")
    print()


if __name__ == "__main__":
    main()
