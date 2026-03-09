#ifndef DEFENSE_MISSIONS_H
#define DEFENSE_MISSIONS_H

#include "../AssignmentModel.h"
#include <vector>
#include <string>

struct Resource {
    std::string id;
    std::string type;      // "helicopter", "drone", "troops"
    double capacity;        // payload capacity or troop count
    double range_km;        // operational range
    double speed_kph;       // for travel time calculations
    bool available;
    std::vector<std::string> compatible_mission_types;
};

struct Mission {
    std::string id;
    std::string name;
    int priority;           // 1-10 (higher = more important)
    double min_resources_needed;
    std::string required_resource_type;
    double max_risk_tolerance;
    double location_x;
    double location_y;
    double deadline_hours;   // time window
};

class DefenseMissions : public AssignmentModel {
public:
    DefenseMissions();
    ~DefenseMissions() = default;

    bool Build() override;
    bool Solve() override;
    std::string GetResults() const override;

private:
    std::vector<Resource> resources_;
    std::vector<Mission> missions_;
    double distance(int r, int m) const;
    
    // Variables de decisión (inicializadas en Build)
    std::vector<std::vector<operations_research::MPVariable*>> assign_; // [resource][mission]
};

#endif
