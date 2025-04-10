from qtpy.QtWidgets import QVBoxLayout, QWidget

from wgpu.gui.auto import WgpuCanvas
import pygfx as gfx
import distinctipy
import numpy as np

class TreePlot(QWidget):
    """The actual vispy (or pygfx) tree plot"""

    def __init__(self, lineages, parent=None):
        super().__init__(parent=parent)
        self.layout = QVBoxLayout(self)
        self.lineages = lineages

        self.colors = distinctipy.get_colors(sum([len(x) for x in self.lineages]))
        self.selected_nodes = []
        self.selected_geometry = None

        self.canvas = WgpuCanvas()
        self.renderer = gfx.WgpuRenderer(self.canvas)
        self.scene = gfx.Scene()
        self.camera = gfx.OrthographicCamera(110, 110)
        self.camera.local.position = (50, 0, 0)
        controller = gfx.PanZoomController(self.camera, register_events=self.renderer)

        self.layout.addWidget(self.canvas)

    def _select_nodes(self, event):
        if 'Shift' not in event.modifiers:
            self.selected_nodes = []
        self.selected_nodes.append(
                (event.pick_info["world_object"].name, event.pick_info["vertex_index"]))
        self.selected_geometry.positions.data[:,:] = 0
        for i,(xy0,y) in enumerate(self.selected_nodes):
            self.selected_geometry.positions.data[i,0] = xy0[0]*10
            self.selected_geometry.positions.data[i,1] = xy0[1]-y
            self.selected_geometry.positions.update_range(i)
        self.canvas.request_draw()

    def update(self, mode):
        self.scene.clear()

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

        x = 0
        for itree in range(len(self.lineages)):
            # skip if not selected
            if mode=="lineage":
                skip=True
                for itrack in range(len(self.lineages[itree])):
                    for selected in self.selected_nodes:
                        if selected[0][2] == self.lineages[itree][itrack][0][1]:
                            skip=False
                            break
                        if not skip: break
                if skip: continue

            for itrack in range(len(self.lineages[itree])):
                track = self.lineages[itree][itrack]

                # start markers
                points = gfx.Points(
                    gfx.Geometry(positions=[(x*10, -track[i][2], 0) for i in (0,)]),
                    gfx.PointsMarkerMaterial(marker=track[0][0],
                                             edge_color=self.colors[x],
                                             edge_width=4,
                                             pick_write=True),
                    name=(x, -track[0][2], track[0][1]),
                    render_order=2,
                )
                self.scene.add(points)

                @points.add_event_handler("pointer_down")
                def select_nodes(event):  self._select_nodes(event)

                # middle markers
                if len(track)>2:
                    points = gfx.Points(
                        gfx.Geometry(positions=[(x*10, -i[2], 0) for i in track[1:-1]]),
                        gfx.PointsMarkerMaterial(marker=track[1][0],
                                                 edge_color=self.colors[x],
                                                 edge_width=4,
                                                 pick_write=True),
                        name=(x, -track[1][2], track[0][1]),
                    )
                    self.scene.add(points)

                    @points.add_event_handler("pointer_down")
                    def select_nodes(event):  self._select_nodes(event)

                # end markers
                points = gfx.Points(
                    gfx.Geometry(positions=[(x*10, -track[i][2], 0) for i in (-1,)]),
                    gfx.PointsMarkerMaterial(marker=track[-1][0],
                                             edge_color=self.colors[x],
                                             edge_width=4,
                                             pick_write=True),
                    name=(x, -track[-1][2], track[0][1]),
                )
                self.scene.add(points)

                @points.add_event_handler("pointer_down")
                def select_nodes(event):  self._select_nodes(event)

                # vertical track lines
                positions = [[x*10, -track[i][2], 0.0] for i in (0,-1)]
                line = gfx.Line(
                    gfx.Geometry(positions=np.array(positions).astype(np.float32)),
                    gfx.LineMaterial(thickness=4.0, color=self.colors[x]),
                    render_order=4,
                )
                self.scene.add(line)

                # diagonal division lines
                if track[-1][0]=="triangle_up":
                    iprev = itrack-1
                    while self.lineages[itree][iprev][0][2]-1 != track[-1][2]:
                        iprev -= 1
                    inext = itrack+1
                    while self.lineages[itree][inext][0][2]-1 != track[-1][2]:
                        inext += 1
                    positions = [[(x-(itrack-iprev))*10, -self.lineages[itree][iprev][0][2], 0.0],
                                 [x*10, -track[-1][2], 0.0],
                                 [(x-(itrack-inext))*10, -self.lineages[itree][inext][0][2], 0.0]]
                    line = gfx.Line(
                        gfx.Geometry(positions=np.array(positions).astype(np.float32)),
                        gfx.LineMaterial(thickness=2.0, color="white"),
                    )
                    self.scene.add(line)

                x += 1

        self.selected_nodes = []
        self.canvas.request_draw(lambda: self.renderer.render(self.scene, self.camera))
