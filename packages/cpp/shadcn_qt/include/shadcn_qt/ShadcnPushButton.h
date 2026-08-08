#pragma once

#include <QPushButton>
#include <QString>

namespace shadcn_qt {

class ShadcnPushButton : public QPushButton {
    Q_OBJECT
    Q_PROPERTY(QString variant READ variant WRITE setVariant)
    Q_PROPERTY(QString shadcnSize READ shadcnSize WRITE setShadcnSize)
public:
    explicit ShadcnPushButton(const QString& text = QString(), QWidget* parent = nullptr);

    void setVariant(const QString& variant);
    QString variant() const;
    void setShadcnSize(const QString& size);
    QString shadcnSize() const;

private:
    void refreshStyle();
    QString m_variant;
    QString m_shadcnSize;
};

} // namespace shadcn_qt
