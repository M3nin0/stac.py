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

    def filter_by_id(self, id: str):
        """Filter the Catalog entities using ID.

        Args:
            id (str): Entity ID

        Returns:
            Catalog: When the entity is found it returns its object. Otherwise, None is returned.
        """
        for _, children, _ in self.walk():
            for child in children:
                if child.id == id:
                    return child

    def walk(self):
        """Return an iterator that recursively loops through a catalog and its subsequent elements
        (Other Catalog or Collection).

        The iteration occurs recursively, starting from the root catalog and running through all
        subsequent catalogs/collections. For each of the retrieved elements, children and items are retrieved,
        generating a 3-tuple (Self, Children, Items) in the return of the iterator.

        For example, for a STAC Catalog with the following structure:

        - Catalog 1
          - Collection 1
            - C1-Items
          - Collection 2
            - C2-Items
          - Items

        When using the `walk` method, you will have an iterator that in the first iteration generates:

           (Catalog 1, Collection Iterator, Items Iterator)

        So `Collection Iterator` contains the collections `Collection 1` and `Collection 2`. Similarly,
        `Items Iterator` holds the values of `Items`. This will be repeated recursively for each catalog/collection
        above from `Catalog 1` (In this example).
        """
        yield self, self.children, self.items

        for child in self.children:
            yield from child.walk()

    def _repr_html_(self):  # pragma: no cover
        """Display the Catalog as HTML for a rich display in IPython."""
        return Utils.render_html('catalog.html', catalog=self)
