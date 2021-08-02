"""This module introduces a class that represents a list of references to other
documents according to STAC specification."""

import collections.abc
from collections import UserList

from examples._utils import Utils
from examples.link import Link


class Links(UserList):
    """A list of references to other documents according to the STAC specification."""

    def __init__(self, data=None):
        """Create a new list of references to other documents.

        Args:
            data (sequence): Sequence of dictionaries representing Link objects.
        """
        if not isinstance(data, collections.abc.Sequence):
            raise ValueError('The "data" argument must be a valid sequence type.')

        if not all(isinstance(link, (dict, Link)) for link in data):
            raise ValueError('Sequence elements in "data" argument must be a dict or Link.')

        data = [Link(link) if isinstance(link, dict) else link for link in data]

        super(Links, self).__init__(data)

    def _repr_html_(self): # pragma: no cover
        """Display the Links as HTML for a rich display in IPython."""
        return Utils.render_html('links.html', links=self)