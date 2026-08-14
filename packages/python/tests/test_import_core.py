"""Smoke: Core imports without Qt or the separately distributed Pro package."""

import importlib
import importlib.util
import unittest


class TestImportCore(unittest.TestCase):
    def test_import_package_without_qt_widgets(self):
        import shadcn_qt

        self.assertIsInstance(shadcn_qt.__version__, str)
        self.assertTrue(shadcn_qt.__version__)
        self.assertTrue(hasattr(shadcn_qt, "apply_theme"))
        self.assertTrue(hasattr(shadcn_qt, "detect_binding"))
        self.assertTrue(hasattr(shadcn_qt, "enable_native_widget_styling"))

    def test_generated_qss_strings_exist(self):
        from shadcn_qt._generated import base_qss

        self.assertGreater(len(base_qss.LIGHT_QSS), 100)
        self.assertGreater(len(base_qss.DARK_QSS), 100)

    def test_pro_bridge_explains_separate_distribution(self):
        if importlib.util.find_spec("shadcn_qt_pro") is not None:
            self.skipTest("private Pro distribution is installed")
        with self.assertRaisesRegex(ImportError, "private shadcn-qt-pro"):
            importlib.import_module("shadcn_qt.pro")


if __name__ == "__main__":
    unittest.main()
