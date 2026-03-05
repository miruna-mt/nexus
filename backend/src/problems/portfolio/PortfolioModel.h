#ifndef PORTFOLIO_MODEL_H
#define PORTFOLIO_MODEL_H

#include "core/Model.h"
#include <nlohmann/json.hpp>
#include <vector>
#include <string>

using json = nlohmann::json;

struct Proyecto {
    std::string id;
    std::string nombre;
    std::string departamento;
    double inversion_requerida;
    double retorno_esperado_anual;
    double riesgo_estimado;
    int tiempo_retorno_anios;
    int prioridad_estrategica;
};

struct Restriccion {
    std::string tipo;
    // Campos variables según el tipo
    std::string departamento;
    double maximo_inversion;
    int valor_minimo;
    std::vector<std::string> proyectos_excluidos;
    std::string descripcion;
};

class PortfolioModel : public Model {
public:
    PortfolioModel() = default;
    virtual ~PortfolioModel() = default;

    bool loadData(const std::string& filename);
    bool Build() override;
    bool Solve() override;
    std::string GetResults() const override;

protected:
    double presupuesto_total;
    double tasa_libre_riesgo;
    double aversion_riesgo;
    std::vector<Proyecto> proyectos;
    std::vector<std::vector<double>> matriz_correlacion;
    std::vector<Restriccion> restricciones;
    
    // Variables de decisión
    std::vector<operations_research::MPVariable*> seleccion; // 0/1 o continuas
};

#endif
