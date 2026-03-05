#ifndef SCHEDULING_MODEL_H
#define SCHEDULING_MODEL_H

#include "core/Model.h"
#include <nlohmann/json.hpp>
#include <vector>
#include <string>

using json = nlohmann::json;

struct Tarea {
    std::string id;
    std::string nombre;
    int duracion;
    std::vector<std::string> dependencias;  // IDs de tareas que deben preceder a esta
    int recursos_necesarios;
    int fecha_entrega;
    double penalizacion_retraso;
};

struct Recurso {
    std::string id;
    std::string nombre;
    int cantidad_disponible;
};

class SchedulingModel : public Model {
public:
    SchedulingModel() = default;
    virtual ~SchedulingModel() = default;

    bool loadData(const std::string& filename);
    bool Build() override;
    bool Solve() override;
    std::string GetResults() const override;

protected:
    std::vector<Tarea> tareas;
    std::vector<Recurso> recursos;
    int horizonte_temporal;
    std::string objetivo;  // "minimize_makespan", "minimize_delay", etc.
};

#endif
