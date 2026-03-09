#include "cloud_vms.h"
#include <iostream>
#include <fstream>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

CloudVMs::CloudVMs() : AssignmentModel() {
    name_ = "Cloud - Virtual Machine Allocation";
    description_ = "Assign VMs to physical servers minimizing energy consumption";
}

bool CloudVMs::Build() {
    std::cout << "☁️ Building Cloud VMs model..." << std::endl;
    
    // 1. Cargar datos del JSON
    std::string filename = "data/assignment/cloud_vms.json";
    std::ifstream f(filename);
    if (!f.is_open()) {
        std::cerr << "❌ Error: could not open " << filename << std::endl;
        return false;
    }
    
    json data = json::parse(f);
    
    // Cargar servidores
    for (const auto& s : data["servers"]) {
        Server sv;
        sv.id = s["id"];
        sv.name = s["name"];
        sv.cpu_cores = s["cpu_cores"];
        sv.ram_gb = s["ram_gb"];
        sv.storage_tb = s["storage_tb"];
        sv.power_watt = s["power_watt"];
        sv.active = false;  // se determinará en la solución
        servers_.push_back(sv);
    }
    
    // Cargar VMs
    for (const auto& v : data["vms"]) {
        VM vm;
        vm.id = v["id"];
        vm.name = v["name"];
        vm.cpu_cores = v["cpu_cores"];
        vm.ram_gb = v["ram_gb"];
        vm.storage_tb = v["storage_tb"];
        vm.priority = v["priority"];
        
        // Cargar anti-afinidades si existen
        if (v.contains("anti_affinity_with")) {
            for (const auto& a : v["anti_affinity_with"]) {
                vm.anti_affinity_with.push_back(a);
            }
        }
        
        // Cargar afinidades si existen
        if (v.contains("affinity_with")) {
            for (const auto& a : v["affinity_with"]) {
                vm.affinity_with.push_back(a);
            }
        }
        
        vms_.push_back(vm);
    }
    
    std::cout << "✅ Data loaded: " << servers_.size() << " servers, " 
              << vms_.size() << " VMs" << std::endl;
    
    // 2. Crear solver
    solver_ = std::make_unique<operations_research::MPSolver>("CloudSolver",
        operations_research::MPSolver::CBC_MIXED_INTEGER_PROGRAMMING);
    
    // 3. Crear variables binarias x_{v,s}
    assign_.resize(vms_.size());
    for (size_t v = 0; v < vms_.size(); ++v) {
        assign_[v].resize(servers_.size());
        for (size_t s = 0; s < servers_.size(); ++s) {
            assign_[v][s] = solver_->MakeIntVar(0, 1, 
                "assign_" + vms_[v].id + "_" + servers_[s].id);
        }
    }
    
    // 4. Crear variables para servidores activos (opcional)
    server_active_.resize(servers_.size());
    for (size_t s = 0; s < servers_.size(); ++s) {
        server_active_[s] = solver_->MakeIntVar(0, 1, "server_active_" + servers_[s].id);
    }
    
    // 5. Restricción: cada VM asignada a un solo servidor
    for (size_t v = 0; v < vms_.size(); ++v) {
        operations_research::MPConstraint* constraint = solver_->MakeRowConstraint(1, 1, 
            "one_server_vm_" + vms_[v].id);
        for (size_t s = 0; s < servers_.size(); ++s) {
            constraint->SetCoefficient(assign_[v][s], 1);
        }
    }
    
    // 6. Restricciones de capacidad por servidor
    for (size_t s = 0; s < servers_.size(); ++s) {
        // CPU
        operations_research::MPConstraint* cpu_con = solver_->MakeRowConstraint(
            0, servers_[s].cpu_cores, "cpu_server_" + servers_[s].id);
        // RAM
        operations_research::MPConstraint* ram_con = solver_->MakeRowConstraint(
            0, servers_[s].ram_gb, "ram_server_" + servers_[s].id);
        // Storage
        operations_research::MPConstraint* storage_con = solver_->MakeRowConstraint(
            0, servers_[s].storage_tb, "storage_server_" + servers_[s].id);
        
        for (size_t v = 0; v < vms_.size(); ++v) {
            cpu_con->SetCoefficient(assign_[v][s], vms_[v].cpu_cores);
            ram_con->SetCoefficient(assign_[v][s], vms_[v].ram_gb);
            storage_con->SetCoefficient(assign_[v][s], vms_[v].storage_tb);
        }
    }
    
    // 7. Relación servidor activo (si tiene al menos una VM)
    for (size_t s = 0; s < servers_.size(); ++s) {
        operations_research::MPConstraint* active_con = solver_->MakeRowConstraint(
            -solver_->infinity(), 0, "active_server_" + servers_[s].id);
        
        double sum_coeff = 0;
        for (size_t v = 0; v < vms_.size(); ++v) {
            active_con->SetCoefficient(assign_[v][s], 1);
            sum_coeff += 1;
        }
        active_con->SetCoefficient(server_active_[s], -sum_coeff);
        active_con->SetUB(0);
    }
    
    // 8. Función objetivo: minimizar consumo energético
    operations_research::MPObjective* objective = solver_->MutableObjective();
    objective->SetMinimization();
    
    for (size_t s = 0; s < servers_.size(); ++s) {
        objective->SetCoefficient(server_active_[s], servers_[s].power_watt);
    }
    
    std::cout << "✅ Model built with " << solver_->NumVariables() << " variables and "
              << solver_->NumConstraints() << " constraints." << std::endl;
    
    return true;
}

bool CloudVMs::Solve() {
    std::cout << "🧮 Solving Cloud VMs model..." << std::endl;
    
    if (!solver_) {
        std::cerr << "❌ Solver not initialized" << std::endl;
        return false;
    }
    
    const operations_research::MPSolver::ResultStatus result = solver_->Solve();
    
    if (result == operations_research::MPSolver::OPTIMAL) {
        std::cout << "✅ Optimal solution found!" << std::endl;
        std::cout << "⚡ Total power consumption: " << solver_->Objective().Value() << " W" << std::endl;
        return true;
    } else {
        std::cerr << "❌ No optimal solution found. Status: " << result << std::endl;
        return false;
    }
}

std::string CloudVMs::GetResults() const {
    json results;
    results["status"] = "optimal";
    results["objective_value"] = solver_->Objective().Value();
    results["objective_units"] = "W";
    
    json assignments = json::array();
    json servers_used = json::array();
    
    for (size_t v = 0; v < vms_.size(); ++v) {
        for (size_t s = 0; s < servers_.size(); ++s) {
            if (assign_[v][s]->solution_value() > 0.5) {
                json item;
                item["vm"] = vms_[v].name;
                item["server"] = servers_[s].name;
                item["cpu"] = vms_[v].cpu_cores;
                item["ram"] = vms_[v].ram_gb;
                assignments.push_back(item);
            }
        }
    }
    
    for (size_t s = 0; s < servers_.size(); ++s) {
        if (server_active_[s]->solution_value() > 0.5) {
            servers_used.push_back(servers_[s].name);
        }
    }
    
    results["assignments"] = assignments;
    results["servers_used"] = servers_used;
    
    return results.dump(2);
}
