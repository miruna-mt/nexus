import os
import json
import subprocess

base = r"C:\Users\Miruna\nexus"
issues = []

# ============================================================
# 1. Renombrar el cookbook 02 con git mv
# ============================================================
old_name = "02_workload_balancing.py"
new_name = "02_team_capacity_planning.py"
result = subprocess.run(
    ["git", "mv", "cookbooks/" + old_name, "cookbooks/" + new_name],
    cwd=base, capture_output=True, text=True
)
if result.returncode == 0:
    print("OK: renombrado a " + new_name)
else:
    print("MISS: git mv fallo - " + result.stderr.strip())
    raise SystemExit(1)

# ============================================================
# 2. Actualizar banner + docstring del cookbook
# ============================================================
path = os.path.join(base, r"cookbooks", new_name)
with open(path, "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace("Cookbook 02 - Workload Balancing", "Cookbook 02 - Team Capacity Planning", 1)
c = c.replace('banner("Cookbook 02 - Workload Balancing")', 'banner("Cookbook 02 - Team Capacity Planning")', 1)

# Actualizar docstring scenario
old_doc = "Scenario     : Marketing agency project allocation"
new_doc = "Scenario     : Marketing agency team capacity planning"
c = c.replace(old_doc, new_doc, 1)

# Actualizar Run path
c = c.replace("Run: python cookbooks/02_workload_balancing.py", "Run: python cookbooks/02_team_capacity_planning.py", 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(c)
print("OK: banner + docstring actualizados")

# ============================================================
# 3. README de cookbooks
# ============================================================
path = os.path.join(base, r"cookbooks\README.md")
with open(path, "r", encoding="utf-8") as f:
    r = f.read()

old_row = "| 02 | `02_workload_balancing.py` | Assignment | Media |"
new_row = "| 02 | `02_team_capacity_planning.py` | Assignment | Media |"
if old_row in r:
    r = r.replace(old_row, new_row, 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(r)
    print("OK: README actualizado")
else:
    issues.append("README")

# ============================================================
# 4. frontend/script.js
# ============================================================
path = os.path.join(base, r"frontend\script.js")
with open(path, "r", encoding="utf-8") as f:
    c = f.read()

old = "name: 'Assignment - Workload Balancing',"
new = "name: 'Assignment - Team Capacity Planning',"
if old in c:
    c = c.replace(old, new, 1)
    print("OK: script.js name actualizado")
else:
    issues.append("script.js")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

# ============================================================
# 5. assignment.py: leer warning_threshold_days + lenguaje "queued work"
# ============================================================
path = os.path.join(base, r"app\models\assignment.py")
with open(path, "r", encoding="utf-8-sig") as f:
    c = f.read()

# 5a. Normalizador: preservar warning_threshold_days
old = '''    return {
        "proyectos": [norm_project(p) for p in pick(data, "projects", "proyectos")],
        "equipos":   [norm_team(t)    for t in pick(data, "teams",    "equipos")],
        "unit_name": data.get("unit_name", "case"),
        "subject":   data.get("subject", ""),
    }'''
new = '''    return {
        "proyectos": [norm_project(p) for p in pick(data, "projects", "proyectos")],
        "equipos":   [norm_team(t)    for t in pick(data, "teams",    "equipos")],
        "unit_name": data.get("unit_name", "case"),
        "subject":   data.get("subject", ""),
        "warning_threshold_days": data.get("warning_threshold_days", 15),
    }'''
if old in c:
    c = c.replace(old, new, 1)
    print("OK: normalizador con warning_threshold_days")
else:
    issues.append("normalizador")

# 5b. cargar_datos
old = 'self.subject = data.get("subject", "")'
new = 'self.subject = data.get("subject", "")\n        self.warning_threshold_days = data.get("warning_threshold_days", 15)'
if old in c:
    c = c.replace(old, new, 1)
    print("OK: cargar_datos lee warning_threshold_days")
else:
    issues.append("cargar_datos")

# 5c. Warning con lenguaje nuevo
old = '''        warning = None
        if max_backlog > 30 and busiest:
            warning = f"\\u26A0 {busiest['name']} is {busiest['backlog_days']} days behind \\u2014 exceeds the standard 30-day resolution timeframe."
        elif max_backlog > 15 and busiest:
            warning = f"\\u26A0 {busiest['name']} is {busiest['backlog_days']} days behind \\u2014 approaching the 15-day regulatory limit."'''

new = '''        warning = None
        if max_backlog > self.warning_threshold_days * 2 and busiest:
            warning = f"\\u26A0 {busiest['name']} has {busiest['backlog_days']} days of queued work \\u2014 well above the {self.warning_threshold_days}-day threshold."
        elif max_backlog > self.warning_threshold_days and busiest:
            warning = f"\\u26A0 {busiest['name']} has {busiest['backlog_days']} days of queued work \\u2014 above the {self.warning_threshold_days}-day threshold."'''

if old in c:
    c = c.replace(old, new, 1)
    print("OK: warning con queued work + threshold configurable")
else:
    issues.append("warning")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

# ============================================================
# 6. JSONs: warning_threshold_days + subject actualizado
# ============================================================
jsons = {
    r"data\assignment\proyectos_equipos.json": {
        "warning_threshold_days": 45,
        "subject": "Team capacity \u00b7 Marketing agency",
    },
    r"examples\assignment_agency_sample.json": {
        "warning_threshold_days": 45,
        "subject": "Team capacity \u00b7 Creative studio",
    },
    r"data\assignment\assignment_case_triage.json": {
        "warning_threshold_days": 15,
        "subject": "Bank investigations \u00b7 Case triage",
    },
    r"examples\assignment_case_triage_sample.json": {
        "warning_threshold_days": 15,
        "subject": "Investment bank \u00b7 Trade settlement",
    },
}

for rel, updates in jsons.items():
    p = os.path.join(base, rel)
    with open(p, "r", encoding="utf-8-sig") as f:
        d = json.load(f)
    for k, v in updates.items():
        d[k] = v
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    print("OK: " + rel)

if issues:
    print("")
    print("MISS: " + ", ".join(issues))
