# do not put the from __future__ import annotations as it breaks the injection


from qtpy.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)
from superqt import QCollapsible

from .node_selection_list import NodeSelectionList
from .qt_widgets.flip_axes_widget import FlipTreeWidget
from .qt_widgets.navigation_widget import NavigationWidget
from .qt_widgets.tree_view_feature_widget import TreeViewFeatureWidget
from .qt_widgets.tree_view_mode_widget import TreeViewModeWidget
from .tracks import Tracks
from .tree_plot import TreePlot

import numpy as np
from funtracks.data_model import NodeAttr

class TreeWidget(QWidget):
    """pyqtgraph-based widget for lineage tree visualization and navigation"""

    def __init__(self, tracks: Tracks | None = None):
        super().__init__()
        self.tracks = tracks
        self.mode = "all"  # options: "all", "lineage"
        self.feature = "tree"  # options: "tree", "area"
        self.view_direction = "vertical"  # options: "horizontal", "vertical"

        self.selected_nodes = NodeSelectionList()

        def recurse_tree(node):
            positions = tracks.get_nodes_attr([node], NodeAttr.POS.value, required=True)
            _lineage = [["square", node, positions[:, 0][0]]]
            succs = tracks.successors(node)
            while len(succs)==1:
                node = succs[0]
                positions = tracks.get_nodes_attr([node], NodeAttr.POS.value, required=True)
                _lineage.append(["circle", node, positions[:, 0][0]])
                succs = tracks.successors(node)
            if len(succs)==0:
                _lineage[-1][0] = "cross"
                lineages.append(_lineage)
            if len(succs)>1:
                recurse_tree(succs[0])
                _lineage[-1][0] = "triangle_up"
                lineages.append(_lineage)
                recurse_tree(succs[1])

        lineages = []
        nodes = tracks.nodes()
        in_degrees = tracks.in_degree(nodes)
        for iprogenitor in np.nonzero(in_degrees==0)[0]:
            recurse_tree(nodes[iprogenitor].item())

        # Construct the tree view pyqtgraph widget
        layout = QVBoxLayout()

        self.tree_plot: TreePlot = TreePlot(lineages)
        # Add radiobuttons for switching between different display modes
        self.mode_widget = TreeViewModeWidget()
        self.mode_widget.change_mode.connect(self._set_mode)

        # Add buttons to change which feature to display
        self.feature_widget = TreeViewFeatureWidget()
        self.feature_widget.change_feature.connect(self._set_feature)

        # Add navigation widget
        self.navigation_widget = NavigationWidget(
            self.tracks,
            self.view_direction,
            self.selected_nodes,
            self.feature,
        )

        # Add widget to flip the axes
        self.flip_widget = FlipTreeWidget()
        self.flip_widget.flip_tree.connect(self._flip_axes)

        # Construct a toolbar and set main layout
        panel_layout = QHBoxLayout()
        panel_layout.addWidget(self.mode_widget)
        panel_layout.addWidget(self.feature_widget)
        panel_layout.addWidget(self.navigation_widget)
        panel_layout.addWidget(self.flip_widget)
        panel_layout.setSpacing(0)
        panel_layout.setContentsMargins(0, 0, 0, 0)

        panel = QWidget()
        panel.setLayout(panel_layout)
        panel.setMaximumWidth(930)
        panel.setMaximumHeight(82)

        # Make a collapsible for TreeView widgets
        collapsable_widget = QCollapsible("Show/Hide Tree View Controls")
        collapsable_widget.layout().setContentsMargins(0, 0, 0, 0)
        collapsable_widget.layout().setSpacing(0)
        collapsable_widget.addWidget(panel)
        collapsable_widget.collapse(animate=False)

        layout.addWidget(collapsable_widget)
        layout.addWidget(self.tree_plot)
        layout.setSpacing(0)
        self.setLayout(layout)
        self.refresh(self.tracks)

    def toggle_display_mode(self):
        """Toggle display mode."""
        self.mode_widget._toggle_display_mode()

    def toggle_feature_mode(self):
        """Toggle feature mode."""
        self.feature_widget._toggle_feature_mode()

    def _flip_axes(self):
        """Flip the axes of the plot"""
        if self.view_direction == "horizontal":
            self.view_direction = "vertical"
        else:
            self.view_direction = "horizontal"

    def _update_selected(self):
        """Called whenever the selection list is updated."""

    def refresh(self, tracks: Tracks) -> None:
        """Called when the TracksViewer emits the tracks_updated signal, indicating
        that a new set of tracks should be viewed.
        """

    def _set_mode(self, mode: str) -> None:
        """Set the display mode to all or lineage view. Currently, linage
        view is always horizontal and all view is always vertical.

        Args:
            mode (str): The mode to set the view to. Options are "all" or "lineage"

        """

    def _set_feature(self, feature: str) -> None:
        """Set the feature mode to 'tree' or 'area'. For this the view is always
        horizontal.

        Args:
            feature (str): The feature to plot. Options are "tree" or "area"

        """
        if feature not in ["tree", "area"]:
            raise ValueError(f"Feature must be 'tree' or 'area', got {feature}")

    def _update_lineage_df(self) -> None:
        """Subset dataframe to include only nodes belonging to the current lineage"""
