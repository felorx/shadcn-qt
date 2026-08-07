#include "qtshadcn/ShadcnPushButton.h"

#include <QStyle>

using namespace qtshadcn;

ShadcnPushButton::ShadcnPushButton(const QString& text, QWidget* parent)
    : QPushButton(text, parent)
{
    setObjectName(QStringLiteral("qtshadcn-button"));
    setVariant(QStringLiteral("default"));
    setShadcnSize(QStringLiteral("default"));
}

void ShadcnPushButton::setVariant(const QString& variant)
{
    setProperty("qtshadcn_variant", variant);
    refreshStyle();
}

void ShadcnPushButton::setShadcnSize(const QString& size)
{
    setProperty("qtshadcn_size", size);
    refreshStyle();
}

void ShadcnPushButton::refreshStyle()
{
    if (style()) {
        style()->unpolish(this);
        style()->polish(this);
    }
}
