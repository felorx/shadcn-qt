# Button

Mirrors [shadcn/ui Button](https://ui.shadcn.com/docs/components/button) variants using dynamic properties consumed by generated QSS.

**Variants:** `default`, `secondary`, `outline`, `ghost`, `destructive`, `link`  
**Sizes:** `default`, `sm`, `lg`, `icon` (QSS hooks; `icon` padding can be extended)

## Python

```python
from qtshadcn import Button, apply_theme
from qtshadcn._qt import QtWidgets, app_exec

app = QtWidgets.QApplication([])
apply_theme(app, "light")

b = Button("Outline", variant="outline", size="sm")
b.show()
app_exec(app)
```

## C++

```cpp
#include <qtshadcn/ShadcnPushButton.h>

auto* btn = new qtshadcn::ShadcnPushButton(QStringLiteral("Outline"));
btn->setVariant(QStringLiteral("outline"));
btn->setShadcnSize(QStringLiteral("sm"));
```

The Qt properties are named `variant` and `shadcnSize`, so Qt Designer and `.ui` generators can edit and restore them. The widget also sets `qtshadcn_component="button"`; styling therefore continues to work when an application changes its `objectName`.
