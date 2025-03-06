import numpy as np
import pandas as pd
from funtracks.data_model import NodeAttr

from tree_view.tracks_from_df import tracks_from_df

csv_path = "hela_example_tracks.csv"
df = pd.read_csv(csv_path)
df["time"] = df["t"]

tracks = tracks_from_df(df, features={"track_id": "track_id", "area": "area"})

# example vectorized functions with numpy arrays (use these as much as possible)
nodes = tracks.nodes()
print(f"Nodes array has shape {nodes.shape} and first value {nodes[0]}")
edges = tracks.edges()
print(f"Edges array has shape {edges.shape} and first value {edges[0]}")
out_degrees = tracks.out_degree(nodes)
print(f"Out degrees has shape {out_degrees.shape} and max value {np.max(out_degrees)}")
track_ids = tracks.get_nodes_attr(nodes, NodeAttr.TRACK_ID.value, required=True)
print(f"Track IDs has shape {track_ids.shape} and first value {track_ids[0]}")
positions = tracks.get_nodes_attr(nodes, NodeAttr.POS.value, required=True)
print(f"Positions has shape {positions.shape} and first value {positions[0]}")
# first columns of position array is times
times = positions[:, 0]
print(f"Times has shape {times.shape} and first value {times[0]}")
areas = tracks.get_nodes_attr(nodes, NodeAttr.AREA.value, required=True)
print(f"Area has shape {areas.shape} and first value {areas[0]}")

# example singular functions with native python types
# (these dont really make sense in bulk, although in_edge and out_edges could)
node = nodes[0].item()
preds = tracks.predecessors(node)
print(f"Node {node} has predecessors {preds}")
succs = tracks.successors(node)
print(f"Node {node} has successors {succs}")
