path = r"C:\Users\Miruna\nexus\app\models\assignment.py"
with open(path, "r", encoding="utf-8-sig") as f:
    c = f.read()

issues = []

# ============================================================
# 1. Simplificar get_infeasible_narrative: solo casos sin equipo compatible
# ============================================================
old = '''    def get_infeasible_narrative(self):
        """Explain why no feasible solution was found."""
        # 1. Casos sin equipo compatible
        impossible_cases = []
        for i in range(self.num_cases):
            req = set(self.cases[i]["required_skills"])
            has_team = False
            for j in range(self.num_teams):
                if req.issubset(set(self.teams[j]["specialties"])):
                    has_team = True
                    break
            if not has_team:
                impossible_cases.append(self.cases[i]["name"])

        # 2. Capacidad total vs demanda
        total_hours = sum(self.cases[i]["hours"] for i in range(self.num_cases))
        capacity_mult = 1.0
        if self.params and "capacity_multiplier" in self.params:
            capacity_mult = float(self.params["capacity_multiplier"]) / 100.0
        total_capacity = sum(
            self.teams[j]["members"] * 6 * capacity_mult
            for j in range(self.num_teams)
        )

        if impossible_cases:
            sample = ", ".join(impossible_cases[:3])
            extra = f" (+{len(impossible_cases) - 3} more)" if len(impossible_cases) > 3 else ""
            insight = f"No team has the required skills for: {sample}{extra}. Add a team with those skills, or remove those cases."
            warning = f"\\u26A0 {len(impossible_cases)} case(s) with no compatible team."
        elif total_hours > total_capacity:
            shortfall = round(total_hours - total_capacity, 0)
            insight = f"Total workload ({total_hours}h) exceeds total capacity ({round(total_capacity, 0)}h). Raise capacity_multiplier or add team members."
            warning = f"\\u26A0 Shortfall: {int(shortfall)}h."
        else:
            insight = "The model could not find a feasible assignment with the current constraints."
            warning = None

        return {
            "status": "infeasible",
            "narrative": {
                "titular": f"No feasible assignment<br><span class=\\'hero-metrics\\'>{self.num_cases} {self.unit_name}s \\u00B7 {self.num_teams} teams \\u00B7 check the constraints</span>",
                "comparacion": f"Total demand: {int(total_hours)}h. Total capacity: {int(total_capacity)}h.",
                "insight": insight,
                "warning": warning,
            }
        }'''

new = '''    def get_infeasible_narrative(self):
        """Explain why no feasible solution was found."""
        # Casos sin equipo compatible
        impossible_cases = []
        for i in range(self.num_cases):
            req = set(self.cases[i]["required_skills"])
            has_team = False
            for j in range(self.num_teams):
                if req.issubset(set(self.teams[j]["specialties"])):
                    has_team = True
                    break
            if not has_team:
                impossible_cases.append(self.cases[i]["name"])

        total_hours = sum(self.cases[i]["hours"] for i in range(self.num_cases))

        if impossible_cases:
            sample = ", ".join(impossible_cases[:3])
            extra = f" (+{len(impossible_cases) - 3} more)" if len(impossible_cases) > 3 else ""
            insight = f"No team has the required skills for: {sample}{extra}. Add a team with those skills, or remove those cases."
            warning = f"\\u26A0 {len(impossible_cases)} case(s) with no compatible team."
        else:
            insight = "The model could not find a feasible assignment with the current constraints."
            warning = None

        return {
            "status": "infeasible",
            "narrative": {
                "titular": f"No feasible assignment<br><span class=\\'hero-metrics\\'>{self.num_cases} {self.unit_name}s \\u00B7 {self.num_teams} teams \\u00B7 check the constraints</span>",
                "comparacion": f"Total demand: {int(total_hours)}h across {self.num_cases} {self.unit_name}s.",
                "insight": insight,
                "warning": warning,
            }
        }'''

if old in c:
    c = c.replace(old, new, 1)
    print("OK: get_infeasible_narrative simplificado")
else:
    issues.append("infeasible")

# ============================================================
# 2. Cambiar umbral del warning de 5 a 15 dias
# ============================================================
old2 = '''        warning = None
        if max_backlog > 5 and busiest:
            warning = f"\\u26A0 {busiest['name']} is {busiest['backlog_days']} days behind. Consider rebalancing or adding capacity."'''

new2 = '''        warning = None
        if max_backlog > 30 and busiest:
            warning = f"\\u26A0 {busiest['name']} is {busiest['backlog_days']} days behind \\u2014 exceeds the standard 30-day resolution timeframe."
        elif max_backlog > 15 and busiest:
            warning = f"\\u26A0 {busiest['name']} is {busiest['backlog_days']} days behind \\u2014 approaching the 15-day regulatory limit."'''

if old2 in c:
    c = c.replace(old2, new2, 1)
    print("OK: warning 15/30 dias")
else:
    issues.append("warning")

if issues:
    print("")
    print("MISS: " + ", ".join(issues))

with open(path, "w", encoding="utf-8") as f:
    f.write(c)
