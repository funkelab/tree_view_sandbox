import ast

import networkx as nx
import pandas as pd
from funtracks.data_model import NodeAttr

from .tracks import Tracks


def tracks_from_df(
    df: pd.DataFrame,
    features: dict[str, str] | None = None,
) -> Tracks:
    """Turns a pandas data frame with columns:
        t,[z],y,x,id,parent_id,[seg_id], [optional custom attr 1], ...
    into a SolutionTracks object.

    Cells without a parent_id will have an empty string or a -1 for the parent_id.

    Args:
        df (pd.DataFrame):
            a pandas DataFrame containing columns
            t,[z],y,x,id,parent_id,[seg_id], [optional custom attr 1], ...
        features (dict[str: str] | None, optional):
            Dict mapping measurement attributes (area, volume) to value that specifies a
            column from which to import. If value equals to "Recompute", recompute these
            values instead of importing them from a column. Defaults to None.

    Returns:
        TrackGraph: a tracks object wrapping a networkx graph
    Raises:
        ValueError: if the segmentation IDs in the dataframe do not match the provided
            segmentation

    """
    if features is None:
        features = {}
    # check that the required columns are present
    required_columns = ["id", NodeAttr.TIME.value, "y", "x", "parent_id"]
    for column in required_columns:
        assert column in df.columns, (
            f"Required column {column} not found in dataframe columns {df.columns}"
        )

    if not df["id"].is_unique:
        raise ValueError("The 'id' column must contain unique values")

    df = df.map(lambda x: None if pd.isna(x) else x)  # Convert NaN values to None

    # Convert custom attributes stored as strings back to lists
    for col in df.columns:
        if col not in required_columns:
            df[col] = df[col].apply(
                lambda x: ast.literal_eval(x)
                if isinstance(x, str) and x.startswith("[") and x.endswith("]")
                else x
            )
    # sort the dataframe to ensure that parents get added to the graph before children
    df = df.sort_values(NodeAttr.TIME.value)

    graph = nx.DiGraph()
    for _, row in df.iterrows():
        row_dict = row.to_dict()
        _id = int(row["id"])
        parent_id = row["parent_id"]
        if "z" in df.columns:
            pos = [int(row["time"]), row["z"], row["y"], row["x"]]
            ndims = 4
        else:
            pos = [int(row["time"]), row["y"], row["x"]]
            ndims = 3

        attrs = {
            NodeAttr.POS.value: pos,
        }

        # add all other columns into the attributes
        for attr in required_columns:
            del row_dict[attr]
        attrs.update(row_dict)

        if "track_id" in df.columns:
            attrs[NodeAttr.TRACK_ID.value] = row["track_id"]

        # add the node to the graph
        graph.add_node(_id, **attrs)

        # add the edge to the graph, if the node has a parent
        # note: this loading format does not support edge attributes
        if not pd.isna(parent_id) and parent_id != -1:
            assert parent_id in graph.nodes, (
                f"Parent id {parent_id} of node {_id} not in graph yet"
            )
            graph.add_edge(parent_id, _id)

    tracks = Tracks(
        graph=graph,
        position_attr=NodeAttr.POS.value,
        ndim=ndims,
    )

    return tracks
