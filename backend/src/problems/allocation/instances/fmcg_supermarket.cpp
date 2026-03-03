#include "allocation/AllocationModel.h"

class FMCGSupermarketAllocation : public AllocationModel {
public:
    bool Build() override {
        // Aquí vendrá la implementación específica para supermercados
        return true;
    }
    
    bool Solve() override {
        // Usar OR-Tools para resolver
        return true;
    }
    
    std::string GetResults() const override {
        return "{\"result\": \"FMCG allocation example\"}";
    }
};
