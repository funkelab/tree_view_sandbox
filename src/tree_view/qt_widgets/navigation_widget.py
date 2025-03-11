from __future__ import annotations

from typing import TYPE_CHECKING

from qtpy.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QPushButton,
    QWidget,
)

if TYPE_CHECKING:
    from ..node_selection_list import NodeSelectionList
    from ..tracks import Tracks


class NavigationWidget(QWidget):
    """Widget for controlling navigation in the tree widget

    Args:
        tracks (Tracks): The tracks being displayed
        view_direction (str): The view direction of the tree widget. Options:
            "vertical", "horizontal".
        selected_nodes (NodeSelectionList): The list of selected nodes.
        feature (str): The feature currently being displayed

    """

    def __init__(
        self,
        tracks: Tracks,
        view_direction: str,
        selected_nodes: NodeSelectionList,
        feature: str,
    ):
        super().__init__()
        self.tracks = tracks
        self.view_direction = view_direction
        self.selected_nodes = selected_nodes
        self.feature = feature

        navigation_box = QGroupBox("Navigation [\u2b05 \u27a1 \u2b06 \u2b07]")
        navigation_layout = QHBoxLayout()
        left_button = QPushButton("\u2b05")
        right_button = QPushButton("\u27a1")
        up_button = QPushButton("\u2b06")
        down_button = QPushButton("\u2b07")

        left_button.clicked.connect(lambda: self.move("left"))
        right_button.clicked.connect(lambda: self.move("right"))
        up_button.clicked.connect(lambda: self.move("up"))
        down_button.clicked.connect(lambda: self.move("down"))

        navigation_layout.addWidget(left_button)
        navigation_layout.addWidget(right_button)
        navigation_layout.addWidget(up_button)
        navigation_layout.addWidget(down_button)
        navigation_box.setLayout(navigation_layout)
        navigation_box.setMaximumWidth(250)
        navigation_box.setMaximumHeight(60)

        layout = QHBoxLayout()
        layout.addWidget(navigation_box)

        self.setLayout(layout)

    def move(self, direction: str) -> None:
        """Move in the given direction on the tree view. Will select the next
        node in that direction, based on the orientation of the widget.

        Args:
            direction (str): The direction to move. Options: "up", "down",
                "left", "right"

        """
        if len(self.selected_nodes) == 0:
            return
        node_id = self.selected_nodes[0]

        if direction == "left":
            if self.view_direction == "horizontal":
                next_node = self.get_predecessor(node_id)
            else:
                next_node = self.get_next_track_node(
                    self.tracks, node_id, forward=False
                )
        elif direction == "right":
            if self.view_direction == "horizontal":
                next_node = self.get_successor(node_id)
            else:
                next_node = self.get_next_track_node(self.tracks, node_id)
        elif direction == "up":
            if self.view_direction == "horizontal":
                next_node = self.get_next_track_node(self.tracks, node_id)
            else:
                next_node = self.get_predecessor(node_id)
        elif direction == "down":
            if self.view_direction == "horizontal":
                next_node = self.get_next_track_node(
                    self.tracks, node_id, forward=False
                )
            else:
                next_node = self.get_successor(node_id)
        else:
            raise ValueError(
                f"Direction must be one of 'left', 'right', 'up', 'down', "
                f"got {direction}"
            )
        if next_node is not None:
            self.selected_nodes.add(next_node)

    def get_next_track_node(
        self, tracks: Tracks, node_id: str, forward=True
    ) -> str | None:
        """Get the node at the same time point in an adjacent track.

        Args:
            tracks (Tracks): the tracks in which to find the next node (could be a
                subset of all tracks)
            node_id (str): The current node ID to get the next from.
            forward (bool, optional): If true, pick the next track (right/down).
                Otherwise, pick the previous track (left/up). Defaults to True.

        """
        # TODO: implement
        return

    def get_predecessor(self, node_id: str) -> str | None:
        """Get the predecessor node of the given node_id

        Args:
            node_id (str): the node id to get the predecessor of

        Returns:
            str | None: THe node id of the predecessor, or none if no predecessor
            is found

        """
        # TODO: implement
        return

    def get_successor(self, node_id: str) -> str | None:
        """Get the successor node of the given node_id. If there are two children,
        picks one arbitrarily.

        Args:
            node_id (str): the node id to get the successor of

        Returns:
            str | None: THe node id of the successor, or none if no successor
            is found

        """
        # TODO: Implement
        return
