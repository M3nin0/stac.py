"""A base class for the SpatioTemporal Asset Catalog (STAC) data model.

The Item, Catalog, and Collection classes share the principle of
being connected by link relations. The Traversable class can be used
as a base class for that purpose.
"""

from collections import UserDict
from examples.links import Links
from examples.relation import RelationType


class Traversable(UserDict):
    """A base class for the SpatioTemporal Asset Catalog (STAC) data model.

    The STAC specifications define related JSON object types connected by
    link relations to support a HATEOAS-style traversable interface.
    This class knows how to handle the property ``links`` to take
    advantage of the relationship between the various STAC elements (Catalog,
    Collection, and Item)

    Todo:
        - Can a Collection or Catalog have more than one root or parent link?
    """

    def __init__(self, data=None):
        """Initialize the instance with dictionary data.

        Args:
            data (dict): Dict with catalog metadata.
        """
        super(Traversable, self).__init__(data or {})

    @property
    def stac_version(self):
        """The implemented STAC version."""
        return self['stac_version']

    @property
    def stac_extensions(self):
        """A list of extension identifiers supported by the entity."""
        return self.get('stac_extensions', [])

    @property
    def id(self):
        """Entity Identifier."""
        return self['id']

    @property
    def url(self):
        """URL to the self entity.

        Returns:
            str/None: An absolute URL.

        Raises:
            RuntimeError: If multiple self links are found.
        """
        link = self.links(RelationType.SELF, single=True)
        return link[0]['href'] if link else None

    @property
    def root(self):
        """The root Catalog or Collection."""
        links = self.links(RelationType.CHILD, single=True)
        return links[0].resource() if links else None

    @property
    def parent(self):
        """The parent Catalog or Collection."""
        links = self.links(RelationType.PARENT, single=True)
        return links[0].resource() if links else None

    def links(self, rel_type=None, single=False, mandatory=False):
        """Return a list of references to catalogs, collections, items or other kind of resources.

        Args:
            rel_type (RelationType): Filter links satisfying the relation type.

            single (bool): If True, assure that only a single resource link with the given
                           relationship exists, otherwise, if many resources link with the
                           given relation is found, an exception is raisen. Defaults to False.

            mandatory (bool): If True, assure that at least one link is found. Defaults to False.

        Returns:
            Links: A list of links.

        Raises:
            RuntimeError: If mandatory and no links found,
                or if a single link is required and multiple are found.
        """
        selected_links = self.get('links', [])

        if rel_type:
            selected_links = [link for link in selected_links if link['rel'] == rel_type.value]

        if mandatory and not selected_links:
            raise RuntimeError(f'No link found with relationship: {rel_type}.')

        if single and (len(selected_links) > 1):
            raise RuntimeError(f'Found more than one link with relationship: {rel_type}.')

        return Links(selected_links)
