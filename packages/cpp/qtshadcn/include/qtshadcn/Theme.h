#pragma once

#include <QString>

class QApplication;

namespace qtshadcn {

/** Apply generated light or dark QSS from Qt resources (:qtshadcn). */
void applyTheme(QApplication* app, const QString& mode = QStringLiteral("light"));

} // namespace qtshadcn
