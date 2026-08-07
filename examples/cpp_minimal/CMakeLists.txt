cmake_minimum_required(VERSION 3.16)
project(qtshadcn_cpp_minimal LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)

find_package(QT NAMES Qt6 Qt5 REQUIRED COMPONENTS Widgets Core)
find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Widgets Core)

add_subdirectory(../../packages/cpp/qtshadcn qtshadcn_build)

add_executable(qtshadcn_cpp_minimal main.cpp)
target_link_libraries(qtshadcn_cpp_minimal PRIVATE QtShadcn Qt${QT_VERSION_MAJOR}::Widgets)
