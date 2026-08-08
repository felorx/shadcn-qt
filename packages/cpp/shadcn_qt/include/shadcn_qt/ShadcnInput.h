#pragma once

#include <QLineEdit>

namespace shadcn_qt {

class ShadcnInput : public QLineEdit {
    Q_OBJECT
public:
    explicit ShadcnInput(QWidget* parent = nullptr);
};

} // namespace shadcn_qt
