#ifndef MODEL_H
#define MODEL_H

#include <string>
#include <memory>
#include "ortools/linear_solver/linear_solver.h"

namespace operations_research {
    class MPSolver;
    class MPVariable;
}

class Model {
public:
    virtual ~Model() = default;
    
    virtual bool Build() = 0;
    virtual bool Solve() = 0;
    virtual std::string GetResults() const = 0;
    
protected:
    std::string name_;
    std::string description_;
    std::unique_ptr<operations_research::MPSolver> solver_;
};

#endif
