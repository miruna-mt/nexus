"""
Cookbook 05 - Cash-in-Transit Routing
======================================

Problem type : Routing
Industry     : Banking / Security
Scenario     : Cash-in-transit operator in Madrid

Same engine as the agri-food cookbook. Different industry, different data.
Demonstrates the same RoutingModel that handles FMCG also handles
high-security cash movement under tight time windows.

Run: python cookbooks/05_vehicle_routing_cash_transit.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.logistics.routing import RoutingModel
from cookbooks._common import load_json, banner, print_narrative


def main():
    banner("Cookbook 05 - Cash-in-Transit Routing")

    # 1. Load a real-world instance: 4 armored trucks, 24 stops across Madrid
    data = load_json("examples/routing_cash_transit.json")

    # 2. Build and solve with the SAME engine used by agri-food routing
    model = RoutingModel()
    model.cargar_datos(data_dict=data)
    model.build()
    model.solve()

    # 3. Print the narrative result
    results = model.get_results()
    print_narrative(results)

    # 4. Print the routes
    print("  Routes:")
    for ruta in results.get("rutas", []):
        paradas = " -> ".join(ruta.get("paradas", []))
        print("    " + ruta["vehiculo"] + " · " + str(ruta["distancia"]) + " km · " + paradas)
    print()


if __name__ == "__main__":
    main()
