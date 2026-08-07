#include "qtshadcn/ShadcnPushButton.h"

#include <QStyle>

using namespace qtshadcn;

ShadcnPushButton::ShadcnPushButton(const QString& text, QWidget* parent)
    : QPushButton(text, parent)
{
    setObjectName(QStringLiteral("qtshadcn-button"));
    setProperty("qtshadcn_component", QStringLiteral("button"));
    setVariant(QStringLiteral("default"));
    setShadcnSize(QStringLiteral("default"));
}

void ShadcnPushButton::setVariant(const QString& variant)
{
    m_variant = variant;
    setProperty("qtshadcn_variant", m_variant);
    refreshStyle();
}

QString ShadcnPushButton::variant() const
{
    return m_variant;
}

void ShadcnPushButton::setShadcnSize(const QString& size)
{
    m_shadcnSize = size;
    setProperty("qtshadcn_size", m_shadcnSize);
    refreshStyle();
}

QString ShadcnPushButton::shadcnSize() const
{
    return m_shadcnSize;
}

void ShadcnPushButton::refreshStyle()
{
    if (style()) {
        style()->unpolish(this);
        style()->polish(this);
    }
}
