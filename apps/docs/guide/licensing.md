# Licensing and dependencies

Current shadcn-qt releases use
`GPL-3.0-only OR LicenseRef-Shadcn-Qt-Commercial`.

## Choose a shadcn-qt path

- Use **GPL-3.0-only** when the complete distributed work is GPL-compatible and
  you can satisfy the GPLv3 obligations.
- Buy a **commercial developer-seat license** when the application must remain
  proprietary. The standard terms allow unlimited applications and end-user
  copies without runtime royalties.
- An **evaluation Order Form** permits internal evaluation only for its stated
  period.

The PyPI package is the same for GPL and commercial customers. There is no
online activation. Commercial entitlement comes from an accepted Order Form or
license certificate; installing from PyPI alone grants no commercial rights.

## Qt and binding licenses are separate

| Binding/framework | Upstream choices | Proprietary application note |
| --- | --- | --- |
| PySide6 / Qt for Python | LGPLv3, GPLv3, Qt commercial | LGPL can be usable only when all obligations and the exact module licenses are satisfied |
| PyQt5 / PyQt6 | GPLv3, Riverbank Commercial License | PyQt is not LGPL; a GPL-incompatible application generally needs Riverbank commercial rights |
| Qt | LGPLv3/GPLv3 or Qt commercial, depending on module | Review the exact modules, linking, distribution method, and third-party notices |

A shadcn-qt commercial license never substitutes for a Qt or PyQt commercial
license. Consult the official [Qt licensing FAQ](https://www.qt.io/faq/qt-open-source-licensing),
[Qt for Python docs](https://doc.qt.io/qtforpython-6/), and
[Riverbank PyQt license page](https://riverbankcomputing.com/software/pyqt).

Release rights are described by the license files shipped inside every wheel
and sdist. This guide is not legal advice.
