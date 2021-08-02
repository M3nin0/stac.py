"""This module introduces a class that represent an asset
according to the STAC specification."""

import collections.abc
from collections import UserDict

from examples._utils import Utils
from examples.relation import RelationType
from examples.resource_factory import ResourceFactory


class Asset(UserDict):
    """A class for representing assets."""

    def __init__(self, data):
        """Initialize the instance with dictionary data.

        Args:
            data (dict): Dict with Link metadata.
        """
        if not isinstance(data, collections.abc.Mapping):
            raise ValueError('data parameter must be a mapping.')

        super(Asset, self).__init__(data or {})

    @property
    def href(self):
        """URL associated to the Asset."""
        return self['href']

    @property
    def title(self):
        """A human readable title to be used in rendered displays of the Asset."""
        return self.get('title')

    @property
    def description(self):
        """Detailed multi-line description to fully explain the Asset.

        Returns:
            str: The Asset description.

        Note:
            CommonMark 0.29 syntax MAY be used for rich text representation.
        """
        return self.get('description')

    @property
    def type(self):
        """Media type of the Asset object."""
        return self.get('type')

    @property
    def roles(self):
        """The semantic roles of the asset."""
        return self.get('roles', [])

    def _repr_html_(self):  # pragma: no cover
        """Display the Asset as HTML for a rich display in IPython."""
        return Utils.render_html('link.html', asset=self)
