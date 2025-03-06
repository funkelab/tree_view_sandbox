# Converting the motile tracker tree view to VisPy
The motile tracker currently has implemented a tree view for navigating and editing lineage results. It is implemented with pyqtgraph, which is prohibitively slow for medium/large datasets (1.15 seconds for 8601 nodes, the HeLa sample dataset). This is especially bad for editing, since the interactivity of the UI is bottlenecked by re-drawing the tree view when a node/edge is added or deleted. We want to re-implement the tree view in VisPy to speed up editing interaction time and to allow more customization in the future, including potential re-use of graph visualization code in the data view.

## Design discussion points
The tracking results are represented as a Tracks data structure, which contains a networkx graph with the lineage information. Currently the tree view converts the networkx graph into a pandas data frame before updating the visualization. This means that the data frame must also be re-built or edited whenever the user edits the graph, and duplicates a lot of information.

Ideally, the new tree view will operate directly on the Tracks data structure. The existing Tracks API will likely need to be augmented to avoid using the networkx API directly - we can work together on specifying the necessary functions. 

Additionally, in the future we want to replace the Points and Tracks napari layers in the dataview with custom VisPy graph rendering. Any design that allows us to re-use VisPy components for rendering graphs in data space as well as in the tree view space will help with that step in the future.

For performance, we expect that drawing the graph without the pyqtgraph overhead will already be fast enough (<0.1 second for 8601 nodes) to allow editing to feel interactive while still re-drawing the whole graph every time. However, if this is not the case, we can discuss implementing incremental updates or other optimizations.

## Specification of functionality
See the current motile tracker implementation for a working example. We want to start with re-implementing current functionality, but future plans are mentioned to guide the design and minor, easy-to-implement improvements can be added during the re-write.

### Tree view data display
- [ ] Nodes of the graph are (face) colored by track id 
    - *Planned*: face/edge color configurable based on any node/edge features
- [ ] Nodes have symbols based on their "type" (triangle for a division, x for an endpoint, circle for other cells)
    - *Planned*: square for start point
- [ ] Standard view displays all the lineages, with time on one axis, and the other axis laid out so that lineages do not cross 
    - *Planned*: support divisions with more than 2 children
    - *Planned*: need to support or at least not fail on merges (from 2 or more parents), which would likely require crossing edges
- [ ] Feature view displays all the lineages, laid out with time on one axis and cell area/volume on the other axis
    -  *Planned*: support other continuous features than area (that will be stored on the graph)
- [ ] All view displays all the lineages, while "lineage" mode displays the currently selected lineage(s) (all lineages with at least one selected node)
- [ ] Tree view toggle display between all and lineage only mode by: 
    - [ ] Pressing `Q`
    - [ ] Using the radio button in the menu
- [ ] Tree view toggle between standard view and feature display by: 
    - [ ] Pressing `W`
    - [ ] Using the radio button in the menu
- *Planned*: Hovering nodes displays the node id
- *Planned*: Track IDs are displayed in the tracks UI (potentially column labels)
- *Planned*: Display other subsets of the data rather than just selected lineages and all. (We will be implementing track/node groups shortly)

### Tree view data selection
- [ ] Clicking on a node selects it, and un-selects other nodes
- [ ] Shift-click on a node selects it, and does not un-select other nodes
- [ ] Selected nodes are larger and have a light blue outline

*Note:* Shift-dragging on the canvas to select all nodes inside the selection box is currently supported, but is not required in the new implementation.

*Planned*: edge selection (I expect this to be difficult until we switch data structures from networkx)

### Tree view canvas controls
- [ ] Pan by mouse drag
- [ ] Zoom by mouse wheel/track pad scroll
- [ ] Zoom horizontally by: 
    - [ ] Drag horizontally when holding right mouse button
    - [ ] Hold x and mouse wheel/track pad scroll
- [ ] Zoom vertically by: 
    - [ ] Drag vertically when holding right mouse button
    - [ ] Hold y and mouse wheel/track pad scroll
- [ ] Reset view by: right mouse click
- [ ] Flip the x and y tree view axes by:
    - [ ] Press `f`
    - [ ] The `Flip` button

### Tree view navigation
**Note**: The desired functionality described below is a little different than what is currently implemented.

- [ ] Arrow keys/buttons that go along the time axis (up/down when time is vertical, right/left when horizontal) select the next/previous cell in the lineage. At division, one next child is chosen arbitrarily (currently left/bottom).
- [ ] Arrow keys/buttons that go along the non-time axis select the next cell in that direction in that time point. If there is no next cell in that time point, it does nothing. "next" is determined by the view. In standard view, it is the next track in the layout with a cell in that time point. In feature view, it is the node with the next largest/smallest feature value in that time point.
    - *note*: currently, in lineage only mode, you can currently navigate to the "next" lineage using the arrow keys to go beyond the currently visible nodes. This should not happen anymore.
- [ ] *Planned*: Add a new keybind (shift + arrow?) that displays the "next" lineage (in either view, regardless of whether the next lineage has nodes in the current time point).  
