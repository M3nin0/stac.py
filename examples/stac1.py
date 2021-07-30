import collections.abc

import jinja2
import requests

from enum import Enum
from pkg_resources import resource_filename as _resource_filename
from shapely.geometry import box as _box

_template_loader = jinja2.FileSystemLoader(searchpath=_resource_filename(__name__, 'templates/'))
_template_env = jinja2.Environment(loader=_template_loader)


class Utils:
    """HTTP utility class."""

    @staticmethod
    def _get(url, params=None):
        """Query the STAC service using HTTP GET verb and return the result as a JSON document.

        :param url: The URL to query must be a valid STAC endpoint.
        :type url: str
        :param params: (optional) Dictionary, list of tuples or bytes to send
            in the query string for the underlying `Requests`.
        :type params: dict

        :rtype: dict

        :raises ValueError: If the response body does not contain a valid json.
        """
        response = requests.get(url, params=params)

        response.raise_for_status()

        content_type = response.headers.get('content-type')

        if content_type not in ('application/json', 'application/geo+json'):
            raise ValueError('HTTP response is not JSON: Content-Type: {}'.format(content_type))

        return response.json()

    @staticmethod
    def render_html(template_name, **kwargs):  # pragma: no cover
        """Render Jinja2 HTML template."""
        template = _template_env.get_template(template_name)
        return template.render(**kwargs)


class RelationType(Enum):
    SELF = 'self'
    ROOT = 'root'
    PARENT = 'parent'
    CHILD = 'child'
    ITEM = 'item'
    LICENSE = 'license'
    DERIVED_FROM = 'derived_from'
    ALTERNATE = 'alternate'
    CANONICAL = 'canonical'
    VIA = 'via'
    PREV = 'prev'
    NEXT = 'next'
    PREVIEW = 'preview'

    def __str__(self):
        return self.value


