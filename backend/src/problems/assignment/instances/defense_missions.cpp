#include "defense_missions.h"
#include <iostream>
#include <fstream>
#include <cmath>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

DefenseMissions::DefenseMissions() : AssignmentModel() {
    name_ = "Defense - Mission Assignment";
    description_ = "Assign military resources to missions maximizing strategic value";
}

double DefenseMissions::distance(int r, int m) const {
    // Euclidean distance between resource base and mission location
    // For simplicity, assume resources are at (0,0) - we can extend later
    double dx = missions_[m].location_x;
    double dy = missions_[m].location_y;
    return std::sqrt(dx*dx + dy*dy);
}

bool DefenseMissions::Build() {
    std::cout << "🚁 Building Defense Missions model..." << std::endl;
    
    // 1. Cargar datos del JSON
    std::string filename = "data/assignment/defense_missions.json";
    std::ifstream f(filename);
    if (!f.is_open()) {
        std::cerr << "❌ Error: could not open " << filename << std::endl;
        return false;
    }
    
    json data = json::parse(f);
    
    // Cargar recursos
    for (const auto& r : data["resources"]) {
        Resource res;
        res.id = r["id"];
        res.type = r["type"];
        res.capacity = r["capacity"];
        res.range_km = r["range_km"];
        res.speed_kph = r["speed_kph"];
        res.available = r["available"];
        for (const auto& type : r["compatible_mission_types"]) {
            res.compatible_mission_types.push_back(type);
        }
        resources_.push_back(res);
    }
    
    // Cargar misiones
    for (const auto& m : data["missions"]) {
        Mission mis;
        mis.id = m["id"];
        mis.name = m["name"];
        mis.priority = m["priority"];
        mis.min_resources_needed = m["min_resources_needed"];
        mis.required_resource_type = m["required_resource_type"];
        mis.max_risk_tolerance = m["max_risk_tolerance"];
        mis.location_x = m["location_x"];
        mis.location_y = m["location_y"];
        mis.deadline_hours = m["deadline_hours"];
        missions_.push_back(mis);
    }
    
    std::cout << "✅ Data loaded: " << resources_.size() << " resources, " 
              << missions_.size() << " missions" << std::endl;
    
    // 2. Crear solver
    solver_ = std::make_unique<operations_research::MPSolver>("DefenseSolver",
        operations_research::MPSolver::CBC_MIXED_INTEGER_PROGRAMMING);
    
    // 3. Crear variables binarias x_{r,m}
    assign_.resize(resources_.size());
    for (size_t r = 0; r < resources_.size(); ++r) {
        assign_[r].resize(missions_.size());
        for (size_t m = 0; m < missions_.size(); ++m) {
            assign_[r][m] = solver_->MakeIntVar(0, 1, 
                "assign_" + resources_[r].id + "_" + missions_[m].id);
        }
    }
    
    // 4. Restricciones: cada recurso asignado a una sola misión
    for (size_t r = 0; r < resources_.size(); ++r) {
        operations_research::MPConstraint* constraint = solver_->MakeRowConstraint(
            0, 1, "resource_" + resources_[r].id);
        for (size_t m = 0; m < missions_.size(); ++m) {
            constraint->SetCoefficient(assign_[r][m], 1);
        }
    }
    
    // 5. Restricciones: requisitos mínimos por misión
    for (size_t m = 0; m < missions_.size(); ++m) {
        operations_research::MPConstraint* constraint = solver_->MakeRowConstraint(
            missions_[m].min_resources_needed, solver_->infinity(), 
            "mission_" + missions_[m].id);
        for (size_t r = 0; r < resources_.size(); ++r) {
            constraint->SetCoefficient(assign_[r][m], resources_[r].capacity);
        }
    }
    
    // 6. Restricción de alcance (range)
    for (size_t r = 0; r < resources_.size(); ++r) {
        for (size_t m = 0; m < missions_.size(); ++m) {
            if (distance(r, m) > resources_[r].range_km) {
                assign_[r][m]->SetUB(0);  // no puede asignarse si fuera de alcance
            }
        }
    }
    
    // 7. Función objetivo: maximizar prioridades
    operations_research::MPObjective* objective = solver_->MutableObjective();
    objective->SetMaximization();
    
    for (size_t r = 0; r < resources_.size(); ++r) {
        for (size_t m = 0; m < missions_.size(); ++m) {
            objective->SetCoefficient(assign_[r][m], missions_[m].priority);
        }
    }
    
    std::cout << "✅ Model built with " << solver_->NumVariables() << " variables and "
              << solver_->NumConstraints() << " constraints." << std::endl;
    
    return true;
}

bool DefenseMissions::Solve() {
    std::cout << "🧮 Solving Defense Missions model..." << std::endl;
    
    if (!solver_) {
        std::cerr << "❌ Solver not initialized" << std::endl;
        return false;
    }
    
    const operations_research::MPSolver::ResultStatus result = solver_->Solve();
    
    if (result == operations_research::MPSolver::OPTIMAL) {
        std::cout << "✅ Optimal solution found!" << std::endl;
        std::cout << "🎯 Total mission value: " << solver_->Objective().Value() << std::endl;
        return true;
    } else {
        std::cerr << "❌ No optimal solution found. Status: " << result << std::endl;
        return false;
    }
}

std::string DefenseMissions::GetResults() const {
    json results;
    results["status"] = "optimal";
    results["objective_value"] = solver_->Objective().Value();
    
    json assignments = json::array();
    for (size_t r = 0; r < resources_.size(); ++r) {
        for (size_t m = 0; m < missions_.size(); ++m) {
            if (assign_[r][m]->solution_value() > 0.5) {
                json item;
                item["resource"] = resources_[r].id + " (" + resources_[r].type + ")";
                item["mission"] = missions_[m].name;
                item["priority"] = missions_[m].priority;
                assignments.push_back(item);
            }
        }
    }
    results["assignments"] = assignments;
    
    return results.dump(2);
}
