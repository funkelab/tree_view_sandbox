from qtpy.QtWidgets import QVBoxLayout, QWidget

from wgpu.gui.auto import WgpuCanvas
import pygfx as gfx
import distinctipy
import numpy as np

class TreePlot(QWidget):
    """The actual vispy (or pygfx) tree plot"""

    def __init__(self, times, parent=None):
        super().__init__(parent=parent)
        self.layout = QVBoxLayout(self)
        self.times = times

        self.colors = distinctipy.get_colors(len(self.times))
        self.selected_nodes = []
        self.selected_geometry = None
        self.update()

    def update(self):
        self.canvas = WgpuCanvas()
        self.renderer = gfx.WgpuRenderer(self.canvas)
        self.scene = gfx.Scene()
        self.camera = gfx.OrthographicCamera(110, 110)
        self.camera.local.position = (50, 0, 0)
        controller = gfx.PanZoomController(self.camera, register_events=self.renderer)
        #controllerX = gfx.PanZoomController(register_events=self.renderer)
        #controllerX.add_camera(self.camera, exclude_state={"x", "width"})
        #controllerY = gfx.PanZoomController(register_events=self.renderer)
        #controllerY.add_camera(self.camera, include_state={"y", "height"})
        #controller.controls = {
        #    "mouse1": ("pan", "drag", (1, 1)),
        #    "wheel": ("zoom", "push", (0.01, 0)),
        #    "shift+wheel": ("zoom", "push", (0.01, 0)),
        #    "control+wheel": ("zoom", "push", (0, 0.01)),
        #    }

        #self.renderer.add_event_handler(self._on_click, "click")
        self.layout.addWidget(self.canvas)

        def _select_nodes(event):
            if 'Shift' not in event.modifiers:
                self.selected_nodes = []
            self.selected_nodes.append(
                    (event.pick_info["world_object"].name, event.pick_info["vertex_index"]))
            self.selected_geometry.positions.data[:,:] = 0
            for i,(itime,ivertex) in enumerate(self.selected_nodes):
                self.selected_geometry.positions.data[i,0] = itime*10
                self.selected_geometry.positions.data[i,1] = -self.times[itime][ivertex][2]
                self.selected_geometry.positions.update_range(i)
            self.canvas.request_draw()

        for itime in range(len(self.times)):
            # selected markers
            self.selected_geometry = gfx.Geometry(positions=[(0,0,0) for _ in range(100)])
            points = gfx.Points(
                self.selected_geometry,
                gfx.PointsMarkerMaterial(marker="circle",
                                         edge_color="lightblue",
                                         edge_width=6),
                render_order=3,
            )
            self.scene.add(points)

            # start markers
            points = gfx.Points(
                gfx.Geometry(positions=[(itime*10, -self.times[itime][i][2], 0) for i in (0,)]),
                gfx.PointsMarkerMaterial(marker=self.times[itime][0][0],
                                         edge_color=self.colors[itime],
                                         edge_width=4,
                                         pick_write=True),
                name=itime,
                render_order=2,
            )
            self.scene.add(points)

            @points.add_event_handler("pointer_down")
            def select_nodes(event):  _select_nodes(event)

            # middle markers
            if len(self.times[itime])>2:
                points = gfx.Points(
                    gfx.Geometry(positions=[(itime*10, -x[2], 0) for x in self.times[itime][1:-1]]),
                    gfx.PointsMarkerMaterial(marker=self.times[itime][1][0],
                                             edge_color=self.colors[itime],
                                             edge_width=4,
                                             pick_write=True),
                    name=itime,
                )
                self.scene.add(points)

                @points.add_event_handler("pointer_down")
                def select_nodes(event):  _select_nodes(event)

            # end markers
            points = gfx.Points(
                gfx.Geometry(positions=[(itime*10, -self.times[itime][i][2], 0) for i in (-1,)]),
                gfx.PointsMarkerMaterial(marker=self.times[itime][-1][0],
                                         edge_color=self.colors[itime],
                                         edge_width=4,
                                         pick_write=True),
                name=itime,
            )
            self.scene.add(points)

            @points.add_event_handler("pointer_down")
            def select_nodes(event):  _select_nodes(event)

            # lines
            positions = [[itime*10, -self.times[itime][i][2], 0.0] for i in (0,-1)]
            line = gfx.Line(
                gfx.Geometry(positions=np.array(positions).astype(np.float32)),
                gfx.LineMaterial(thickness=4.0, color=self.colors[itime]),
                render_order=4,
            )
            self.scene.add(line)

            # division lines
            if self.times[itime][-1][0]=="triangle_up":
                iprev = itime-1
                while self.times[iprev][0][2]-1 != self.times[itime][-1][2]:
                    iprev -= 1
                inext = itime+1
                while self.times[inext][0][2]-1 != self.times[itime][-1][2]:
                    inext += 1
                positions = [[iprev*10, -self.times[iprev][0][2], 0.0],
                             [itime*10, -self.times[itime][-1][2], 0.0],
                             [inext*10, -self.times[inext][0][2], 0.0]]
                line = gfx.Line(
                    gfx.Geometry(positions=np.array(positions).astype(np.float32)),
                    gfx.LineMaterial(thickness=2.0, color="white"),
                )
                self.scene.add(line)

        self.canvas.request_draw(lambda: self.renderer.render(self.scene, self.camera))
