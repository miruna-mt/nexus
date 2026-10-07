# Nexus

**Connect. Optimize. Decide.**

A multi-industry optimization engine that turns business problems into optimal decisions.

---

## 🧠 What is Nexus?

Nexus solves resource allocation problems across industries with a simple web interface and a powerful optimization engine.

Instead of organizing by sector, Nexus organizes by **problem type**. Each problem type has a core mathematical model, and industries are just instances with different data.

| Problem type | What it solves |
|--------------|----------------|
| 🚚 **Routing** | Find the optimal route between multiple points |
| 📊 **Assignment** | Assign resources to tasks |
| 📦 **Inventory** | Decide when and how much to order |
| 💰 **Portfolio** | Select combinations under risk |

---

## ✨ Features

- 🔧 **Generic core** — Built with Google OR-Tools
- 🧩 **Problem-based taxonomy** — Same engine, different data
- 🌐 **Web interface** with 3 interaction levels:
  - **Demo** — Predefined scenarios
  - **Parametric** — Adjust parameters with sliders
  - **Expert** — Upload your own JSON *(coming soon)*
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
``` 

Open http://localhost:8080

---

## 📊 Scenarios

Three instances per problem type. One implemented, two planned.

| Routing | Status |
|---------|--------|
| 🍊 Agri-food distribution (Murcia) | ✅ |
| Last-mile delivery | 🔜 |
| Industrial maintenance | 🔜 |

| Assignment | Status |
|------------|--------|
| 📣 Marketing agency projects | ✅ |
| Cloud infrastructure | 🔜 |
| Shift scheduling | 🔜 |

| Inventory | Status |
|-----------|--------|
| 🛒 Supermarket perishables | ✅ |
| Defense ammunition | 🔜 |
| Energy storage | 🔜 |

| Portfolio | Status |
|-----------|--------|
| 💹 Markowitz investment | ✅ |
| R&D project selection | 🔜 |
| Marketing budget allocation | 🔜 |

---

## 🏗️ Architecture

Every model follows the same contract:

```python
SetParams()      # optional user parameters
cargar_datos()   # load JSON data
build()          # variables, constraints, objective
solve()          # run OR-Tools
get_results()    # JSON output + narrative
```

**Adding a new instance**: JSON + description + one line in the config. Nothing else.

**Adding a new problem type**: one new model file. Plugs into the same API and the same UI.

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 🏛️ About MMTrufin StratEdge

Nexus is built by **[MMTrufin StratEdge](https://mtrufin.com)** — an elite, independent consulting boutique specialized in eliminating the translation gap between boardroom strategy and complex execution.

We audit corporate system logic, data flows, and relational architecture to ensure technical implementation aligns perfectly with financial targets. Serving medium to large enterprises across heavily regulated, high-volume, and data-dense industries — including banking, FMCG, media, and security networks.

**Nexus is the proof that we do not stop at the slide deck. We build the engine.*

*Built by Miruna Trufin — a strategist who codes.*
*

