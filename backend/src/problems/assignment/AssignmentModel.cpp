#include "AssignmentModel.h"
#include <iostream>
#include <fstream>

bool AssignmentModel::loadData(const std::string& filename) {
    std::cout << "Cargando datos desde " << filename << std::endl;
    return true;
}

bool AssignmentModel::Build() {
    std::cout << "Construyendo modelo Assignment" << std::endl;
    return true;
}

bool AssignmentModel::Solve() {
    std::cout << "Resolviendo modelo Assignment" << std::endl;
    return true;
}

std::string AssignmentModel::GetResults() const {
    return "{}";
}
