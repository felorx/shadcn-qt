#include "qtshadcn/ShadcnInput.h"

using namespace qtshadcn;

ShadcnInput::ShadcnInput(QWidget* parent)
    : QLineEdit(parent)
{
    setObjectName(QStringLiteral("qtshadcn-input"));
    setProperty("qtshadcn_component", QStringLiteral("input"));
}
