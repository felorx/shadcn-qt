#include "shadcn_qt/ShadcnInput.h"

#include <QVariant>

using namespace shadcn_qt;

ShadcnInput::ShadcnInput(QWidget* parent)
    : QLineEdit(parent)
{
    setObjectName(QStringLiteral("shadcn-qt-input"));
    setProperty("shadcn_qt_component", QStringLiteral("input"));
}
