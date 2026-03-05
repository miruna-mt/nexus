#ifndef ASSIGNMENT_MODEL_H
#define ASSIGNMENT_MODEL_H

#include "core/Model.h"
#include <nlohmann/json.hpp>
#include <vector>
#include <string>

using json = nlohmann::json;

struct Product {
    std::string id;
    std::string nombre;
    double stock;
    double precio;
    double coste;
    int dias_caducidad;
    double penalizacion_caducidad;
};

struct Tienda {
    std::string id;
    std::string nombre;
    double capacidad;
};

struct Demanda {
    std::string producto_id;
    std::string tienda_id;
    double unidades_por_dia;
};

class AssignmentModel : public Model {
public:
    AssignmentModel() = default;
    virtual ~AssignmentModel() = default;

    bool loadData(const std::string& filename);
    bool Build() override;
    bool Solve() override;
    std::string GetResults() const override;

protected:
    std::vector<Product> productos;
    std::vector<Tienda> tiendas;
    std::vector<Demanda> demandas;
    int horizonte_dias;
    std::vector<std::vector<operations_research::MPVariable*>> x;
    std::vector<std::vector<operations_research::MPVariable*>> exceso;
};

#endif
