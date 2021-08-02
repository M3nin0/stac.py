"""This module introduces a base class for STAC Catalogs and Collections."""

from collections import UserDict
from typing import Generator

from examples.link import Link
from examples.links import Links
from examples.relation import RelationType


class BaseContainer(UserDict):
    """A base class for STAC Catalogs and Collections.

    Note:
        For information on the possible relationship types, please, see:

        - https://github.com/radiantearth/stac-spec/blob/v1.0.0/catalog-spec/catalog-spec.md#relation-types

        - https://github.com/radiantearth/stac-spec/blob/v1.0.0/collection-spec/collection-spec.md#relation-types

    Todo:
        - Check if a Collection or Catalog can have more than one root or parent link.
    """

    def __init__(self, data=None):
        """Initialize the instance with dictionary data.

        Args:
            data (dict): Dict with catalog metadata.
        """
        super(BaseContainer, self).__init__(data or {})

    @property
    def stac_version(self):
        """The STAC version the Catalog/Collection implements.

        Returns:
            str: The STAC version the Catalog/Collection implements.
        """
        return self['stac_version']

    @property
    def stac_extensions(self):
        """A list of extension identifiers the Catalog/Collection implements.

        Returns:
            list: A list of extension identifiers the Catalog/Collection implements.
                Can return an empty list.
        """
        return self.get('stac_extensions', [])

    @property
    def id(self):
        """Identifier for the Catalog/Collection.

        Returns:
            str:  Identifier for the Catalog/Collection.
        """
        return self['id']

    @property
    def title(self):
        """A short descriptive one-line title for the Catalog/Collection.

        Returns:
            str/None: A short descriptive one-line title for the Catalog/Collection.
        """
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
    def links(self):
        """Return a list of references to catalogs, collections, items or other kind of resource."""
        return self._links()

    @property
    def url(self):
        """URL to the self entity.

        Returns:
            str/None: An absolute URL.

        Raises:
            RuntimeError: If multiple self links are found.
        """
        link = self._links(RelationType.SELF, single=True)
        return link[0]['href'] if link else None

    @property
    def parent(self):
        """The parent Catalog or Collection.

        Returns:
            Catalog/Collection: The parent Catalog or Collection.
        """
        links = self._links(RelationType.PARENT, single=True)

        return links[0].resource() if links else None

    @property
    def root(self):
        """The root Catalog or Collection.

        Returns:
            Catalog/Collection: The root Catalog or Collection.
        """
        links = self._links(RelationType.CHILD, single=True)

        return links[0].resource() if links else None

    @property
    def children(self):
        """Return an iterator over the children entities.

        Yields:
            Catalog/Collection: A child entity such as Collection or even a Catalog.
        """
        links = self._links(RelationType.CHILD)

        for link in links:
            yield link.resource()

    @property
    def items(self):
        """Return an iterator over the related Item entities.

        Yields:
            Item: An Item related to the Catalog or Collection.
        """
        links = self._links(RelationType.ITEM)

        for link in links:
            yield link.resource()

    def _links(self, rel_type=None, single=False, mandatory=False):
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
