#ifndef CLOUD_VMS_H
#define CLOUD_VMS_H

#include "../AssignmentModel.h"
#include <vector>
#include <string>

struct Server {
    std::string id;
    std::string name;
    double cpu_cores;
    double ram_gb;
    double storage_tb;
    double power_watt;
    bool active;
};

struct VM {
    std::string id;
    std::string name;
    double cpu_cores;
    double ram_gb;
    double storage_tb;
    int priority;
    std::vector<std::string> anti_affinity_with;
    std::vector<std::string> affinity_with;
};

class CloudVMs : public AssignmentModel {
public:
    CloudVMs();
    ~CloudVMs() = default;

    bool Build() override;
    bool Solve() override;
    std::string GetResults() const override;

private:
    std::vector<Server> servers_;
    std::vector<VM> vms_;
    std::vector<std::vector<operations_research::MPVariable*>> assign_;
    std::vector<operations_research::MPVariable*> server_active_;
};

#endif
