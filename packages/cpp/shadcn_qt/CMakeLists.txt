cmake_minimum_required(VERSION 3.16)
project(ShadcnQt VERSION 0.2.4 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)

find_package(QT NAMES Qt6 Qt5 REQUIRED COMPONENTS Widgets Core)
find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Widgets Core)

add_library(ShadcnQt STATIC
  src/Theme.cpp
  src/ShadcnPushButton.cpp
  src/ShadcnCard.cpp
  src/ShadcnInput.cpp
  include/shadcn_qt/ShadcnPushButton.h
  include/shadcn_qt/ShadcnCard.h
  include/shadcn_qt/ShadcnInput.h
  shadcn_qt.qrc
)
add_library(shadcn_qt::ShadcnQt ALIAS ShadcnQt)

target_include_directories(ShadcnQt PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)

target_link_libraries(ShadcnQt PUBLIC Qt${QT_VERSION_MAJOR}::Widgets)

include(GNUInstallDirs)
include(CMakePackageConfigHelpers)
set(SHADCN_QT_CMAKE_DIR ${CMAKE_INSTALL_LIBDIR}/cmake/ShadcnQt)
set(SHADCN_QT_REPOSITORY_ROOT ${CMAKE_CURRENT_SOURCE_DIR}/../../..)

write_basic_package_version_file(
  ${CMAKE_CURRENT_BINARY_DIR}/ShadcnQtConfigVersion.cmake
  VERSION ${PROJECT_VERSION}
  COMPATIBILITY SameMajorVersion
)

install(TARGETS ShadcnQt
  EXPORT ShadcnQtTargets
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)

install(DIRECTORY include/shadcn_qt
  DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
  FILES_MATCHING PATTERN "*.h"
)

install(EXPORT ShadcnQtTargets
  FILE ShadcnQtTargets.cmake
  NAMESPACE shadcn_qt::
  DESTINATION ${SHADCN_QT_CMAKE_DIR}
)

install(FILES ShadcnQtConfig.cmake
  ${CMAKE_CURRENT_BINARY_DIR}/ShadcnQtConfigVersion.cmake
  DESTINATION ${SHADCN_QT_CMAKE_DIR}
)

install(FILES
  ${SHADCN_QT_REPOSITORY_ROOT}/LICENSE
  ${SHADCN_QT_REPOSITORY_ROOT}/NOTICE.md
  ${SHADCN_QT_REPOSITORY_ROOT}/LICENSES/GPL-3.0-only.txt
  ${SHADCN_QT_REPOSITORY_ROOT}/LICENSES/LicenseRef-Shadcn-Qt-Commercial.txt
  DESTINATION ${CMAKE_INSTALL_DATADIR}/licenses/ShadcnQt
)