class Link(dict):
    """A reference to other document according to the STAC specification."""

    def __init__(self, data):
        """Initialize instance with dictionary data.

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
        """Relationship with the linked document. """
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
        data = Utils._get(self['href'])

        if 'type' in data:
            # the type field should be present in:
            # - Item (Feature);
            # - ItemCollection (FeatureCollection);
            # - Catalog (for STAC 1.0.0-rc1 or above);
            # - Collection (for STAC 1.0.0-rc1 or above)
            if data['type'] == 'Catalog':
                return Catalog(data)
            elif data['type'] == 'Collection':
                return Collection(data)
            elif data['type'] == 'Feature':
                return Item(data)
            elif data['type'] == 'FeatureCollection':
                return ItemCollection(data)
        else:
            # try to figure out the returned object from the followed link
            if {'extent', 'providers', 'properties'} & set(data.keys()):
                return Collection(data)
            elif {'stac_version', 'description', 'links'}.issubset(set(data.keys())):
                return Catalog(data)

        #raise RuntimeError(f'Unknow relation type: {self["rel"]}.')
        return data

    def _repr_html_(self): # pragma: no cover
        """Display the Link as HTML.

        This integrates a rich display in IPython.
        """
        return Utils.render_html('link.html', link=self)


class Links(list):
    """A list of references to other documents according to the STAC specification."""

    def __init__(self, data=None, validate=False):
        """Create a new list of references to other documents.

        Args:
            data (sequence): Sequence of dictionaries representing Link objects.

            validate (bool): If `True`, validate the Link document with JSON Schema. Default is `False`.
        """
        if not isinstance(data, collections.abc.Sequence):
            raise ValueError('data parameter must be a sequence.')

        if not all(isinstance(l, (dict, Link)) for l in data):
            raise ValueError('Sequence elements in data parameter must be a dict or a Link.')

        data = [Link(l) if isinstance(l, dict) else l for l in data]

        super(Links, self).__init__(data)

    def _repr_html_(self): # pragma: no cover
        """Display the Links as HTML.

        This integrates a rich display in IPython.
        """
        return Utils.render_html('links.html', links=self)

    def __getitem__(self, y):
        """Get Link identified by the key or slice it.

        Returns:
            Link or Links: A specific Link item or a slice of the Links.

        Example:
            Get the first link of a catalog:
            .. doctest::
                :skipif: STAC_EXAMPLE_URL is None
                >>> from stac import *
                >>> service = stac.service(WTSS_EXAMPLE_URL)
                >>> catalog = service.catalog()
                >>> links = catalog.links
                >>> links[0]
                {...
        """
        v = super(Links, self).__getitem__(y)

        return v if isinstance(v, Link) else Links(v)


class Provider(dict):
    """A organization or person that captures or processes the content of a Collection."""

    def __init__(self, data):
        """Initialize instance with dictionary data.

        Args:
            data (dict): Dict with provider metadata.
        """
        super(Provider, self).__init__(data or {})

    @property
    def name(self):
        """The data provider name."""
        return self['name']

    @property
    def description(self):
        """Detailed multi-line description about the data provider.

        Returns:
            str: A description of the data provider.

        Note:
            CommonMark 0.29 syntax MAY be used for rich text representation.
        """
        return self.get('description')

    @property
    def roles(self):
        """Provider roles."""
        return self.get('roles')

    @property
    def url(self):
        """A url for more detail about the data provider."""
        return self.get('url')

    def _repr_html_(self): # pragma: no cover
        """Display the Provider as HTML.

        This integrates a rich display in IPython.
        """
        return Utils.render_html('provider.html', provider=self)


class Providers(list):
    """A list of data providers."""

    def __init__(self, data=None, validate=False):
        """Create a new list of data providers.

        Args:
            data (sequence): Sequence of dictionaries representing Provider objects.

            validate (bool): If `True`, validate the providers document with JSON Schema. Default is `False`.
        """
        if not isinstance(data, collections.abc.Sequence):
            raise ValueError('data parameter must be a sequence.')

        if not all(isinstance(l, (dict, Provider)) for l in data):
            raise ValueError('Sequence elements in data parameter must be a dict or a Provider.')

        data = [Provider(p) if isinstance(p, dict) else p for p in data]

        super(Providers, self).__init__(data)

    def _repr_html_(self): # pragma: no cover
        """Display the Links as HTML.

        This integrates a rich display in IPython.
        """
        return Utils.render_html('providers.html', providers=self)

    def __getitem__(self, y):
        """Get Provider identified by the key or slice it.

        Returns:
            Provider or Providers: A specific Provider item or a slice of the Providers list.
        """
        v = super(Providers, self).__getitem__(y)

        return v if isinstance(v, Provider) else Providers(v)


class Extent():
    """The Extent object."""

    def __init__(self, data):
        """Initialize instance with dictionary data.

        Args:
            data (dict): Dict with spatial and temporal metadata.
        """
        self._spatial = data['spatial']['bbox']

        interval = data['temporal']['interval']
        self._temporal = [i for i in interval]

    @property
    def spatial(self):
        """The spatial extent.

        Tip:

            You can create polygons from the spatial extent by
            using Shapely:

            .. code:: python

                >>> from shapely.geometry import box
                >>> [box(*b) for b in extent.spatial]
        """
        return self._spatial

    @property
    def temporal(self):
        """The temporal extent."""
        return self._temporal

    def _repr_html_(self): # pragma: no cover
        """Display the Links as HTML.

        This integrates a rich display in IPython.
        """
        return Utils.render_html('extent.html', extent=self)


class BaseContainer(dict):
    """A base class for STAC Catalogs and Collections."""

    def __init__(self, data=None, validate=False):
        """Initialize instance with dictionary data.

        Args:
            data (dict): Dict with catalog metadata.

            validate (bool): If `True`, validate the catalog/collection document with JSON Schema.
                             Default is `False`.
        """
        self._validate = validate
        super(BaseContainer, self).__init__(data or {})

    @property
    def stac_version(self):
        """The STAC version the catalog/collection implements.

        Returns:
            str: The STAC version the catalog/collection implements.
        """
        return self['stac_version']

    @property
    def stac_extensions(self):
        """A list of extension identifiers the catalog/collection implements.

        Returns:
            list: A list of extension identifiers the catalog/collection implements.
        """
        return self.get('stac_extensions', [])

    @property
    def id(self):
        """Identifier for the catalog/collection.

        Returns:
            str:  Identifier for the catalog/collection.
        """
        return self['id']

    @property
    def title(self):
        """A short descriptive one-line title for the catalog/collection.

        Returns:
            str: A short descriptive one-line title for the catalog/collection.
        """
        return self.get('title', None)

    @property
    def description(self):
        """Detailed multi-line description to fully explain the catalog/collection.

        Returns:
            str: The catalog/collection description.

        Note:
            CommonMark 0.29 syntax MAY be used for rich text representation.
        """
        return self['description']

    @property
    def links(self, rel_type=None):
        """A list of references to catalogs, collections or items.

        Args:
            rel_type (RelationType): Relation type.

        Returns:
            Links: A list of references to catalogs, collections, items,
                   license informtaion, or data producr derivation.

        Note:
            A catalog/collection can include a link to itself (relation self).
        """
        if rel_type:
            selected_links = [link for link in self['links'] if link['rel'] == rel_type.value]
            return Links(selected_links)
        else:
            return Links(self.get('links', []))

    @property
    def url(self):
        """URL of the catalog/collection (self relation of STAC Spec).

        Returns:
            str or None: Absolute catalog/collection URL

        Raises:
            RuntimeError: If no self link is found or if multiple links
                          with self relationship are found.
        See:
            STAC Relationship types:

            - https://github.com/radiantearth/stac-spec/blob/v1.0.0/catalog-spec/catalog-spec.md#relation-types

            - https://github.com/radiantearth/stac-spec/blob/master/collection-spec/collection-spec.md#relation-types
        """
        self_link = self.links(RelationType.SELF)

        print(self.__class__.__name__)

        if len(self_link) == 1:
            return self_link[0]['href']
        elif not self_link:
            return None

        raise RuntimeError('Multiple self links found.')

    @property
    def parent(self):
        """The parent entity of the catalog/collection.

        Returns:
            Catalog or Collection: The parent entity of this catalog/collection.

        Raises:
            RuntimeError: If the parent object is not a Catalog or Collection.

        See:
            STAC Relationship types:

            - https://github.com/radiantearth/stac-spec/blob/v1.0.0/catalog-spec/catalog-spec.md#relation-types

            - https://github.com/radiantearth/stac-spec/blob/master/collection-spec/collection-spec.md#relation-types
        """
        resource = self._resource(RelationType.PARENT)

        if not isinstance(resource, (Catalog, Collection)):
            raise RuntimeError('The returned resource is not a Catalog or Collection.')

        return resource

    @property
    def root(self):
        """The root entity of the catalog/collection (STAC Catalog or Collection).

        Returns:
            Catalog or Collection: The root entity of this catalog.

        See:
            STAC Relationship types: https://github.com/radiantearth/stac-spec/blob/v1.0.0/catalog-spec/catalog-spec.md#relation-types
        """
        resource = self._resource(RelationType.ROOT)

        if not isinstance(resource, (Catalog, Collection)):
            raise RuntimeError('The returned resource is not a Catalog or Collection.')

        return resource

    @property
    def children(self):
        """Generator to children STAC entities (Catalog or Collection).

        Yields:
            Catalog or Collection: Child STAC entity.

        See:
            STAC Relationship types: https://github.com/radiantearth/stac-spec/blob/v1.0.0/catalog-spec/catalog-spec.md#relation-types
        """
        for child in self._resources(RelationType.CHILD):
            assert(isinstance(child, (Catalog, Collection)))
            yield child

    @property
    def items(self):
        """Generator to STAC Items entities.

        Yields:
            Item: STAC Item entity.

        See:
            STAC Relationship types: https://github.com/radiantearth/stac-spec/blob/v1.0.0/catalog-spec/catalog-spec.md#relation-types
        """
        for item in self._resources(RelationType.ITEM):
            assert(isinstance(item, Item))
            yield item

    def _resource(self, rel_type=RelationType.PARENT):
        """Retrieve STAC Catalog/Collection resource based on their relationship type.

        Args:
            rel_type (str): String with a STAC Spec valid relationship type (e.g. root, parent)

        Returns:
            None or object: Returns None if no object with the specified relationship is identified or
            an object of the type found in the relation (e.g. STAC Item, STAC Catalog).

        Raises:
            RuntimeError: When more than one link of type `rel_type` is identified.

        Note:
            The types returned by this method are assumed to be unique, and cannot return a list of values. For example,
             an object with `root` relation can be retrieved with this method, since in the catalog, only one object
             with this relation is expected.

        See:
            STAC Relationship types: https://github.com/radiantearth/stac-spec/blob/v1.0.0/catalog-spec/catalog-spec.md#relation-types
        """
        resources = list(self._resources(rel_type))

        if len(resources) == 0:
            return None

        if len(resources) > 1:
            raise RuntimeError(f'Found more than one link of type: {rel_type.data}.')

        return resources[0]

    def _resources(self, rel_type):
        """Retrieve STAC Catalog resources based on their relationship type.

        Args:
            rel_type (str): String with a STAC Spec valid relationship type (e.g. root, parent)

        Yields:
            None or object: Yields None if no object with the specified relationship is identified or
            an object of the type found in the relation (e.g. STAC Item, STAC Catalog).

        Note:
            Unlike the `_resource` method, this method allows multiple objects to be returned from the search.
            For example, retrieving objects with `children` relations which can return multiple objects,
            can be done with this method.

        See:
            Relationship types: https://github.com/radiantearth/stac-spec/blob/master/catalog-spec/catalog-spec.md#relation-types
        """
        selected_links = self.links(rel_type)

        for link in selected_links:
            yield link.resource()


class Catalog(BaseContainer):
    """The STAC Catalog."""

    def __init__(self, data=None, validate=False):
        """Initialize instance with dictionary data.

        Args:
            data (dict): Dict with catalog metadata.

            validate (bool): If `True`, validate the Catalog document with JSON Schema. Default is `False`.
        """
        super(BaseContainer, self).__init__(data, validate)

    def _repr_html_(self): # pragma: no cover
        """Display the Catalog as HTML.

        This integrates a rich display in IPython.
        """
        return Utils.render_html('catalog.html', catalog=self)


class Collection(BaseContainer):

    def __init__(self, data=None, validate=False):
        """Initialize instance with dictionary data.

        Args:
            data (dict): Dict with collection metadata.

            validate (bool): If `True`, validate the Collection document with JSON Schema. Default is `False`.
        """
        super(BaseContainer, self).__init__(data, validate)

    @property
    def keywords(self):
        """List of keywords describing the Collection.

        Returns:
            list: A list of of keywords describing the Collection.
        """
        return self.get('keywords', [])

    @property
    def license(self):
        """Collection's license.

        Returns:
            str: Collection's license.
        """
        return self['license']

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
        pass

    @property
    def assets(self):
        pass

    @property
    def derived_from(self):
        pass

    def _repr_html_(self): # pragma: no cover
        """Display the Collection as HTML.

        This integrates a rich display in IPython.
        """
        return Utils.render_html('collection.html', collection=self)

class Item(dict):

    def __init__(self, data=None, validate=False):
        """Initialize instance with dictionary data.

        :param data: Dict with catalog metadata.
        :param validate: true if the Catalog should be validate using its jsonschema. Default is False.
        """
        self._validate = validate
        super(Item, self).__init__(data or {})


class ItemCollection(dict):

    def __init__(self, data=None, validate=False):
        """Initialize instance with dictionary data.

        :param data: Dict with catalog metadata.
        :param validate: true if the Catalog should be validate using its jsonschema. Default is False.
        """
        self._validate = validate
        super(ItemCollection, self).__init__(data or {})


class Service:
    """This class implements a Python API client wrapper for STAC catalogs and services.

        See https://github.com/radiantearth/stac-spec for more information on STAC.

        :param url: URL for the Root STAC Catalog.
        :type url: str
        """

    def __init__(self, url, validate=False, access_token=None):
        """Create a STAC client attached to the given host address (an URL).

        :param url: URL for the Root STAC Catalog.
        :type url: str
        :param validate: True if responses should ve validated
        :type validate: bool
        :param access_token: Authentication for the STAC API
        :type access_token: str
        """
        self._url = url
        self._collections = dict()
        self._catalog = dict()
        self._validate = validate
        self._access_token = f'?access_token={access_token}' if access_token else ''


def catalog(url):
    doc = Utils._get(url)

    return Catalog(doc)


if __name__ == '__main__':
    url = 'https://earth-search.aws.element84.com/v0/'
    # url = 'https://brazildatacube.dpi.inpe.br/stac/'

    cat = catalog(url)

    print(cat._repr_html_())

    # print(cat.links._repr_html_())
    #
    # links = cat.links
    #
    # for l in links:
    #     print(l)
    #     print(type(l))
    #
    # print(links[1:])
    # print(type(links[1:]))
    #
    # from pprint import pprint
    #
    # print("URL")
    # pprint(cat.url)
    #
    # print("Parent")
    # pprint(cat.parent)
    #
    # print("root")
    # pprint(cat.root)
    #
    # print("Children")
    # for child in cat.children:
    #     pprint(child)
    #
    # print("Items")
    # for item in cat.items:
    #     pprint(item)
    #
    # service = stac.service('url')
