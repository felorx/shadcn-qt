# Component catalog

All Python widgets are importable from either `qtshadcn` or `qtshadcn.widgets`.

| Component | Qt base | Purpose |
|---|---|---|
| Button | QPushButton | default, destructive, outline, secondary, ghost, link variants |
| Input | QLineEdit | single-line input and invalid state |
| TextArea | QPlainTextEdit | multi-line input and invalid state |
| Card | QFrame | styled content container |
| Label | QLabel | default, muted, lead, large, small typography |
| Checkbox | QCheckBox | boolean selection |
| RadioButton | QRadioButton | exclusive selection |
| Switch | QCheckBox | switch-styled boolean selection |
| Select | QComboBox | item selection |
| Slider | QSlider | numeric range input |
| Progress | QProgressBar | progress indicator |
| Tabs | QTabWidget | tabbed container |
| Badge | QLabel | compact status label |
| Alert | QFrame | default or destructive message container |
| Separator | QFrame | horizontal or vertical divider |

These are Qt-native subclasses: existing signals, slots, models, accessibility metadata, layouts, and test tools continue to work.
