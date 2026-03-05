#ifndef FMCG_PRODUCTOS_TIENDAS_H
#define FMCG_PRODUCTOS_TIENDAS_H

#include "../AssignmentModel.h"

class FMCGProductosTiendas : public AssignmentModel {
public:
    FMCGProductosTiendas();
    bool Build() override;
    bool Solve() override;
    std::string GetResults() const override;
};

#endif
