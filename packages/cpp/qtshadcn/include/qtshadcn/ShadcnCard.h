#pragma once

#include <QFrame>

namespace qtshadcn {

class ShadcnCard : public QFrame {
    Q_OBJECT
public:
    explicit ShadcnCard(QWidget* parent = nullptr);
};

} // namespace qtshadcn
