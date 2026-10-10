"""
Shared helpers for Nexus cookbooks.

Run any cookbook from the repository root:
    python cookbooks/01_vehicle_routing_delivery.py
"""
import json
import os
import sys

# Force UTF-8 output on Windows terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_json(relative_path):
    """Load a JSON file relative to the repo root."""
    full_path = os.path.join(REPO_ROOT, relative_path)
    with open(full_path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def banner(title):
    """Print a consistent header for each cookbook."""
    line = "=" * 60
    print()
    print(line)
    print("  " + title)
    print(line)
    print()


def print_narrative(results):
    """Print the narrative block returned by any Nexus model."""
    narrative = results.get("narrative", {})
    titular = narrative.get("titular", "")
    comparacion = narrative.get("comparacion", "")
    insight = narrative.get("insight", "")
    warning = narrative.get("warning", "")

    if titular:
        print("  " + titular)
    if comparacion:
        print("  -> " + comparacion)
    if insight:
        print("  -> " + insight)
    if warning:
        print()
        print("  " + warning)
    print()
