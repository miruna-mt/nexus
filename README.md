# Nexus

**Multi-problem optimization engine in C++**  
Turn business problems into optimal decisions.

Built on a **taxonomy of optimization problems** that transcend industries:
📦 **Resource Allocation** | 🗺️ **Routing** | 💰 **Portfolio Optimization** | 📊 **Inventory Management** | 📍 **Facility Location** | 🎲 **Stochastic Optimization** | 📅 **Project Scheduling**

---

## 🧠 What is Nexus?

Nexus is a **C++ optimization framework** with a web interface that solves **real-world resource allocation problems** by recognizing that the same mathematical structures appear across industries.

Instead of organizing by sector, Nexus organizes by **problem type**:
- **Allocation**: assign scarce resources (FMCG, defense, cloud)
- **Routing**: plan routes and schedules (logistics, defense, industrial)
- **Portfolio**: select optimal combinations under risk (finance, energy, R&D)
- **Inventory**: manage stock levels (FMCG, defense, energy)
- **Location**: decide where to place facilities (logistics, energy, retail)

Each problem type has a **core mathematical model**, and industries are just **instances** with different data.

---

## ✨ Features

- 🔧 **Generic core** – Optimization engine built with Google OR-Tools
- 🧩 **Problem-based taxonomy** – Same code, different data
- 🌐 **Web interface** – User-friendly frontend (HTML/JS/CSS)
- 📊 **7 problem types × multiple industries** = 20+ instances included
- 🔄 **Easily extensible** – Add a new instance by creating a JSON file

---

## 🚀 Quick Start

```bash
git clone https://github.com/miruna-mt/nexus.git
cd nexus/backend && mkdir build && cd build
cmake .. && make
./nexus
# Then open http://localhost:8080

---

🛠️ Tech Stack
Backend: C++17, Crow (web framework), OR-Tools (optimization), nlohmann/json

Frontend: HTML, CSS, JavaScript (vanilla)

Build: CMake + vcpkg

---

📁 Project Structure

nexus/
├── backend/
│   ├── src/
│   │   ├── core/               # Abstract optimization engine
│   │   ├── problems/            # Problem taxonomy
│   │   │   ├── allocation/      # Allocation models
│   │   │   │   └── instances/   # FMCG, defense, cloud...
│   │   │   ├── routing/         # Routing models
│   │   │   │   └── instances/   # Logistics, patrol...
│   │   │   ├── portfolio/       # Portfolio models
│   │   │   │   └── instances/   # Finance, energy...
│   │   │   ├── inventory/       # Inventory models
│   │   │   │   └── instances/   # FMCG, defense...
│   │   │   └── location/        # Location models
│   │   │       └── instances/   # Warehouses, windfarms...
│   │   └── data/                # JSON data for each instance
│   └── build/
├── frontend/                     # Web interface
└── docs/                         # GitHub Pages documentation

---

📄 License
MIT License – feel free to use, modify, and distribute.

---

👤 Author
Miruna Trufin – Simplifying the impossible, one 'what if...?' at a time.


