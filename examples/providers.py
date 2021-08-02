"""This module introduces a class that models a list of data provider
according to STAC specification."""

import collections.abc
from collections import UserList

from examples._utils import Utils
from examples.provider import Provider


class Providers(UserList):
    """A list of data providers."""

    def __init__(self, data):
        """Create a new list of data providers.

        Args:
            data (sequence): Sequence of dictionaries representing Provider objects.
        """
        if not isinstance(data, collections.abc.Sequence):
            raise ValueError('data parameter must be a sequence.')

        if not all(isinstance(p, (dict, Provider)) for p in data):
            raise ValueError('Sequence elements in data parameter must be a dict or a Provider.')

        data = [Provider(p) if isinstance(p, dict) else p for p in data]

        super(Providers, self).__init__(data)

    def _repr_html_(self):  # pragma: no cover
        """Display the Providers as HTML for a rich display in IPython."""
        return Utils.render_html('providers.html', providers=self)

