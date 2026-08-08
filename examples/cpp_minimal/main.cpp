#include <QApplication>
#include <QHBoxLayout>
#include <QLabel>
#include <QVBoxLayout>
#include <QWidget>

#include <shadcn_qt/ShadcnCard.h>
#include <shadcn_qt/ShadcnInput.h>
#include <shadcn_qt/ShadcnPushButton.h>
#include <shadcn_qt/Theme.h>

int main(int argc, char* argv[])
{
    QApplication app(argc, argv);
    shadcn_qt::applyTheme(&app, QStringLiteral("light"));

    QWidget window;
    window.setWindowTitle(QStringLiteral("shadcn-qt C++ minimal"));
    auto* root = new QVBoxLayout(&window);

    auto* card = new shadcn_qt::ShadcnCard(&window);
    auto* lay = new QVBoxLayout(card);
    lay->setContentsMargins(24, 24, 24, 24);
    lay->setSpacing(12);
    lay->addWidget(new QLabel(QStringLiteral("Card + Button + Input"), card));

    auto* input = new shadcn_qt::ShadcnInput(card);
    input->setPlaceholderText(QStringLiteral("Email"));
    lay->addWidget(input);

    auto* row = new QHBoxLayout();
    auto* primary = new shadcn_qt::ShadcnPushButton(QStringLiteral("Primary"), card);
    primary->setVariant(QStringLiteral("default"));
    auto* outline = new shadcn_qt::ShadcnPushButton(QStringLiteral("Outline"), card);
    outline->setVariant(QStringLiteral("outline"));
    row->addWidget(primary);
    row->addWidget(outline);
    lay->addLayout(row);

    root->addWidget(card);
    window.resize(420, 280);
    window.show();
    return app.exec();
}
