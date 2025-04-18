from qtpy.QtWidgets import QVBoxLayout, QWidget

from wgpu.gui.auto import WgpuCanvas
import pygfx as gfx
import distinctipy
import numpy as np
from collections import namedtuple
import pylinalg as la
import copy

class TreePlot(QWidget):
    """The actual vispy (or pygfx) tree plot"""

    def __init__(self, lineages, parent=None):
        super().__init__(parent=parent)
        self.layout = QVBoxLayout(self)
        self.lineages = lineages

        self.colors = distinctipy.get_colors(sum([len(x) for x in self.lineages]))
        self.selected_nodes = []
        self.selected_lineages = []
        self.selected_geometry = None
        self.mode = "all"  # options: "all", "lineage"
        self.feature = "tree"  # options: "tree", "area"
        self.view_direction = "vertical"  # options: "horizontal", "vertical"

        self.NameData = namedtuple('NameData', 'x, node, offset, time, area, itree, itrack')

        self.canvas = WgpuCanvas()
        self.renderer = gfx.WgpuRenderer(self.canvas)
        self.scene = gfx.Scene()
        self.camera = gfx.OrthographicCamera(110, 110, maintain_aspect=False)
        self.controller_xy = gfx.PanZoomController(register_events=self.renderer)
        self.controller_xy.add_camera(self.camera)
        self.controller_x = gfx.PanZoomController(register_events=self.renderer, enabled=False)
        self.controller_x.add_camera(self.camera, include_state={"x", "width"})
        self.controller_y = gfx.PanZoomController(register_events=self.renderer, enabled=False)
        self.controller_y.add_camera(self.camera, include_state={"y", "height"})

        self.layout.addWidget(self.canvas)

        self.canvas.request_draw(self.animate)

    def animate(self):
        self.renderer.render(self.scene, self.camera)

    def set_event_handler(self, f):
        self.canvas.add_event_handler(f, "*")

    def both_xy(self):
        self.controller_xy.enabled=True
        self.controller_x.enabled=False
        self.controller_y.enabled=False

    def only_x(self):
        self.controller_xy.enabled=False
        self.controller_x.enabled=True

    def only_y(self):
        self.controller_xy.enabled=False
        self.controller_y.enabled=True

    def _select_nodes(self, event):
        if 'Shift' not in event.modifiers:
            self.selected_nodes = []
        self.selected_nodes.append(
                (event.pick_info["world_object"].name, event.pick_info["vertex_index"]))
        self.draw_selected_nodes()

    def draw_selected_nodes(self):
        self.selected_geometry.positions.data[:,:] = 0
        for i,(nd,vi) in enumerate(self.selected_nodes):
            self.selected_geometry.colors.data[i] = [0.68,0.85,0.90,1]  # light blue
            self.selected_geometry.colors.update_range(i)
            self.selected_geometry.positions.data[i,0] = nd.x*10 if self.feature == "tree" else nd.area[vi+nd.offset]
            self.selected_geometry.positions.data[i,1] = nd.time[vi+nd.offset]
            self.selected_geometry.positions.update_range(i)
        self.canvas.request_draw()

    def select_next_cell(self):
        node = self.selected_nodes[-1]
        track = self.selected_lineages[node[0].itree][node[0].itrack]
        if node[1] + node[0].offset < len(track)-1:
            icell = node[1] + node[0].offset + 1
            if icell == len(track)-1:
                offset = len(track)-1
                vi = 0
            else:
                offset = 1
                vi = icell-1
            time, area = [-t.time for t in track], [t.area for t in track]
            self.selected_nodes[-1] = (
                self.NameData(node[0].x, track[0].node, offset, time, area,
                              node[0].itree, node[0].itrack),
                vi
                )
            self.draw_selected_nodes()
        elif track[-1].marker=="triangle_up":
            iprev = node[0].itrack-1
            while self.selected_lineages[node[0].itree][iprev][0].time-1 != track[-1].time:
                iprev -= 1
            track = self.selected_lineages[node[0].itree][iprev]
            x = node[0].x - (node[0].itrack - iprev)
            time, area = [-t.time for t in track], [t.area for t in track]
            self.selected_nodes[-1] = (
                self.NameData(x, track[0].node, 0, time, area, node[0].itree, iprev),
                0
                )
            self.draw_selected_nodes()

    def select_prev_cell(self):
        node = self.selected_nodes[-1]
        track = self.selected_lineages[node[0].itree][node[0].itrack]
        if node[1] + node[0].offset > 0:
            icell = node[1] + node[0].offset - 1
            if icell == 0:
                offset = 0
                vi = 0
            else:
                offset = 1
                vi = icell-1
            time, area = [-t.time for t in track], [t.area for t in track]
            self.selected_nodes[-1] = (
                self.NameData(node[0].x, track[0].node, offset,
                              time, area, node[0].itree, node[0].itrack),
                vi
                )
            self.draw_selected_nodes()
        elif track[0].marker=="square":
            iprev = node[0].itrack-1
            while iprev>=0 and self.selected_lineages[node[0].itree][iprev][-1].time+1 > track[0].time:
                iprev -= 1
            if iprev>=0 and self.selected_lineages[node[0].itree][iprev][-1].time+1 == track[0].time:
                iparent = iprev
            else:
                inext = node[0].itrack+1
                while inext<len(self.selected_lineages[node[0].itree]) and \
                        self.selected_lineages[node[0].itree][inext][-1].time+1 > track[0].time:
                    inext += 1
                if inext<len(self.selected_lineages[node[0].itree]) and \
                        self.selected_lineages[node[0].itree][inext][-1].time+1 == track[0].time:
                    iparent = inext
                else:
                    return
            track = self.selected_lineages[node[0].itree][iparent]
            x = node[0].x - (node[0].itrack - iparent)
            time, area = [-t.time for t in track], [t.area for t in track]
            self.selected_nodes[-1] = (
                self.NameData(x, track[0].node, len(time)-1, time, area, node[0].itree, iparent),
                0
                )
            self.draw_selected_nodes()

    def select_next_lineage(self):
        node = self.selected_nodes[-1]
        itree, itrack = node[0].itree, node[0].itrack+1
        if itrack == len(self.selected_lineages[itree]):
            itrack = 0
            itree += 1
        found = False
        dx = 1
        while itree < len(self.selected_lineages) and itrack < len(self.selected_lineages[itree]):
            time = -node[0].time[node[1]+node[0].offset]
            times = [x.time for x in self.selected_lineages[itree][itrack]]
            if time in times:
                icell = times.index(time)
                found = True
                break
            dx += 1
            itrack += 1
            if itrack == len(self.selected_lineages[itree]):
                itrack = 0
                itree += 1
        if found:
            track = self.selected_lineages[itree][itrack]
            if icell == 0:
                offset = 0
                vi = 0
            elif icell==len(track)-1:
                offset = len(track)-1
                vi = 0
            else:
                offset = 1
                vi = icell-1
            time, area = [-t.time for t in track], [t.area for t in track]
            self.selected_nodes[-1] = (
                self.NameData(node[0].x+dx, track[0].node, offset, time, area, itree, itrack),
                vi
                )
            self.draw_selected_nodes()

    def select_prev_lineage(self):
        node = self.selected_nodes[-1]
        itree, itrack = node[0].itree, node[0].itrack-1
        if itrack == -1:
            itree -= 1
            itrack = len(self.selected_lineages[itree])-1
        found = False
        dx = 1
        while itree >= 0 and itrack >= 0:
            time = -node[0].time[node[1]+node[0].offset]
            times = [x.time for x in self.selected_lineages[itree][itrack]]
            if time in times:
                icell = times.index(time)
                found = True
                break
            dx += 1
            itrack -= 1
            if itrack == -1:
                itree -= 1
                itrack = len(self.selected_lineages[itree])-1
        if found:
            track = self.selected_lineages[itree][itrack]
            if icell == 0:
                offset = 0
                vi = 0
            elif icell==len(track)-1:
                offset = len(track)-1
                vi = 0
            else:
                offset = 1
                vi = icell-1
            time, area = [-t.time for t in track], [t.area for t in track]
            self.selected_nodes[-1] = (
                self.NameData(node[0].x-dx, track[0].node, offset, time, area, itree, itrack),
                vi
                )
            self.draw_selected_nodes()

    def select_next_feature(self):
        node = self.selected_nodes[-1]
        icell = node[1] + node[0].offset
        time = -node[0].time[icell]
        feature = node[0].area[icell]
        feature_next = np.inf
        found = False
        for itree in range(len(self.selected_lineages)):
            for itrack in range(len(self.selected_lineages[itree])):
                times = [x.time for x in self.selected_lineages[itree][itrack]]
                if time in times:
                    icell = times.index(time)
                    thisfeature = self.selected_lineages[itree][itrack][icell].area
                    if feature < thisfeature < feature_next:
                        itree_next, itrack_next, icell_next = itree, itrack, icell
                        feature_next = thisfeature
                        found = True
        if found:
            track = self.selected_lineages[itree_next][itrack_next]
            x = sum([len(x) for x in self.selected_lineages[0:itree_next]]) + itrack_next
            if icell_next == 0:
                offset = 0
                vi = 0
            elif icell_next==len(track)-1:
                offset = len(track)-1
                vi = 0
            else:
                offset = 1
                vi = icell_next-1
            time, area = [-t.time for t in track], [t.area for t in track]
            self.selected_nodes[-1] = (
                self.NameData(x, track[0].node, offset, time, area, itree_next, itrack_next),
                vi
                )
            self.draw_selected_nodes()

    def select_prev_feature(self):
        node = self.selected_nodes[-1]
        icell = node[1] + node[0].offset
        time = -node[0].time[icell]
        feature = node[0].area[icell]
        feature_prev = 0
        found = False
        for itree in range(len(self.selected_lineages)):
            for itrack in range(len(self.selected_lineages[itree])):
                times = [x.time for x in self.selected_lineages[itree][itrack]]
                if time in times:
                    icell = times.index(time)
                    thisfeature = self.selected_lineages[itree][itrack][icell].area
                    if feature > thisfeature > feature_prev:
                        itree_prev, itrack_prev, icell_prev = itree, itrack, icell
                        feature_prev = thisfeature
                        found = True
        if found:
            track = self.selected_lineages[itree_prev][itrack_prev]
            x = sum([len(x) for x in self.selected_lineages[0:itree_prev]]) + itrack_prev
            if icell_prev == 0:
                offset = 0
                vi = 0
            elif icell_prev==len(track)-1:
                offset = len(track)-1
                vi = 0
            else:
                offset = 1
                vi = icell_prev-1
            time, area = [-t.time for t in track], [t.area for t in track]
            self.selected_nodes[-1] = (
                self.NameData(x, track[0].node, offset, time, area, itree_prev, itrack_prev),
                vi
                )
            self.draw_selected_nodes()

    def set_mode(self, mode):
        self.mode = mode

    def set_feature(self, feature):
        self.feature = feature

    def set_view_direction(self, direction):
        self.view_direction = direction

    def get_feature(self):
        return self.feature

    def get_view_direction(self):
        return self.view_direction

    def reset_fov(self):
        self.controller_xy.enabled=False
        self.camera.set_state(self.camera_state0)
        self.controller_xy.enabled=True

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
        iselected_tree = 0
        self.selected_lineages = []
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
            self.selected_lineages.append(self.lineages[itree])

            for itrack in range(len(self.lineages[itree])):
                track = self.lineages[itree][itrack]
                time, area =  [-t.time for t in track], [t.area for t in track],

                # start markers
                points = gfx.Points(
                    gfx.Geometry(positions=[(x*10 if self.feature == "tree" else track[i].area,
                                             -track[i].time,
                                             0) for i in (0,)]),
                    gfx.PointsMarkerMaterial(marker=track[0].marker,
                                             edge_color=self.colors[x],
                                             edge_width=4,
                                             pick_write=True),
                    name=self.NameData(x, track[0].node, 0, time, area, iselected_tree, itrack),
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
                        name=self.NameData(x, track[0].node, 1, time, area, iselected_tree, itrack),
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
                    name=self.NameData(x, track[0].node, len(time)-1, time, area, iselected_tree, itrack),
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
            iselected_tree += 1

        self.selected_nodes = []

        if self.view_direction == "horizontal":
            self.scene.local.rotation = la.quat_from_axis_angle([0., 0., 1.], 3.14159/2)
        else:
            self.scene.local.rotation = [0., 0., 0., 1.]

        self.camera.show_object(self.scene)
        self.camera_state0 = copy.deepcopy(self.camera.get_state())
        self.canvas.update()

