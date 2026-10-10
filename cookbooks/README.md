# Nexus Cookbooks

**Runnable, self-contained examples of Nexus applied to real business problems.**

Each cookbook is a small Python script that imports a Nexus model directly
(no web server needed), loads a JSON instance, solves it, and prints the
narrative result. They are designed to be read, copied, and adapted.

## Why cookbooks?

Nexus separates the **mathematical structure** of a problem from the **data**
that instantiates it. These cookbooks demonstrate that separation in code:
the same engine powers radically different scenarios with only a JSON swap.

## Available cookbooks

| # | File | Problem | Industry |
|---|------|---------|----------|
| 01 | `01_vehicle_routing_delivery.py` | Routing | FMCG |
| 02 | `02_workload_balancing.py` | Assignment | Media |
| 03 | `03_inventory_optimization.py` | Inventory | FMCG |
| 04 | `04_portfolio_optimization_markowitz.py` | Portfolio | Banking |

More cookbooks coming soon, one per industry × problem combination.

## Running a cookbook

From the repository root, with the virtual environment active:

python cookbooks/01_vehicle_routing_delivery.py


Each cookbook is standalone. No configuration. No server. No JSON editing.

## Structure

Every cookbook follows the same shape:

1. **Load** an instance from `data/` (or your own JSON).
2. **Build and solve** using the shared Nexus model.
3. **Print** the narrative result plus the key outputs.

The shared helper `_common.py` provides `load_json()`, `banner()` and
`print_narrative()` so each cookbook stays under 40 lines.

## Adding your own cookbook

1. Copy any existing cookbook as a template.
2. Point `load_json()` at your own data file.
3. Run it. That is it.

If you build something useful, open a PR. We would love to see new
problem × industry combinations.
