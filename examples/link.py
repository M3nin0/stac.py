"""This module introduces a class that represent a reference to other document
according to the STAC specification."""

from collections import UserDict
from examples._utils import Utils
from examples.relation import RelationType
from examples.resource_factory import ResourceFactory


class Link(UserDict):
    """A reference to other document according to the STAC specification."""

    def __init__(self, data):
        """Initialize the instance with dictionary data.

        Args:
            data (dict): Dict with Link metadata.
        """
        super(Link, self).__init__(data or {})

    @property
    def href(self):
        """URL associated to the Link."""
        return self['href']

    @property
    def rel(self):
        """Relationship with the linked document."""
        return RelationType[self['rel']]

    @property
    def type(self):
        """Media type of the referenced entity."""
        return self['type']

    @property
    def title(self):
        """A human readable title to be used in rendered displays of the link."""
        return self['title']

    def resource(self):
        """Resolve the link and retrieve the associated resource.

        This methos works as a factory for Catalogs, Collections,
        Item (Feature), and Item collection (Feature Collection)

        Returns:
            Catalog, Collection, Item, ItemCollection, dict: Any STAC object or a dictionary if
                the resource type is not known.
        """
        # TODO: pass mime-type
        # TODO: create an extesible resource_factory
        # TODO: allow JSONSchema validation
        data = Utils.get(self['href'])
        return ResourceFactory.make(data)

    def _repr_html_(self):  # pragma: no cover
        """Display the Link as HTML for a rich display in IPython."""
        return Utils.render_html('link.html', link=self)
