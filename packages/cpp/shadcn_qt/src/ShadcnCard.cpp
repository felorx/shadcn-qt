#include "shadcn_qt/ShadcnCard.h"

#include <QtGlobal>
#include <QVariant>

using namespace shadcn_qt;

ShadcnCard::ShadcnCard(QWidget* parent)
    : QFrame(parent)
{
    setObjectName(QStringLiteral("shadcn-qt-card"));
    setProperty("shadcn_qt_component", QStringLiteral("card"));
#if QT_VERSION >= QT_VERSION_CHECK(6, 0, 0)
    setFrameShape(QFrame::Shape::StyledPanel);
    setFrameShadow(QFrame::Shadow::Plain);
#else
    setFrameShape(QFrame::StyledPanel);
    setFrameShadow(QFrame::Plain);
#endif
}
