"""Smoke: core imports work without loading widget subclasses (no Qt binding required for theme-only)."""

import unittest


class TestImportCore(unittest.TestCase):
    def test_import_package_without_qt_widgets(self):
        import qtshadcn

        self.assertTrue(hasattr(qtshadcn, "apply_theme"))
        self.assertTrue(hasattr(qtshadcn, "detect_binding"))
        self.assertTrue(hasattr(qtshadcn, "enable_native_widget_styling"))

    def test_generated_qss_strings_exist(self):
        from qtshadcn._generated import base_qss

        self.assertGreater(len(base_qss.LIGHT_QSS), 100)
        self.assertGreater(len(base_qss.DARK_QSS), 100)


if __name__ == "__main__":
    unittest.main()
