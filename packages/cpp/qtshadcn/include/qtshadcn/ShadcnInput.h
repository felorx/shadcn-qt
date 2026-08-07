#pragma once

#include <QLineEdit>

namespace qtshadcn {

class ShadcnInput : public QLineEdit {
    Q_OBJECT
public:
    explicit ShadcnInput(QWidget* parent = nullptr);
};

} // namespace qtshadcn
