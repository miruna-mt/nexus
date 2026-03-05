#ifndef LOCATION_MODEL_H
#define LOCATION_MODEL_H

#include "core/Model.h"
#include <nlohmann/json.hpp>
#include <vector>
#include <string>

using json = nlohmann::json;

struct Ubicacion {
    std::string id;
    std::string nombre;
    double coste_apertura;
    double capacidad_maxima;
    std::vector<double> coordenadas;
};

struct ClienteLocation {
    std::string id;
    std::string nombre;
    double demanda_mensual;
    std::vector<double> coordenadas;
};

class LocationModel : public Model {
public:
    LocationModel() = default;
    virtual ~LocationModel() = default;

    bool loadData(const std::string& filename);
    bool Build() override;
    bool Solve() override;
    std::string GetResults() const override;

protected:
    int num_almacenes_max;
    double presupuesto_total;
    double coste_transporte_por_km_unidad;
    std::vector<Ubicacion> ubicaciones;
    std::vector<ClienteLocation> clientes;
};

#endif
