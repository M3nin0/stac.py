import collections.abc

import jinja2
import requests

from pkg_resources import resource_filename as _resource_filename


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
        return self['rel']

    @property
    def type(self):
        """Media type of the referenced entity."""
        return self['type']

    @property
    def title(self):
        """A human readable title to be used in rendered displays of the link."""
        return self['title']

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


class Catalog(dict):
    """The STAC Catalog."""

    def __init__(self, data=None, validate=False):
        """Initialize instance with dictionary data.

        Args:
            data (dict): Dict with catalog metadata.

            validate (bool): If `True`, validate the Catalog document with JSON Schema. Default is `False`.
        """
        self._validate = validate
        super(Catalog, self).__init__(data or {})

        # self._schema = json.loads(resource_string(__name__, f'jsonschemas/{self.stac_version}/catalog.json'))

        # if self._validate:
        #     Utils.validate(self)

    @property
    def stac_version(self):
        """The STAC version the Catalog implements.

        Returns:
            str: The STAC version the Catalog implements.
        """
        return self['stac_version']

    @property
    def stac_extensions(self):
        """A list of extension identifiers the Catalog implements.

        Returns:
            list: A list of extension identifiers the Catalog implements.
        """
        return self.get('stac_extensions', [])

    @property
    def id(self):
        """Identifier for the Catalog.

        Returns:
            str:  Identifier for the Catalog.
        """
        return self['id']

    @property
    def title(self):
        """A short descriptive one-line title for the Catalog.

        Returns:
            str: A short descriptive one-line title for the Catalog.
        """
        return self['title'] if 'title' in self else None

    @property
    def description(self):
        """Detailed multi-line description to fully explain the Catalog.

        Returns:
            str: A short descriptive one-line title for the Catalog.

        Note:
            CommonMark 0.29 syntax MAY be used for rich text representation.
        """
        return self['description']

    @property
    def links(self):
        """A list of references to catalogs, collections or items.

        Returns:
            Links: A list of references to catalogs, collections or items.

        Raises:
            RuntimeError: If the catalog self link can not be found.

        Note:
            A catalog can include a link to itself (relation self or root).
        """
        return Links(self.get('links'))

    @property
    def url(self):
        """Absolute URL of the catalog (self relation of STAC Spec).

        Returns:
            str: Absolute Catalog URL

        See:
            STAC Relationship types: https://github.com/radiantearth/stac-spec/blob/v1.0.0/catalog-spec/catalog-spec.md#relation-types
        """
        self_link = [link for link in self['links'] if link['rel'] == 'self']

        if len(self_link) != 1:
            raise RuntimeError('Could not determine the catalog self link.')

        return self_link[0]['href']

    @property
    def parent(self):
        """root entity of the catalog (STAC Catalog or Collection).

        Returns:
            Catalog or Collection: The root entity of this catalog.

        See:
            STAC Relationship types: https://github.com/radiantearth/stac-spec/blob/v1.0.0/catalog-spec/catalog-spec.md#relation-types
        """
        resource = self._resource('parent')

        if resource and not isinstance(resource, Catalog) and not isinstance(resource, Collection):
            raise RuntimeError('The returned resource is not a Catalog or Collection.')

        return resource

    @property
    def root(self):
        """root entity of the catalog (STAC Catalog or Collection).

        Returns:
            Catalog or Collection: The root entity of this catalog.

        See:
            STAC Relationship types: https://github.com/radiantearth/stac-spec/blob/v1.0.0/catalog-spec/catalog-spec.md#relation-types
        """
        resource = self._resource('root')

        if resource and not isinstance(resource, Catalog) and not isinstance(resource, Collection):
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
        for child in self._resources('child'):
            assert(isinstance(child, Catalog) or isinstance(child, Collection))
            yield child

    @property
    def items(self):
        """Generator to STAC Items entities.

        Yields:
            Item: STAC Item entity.

        See:
            STAC Relationship types: https://github.com/radiantearth/stac-spec/blob/v1.0.0/catalog-spec/catalog-spec.md#relation-types
        """
        for item in self._resources('item'):
            assert(isinstance(item, Item))
            yield item

    def _resource(self, rel_type):
        """Retrieve STAC Catalog resource based on their relationship type.

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
            raise RuntimeError(f'Found more than one link of type: {rel_type}.')

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
        links = [link for link in self['links'] if link['rel'] == rel_type]

        for link in links:
            doc = Utils._get(link['href'])

            if 'type' in doc:
                resource = resource_factory(doc['type'], doc)
            else:
                # figure out the returned object from the followed link
                resource = (Collection(doc)
                            if {'extent', 'providers', 'properties'} & set(doc.keys())
                            else Catalog(doc))

            yield resource

    # @property
    # def schema(self):
    #     """:return: the Catalog jsonschema."""
    #     return self._schema


class Collection(dict):

    def __init__(self, data=None, validate=False):
        """Initialize instance with dictionary data.

        :param data: Dict with catalog metadata.
        :param validate: true if the Catalog should be validate using its jsonschema. Default is False.
        """
        self._validate = validate
        super(Collection, self).__init__(data or {})


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


def resource_factory(resource_type, data):
    # ToDo: Review this factory.
    if resource_type == 'Catalog':
        return Catalog(data)
    elif resource_type == 'Collection':
        return Collection(data)
    elif resource_type == 'Feature':
        return Item(data)
    elif resource_type == 'FeatureCollection':
        return ItemCollection(data)


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
    # url = 'https://earth-search.aws.element84.com/v0/'
    url = 'https://brazildatacube.dpi.inpe.br/stac/'

    cat = catalog(url)
    print(cat.links._repr_html_())

    links = cat.links

    for l in links:
        print(l)
        print(type(l))

    print(links[1:])
    print(type(links[1:]))

    from pprint import pprint

    print("URL")
    pprint(cat.url)

    print("Parent")
    pprint(cat.parent)

    print("root")
    pprint(cat.root)

    print("Children")
    for child in cat.children:
        pprint(child)

    print("Items")
    for item in cat.items:
        pprint(item)

    # service = stac.service('url')
