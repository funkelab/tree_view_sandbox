from qtpy.QtWidgets import QVBoxLayout, QWidget

import numpy as np

# vispy
from vispy import scene

# pygfx
from wgpu.gui.auto import WgpuCanvas
import pygfx as gfx


class TreePlot(QWidget):
    """The actual vispy (or pygfx) tree plot"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        layout = QVBoxLayout(self)

        # vispy
        self.canvas = scene.SceneCanvas(keys="interactive", size=(800, 600), show=True)
        self.view = self.canvas.central_widget.add_view()
        self.canvas.events.mouse_press.connect(self._on_click)
        camera = scene.cameras.PanZoomCamera(
            parent=self.view.scene, aspect=1, name="PanZoom"
        )
        self.view.camera = camera
        layout.addWidget(self.canvas.native)

        # pygfx
        self.canvas2 = WgpuCanvas()
        self.renderer2 = gfx.WgpuRenderer(self.canvas2)
        self.scene2 = gfx.Scene()
        self.camera2 = gfx.OrthographicCamera(110, 110)
        self.camera2.local.position = (50, 0, 0)
        self.renderer2.add_event_handler(self._on_click, "click")
        layout.addWidget(self.canvas2)

    def _on_click(self, arg):
        #pos = np.random.rand(10,2).astype(np.float32) * 100

        # vispy
        scene.visuals.Line(pos=pos, color="white", parent=self.canvas.scene)
        self.canvas.update()

        # pygfx
        positions = np.column_stack([pos, np.zeros((10,)).astype(np.float32)])
        line = gfx.Line(
            gfx.Geometry(positions=positions),
            gfx.LineMaterial(thickness=2.0, color=(0.0, 0.7, 0.3, 1.0)),
        )
        self.scene2.add(line)
        self.canvas2.request_draw(lambda: self.renderer2.render(self.scene2, self.camera2))
