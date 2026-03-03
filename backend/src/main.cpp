#include "crow.h"

int main() {
    crow::SimpleApp app;

    CROW_ROUTE(app, "/")([](){
        return "Hola desde Nexus! El motor esta vivo.";
    });

    app.port(8080).multithreaded().run();
}
