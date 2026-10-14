"""
Cookbook 08 - Marketing Budget Allocation
==========================================

Problem type : Portfolio
Industry     : Media / Marketing
Scenario     : CMO allocating EUR 1M across 6 strategic investment blocks

Same Markowitz engine used for financial portfolios, now applied to
marketing: blocks have expected ROI and variance, and the model
maximizes risk-adjusted return under per-block budget caps.

Run: python cookbooks/08_portfolio_marketing_budget.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.portfolio import PortfolioModel
from cookbooks._common import load_json, banner, print_narrative


def main():
    banner("Cookbook 08 - Marketing Budget Allocation")

    # 1. Load a real-world instance: EUR 1M across 6 investment blocks
    data = load_json("data/portfolio/portfolio_marketing_budget.json")

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
        print("    " + c["activo"].ljust(22)
              + " \u00B7 " + str(c["peso_pct"]).rjust(5) + "%"
              + " \u00B7 EUR " + str(int(c["inversion"])).rjust(7)
              + " \u00B7 ROI " + str(c["rentabilidad_pct"]) + "%"
              + " \u00B7 risk " + str(c["riesgo_pct"]) + "%")
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
    print("    " + str(total_return) + "% expected ROI \u00B7 " + str(total_risk) + "% volatility")
    print("    -> If blocks moved independently, risk would be ~" + str(round(weighted_risk, 2)) + "%.")
    print("       Diversification saves ~" + str(saved) + " points of risk.")
    print()

    # 6. 70-20-10 framework view
    core = ["Performance Media", "Web & CRO"]
    growth = ["Brand Media", "Content & SEO"]
    experiment = ["PR & Events", "Creative Production"]

    def bucket_weight(names):
        return sum(c["peso_pct"] for c in results["cartera"] if c["activo"] in names)

    print("  Framework view (70-20-10):")
    print("    Core / Performance     " + str(round(bucket_weight(core), 1)).rjust(5) + "%"
          + "   -> " + ", ".join(core))
    print("    Growth / Brand         " + str(round(bucket_weight(growth), 1)).rjust(5) + "%"
          + "   -> " + ", ".join(growth))
    print("    Experimentation        " + str(round(bucket_weight(experiment), 1)).rjust(5) + "%"
          + "   -> " + ", ".join(experiment))
    print()


if __name__ == "__main__":
    main()
