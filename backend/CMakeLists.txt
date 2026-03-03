cmake_minimum_required(VERSION 3.15)
project(Nexus)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Crow REQUIRED)
find_package(nlohmann_json REQUIRED)
find_package(ortools CONFIG REQUIRED)

add_executable(nexus 
    src/main.cpp
)

target_link_libraries(nexus
    PRIVATE
        Crow::Crow
        nlohmann_json::nlohmann_json
        ortools::ortools
)

# Copiar frontend al directorio de salida (aunque ahora esté vacío)
add_custom_command(TARGET nexus POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_directory
        ${CMAKE_SOURCE_DIR}/../frontend
        $<TARGET_FILE_DIR:nexus>/frontend
)
