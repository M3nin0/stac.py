"""This module introduces a base class for linked resources."""

from collections import UserList

from examples.links import Links
from examples.relation import RelationType


class LinkedResources(UserList):
    """Models entities that can be linked according to STAC specification.

    See:
        For information on the possible relationship types, please, see:

        - https://github.com/radiantearth/stac-spec/blob/v1.0.0/catalog-spec/catalog-spec.md#relation-types

        - https://github.com/radiantearth/stac-spec/blob/master/collection-spec/collection-spec.md#relation-types
    """

    def __init__(self, links):
        """Initialize the object instance from a dict with links."""
        super(LinkedResources, self).__init__(links or {})

    @property
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
        selected_links = [link for link in self if link['rel'] == rel_type] if rel_type else self

        if mandatory and not selected_links:
            raise RuntimeError(f'No link found with relationship: {rel_type}.')

        if single and (len(selected_links) > 1):
            raise RuntimeError(f'Found more than one link with relationship: {rel_type}.')

        return Links(selected_links)

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
    def parent(self):
        """One ore more links to the parent entity.

        Returns:
            Links: The links to the parent entities.
        """
        return self.links(RelationType.PARENT)

    @property
    def root(self):
        """One or more links to the root entity.

        Returns:
            Links: The links to the root entities.
        """
        return self.links(RelationType.ROOT)
