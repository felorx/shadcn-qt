# qtshadcn (Python)

Install with exactly **one** Qt binding extra:

```bash
pip install -e ".[pyside6]"
# or: pyqt6 | pyside2 | pyqt5
```

Regenerate styles after editing `packages/design-tokens/tokens.json`:

```bash
python ../../tools/token-codegen/generate.py
```
