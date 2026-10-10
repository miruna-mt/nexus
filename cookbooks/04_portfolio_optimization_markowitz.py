"""
Cookbook 04 - Portfolio Optimization (Markowitz)
==================================================

Problem type : Portfolio
Industry     : Banking / Finance
Scenario     : Markowitz investment portfolio

Uses the same Nexus PortfolioModel that powers every portfolio scenario.
Same math, different data.

Run: python cookbooks/04_portfolio_optimization_markowitz.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.portfolio import PortfolioModel
from cookbooks._common import load_json, banner, print_narrative


def main():
    banner("Cookbook 04 - Portfolio Optimization (Markowitz)")

    # 1. Load a real-world instance: 6 assets, correlations, capital
    data = load_json("data/portfolio/cartera_markowitz.json")

    # 2. Build and solve with the same engine used by every portfolio scenario
    model = PortfolioModel()
    model.cargar_datos(data_dict=data)
    model.build()
    model.solve()

    # 3. Print the narrative result
    results = model.get_results()
    print_narrative(results)

    # 4. Print the portfolio composition
    print("  Portfolio composition:")
    for c in results.get("cartera", []):
        print("    " + c["activo"].ljust(28)
              + " · " + str(c["peso_pct"]).rjust(5) + "%"
              + " · EUR " + str(c["inversion"])
              + " · return " + str(c["rentabilidad_pct"]) + "%"
              + " · risk " + str(c["riesgo_pct"]) + "%")
    print()


if __name__ == "__main__":
    main()
