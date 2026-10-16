"""
Cookbook 07 - Multi-Channel Media Planning
================================================

Problem type : Portfolio
Industry     : Media
Scenario     : Multi-channel campaign for a luxury watch brand (EUR 2M)

Same Markowitz engine used for financial portfolios, now applied to media
planning: TV networks have different GRP efficiency and audience volatility,
and the model finds the allocation that maximizes reach for a given risk.

Target: Adults 25-59 · Urban · High income

Run: python cookbooks/07_media_planning.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.portfolio import PortfolioModel
from cookbooks._common import load_json, banner, print_narrative


def main():
    banner("Cookbook 07 - Multi-Channel Media Planning")

    # 1. Load a real-world instance: 12 network x daypart combinations
    data = load_json("data/portfolio/portfolio_media_planning.json")

    # 2. Build and solve with the SAME engine used by financial portfolios
    model = PortfolioModel()
    model.cargar_datos(data_dict=data)
    model.build()
    model.solve()

    # 3. Print the narrative result
    results = model.get_results()
    print_narrative(results)

    # 4. Print the allocation
    print("  Allocation:")
    for c in results.get("cartera", []):
        print("    " + c["activo"].ljust(28)
              + " · " + str(c["peso_pct"]).rjust(5) + "%"
              + " · EUR " + str(int(c["inversion"])).rjust(7))
    print()

    # 5. Interpretation
    roas = results["rentabilidad_esperada_pct"] / 100
    print("  Interpretation:")
    print("    " + str(round(roas, 2)) + " ROAS for EUR " + str(int(data["total_capital"])) + " budget")
    print("    Concentrated on " + str(len(results["cartera"])) + " of " + str(len(data["assets"])) + " available channels")
    print("    -> Raise risk_aversion to diversify; lower it to concentrate further.")
    print()


if __name__ == "__main__":
    main()
