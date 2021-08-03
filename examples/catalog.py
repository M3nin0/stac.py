"""A class that models a STAC Catalog."""

from examples._utils import Utils
from examples.relation import RelationType
from examples.traversable import Traversable


class Catalog(Traversable):
    """A class that models a STAC Catalog."""

    def __init__(self, data=None):
        """Initialize the Catalog instance with dictionary data.

        Args:
            data (dict): A Python dictionary with catalog metadata.
        """
        super(Catalog, self).__init__(data)

    @property
    def title(self):
        """A short descriptive one-line title for the Catalog."""
        return self.get('title', None)

    @property
    def description(self):
        """Detailed multi-line description to fully explain the Catalog/Collection.

        Returns:
            str: The Catalog/Collection description.

        Note:
            CommonMark 0.29 syntax MAY be used for rich text representation.
        """
        return self['description']

    @property
    def children(self):
        """Return an iterator over the children entities.

        Yields:
            Catalog/Collection: A child entity such as Collection or even a Catalog.
        """
        links = self.links(RelationType.CHILD)

        for link in links:
            yield link.resource()

    @property
    def items(self):
        """Return an iterator over the related Item entities.

        Yields:
            Item: An Item related to the Catalog or Collection.
        """
        links = self.links(RelationType.ITEM)

        for link in links:
            yield link.resource()

    def _repr_html_(self):  # pragma: no cover
        """Display the Catalog as HTML for a rich display in IPython."""
        return Utils.render_html('catalog.html', catalog=self)
