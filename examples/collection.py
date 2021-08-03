"""This module introduces a class that models a STAC Collection."""

from typing import Union

from examples.assets import Assets
from examples.catalog import Catalog
from examples.extent import Extent
from examples.providers import Providers
from examples.relation import RelationType

from examples.links import Links
from examples._utils import Utils


class Collection(Catalog):
    """STAC Collection class."""

    def __init__(self, data=None):
        """Initialize the Collection instance with dictionary data.

        Args:
            data (dict): A dict with STAC Collection metadata.
        """
        super(Collection, self).__init__(data)

    @property
    def keywords(self):
        """List of keywords describing the Collection.

        Returns:
            list: A list of of keywords describing the Collection.
        """
        return self.get('keywords', [])

    @property
    def license(self) -> Union[str, Links]:
        """Collection's license.

        Returns:
            str/Links: A string based on a `SPDX License identifier <https://spdx.org/licenses/>`_ or
                          a list of license URL(s) for the Collection .
        """
        lic = self['license']

        if lic in ('various', 'proprietary'):
            return self._links(RelationType.LICENSE, mandatory=True)
        else:
            return lic

    @property
    def providers(self):
        """The list of data providers."""
        return Providers(self.get('providers', []))

    @property
    def extent(self):
        """The Spatial and temporal extents."""
        return Extent(self.get('extent'))

    @property
    def summaries(self):
        """A map of property summaries."""
        return self.get('summaries')

    @property
    def assets(self):
        """The list of assets."""
        return Assets(self.get('assets', {}))

    @property
    def derived_from(self):
        """STAC Collection that was used as input data in the creation of this Collection"""
        pass

    def _repr_html_(self): # pragma: no cover
        """Display the Collection as HTML for a rich display in IPython."""
        return Utils.render_html('collection.html', collection=self)