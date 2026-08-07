include(CMakeFindDependencyMacro)
find_package(QT NAMES Qt6 Qt5 REQUIRED COMPONENTS Widgets Core)
find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Widgets Core)
include("${CMAKE_CURRENT_LIST_DIR}/QtShadcnTargets.cmake")
