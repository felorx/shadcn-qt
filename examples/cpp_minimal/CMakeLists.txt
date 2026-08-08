cmake_minimum_required(VERSION 3.16)
project(shadcn_qt_cpp_minimal LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)

find_package(QT NAMES Qt6 Qt5 REQUIRED COMPONENTS Widgets Core)
find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Widgets Core)

find_package(ShadcnQt 0.1 CONFIG QUIET)
if(NOT ShadcnQt_FOUND)
  add_subdirectory(../../packages/cpp/shadcn_qt shadcn_qt_build)
endif()

add_executable(shadcn_qt_cpp_minimal main.cpp)
target_link_libraries(
  shadcn_qt_cpp_minimal
  PRIVATE shadcn_qt::ShadcnQt Qt${QT_VERSION_MAJOR}::Widgets
)
