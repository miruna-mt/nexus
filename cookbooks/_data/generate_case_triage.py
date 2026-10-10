"""
Generate a realistic dataset for the case triage cookbook.

Represents a snapshot of a bank investigations backlog: ~200 cases
distributed across 6 specialized teams.

Fixed seed so the output is reproducible and stable across runs.

Run: python cookbooks/_data/generate_case_triage.py
"""
import json
import random
import os


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


TEAMS = [
    {"id": "T1", "name": "Accounts Investigations",
     "specialties": ["accounts", "transfers"], "members": 8},
    {"id": "T2", "name": "Card Investigations",
     "specialties": ["cards", "payments"], "members": 9},
    {"id": "T3", "name": "Fraud Unit",
     "specialties": ["fraud", "cards", "accounts"], "members": 6},
    {"id": "T4", "name": "Premium & VIP",
     "specialties": ["premium", "accounts", "cards"], "members": 5},
    {"id": "T5", "name": "Compliance & Regulatory",
     "specialties": ["compliance", "regulatory", "aml"], "members": 5},
    {"id": "T6", "name": "General Complaints",
     "specialties": ["complaints", "general", "accounts", "cards"], "members": 7},
]


# (title_pattern, skills, priority_distribution, hours_range, count)
TEMPLATES = [
    ("Card dispute #{n}",         ["cards"],                        {"low": 0.5, "medium": 0.4, "high": 0.1}, (2, 5), 25),
    ("Chargeback #{n}",           ["cards", "payments"],            {"low": 0.4, "medium": 0.5, "high": 0.1}, (3, 6), 15),
    ("Transfer investigation #{n}", ["accounts", "transfers"],      {"low": 0.3, "medium": 0.5, "high": 0.2}, (3, 7), 20),
    ("Account review #{n}",       ["accounts"],                     {"low": 0.5, "medium": 0.4, "high": 0.1}, (2, 5), 20),
    ("Fraud alert #{n}",          ["fraud", "cards"],               {"low": 0.1, "medium": 0.4, "high": 0.5}, (4, 10), 20),
    ("AML investigation #{n}",    ["fraud", "accounts"],            {"low": 0.1, "medium": 0.4, "high": 0.5}, (5, 12), 15),
    ("Premium retention #{n}",    ["premium", "accounts"],          {"low": 0.2, "medium": 0.4, "high": 0.4}, (3, 7), 15),
    ("VIP escalation #{n}",       ["premium", "cards"],             {"low": 0.1, "medium": 0.3, "high": 0.6}, (4, 8), 10),
    ("Compliance query #{n}",     ["compliance", "regulatory"],     {"low": 0.2, "medium": 0.6, "high": 0.2}, (4, 10), 15),
    ("Regulatory filing #{n}",    ["regulatory", "compliance"],     {"low": 0.2, "medium": 0.5, "high": 0.3}, (5, 12), 10),
    ("General complaint #{n}",    ["complaints", "general"],        {"low": 0.6, "medium": 0.3, "high": 0.1}, (2, 4), 20),
    ("Fee complaint #{n}",        ["complaints", "accounts"],       {"low": 0.7, "medium": 0.3, "high": 0.05}, (2, 4), 15),
]


def generate(seed=42):
    random.seed(seed)
    cases = []
    case_id = 1000

    for pattern, skills, priority_dist, hours_range, count in TEMPLATES:
        for _ in range(count):
            case_id += 1
            num = random.randint(1000, 9999)
            name = pattern.replace("{n}", str(num))

            priorities = list(priority_dist.keys())
            weights = [priority_dist[p] for p in priorities]
            priority = random.choices(priorities, weights=weights, k=1)[0]

            hours = random.randint(hours_range[0], hours_range[1])

            cases.append({
                "id": case_id,
                "name": name,
                "hours": hours,
                "priority": priority,
                "required_skills": skills,
            })

    random.shuffle(cases)

    return {
        "unit_name": "case",
        "teams": TEAMS,
        "cases": cases,
    }


if __name__ == "__main__":
    data = generate(seed=42)
    out_path = os.path.join(REPO_ROOT, "examples", "assignment_case_triage.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    total_hours = sum(c["hours"] for c in data["cases"])
    total_members = sum(t["members"] for t in data["teams"])
    capacity_per_day = total_members * 6
    backlog_days = round(total_hours / capacity_per_day, 1)

    print("OK: examples/assignment_case_triage.json generado")
    print("    " + str(len(data["cases"])) + " cases, " + str(len(data["teams"])) + " teams")
    print("    Total hours: " + str(total_hours) + "h")
    print("    Daily capacity: " + str(capacity_per_day) + "h")
    print("    Backlog if evenly distributed: " + str(backlog_days) + " days")
