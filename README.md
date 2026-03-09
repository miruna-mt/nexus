# Nexus
**Connect. Optimize. Decide.**

A multi-industry optimization engine that turns business problems into optimal decisions.

Built on a **taxonomy of optimization problems** that transcend industries:
📦 **Allocation** | 🗺️ **Routing** | 📊 **Inventory** | 💰 **Portfolio** | 📍 **Location** | 🎲 **Stochastic** | 📅 **Scheduling**

---

## 🧠 What is Nexus?

Nexus helps you solve resource allocation problems across different industries with a simple web interface and powerful optimization engine.

Instead of organizing by sector, Nexus organizes by **problem type**. Each problem type has a core mathematical model, and industries are just instances with different data. Just select a scenario, tweak the parameters or upload your own data — the engine does the math, you get the answers.
---

## ✨ Features

- 🔧 **Generic core** – Optimization engine built with Google OR-Tools
- 🧩 **Problem-based taxonomy** – Same code, different data
- 🌐 **Web interface** – User-friendly frontend with 3 interaction levels
- 📊 **3 instances already implemented** (FMCG, Defense, Cloud) out of 21 planned
- 🔄 **Easily extensible** – Add a new instance by creating:
  - C++ code in `backend/src/problems/[tipo]/instances/`
  - Description in `frontend/descriptions/[instancia].html`
  - Result template in `frontend/templates/[instancia].html`

---

## 🚀 Quick Start

```bash
git clone https://github.com/miruna-mt/nexus.git
cd nexus/backend && mkdir build && cd build
cmake .. && make
./nexus
# Then open http://localhost:8080
```

---

## 🏗️ Project Structure

```
nexus/
├── backend/
│   ├── src/
│   │   ├── core/               # Abstract optimization engine
│   │   ├── problems/            # Problem taxonomy
│   │   │   ├── assignment/      # Assignment models
│   │   │   │   └── instances/   # FMCG, Defense, Cloud...
│   │   │   ├── routing/         # (pending)
│   │   │   └── ...
│   │   └── data/                # JSON data for each instance
│   └── build/
├── frontend/
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   ├── descriptions/            # HTML descriptions per instance
│   │   ├── fmcg_productos_tiendas.html
│   │   ├── defense_missions.html
│   │   └── cloud_vms.html
│   └── templates/                # Result templates per instance
│       ├── fmcg_productos_tiendas.html
│       ├── defense_missions.html
│       └── cloud_vms.html
└── docs/
```

---

## ✅ Implemented Instances

| Problem Type | Instance | Status |
|--------------|----------|--------|
| Assignment | FMCG · Products to Stores | ✅ |
| Assignment | Defense · Mission Assignment | ✅ |
| Assignment | Cloud · Virtual Machine Allocation | ✅ |
| Routing | Logistics · Delivery | ⏳ |
| ... | (18 more planned) | ⏳ |

---

## 📄 License

MIT License – feel free to use, modify, and distribute.

---

## 👤 Author

**Miruna Trufin** – Simplifying the impossible, one 'what if...?' at a time.
