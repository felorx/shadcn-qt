#include "shadcn_qt/ShadcnPushButton.h"

#include <QStyle>
#include <QVariant>

using namespace shadcn_qt;

ShadcnPushButton::ShadcnPushButton(const QString& text, QWidget* parent)
    : QPushButton(text, parent)
{
    setObjectName(QStringLiteral("shadcn-qt-button"));
    setProperty("shadcn_qt_component", QStringLiteral("button"));
    setVariant(QStringLiteral("default"));
    setShadcnSize(QStringLiteral("default"));
}

void ShadcnPushButton::setVariant(const QString& variant)
{
    m_variant = variant;
    refreshStyle();
}

QString ShadcnPushButton::variant() const
{
    return m_variant;
}

void ShadcnPushButton::setShadcnSize(const QString& size)
{
    m_shadcnSize = size;
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
