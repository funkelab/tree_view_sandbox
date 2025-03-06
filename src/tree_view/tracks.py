from __future__ import annotations

import networkx as nx
import numpy as np
from psygnal import Signal


class Tracks:
    """A graph representation of a tracking solution.
    The graph nodes represent detections and must have a position attribute (which
    includes time). Edges in the graph represent links across time.

    Attributes:
        graph (nx.DiGraph): A graph with nodes representing detections and
            and edges representing links across time.
        position_attr (str): The attribute holding the position (including time)
        ndim (int): The number of dimensions of the data. Must match the length of the
            position attribute arrays (includes time)

    """

    data_changed = Signal()

    def __init__(
        self,
        graph: nx.DiGraph,
        position_attr: str,
        ndim: int | None = None,
    ):
        self.graph = graph
        self.position_attr = position_attr
        self.ndim = ndim

    def nodes(self):
        return np.array(self.graph.nodes())

    def edges(self):
        return np.array(self.graph.edges())

    def in_degree(self, nodes: np.ndarray | None = None) -> np.ndarray:
        if nodes is not None:
            return np.array([self.graph.in_degree(node.item()) for node in nodes])
        else:
            return np.array(self.graph.in_degree())

    def out_degree(self, nodes: np.ndarray | None = None) -> np.ndarray:
        if nodes is not None:
            return np.array([self.graph.out_degree(node.item()) for node in nodes])
        else:
            return np.array(self.graph.out_degree())

    def predecessors(self, node: int) -> list[int]:
        return list(self.graph.predecessors(node))

    def successors(self, node: int) -> list[int]:
        return list(self.graph.successors(node))

    # TODO: may need connected components or lineage ids stored on the graph

    def get_node_attr(self, node: int, attr: str, required: bool = False) -> float:
        if required:
            return self.graph.nodes[node][attr]
        else:
            return self.graph.nodes[node].get(attr, None)

    def get_nodes_attr(
        self, nodes: np.ndarray, attr: str, required: bool = False
    ) -> np.ndarray:
        return np.array(
            [self.get_node_attr(node, attr, required=required) for node in nodes]
        )

    def get_edge_attr(
        self, edge: tuple[int, int], attr: str, required: bool = False
    ) -> float:
        if required:
            return self.graph.edges[edge][attr]
        else:
            return self.graph.edges[edge].get(attr, None)

    def get_edges_attr(
        self, edges: np.ndarray, attr: str, required: bool = False
    ) -> np.ndarray:
        return np.array(
            [self.get_edge_attr(edge, attr, required=required) for edge in edges]
        )
