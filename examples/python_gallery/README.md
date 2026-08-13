# Python component gallery

This interactive application covers every public shadcn-qt Core component. It
provides category navigation, component search, light/dark theme switching, and
real interactions for dialogs, menus, popovers, tooltips, and notifications.
Every preview uses the classic `new-york` component profile with the Zinc
light/dark palette. The **Native QtWidgets** section adds four full-family
pages made exclusively from stock Qt classes, demonstrating the reversible
compatibility adapter separately from the 65 shadcn-qt subclasses.

From the repository root:

```bash
python -m pip install -e "./packages/python[pyside6]"
python examples/python_gallery/run.py
```

Open a particular component or theme directly:

```bash
python examples/python_gallery/run.py --component DataTable --theme dark
python examples/python_gallery/run.py --component "Native Forms" --theme dark
```

Generate a screenshot without keeping the window open:

```bash
QT_QPA_PLATFORM=offscreen python examples/python_gallery/run.py \
  --component Chart --screenshot /tmp/shadcn-qt-gallery.png
```

Set `SHADCN_QT_BINDING` before launch to run the same gallery with PyQt6,
PySide2, or PyQt5. Keep exactly one Qt binding loaded in each process.

The eight committed light/dark native baselines can be regenerated with:

```bash
python tools/update_native_gallery_baselines.py
```

`packages/python/tests/test_native_gallery_screenshots.py` compares rendered
pages with those baselines using a downsampled perceptual tolerance so small
platform font-rasterization differences do not create noisy failures.
