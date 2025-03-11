from qtpy.QtWidgets import QVBoxLayout, QWidget
from vispy import scene


class TreePlot(QWidget):
    """The actual vispy (or pygfx) tree plot"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        layout = QVBoxLayout(self)
        self.canvas = scene.SceneCanvas(keys="interactive", size=(800, 600), show=True)
        self.view = self.canvas.central_widget.add_view()
        self.canvas.events.mouse_press.connect(self._on_click)
        camera = scene.cameras.PanZoomCamera(
            parent=self.view.scene, aspect=1, name="PanZoom"
        )
        self.view.camera = camera
        layout.addWidget(self.canvas.native)

    def _on_click(self):
        # TODO: Implement
        pass
