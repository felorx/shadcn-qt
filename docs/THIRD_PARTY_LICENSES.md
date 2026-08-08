# Qt binding and third-party license matrix

A shadcn-qt commercial license covers shadcn-qt only. The customer must choose a
compatible license path for the Qt framework, Python binding, Qt modules, and
other bundled material.

| Runtime choice | Upstream options | Closed-source distribution consideration |
| --- | --- | --- |
| PySide6 / Qt for Python | LGPLv3, GPLv3, or Qt commercial | A proprietary application may be possible under LGPLv3 only when all LGPL and applicable module/third-party obligations are satisfied; otherwise obtain Qt commercial rights |
| PyQt6 or PyQt5 | GPLv3 or Riverbank Commercial License | PyQt is not LGPL. GPL-incompatible proprietary distribution generally requires a Riverbank commercial license; Qt is licensed separately |
| Qt C++ | Primarily LGPLv3/GPLv3 or Qt commercial, varying by module | Review every used module, linking/distribution method, device restrictions, and third-party component |

Useful upstream references:

- [Qt open-source licensing FAQ](https://www.qt.io/faq/qt-open-source-licensing)
- [Qt licensing overview](https://doc.qt.io/qt-6/licensing.html)
- [Qt for Python licensing](https://doc.qt.io/qtforpython-6/)
- [Riverbank PyQt license overview](https://riverbankcomputing.com/software/pyqt)
- [Riverbank commercial PyQt FAQ](https://riverbankcomputing.com/commercial/license-faq)

Do not make a blanket promise that choosing PySide automatically makes every
closed-source distribution compliant. Qt modules and bundled third-party code
vary, and LGPL obligations depend on how the product is built and delivered.
For a production release, generate a dependency inventory and have counsel
review the actual product configuration.

The CMake install target places the shadcn-qt license, commercial terms, GPL
text, and notice under `share/licenses/ShadcnQt` (subject to the platform's
`CMAKE_INSTALL_DATADIR`). Keep those files with redistributed C++ packages.
