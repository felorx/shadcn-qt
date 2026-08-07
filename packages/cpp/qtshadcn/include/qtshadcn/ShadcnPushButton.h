#pragma once

#include <QPushButton>
#include <QString>

namespace qtshadcn {

class ShadcnPushButton : public QPushButton {
    Q_OBJECT
public:
    explicit ShadcnPushButton(const QString& text = QString(), QWidget* parent = nullptr);

    void setVariant(const QString& variant);
    void setShadcnSize(const QString& size);

private:
    void refreshStyle();
};

} // namespace qtshadcn
