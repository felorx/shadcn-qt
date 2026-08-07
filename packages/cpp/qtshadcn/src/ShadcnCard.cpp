#include "qtshadcn/ShadcnCard.h"

#include <QtGlobal>

using namespace qtshadcn;

ShadcnCard::ShadcnCard(QWidget* parent)
    : QFrame(parent)
{
    setObjectName(QStringLiteral("qtshadcn-card"));
    setProperty("qtshadcn_component", QStringLiteral("card"));
#if QT_VERSION >= QT_VERSION_CHECK(6, 0, 0)
    setFrameShape(QFrame::Shape::StyledPanel);
    setFrameShadow(QFrame::Shadow::Plain);
#else
    setFrameShape(QFrame::StyledPanel);
    setFrameShadow(QFrame::Plain);
#endif
}
