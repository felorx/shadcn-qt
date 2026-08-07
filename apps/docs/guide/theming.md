# Theming

Semantic colors follow [shadcn/ui](https://ui.shadcn.com/) naming: `background`, `foreground`, `primary`, `destructive`, `muted`, `border`, `ring`, etc.

## Source of truth

Edit [`packages/design-tokens/tokens.json`](https://github.com/qtshadcn/qtshadcn/blob/main/packages/design-tokens/tokens.json) (light and dark palettes, radius scale).

## Code generation

```bash
python tools/token-codegen/generate.py
```

Outputs:

- `packages/python/qtshadcn/_generated/base_light.qss` and `base_dark.qss`
- `packages/python/qtshadcn/_generated/base_qss.py` (`LIGHT_QSS` / `DARK_QSS`)
- `packages/cpp/qtshadcn/include/qtshadcn/ThemeTokens.h`

## Python

```python
from qtshadcn import apply_theme
from qtshadcn._qt import QtWidgets

app = QtWidgets.QApplication([])
apply_theme(app, "dark")
```

Optional palette hints:

```python
from qtshadcn.theme import apply_palette_from_tokens
apply_palette_from_tokens(app, "light")
```

## C++

```cpp
#include <qtshadcn/Theme.h>
qtshadcn::applyTheme(&app, QStringLiteral("dark"));
```
