#ifndef STOCHASTIC_MODEL_H
#define STOCHASTIC_MODEL_H

#include "core/Model.h"
#include <nlohmann/json.hpp>
#include <vector>
#include <string>
#include <random>

using json = nlohmann::json;

struct Escenario {
    std::string id;
    double probabilidad;
    std::vector<double> parametros;  // Ej: retornos en diferentes escenarios
};

class StochasticModel : public Model {
public:
    StochasticModel() = default;
    virtual ~StochasticModel() = default;

    bool loadData(const std::string& filename);
    bool Build() override;
    bool Solve() override;
    std::string GetResults() const override;

protected:
    std::vector<Escenario> escenarios;
    double aversion_riesgo;
    int num_escenarios;
    std::string tipo_objetivo;  // "expected_value", "cvar", "robust"
};

#endif
