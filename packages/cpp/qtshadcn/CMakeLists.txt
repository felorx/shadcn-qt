cmake_minimum_required(VERSION 3.16)
project(QtShadcn LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)

find_package(QT NAMES Qt6 Qt5 REQUIRED COMPONENTS Widgets Core)
find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Widgets Core)

add_library(QtShadcn STATIC
  src/Theme.cpp
  src/ShadcnPushButton.cpp
  src/ShadcnCard.cpp
  src/ShadcnInput.cpp
  include/qtshadcn/ShadcnPushButton.h
  include/qtshadcn/ShadcnCard.h
  include/qtshadcn/ShadcnInput.h
  qtshadcn.qrc
)

target_include_directories(QtShadcn PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)

target_link_libraries(QtShadcn PUBLIC Qt${QT_VERSION_MAJOR}::Widgets)

include(GNUInstallDirs)
set(QTSHADCN_CMAKE_DIR ${CMAKE_INSTALL_LIBDIR}/cmake/QtShadcn)

install(TARGETS QtShadcn
  EXPORT QtShadcnTargets
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)

install(DIRECTORY include/qtshadcn
  DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
  FILES_MATCHING PATTERN "*.h"
)

install(EXPORT QtShadcnTargets
  FILE QtShadcnTargets.cmake
  NAMESPACE qtshadcn::
  DESTINATION ${QTSHADCN_CMAKE_DIR}
)

install(FILES QtShadcnConfig.cmake
  DESTINATION ${QTSHADCN_CMAKE_DIR}
)
