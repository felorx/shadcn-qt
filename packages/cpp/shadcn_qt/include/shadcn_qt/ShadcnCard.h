#pragma once

#include <QFrame>

namespace shadcn_qt {

class ShadcnCard : public QFrame {
    Q_OBJECT
public:
    explicit ShadcnCard(QWidget* parent = nullptr);
};

} // namespace shadcn_qt
