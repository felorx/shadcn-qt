#include "qtshadcn/Theme.h"

#include <QApplication>
#include <QFile>
#include <QString>

namespace qtshadcn {

void applyTheme(QApplication* app, const QString& mode)
{
    if (!app) {
        return;
    }
    const QString path = mode == QStringLiteral("dark")
        ? QStringLiteral(":/qtshadcn/base_dark.qss")
        : QStringLiteral(":/qtshadcn/base_light.qss");
    QFile f(path);
    if (f.open(QIODevice::ReadOnly | QIODevice::Text)) {
        app->setStyleSheet(QString::fromUtf8(f.readAll()));
    }
}

} // namespace qtshadcn
