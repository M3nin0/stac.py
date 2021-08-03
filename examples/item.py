"""This module introduces a class that models a SpatioTemporal Asset Catalog (STAC) Item."""

from collections import UserDict

from examples._utils import Utils
from examples.links import Links
from examples.relation import RelationType


class Item(UserDict):
    """A class that models a SpatioTemporal Asset Catalog (STAC) Item.

    According to STAC specification, an Item is a GeoJSON Feature
    augmented with foreign members relevant to a STAC object.
    """

    def __init__(self, data=None):
        """Initialize the instance with dictionary data.

        Args:
            data (dict): Dict with catalog metadata.
        """
        super(Item, self).__init__(data or {})

    @property
    def stac_version(self):
        """The STAC version the Item implements."""
        return self['stac_version']

    @property
    def stac_extensions(self):
        """A list of extensions the Item implements."""
        return self.get('stac_extensions', [])

    @property
    def id(self):
        """Identifier of the item in the Catalog/Collection.

        This identifier must be unique in the Catalog/Collection.

        Returns:
            str:  Identifier for the Item.
        """
        return self['id']

    @property
    def geometry(self):
        pass

    @property
    def bbox(self):
        pass

    @property
    def properties(self):
        pass

    @property
    def links(self):
        """Return a list of references to catalogs, collections,
        items or other kind of resources."""
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
    def collection(self):
        """The Collection to which the Item belongs.

        Returns:
            Collection: The Collection to which the Item belongs.
        """
        links = self._links(RelationType.COLLECTION,
                            single=True,
                            mandatory='collection' in self)

        return links[0].resource() if links else None

    @property
    def assets(self):
        pass

    @property
    def collection_id(self):
        """The id of the STAC Collection the Item references to."""
        return self.get('collection', None)

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
        selected_links = self['links']

        if rel_type:
            selected_links = [link for link in selected_links if link['rel'] == rel_type.value]

        if mandatory and not selected_links:
            raise RuntimeError(f'No link found with relationship: {rel_type}.')

        if single and (len(selected_links) > 1):
            raise RuntimeError(f'Found more than one link with relationship: {rel_type}.')

        return Links(selected_links)

    def _repr_html_(self): # pragma: no cover
        """Display the Item as HTML for a rich display in IPython."""
        return Utils.render_html('item.html', item=self)
