#include "AllocationModel.h"
#include <fstream>
#include <iostream>

bool AllocationModel::loadData(const std::string& filename) {
    std::ifstream f(filename);
    if (!f.is_open()) {
        std::cerr << "Error: no se pudo abrir " << filename << std::endl;
        return false;
    }
    
    json data = json::parse(f);
    
    horizonte_dias = data["horizonte_dias"];
    
    // Cargar productos
    for (const auto& p : data["productos"]) {
        productos.push_back({
            p["id"],
            p["nombre"],
            p["stock"],
            p["precio"],
            p["coste"],
            p["dias_caducidad"],
            p["penalizacion_caducidad"]
        });
    }
    
    // Cargar tiendas
    for (const auto& t : data["tiendas"]) {
        tiendas.push_back({
            t["id"],
            t["nombre"],
            t["capacidad"]
        });
    }
    
    // Cargar demandas
    for (const auto& d : data["demanda_estimada"]) {
        demandas.push_back({
            d["producto_id"],
            d["tienda_id"],
            d["unidades_por_dia"]
        });
    }
    
    std::cout << "Datos cargados: " 
              << productos.size() << " productos, "
              << tiendas.size() << " tiendas, "
              << demandas.size() << " demandas" << std::endl;
    
    return true;
}

bool AllocationModel::Build() {
    // Aquí construiremos las variables y restricciones con OR-Tools
    return true;
}

bool AllocationModel::Solve() {
    // Aquí resolveremos
    return true;
}

std::string AllocationModel::GetResults() const {
    // Aquí devolveremos los resultados en JSON
    return "{}";
}
