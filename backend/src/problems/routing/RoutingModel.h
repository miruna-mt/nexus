#ifndef ROUTING_MODEL_H
#define ROUTING_MODEL_H

#include "core/Model.h"
#include <nlohmann/json.hpp>
#include <vector>
#include <string>

using json = nlohmann::json;

struct Vehiculo {
    std::string id;
    std::string nombre;
    double capacidad_kg;
    double autonomia_km;
    double coste_por_km;
    double velocidad_media_kmh;
    int tiempo_maximo_conduccion_min;
    int tiempo_inicio_min;
    int tiempo_fin_min;
};

struct Cliente {
    std::string id;
    std::string nombre;
    std::string direccion;
    std::vector<double> coordenadas;
    double demanda_kg;
    int ventana_inicio_min;
    int ventana_fin_min;
    int tiempo_servicio_min;
    int prioridad;
};

struct Deposito {
    std::string id;
    std::string nombre;
    std::vector<double> coordenadas;
    int horario_inicio_min;
    int horario_fin_min;
};

class RoutingModel : public Model {
public:
    RoutingModel() = default;
    virtual ~RoutingModel() = default;

    bool loadData(const std::string& filename);
    bool Build() override;
    bool Solve() override;
    std::string GetResults() const override;

protected:
    std::vector<Vehiculo> vehiculos;
    std::vector<Cliente> clientes;
    Deposito deposito;
    double coste_fijo_por_vehiculo;
    double penalizacion_fuera_ventana;
    int tiempo_maximo_espera_min;
    std::string objetivo;
};

#endif
