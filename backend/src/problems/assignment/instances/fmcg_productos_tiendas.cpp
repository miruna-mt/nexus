#include "fmcg_productos_tiendas.h"
#include <iostream>
#include <fstream>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

FMCGProductosTiendas::FMCGProductosTiendas() : AssignmentModel() {
    name_ = "FMCG - Productos a Tiendas";
    description_ = "Asignación óptima de productos perecederos a tiendas de una cadena de supermercados";
}

    bool FMCGProductosTiendas::Build() {
        std::cout << "Construyendo modelo FMCG..." << std::endl;
        
        // 1. Cargar datos del JSON
        std::string filename = "data/allocation/fmcg_cadena.json";
        std::ifstream f(filename);
        if (!f.is_open()) {
            std::cerr << "Error: no se pudo abrir " << filename << std::endl;
            return true;
        }
        
        json data = json::parse(f);
        horizonte_dias = data["horizonte_dias"];
        
        // Cargar productos
        for (const auto& p : data["productos"]) {
            Product prod;
            prod.id = p["id"];
            prod.nombre = p["nombre"];
            prod.stock = p["stock"];
            prod.precio = p["precio"];
            prod.coste = p["coste"];
            prod.dias_caducidad = p["dias_caducidad"];
            prod.penalizacion_caducidad = p["penalizacion_caducidad"];
            productos.push_back(prod);
        }
        
        // Cargar tiendas
        for (const auto& t : data["tiendas"]) {
            Tienda store;
            store.id = t["id"];
            store.nombre = t["nombre"];
            store.capacidad = t["capacidad"];
            tiendas.push_back(store);
        }
        
        // Cargar demandas
        for (const auto& d : data["demanda_estimada"]) {
            Demanda dem;
            dem.producto_id = d["producto_id"];
            dem.tienda_id = d["tienda_id"];
            dem.unidades_por_dia = d["unidades_por_dia"];
            demandas.push_back(dem);
        }
        
        std::cout << "Datos cargados: " << productos.size() << " productos, "
                  << tiendas.size() << " tiendas, "
                  << demandas.size() << " demandas" << std::endl;
        
        // 2. Crear solver
        solver_ = std::make_unique<operations_research::MPSolver>("FMCG_Solver", 
            operations_research::MPSolver::GLOP_LINEAR_PROGRAMMING);
        
        // 3. Crear variables x_{p,t}
        x.resize(productos.size());
        for (size_t p = 0; p < productos.size(); ++p) {
            x[p].resize(tiendas.size());
            for (size_t t = 0; t < tiendas.size(); ++t) {
                x[p][t] = solver_->MakeNumVar(0.0, productos[p].stock, 
                    "x_" + productos[p].id + "_" + tiendas[t].id);
            }
        }
        
        // 4. Crear variables exceso_{p,t}
        exceso.resize(productos.size());
        for (size_t p = 0; p < productos.size(); ++p) {
            exceso[p].resize(tiendas.size());
            for (size_t t = 0; t < tiendas.size(); ++t) {
                exceso[p][t] = solver_->MakeNumVar(0.0, productos[p].stock, 
                    "exceso_" + productos[p].id + "_" + tiendas[t].id);
            }
        }
        
        // 5. Restricciones de stock
        for (size_t p = 0; p < productos.size(); ++p) {
            operations_research::MPConstraint* constraint = solver_->MakeRowConstraint(
                0.0, productos[p].stock, "stock_" + productos[p].id);
            for (size_t t = 0; t < tiendas.size(); ++t) {
                constraint->SetCoefficient(x[p][t], 1.0);
            }
        }
        
        // 6. Restricciones de capacidad de tiendas
        for (size_t t = 0; t < tiendas.size(); ++t) {
            operations_research::MPConstraint* constraint = solver_->MakeRowConstraint(
                0.0, tiendas[t].capacidad, "capacidad_" + tiendas[t].id);
            for (size_t p = 0; p < productos.size(); ++p) {
                constraint->SetCoefficient(x[p][t], 1.0);
            }
        }
        
        // 7. Restricciones de exceso (exceso >= x - ventas_esperadas)
        for (size_t p = 0; p < productos.size(); ++p) {
            for (size_t t = 0; t < tiendas.size(); ++t) {
                // Buscar la demanda para este producto y tienda
                double ventas_esperadas = 0.0;
                for (const auto& d : demandas) {
                    if (d.producto_id == productos[p].id && d.tienda_id == tiendas[t].id) {
                        ventas_esperadas = d.unidades_por_dia * std::min(horizonte_dias, productos[p].dias_caducidad);
                        break;
                    }
                }
                
                operations_research::MPConstraint* constraint = solver_->MakeRowConstraint(
                    ventas_esperadas, solver_->infinity(), "exceso_" + productos[p].id + "_" + tiendas[t].id);
                constraint->SetCoefficient(x[p][t], 1.0);
                constraint->SetCoefficient(exceso[p][t], -1.0);
            }
        }
        
        // 8. Función objetivo: maximizar beneficio - penalización por exceso
        operations_research::MPObjective* objective = solver_->MutableObjective();
        objective->SetMaximization();
        
        for (size_t p = 0; p < productos.size(); ++p) {
            double margen = productos[p].precio - productos[p].coste;
            for (size_t t = 0; t < tiendas.size(); ++t) {
                objective->SetCoefficient(x[p][t], margen);
                objective->SetCoefficient(exceso[p][t], -productos[p].penalizacion_caducidad);
            }
        }
        
        std::cout << "Modelo construido con " << solver_->NumVariables() << " variables y "
                  << solver_->NumConstraints() << " restricciones." << std::endl;
        
        return true;
    }
    
    bool FMCGProductosTiendas::Solve() {
        std::cout << "Resolviendo modelo FMCG..." << std::endl;
        const operations_research::MPSolver::ResultStatus result = solver_->Solve();
        
        if (result == operations_research::MPSolver::OPTIMAL) {
            std::cout << "Solución óptima encontrada!" << std::endl;
            std::cout << "Valor objetivo: " << solver_->Objective().Value() << std::endl;
            return true;
        } else {
            std::cerr << "No se encontró solución óptima. Status: " << result << std::endl;
            return false;
        }
    }
    
    std::string FMCGProductosTiendas::GetResults() const {
        json results;
        results["status"] = "optimal";
        results["objective_value"] = solver_->Objective().Value();
        
        json asignaciones = json::array();
        for (size_t p = 0; p < productos.size(); ++p) {
            for (size_t t = 0; t < tiendas.size(); ++t) {
                if (x[p][t]->solution_value() > 0.001) {
                    json item;
                    item["producto"] = productos[p].nombre;
                    item["tienda"] = tiendas[t].nombre;
                    item["unidades"] = x[p][t]->solution_value();
                    item["exceso"] = exceso[p][t]->solution_value();
                    asignaciones.push_back(item);
                }
            }
        }
        results["asignaciones"] = asignaciones;
        
        return results.dump(2);
    }

// Registrar la instancia
extern "C" AssignmentModel* create() {
    return new FMCGProductosTiendas();
}

extern "C" void destroy(AssignmentModel* p) {
    delete p;
}

