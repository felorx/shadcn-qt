#pragma once

#include <QString>

class QApplication;

namespace shadcn_qt {

/** Apply generated light or dark QSS from Qt resources (:/shadcn_qt). */
void applyTheme(QApplication* app, const QString& mode = QStringLiteral("light"));

} // namespace shadcn_qt
