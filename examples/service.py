from examples._utils import Utils
from examples.catalog import Catalog


class Service:
    """This class implements a Python API client wrapper for STAC catalogs and STAC-API services.

    Note:
        For more information on STAC entities, please, refer to https://github.com/radiantearth/stac-spec.

        The STAC-API specification can be found at https://github.com/radiantearth/stac-api-spec.
    """

    def __init__(self, url, validate=False, access_token=None):
        """Create a STAC client attached to the given host address (an URL).

        Args:
            url (str): URL for the Root STAC Catalog.
            validate (bool): True if responses should ve validated against STAC
                JSON Schemas.
            access_token (str): Authentication for the STAC API.
        """
        self._url = url
        self._validate = validate
        self._access_token = f'?access_token={access_token}' if access_token else ''
        self._catalog = None

    def catalog(self):
        """Return the STAC catalog associated to the STAC service or URL."""
        if self._catalog:
            return self._catalog

        data = Utils.get(self._url)
        self._catalog = Catalog(data)
        return self._catalog

    def conformance(self):
        """???"""
        pass

    def collections(self, id=None):
        pass

    def items(self, collectionId=None, itemId=None):
        pass

    def search(self, post=False, **kwargs):
        pass
