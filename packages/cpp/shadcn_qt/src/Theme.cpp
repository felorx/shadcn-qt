#include "shadcn_qt/Theme.h"

#include <QApplication>
#include <QFile>
#include <QString>

namespace shadcn_qt {

void applyTheme(QApplication* app, const QString& mode)
{
    if (!app) {
        return;
    }
    const QString path = mode == QStringLiteral("dark")
        ? QStringLiteral(":/shadcn_qt/base_dark.qss")
        : QStringLiteral(":/shadcn_qt/base_light.qss");
    QFile f(path);
    if (f.open(QIODevice::ReadOnly | QIODevice::Text)) {
        app->setStyleSheet(QString::fromUtf8(f.readAll()));
    }
}

} // namespace shadcn_qt
