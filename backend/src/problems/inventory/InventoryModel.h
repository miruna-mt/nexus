#ifndef INVENTORY_MODEL_H
#define INVENTORY_MODEL_H

#include "core/Model.h"
#include <nlohmann/json.hpp>
#include <vector>
#include <string>

using json = nlohmann::json;

struct ProductoInventario {
    std::string id;
    std::string nombre;
    double stock_inicial;
    double stock_minimo_seguridad;
    double stock_maximo;
    double demanda_diaria_media;
    double desviacion_demanda_diaria;
    int plazo_entrega_dias;
    double coste_unitario;
};

class InventoryModel : public Model {
public:
    InventoryModel() = default;
    virtual ~InventoryModel() = default;

    bool loadData(const std::string& filename);
    bool Build() override;
    bool Solve() override;
    std::string GetResults() const override;

protected:
    int horizonte_dias;
    double coste_pedido_fijo;
    double coste_mantenimiento_por_unidad_dia;
    double coste_rotura_stock_por_unidad;
    std::vector<ProductoInventario> productos;
};

#endif
