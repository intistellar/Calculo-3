from __future__ import annotations

import os
import tempfile
import unittest

from surfacelab.models.integral_model import IntegralModel
from surfacelab.models.surface_model import Limits
from surfacelab.utils.export import ResultExporter
from surfacelab.visualization.vector_plot import MatplotlibSurfaceRenderer


class TestPhase12Export(unittest.TestCase):
    def test_export_text(self):
        result = {
            "success": True,
            "exact": 6,
            "approximate": 6.0,
            "method": "test",
            "procedure": ["Step 1", "Step 2"],
        }
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w", encoding="utf-8") as f:
            path = f.name
        try:
            ResultExporter.export_text(result, path, "Test")
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("Resultado exacto: 6", content)
            self.assertIn("Step 1", content)
        finally:
            os.unlink(path)

    def test_export_image(self):
        model = IntegralModel.create(
            system="cartesian",
            func_expr="0",
            limits=Limits(0, 2, 0, 3),
            integral_type="area",
        ).model
        fig = MatplotlibSurfaceRenderer.render(model, resolution=10)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            path = f.name
        try:
            ResultExporter.export_image(fig, path)
            self.assertTrue(os.path.exists(path))
            self.assertGreater(os.path.getsize(path), 0)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
