#include <QApplication>
#include <QHBoxLayout>
#include <QLabel>
#include <QVBoxLayout>
#include <QWidget>

#include <qtshadcn/ShadcnCard.h>
#include <qtshadcn/ShadcnInput.h>
#include <qtshadcn/ShadcnPushButton.h>
#include <qtshadcn/Theme.h>

int main(int argc, char* argv[])
{
    QApplication app(argc, argv);
    qtshadcn::applyTheme(&app, QStringLiteral("light"));

    QWidget window;
    window.setWindowTitle(QStringLiteral("qtshadcn C++ minimal"));
    auto* root = new QVBoxLayout(&window);

    auto* card = new qtshadcn::ShadcnCard(&window);
    auto* lay = new QVBoxLayout(card);
    lay->setContentsMargins(24, 24, 24, 24);
    lay->setSpacing(12);
    lay->addWidget(new QLabel(QStringLiteral("Card + Button + Input"), card));

    auto* input = new qtshadcn::ShadcnInput(card);
    input->setPlaceholderText(QStringLiteral("Email"));
    lay->addWidget(input);

    auto* row = new QHBoxLayout();
    auto* primary = new qtshadcn::ShadcnPushButton(QStringLiteral("Primary"), card);
    primary->setVariant(QStringLiteral("default"));
    auto* outline = new qtshadcn::ShadcnPushButton(QStringLiteral("Outline"), card);
    outline->setVariant(QStringLiteral("outline"));
    row->addWidget(primary);
    row->addWidget(outline);
    lay->addLayout(row);

    root->addWidget(card);
    window.resize(420, 280);
    window.show();
    return app.exec();
}
