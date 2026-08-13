# Component catalog

All 65 Python widgets are importable from either `shadcn_qt` or
`shadcn_qt.widgets`. The catalog follows the current shadcn/ui component
index while translating browser-only primitives into native Qt behavior.

| Area | Components | Qt mapping |
|---|---|---|
| Actions and forms | Button, ButtonGroup, Toggle, ToggleGroup, Input, InputGroup, InputOTP, TextArea, Checkbox, RadioButton, RadioGroup, Switch, Select, NativeSelect, Combobox, DatePicker, Slider, Field, Label | QPushButton/QToolButton and native Qt editors/groups |
| Layout and disclosure | Accordion, AspectRatio, Card, Carousel, Collapsible, Direction, Resizable, ScrollArea, Separator, Sidebar, Tabs | QFrame, QSplitter, QScrollArea, and QTabWidget composition |
| Dialogs and feedback | Alert, AlertDialog, Dialog, Drawer, HoverCard, Popover, Sheet, Sonner, Toast, Tooltip | QDialog/QFrame/QMenu-style native popup behavior |
| Navigation and menus | Breadcrumb, Command, ContextMenu, DropdownMenu, Menubar, NavigationMenu, Pagination | Qt menus, list filtering, and composed navigation controls |
| Data and content | Avatar, Badge, Calendar, Chart, DataTable, Empty, Item, Kbd, Progress, Skeleton, Spinner, Table, Typography | Native item models, Qt painting, views, labels, and progress controls |
| Conversation | Attachment, Bubble, Marker, Message, MessageScroller | Qt-native composition for the current shadcn chat components |

These are Qt-native subclasses: existing signals, slots, models, accessibility metadata, layouts, and test tools continue to work.

## Interactive gallery

Preview and interact with the complete catalog from a source checkout:

```bash
python examples/python_gallery/run.py
```

The gallery includes category navigation, component search, light/dark theme
switching, and interactive overlay, menu, tooltip, and notification examples.
Use `--component DataTable --theme dark` to open a specific preview directly.

`Chart` deliberately uses `QPainter` for a zero-dependency line/bar baseline. `Direction` applies Qt layout direction recursively through normal QWidget inheritance. Compound components expose Python composition methods such as `Accordion.addItem()`, `Dialog.addWidget()`, `Command.setItems()`, and `DataTable.setRows()`.
