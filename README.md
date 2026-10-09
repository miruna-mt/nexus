# Nexus

**Connect. Optimize. Decide.**

A decision engine for strategy under uncertainty.

---

## 🧠 What is Nexus?

Nexus separates the **mathematical structure** of a problem from the **data** that instantiates it.

Instead of organizing by sector, Nexus organizes by **problem type**. Each problem type has a core mathematical model. Industries are just instances with different data — same math, different inputs.

---

## 🔀 How it works: Problem × Industry × Scenario

Every optimization in Nexus is built from three layers:

| Layer | What it is | Example |
|---|---|---|
| **Problem type** | The mathematical model | Routing |
| **Industry** | The sector where the problem appears | FMCG |
| **Scenario** | The concrete instance with real data | Agri-food distribution in Murcia |

The same routing engine that optimizes agri-food delivery can optimize cash-in-transit or patrol routes. **Same math. Different data.**

### What's available today

| Problem | Today | Next (planned) |
|---|---|---|
| 🚚 **Routing** | 🍊 Agri-food · Murcia (FMCG) | Cash-in-transit (Banking) · Patrol routes (Security) |
| 📊 **Assignment** | 📣 Marketing agency (Media) | Customer case triage (Banking) · Leads to reps (Banking) |
| 📦 **Inventory** | 🛒 Supermarket perishables (FMCG) | Ad slots (Media) · Cash replenishment (Banking) |
| 💰 **Portfolio** | 💹 Markowitz investment (Banking) | Marketing budget (Media) · Brand portfolio (Brand) |

Each new instance is a JSON file + an HTML description + one line in the config. **Nothing else.**

---

## ✨ Features

- 🔧 **Generic core** — Built with Google OR-Tools
- 🧩 **Problem-based taxonomy** — Same engine, different data
- 🌐 **Web interface** with 3 interaction levels:
  - **Demo** — Predefined scenarios
  - **Parametric** — Adjust parameters with sliders
  - 🔒 **Privacy-first Expert mode** — Upload your own JSON; it's processed in memory and never stored or logged
- 🗺️ **Interactive maps** for routing
- 📖 **Narrative results** — Every optimization explains what happened and why
- 🔄 **Easily extensible** — Add an instance with a JSON file, an HTML description, and one line in the frontend

---

## 🚀 Quick Start

```bash
git clone https://github.com/miruna-mt/nexus.git
cd nexus
python -m venv venv && venv\Scripts\activate
pip install fastapi uvicorn ortools
uvicorn app.main:app --reload --port 8080

SetParams()      # optional user parameters
cargar_datos()   # load JSON data
build()          # variables, constraints, objective
solve()          # run OR-Tools
get_results()    # JSON output + narrative

Adding a new instance: JSON + description + one line in the config. Nothing else.

Adding a new problem type: one new model file. Plugs into the same API and the same UI.
🗺️ Roadmap

Four more problem types are planned, all in active exploration:

    🏭 Facility Location — where to open warehouses, data centers, stores

    📅 Project Scheduling — sequencing tasks with dependencies and resource constraints

    🎲 Stochastic Optimization — decisions when the future is uncertain

    🎯 Multi-Objective Optimization — trade-offs when more than one goal matters

All four plug into the same API, the same UI, and the same taxonomy.
📄 License

MIT License — free to use, modify, and distribute.
🏛️ About MMTrufin StratEdge

Nexus is built by MMTrufin StratEdge — an elite, independent consulting boutique specialized in eliminating the translation gap between boardroom strategy and complex execution.

We audit corporate system logic, data flows, and relational architecture to ensure technical implementation aligns perfectly with financial targets. Serving medium to large enterprises across heavily regulated, high-volume, and data-dense industries — including banking, FMCG, media, and security networks.

Nexus is the proof that we do not stop at the slide deck. We build the engine.

Built by Miruna Trufin — a strategist who codes.
Simplifying the impossible, one "what if...?" at a time.
