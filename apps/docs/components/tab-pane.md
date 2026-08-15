# TabPane

`TabPane` is a `QTabWidget` subclass with a Chrome-style document-tab
appearance. The active tab and its page form one continuous surface with no
gap or lower border; outward curved shoulders join both lower tab corners to
the page. The page body keeps a semantic border on its sides, bottom, and the
two exposed parts of its top edge, while the span directly beneath the active
tab remains open so no divider cuts through the connection. The strip outside
the tabs is transparent, while the connected page surface is deliberately
distinct from the window background. Inactive tabs
remain quiet with separators and reuse the complete connected-tab silhouette
on hover, including its outward lower shoulders. Focus, close-button,
disabled, light, and dark states use the shared semantic tokens. Keyboard
focus colors the selected tab's outer Chrome silhouette; it never adds a
second rounded rectangle around the title text and icon.

```python
from shadcn_qt import TabPane

tabs = TabPane()
tabs.setMovable(True)
tabs.setTabsClosable(True)
tabs.addTab(account_page, "Account")
tabs.addTab(security_page, "Security")
tabs.tabCloseRequested.connect(tabs.removeTab)
```

The complete inherited `QTabWidget` API remains available. Enabling native
widget styling gives an ordinary `QTabWidget` the same appearance without
changing its existing tabs, signals, movable setting, or closable setting.
