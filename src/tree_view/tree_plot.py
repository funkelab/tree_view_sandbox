from qtpy.QtWidgets import QVBoxLayout, QWidget

from wgpu.gui.auto import WgpuCanvas
import pygfx as gfx
import distinctipy
import numpy as np
from collections import namedtuple
import pylinalg as la

class TreePlot(QWidget):
    """The actual vispy (or pygfx) tree plot"""

    def __init__(self, lineages, parent=None):
        super().__init__(parent=parent)
        self.layout = QVBoxLayout(self)
        self.lineages = lineages

        self.colors = distinctipy.get_colors(sum([len(x) for x in self.lineages]))
        self.selected_nodes = []
        self.selected_geometry = None
        self.mode = "all"  # options: "all", "lineage"
        self.feature = "tree"  # options: "tree", "area"
        self.view_direction = "vertical"  # options: "horizontal", "vertical"

        self.NameData = namedtuple('NameData', 'x, node, time, area')

        self.canvas = WgpuCanvas()
        self.renderer = gfx.WgpuRenderer(self.canvas)
        self.scene = gfx.Scene()
        self.camera = gfx.OrthographicCamera(110, 110)
        self.camera.local.position = (50, 0, 0)
        controller = gfx.PanZoomController(self.camera, register_events=self.renderer)

        self.layout.addWidget(self.canvas)

    def set_event_handler(self, f):
        self.canvas.add_event_handler(f, "*")

    def _select_nodes(self, event):
        if 'Shift' not in event.modifiers:
            self.selected_nodes = []
        self.selected_nodes.append(
                (event.pick_info["world_object"].name, event.pick_info["vertex_index"]))
        self.selected_geometry.positions.data[:,:] = 0
        for i,(nd,vi) in enumerate(self.selected_nodes):
            self.selected_geometry.colors.data[i] = [0.68,0.85,0.90,1]  # light blue
            self.selected_geometry.colors.update_range(i)
            self.selected_geometry.positions.data[i,0] = nd.x*10 if self.feature == "tree" else nd.area[vi]
            self.selected_geometry.positions.data[i,1] = nd.time[vi]
            self.selected_geometry.positions.update_range(i)
        self.canvas.request_draw()

    def set_mode(self, mode):
        self.mode = mode

    def set_feature(self, feature):
        self.feature = feature

    def set_view_direction(self, direction):
        self.view_direction = direction

    def update(self):
        self.scene.clear()

        # selected markers
        self.selected_geometry = gfx.Geometry(positions=[(0,0,0) for _ in range(100)],
                                              colors=[[0,0,0,0] for _ in range(100)],
                                              )
        points = gfx.Points(
            self.selected_geometry,
            gfx.PointsMarkerMaterial(marker="circle",
                                     color_mode="vertex",
                                     size=15,
                                     size_space="screen",
                                     ),
            render_order=3,
        )
        self.scene.add(points)

        x = 0
        for itree in range(len(self.lineages)):
            # skip if not selected
            if self.mode=="lineage":
                skip=True
                for itrack in range(len(self.lineages[itree])):
                    for selected in self.selected_nodes:
                        if selected[0].node == self.lineages[itree][itrack][0].node:
                            skip=False
                            break
                        if not skip: break
                if skip: continue

            for itrack in range(len(self.lineages[itree])):
                track = self.lineages[itree][itrack]

                # start markers
                points = gfx.Points(
                    gfx.Geometry(positions=[(x*10 if self.feature == "tree" else track[i].area,
                                             -track[i].time,
                                             0) for i in (0,)]),
                    gfx.PointsMarkerMaterial(marker=track[0].marker,
                                             edge_color=self.colors[x],
                                             edge_width=4,
                                             pick_write=True),
                    name=self.NameData(x, track[0].node, [-track[0].time], [track[0].area]),
                    render_order=2,
                )
                self.scene.add(points)

                @points.add_event_handler("pointer_down")
                def select_nodes(event):  self._select_nodes(event)

                # middle markers
                if len(track)>2:
                    points = gfx.Points(
                        gfx.Geometry(positions=[(x*10 if self.feature == "tree" else t.area,
                                                 -t.time,
                                                 0) for t in track[1:-1]]),
                        gfx.PointsMarkerMaterial(marker=track[1].marker,
                                                 edge_color=self.colors[x],
                                                 edge_width=4,
                                                 pick_write=True),
                        name=self.NameData(x, track[0].node, [-t.time for t in track[1:-1]], [t.area for t in track[1:-1]]),
                    )
                    self.scene.add(points)

                    @points.add_event_handler("pointer_down")
                    def select_nodes(event):  self._select_nodes(event)

                # end markers
                points = gfx.Points(
                    gfx.Geometry(positions=[(x*10 if self.feature == "tree" else track[i].area,
                                             -track[i].time,
                                             0) for i in (-1,)]),
                    gfx.PointsMarkerMaterial(marker=track[-1].marker,
                                             edge_color=self.colors[x],
                                             edge_width=4,
                                             pick_write=True),
                    name=self.NameData(x, track[0].node, [-track[-1].time], [track[-1].area]),
                )
                self.scene.add(points)

                @points.add_event_handler("pointer_down")
                def select_nodes(event):  self._select_nodes(event)

                # vertical track lines
                line = gfx.Line(
                    gfx.Geometry(positions=[[x*10 if self.feature == "tree" else t.area,
                                             -t.time,
                                             0.0] for t in track]),
                    gfx.LineMaterial(thickness=4.0, color=self.colors[x]),
                    render_order=4,
                )
                self.scene.add(line)

                # diagonal division lines
                if track[-1].marker=="triangle_up":
                    iprev = itrack-1
                    while self.lineages[itree][iprev][0].time-1 != track[-1].time:
                        iprev -= 1
                    inext = itrack+1
                    while self.lineages[itree][inext][0].time-1 != track[-1].time:
                        inext += 1
                    positions = [[(x-(itrack-iprev))*10 if self.feature == "tree" else self.lineages[itree][iprev][0].area,
                                   -self.lineages[itree][iprev][0].time,
                                   0.0],
                                 [x*10 if self.feature == "tree" else track[-1].area,
                                  -track[-1].time,
                                  0.0],
                                 [(x-(itrack-inext))*10 if self.feature == "tree" else self.lineages[itree][inext][0].area,
                                  -self.lineages[itree][inext][0].time,
                                  0.0]]
                    line = gfx.Line(
                        gfx.Geometry(positions=positions),
                        gfx.LineMaterial(thickness=2.0, color="white"),
                    )
                    self.scene.add(line)

                x += 1

        self.selected_nodes = []

        if self.view_direction == "horizontal":
            self.scene.local.rotation = la.quat_from_axis_angle([0., 0., 1.], 3.14159/2)
        else:
            self.scene.local.rotation = [0., 0., 0., 1.]

        self.canvas.request_draw(lambda: self.renderer.render(self.scene, self.camera))
        self.camera.show_object(self.scene, scale=0.7)
