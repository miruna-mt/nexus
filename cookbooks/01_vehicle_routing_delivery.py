"""
Cookbook 01 - Vehicle Routing for Last-Mile Delivery
=====================================================

Problem type : Routing
Industry     : FMCG
Scenario     : Agri-food distribution (Murcia, Spain)

Uses the same Nexus RoutingModel that powers every routing scenario.
Same math, different data.

Run: python cookbooks/01_vehicle_routing_delivery.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.logistics.routing import RoutingModel
from cookbooks._common import load_json, banner, print_narrative


def main():
    banner("Cookbook 01 - Vehicle Routing for Last-Mile Delivery")

    # 1. Load a real-world instance: 4 trucks, 14 delivery points in Murcia
    data = load_json("data/logistics/routing/logistics_murcia.json")

    # 2. Build and solve with the same engine used by every routing scenario
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
