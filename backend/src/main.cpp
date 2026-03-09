#include <crow.h>
#include <fstream>
#include <iostream>
#include <string>
#include <sstream>

// Includes de las instancias de Assignment
#include "problems/assignment/instances/fmcg_productos_tiendas.h"
#include "problems/assignment/instances/defense_missions.h"
#include "problems/assignment/instances/cloud_vms.h"

// Lee un archivo completo
std::string read_file(const std::string& path) {
    std::ifstream file(path, std::ios::binary);
    if (!file) return "";
    std::stringstream buffer;
    buffer << file.rdbuf();
    return buffer.str();
}

// Función auxiliar para ends_with (C++17 compatible)
bool ends_with(const std::string& str, const std::string& suffix) {
    if (str.length() < suffix.length()) return false;
    return str.compare(str.length() - suffix.length(), suffix.length(), suffix) == 0;
}

int main() {
    crow::SimpleApp app;

    // Ruta para la optimización (POST)
    CROW_ROUTE(app, "/optimize").methods(crow::HTTPMethod::Post)([](const crow::request& req) {
        try {
            auto json = crow::json::load(req.body);
            if (!json) {
                return crow::response(400, "Invalid JSON");
            }

            std::string problem_type = json["problem_type"].s();
            std::string instance = json["instance"].s();

            std::cout << "📥 Request: " << problem_type << " - " << instance << std::endl;

            // Seleccionar la instancia según el tipo de problema
            if (problem_type == "assignment") {
                if (instance == "fmcg_productos_tiendas") {
                    FMCGProductosTiendas modelo;
                    
                    if (!modelo.Build()) {
                        return crow::response(500, "Error building FMCG model");
                    }
                    
                    if (!modelo.Solve()) {
                        return crow::response(500, "Error solving FMCG model");
                    }
                    
                    std::string resultados = modelo.GetResults();
                    crow::response res(resultados);
                    res.set_header("Content-Type", "application/json");
                    return res;
                }
                else if (instance == "defense_missions") {
                    DefenseMissions modelo;
                    
                    if (!modelo.Build()) {
                        return crow::response(500, "Error building Defense model");
                    }
                    
                    if (!modelo.Solve()) {
                        return crow::response(500, "Error solving Defense model");
                    }
                    
                    std::string resultados = modelo.GetResults();
                    crow::response res(resultados);
                    res.set_header("Content-Type", "application/json");
                    return res;
                }

		else if (instance == "cloud_vms") {
		    CloudVMs modelo;
    
    		    if (!modelo.Build()) {
        	    return crow::response(500, "Error building Cloud VMs model");
    		}
    
    if (!modelo.Solve()) {
        return crow::response(500, "Error solving Cloud VMs model");
    }
    
    std::string resultados = modelo.GetResults();
    crow::response res(resultados);
    res.set_header("Content-Type", "application/json");
    return res;
}
                else {
                    return crow::response(404, "Unknown assignment instance");
                }
            }
            else {
                return crow::response(404, "Unknown problem type");
            }
            
        } catch (const std::exception& e) {
            return crow::response(500, e.what());
        }
    });

// Ruta raíz - sirve index.html
CROW_ROUTE(app, "/")([]() {
    auto content = read_file("frontend/index.html");
    if (content.empty()) {
        return crow::response(404, "index.html not found");
    }
    crow::response res(content);
    res.set_header("Content-Type", "text/html");
    return res;
});

    // Ruta para servir archivos estáticos (HTML, CSS, JS, imágenes, etc.)
    CROW_ROUTE(app, "/<path>").methods(crow::HTTPMethod::Get)([](const crow::request& req, std::string path) {
        // Si la ruta está vacía, servir index.html
        if (path.empty()) {
            path = "index.html";
        }
        
        std::string full_path = "frontend/" + path;
        auto content = read_file(full_path);
        
        if (content.empty()) {
            std::cout << "No encontrado: " << full_path << std::endl;
            return crow::response(404);
        }
        
        crow::response res(content);
        
        // Determinar el tipo MIME por la extensión
        if (ends_with(path, ".html")) res.set_header("Content-Type", "text/html");
        else if (ends_with(path, ".css")) res.set_header("Content-Type", "text/css");
        else if (ends_with(path, ".js")) res.set_header("Content-Type", "application/javascript");
        else if (ends_with(path, ".png")) res.set_header("Content-Type", "image/png");
        else if (ends_with(path, ".svg")) res.set_header("Content-Type", "image/svg+xml");
        else if (ends_with(path, ".jpg") || ends_with(path, ".jpeg")) res.set_header("Content-Type", "image/jpeg");
        else if (ends_with(path, ".ico")) res.set_header("Content-Type", "image/x-icon");
        
        return res;
    });

// Ruta para archivos de descripción
CROW_ROUTE(app, "/descriptions/<string>").methods(crow::HTTPMethod::Get)([](const crow::request& req, std::string filename) {
    auto content = read_file("frontend/descriptions/" + filename);
    if (content.empty()) {
        return crow::response(404);
    }
    crow::response res(content);
    res.set_header("Content-Type", "text/html");
    return res;
});
    app.port(8080).multithreaded().run();
}
