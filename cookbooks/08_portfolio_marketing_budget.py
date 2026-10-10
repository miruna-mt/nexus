"""
Cookbook 08 - Marketing Budget Allocation
==========================================

Problem type : Portfolio
Industry     : Media / Marketing
Scenario     : CMO allocating EUR 1M across 6 channels

Same Markowitz engine used for financial portfolios, now applied to
marketing: channels have expected ROI and variance, and the model
maximizes risk-adjusted return under per-channel budget caps.

Run: python cookbooks/08_portfolio_marketing_budget.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.portfolio import PortfolioModel
from cookbooks._common import load_json, banner, print_narrative


def main():
    banner("Cookbook 08 - Marketing Budget Allocation")

    # 1. Load a real-world instance: EUR 1M across 6 marketing channels
    data = load_json("examples/portfolio_marketing_budget.json")

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
        print("    " + c["activo"].ljust(15)
              + " · " + str(c["peso_pct"]).rjust(5) + "%"
              + " · EUR " + str(int(c["inversion"])).rjust(7)
              + " · ROI " + str(c["rentabilidad_pct"]) + "%"
              + " · risk " + str(c["riesgo_pct"]) + "%")
    print()

    # 5. Interpretation: how much risk did diversification actually save?
    total_return = results["rentabilidad_esperada_pct"]
    total_risk = results["riesgo_estimado_pct"]

    weighted_risk = sum(
        (c["peso_pct"] / 100.0) * (c["riesgo_pct"] / 100.0)
        for c in results["cartera"]
    ) * 100

    saved = round(weighted_risk - total_risk, 2)

    print("  Interpretation:")
    print("    " + str(total_return) + "% expected ROI · " + str(total_risk) + "% volatility")
    print("    -> If channels moved independently, risk would be ~" + str(round(weighted_risk, 2)) + "%.")
    print("       Diversification saves ~" + str(saved) + " points of risk.")
    print()


if __name__ == "__main__":
    main()
