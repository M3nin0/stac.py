"""This module introduces a class that models a STAC Catalog."""

from examples._base_container import BaseContainer
from examples._utils import Utils


class Catalog(BaseContainer):
    """The STAC Catalog."""

    def __init__(self, data=None):
        """Initialize the Catalog instance with dictionary data.

        Args:
            data (dict): A Python dictionary with catalog metadata.
        """
        super(Catalog, self).__init__(data)

    def _repr_html_(self):  # pragma: no cover
        """Display the Catalog as HTML for a rich display in IPython."""
        return Utils.render_html('catalog.html', catalog=self)
