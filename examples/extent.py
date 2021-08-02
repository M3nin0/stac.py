"""This module introduces a class that models the Spatial and Temporal extents of a Collection."""

from examples._utils import Utils


class Extent:
    """The Extent object."""

    def __init__(self, data):
        """Initialize instance with dictionary data.

        Args:
            data (dict): Dict with spatial and temporal metadata.
        """
        self._spatial = data['spatial']['bbox']
        self._temporal = data['temporal']['interval']

    @property
    def spatial(self):
        """The spatial extent.

        Tip:

            You can create polygons from the spatial extent by
            using Shapely:

            .. code:: python

                >>> from shapely.geometry import box
                >>> [box(*b) for b in extent.spatial]
        """
        return self._spatial

    @property
    def temporal(self):
        """The temporal extent."""
        return self._temporal

    def _repr_html_(self): # pragma: no cover
        """Display the Extent as HTML for a rich display in IPython."""
        return Utils.render_html('extent.html', extent=self)