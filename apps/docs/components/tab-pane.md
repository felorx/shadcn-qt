# TabPane

`TabPane` is a `QTabWidget` subclass with a Chrome-style document-tab
appearance. The active tab and its page form one continuous surface with no
gap or lower border; outward curved shoulders join both lower tab corners to
the page. The strip outside the tabs is transparent, while the connected page
surface is deliberately distinct from the window background. Inactive tabs
remain quiet with separators and reuse the complete connected-tab silhouette
on hover, including its outward lower shoulders. Focus, close-button,
disabled, light, and dark states use the shared semantic tokens.

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
