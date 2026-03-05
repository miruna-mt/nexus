#include <crow.h>
#include <fstream>
#include <iostream>
#include <string>
#include <sstream>

#include "problems/assignment/instances/fmcg_productos_tiendas.h"

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
            // Crear la instancia del modelo
            FMCGProductosTiendas modelo;
            
            // Ejecutar
            if (!modelo.Build()) {
                return crow::response(500, "Error al construir el modelo");
            }
            
            if (!modelo.Solve()) {
                return crow::response(500, "Error al resolver el modelo");
            }
            
            // Obtener resultados
            std::string resultados = modelo.GetResults();
            
            crow::response res(resultados);
            res.set_header("Content-Type", "application/json");
            return res;
            
        } catch (const std::exception& e) {
            return crow::response(500, e.what());
        }
    });

// Ruta raíz - redirige a index.html
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

    app.port(8080).multithreaded().run();
}
