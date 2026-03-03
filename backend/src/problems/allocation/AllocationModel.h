#ifndef ALLOCATION_MODEL_H
#define ALLOCATION_MODEL_H

#include "core/Model.h"

class AllocationModel : public Model {
public:
    AllocationModel() = default;
    virtual ~AllocationModel() = default;

    // Métodos específicos de asignación (comunes a todas las industrias)
    virtual void setResources(int numResources) { m_numResources = numResources; }
    virtual void setDemands(int numDemands) { m_numDemands = numDemands; }
    
protected:
    int m_numResources;
    int m_numDemands;
};

#endif
