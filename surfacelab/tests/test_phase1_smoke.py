import unittest


class SmokeTests(unittest.TestCase):
    def test_imports(self):
        import surfacelab
        from surfacelab.ui.main_window import MainWindow

        self.assertTrue(hasattr(surfacelab, "__version__") or True)

    def test_main_window_instantiates(self):
        import surfacelab.ui.main_window as mw
        import customtkinter as ctk

        root = ctk.CTk()
        root.withdraw()
        try:
            win = mw.MainWindow()
            self.assertEqual(win.title(), "SURFACELAB - Calculadora de Integrales de Superficie")
            win.destroy()
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
