"""This module introduces a class that represents a list of assets
according to STAC specification."""

import collections.abc
from collections import UserDict

from examples._utils import Utils
from examples.asset import Asset


class Assets(UserDict):
    """A list of assets according to the STAC specification."""

    def __init__(self, data=None):
        """Initialize the Assets instance with dictionary data.

        Args:
            data (dict): A dictionary of assets.
        """
        if not isinstance(data, collections.abc.Mapping):
            raise ValueError('data parameter must be a mapping.')

        data = {k: Asset(v) for k, v in data.items()}

        super(Assets, self).__init__(data)

    def _repr_html_(self): # pragma: no cover
        """Display the Assets as HTML for a rich display in IPython."""
        return Utils.render_html('links.html', assets=self)
