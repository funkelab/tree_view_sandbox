# A Sandbox Repository for Developing a Vispy Lineage Tree Viewer

## Relevant other repositories:
- [motile_tracker](https://github.com/funkelab/motile_tracker) - the current working implementation of the whole motile tracker application
    - [proof of concept vispy implementation](https://github.com/funkelab/motile_tracker/blob/63895ffcdfdc2fa4bf6336510f96370531e50b87/src/motile_plugin/data_views/views/tree_view/tree_plot.py) - This is months old and perhaps not that useful, but included here for completeness
- [finn](https://github.com/funkelab/motile_tracker) - the napari fork turned into our viewing code repo, where this tree view will go when it is complete
    - [layout code](https://github.com/funkelab/finn/blob/main/finn/track_data_views/views/tree_view/tree_widget_utils.py) - the current code that computes the tree view layout (using pandas)
- [spatial_graph](https://github.com/funkelab/motile_tracker) - the reason we are wrapping away the networkx API into a vectorized access pattern. Will replace networkx for in memory graph data structure, and will allow clicking on edges

## Notes:
The current sandbox lacks a couple features that will be needed when integrating into `finn`:
- Data editing. The TreeView should listen to signals from the Tracks object to know when data has changed. We assume that a full redraw is not too expensive - however, to increase usability, the tree view should not reset the axis or zoom level and the layout should remain as consistent as possible given the changes.
- Coordination with other views: colormaps and selection. We currently have a [TracksViewer](https://github.com/funkelab/finn/blob/main/finn/track_data_views/views_coordinator/tracks_viewer.py) object that coordinates selection and colormaps between the tree view and the data views. The treeview should accept colormaps provided externally, and will need to add to (and listen to) a shared selection collection.
