"""This module introduces a class that models a data provider
according to STAC specification."""

from collections import UserDict

from examples._utils import Utils


class Provider(UserDict):
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
        """Display the Provider as HTML for a rich display in IPython."""
        return Utils.render_html('provider.html', provider=self)