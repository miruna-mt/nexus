"""
Cookbook 03 - Inventory Optimization for Perishables
=====================================================

Problem type : Inventory
Industry     : FMCG
Scenario     : Supermarket perishables (12-week horizon)

Uses the same Nexus InventoryModel that powers every inventory scenario.
Same math, different data.

Run: python cookbooks/03_inventory_optimization.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.inventory import InventoryModel
from cookbooks._common import load_json, banner, print_narrative


def main():
    banner("Cookbook 03 - Inventory Optimization for Perishables")

    # 1. Load a real-world instance: 6 perishables, 12-week horizon
    data = load_json("data/inventory/supermercado.json")

    # 2. Build and solve with the same engine used by every inventory scenario
    model = InventoryModel()
    model.cargar_datos(data_dict=data)
    model.build()
    model.solve()

    # 3. Print the narrative result
    results = model.get_results()
    print_narrative(results)

    # 4. Print the cost breakdown
    cb = results.get("cost_breakdown", {})
    if cb:
        print("  Cost breakdown:")
        print("    Ordering    : EUR " + str(cb.get("ordering", 0)))
        print("    Storage     : EUR " + str(cb.get("storage", 0)))
        print("    Out-of-stock: EUR " + str(cb.get("stockout", 0)))
    print()


if __name__ == "__main__":
    main()
