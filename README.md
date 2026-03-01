# Nexus

**Multi-sector optimization engine in C++**  
Turn business problems into optimal decisions.

Built for: FMCG 🛒 | Defense 🎯 | Energy ⚡ | Banking 💰 | Industrial 🏭

---

## 🚀 What is Nexus?

Nexus is a **C++ optimization framework** with a web interface that solves real-world resource allocation problems across multiple industries.  
It abstracts the common mathematical core while adapting to sector-specific constraints.

## ✨ Features

- 🔧 **Generic core** – Optimization engine built with Google OR-Tools  
- 🧩 **Pluggable sectors** – Add new industries easily  
- 🌐 **Web interface** – User-friendly frontend (HTML/JS/CSS)  
- 📊 **5 sectors included**: FMCG, Defense, Energy, Banking, Industrial  

## 🛠️ Tech Stack

- **Backend**: C++17, Crow (web framework), OR-Tools (optimization), nlohmann/json  
- **Frontend**: HTML, CSS, JavaScript (vanilla)  
- **Build**: CMake + vcpkg  

## 📦 How to run (locally)

1. Clone the repo  
2. Install dependencies (vcpkg + OR-Tools + Crow)  
3. Build with CMake  
4. Run the executable  
5. Open `http://localhost:8080` in your browser  

> Detailed instructions coming soon.

## 📁 Project Structure
nexus-mtrufin.com/
├── backend/ # C++ source code
│ ├── src/ # Core engine and sector models
│ └── data/ # Sample JSON inputs for each sector
├── frontend/ # Web interface (served by backend)
└── docs/ # Documentation (GitHub Pages)


## 📄 License

MIT License – feel free to use, modify, and distribute.

## 👤 Author

Built by Miruna Trufin – strategy consultant who codes.  
Adding C++ to the toolkit to build better optimization tools.
