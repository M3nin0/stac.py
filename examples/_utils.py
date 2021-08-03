import jinja2
import requests

from pkg_resources import resource_filename as _resource_filename

_template_loader = jinja2.FileSystemLoader(searchpath=_resource_filename(__name__, 'templates/'))
_template_env = jinja2.Environment(loader=_template_loader)


class Utils:
    """HTTP utility class."""

    @staticmethod
    def get(url, params=None):
        """Query the STAC service using HTTP GET verb and return the result as a JSON document.

        Args:
            url(str): The URL to query. It must be a valid STAC endpoint.
            params (:obj:`dict`, optional): Optional; Dictionary, list of tuples or bytes to send
                in the query string for the underlying `Requests`.

        Returns:
            dict

        Raises:
            ValueError: If the response body does not contain a valid json.
        """
        response = requests.get(url, params=params)
        response.raise_for_status()

        content_type = response.headers.get('content-type')

        if content_type not in ('application/json', 'application/geo+json'):
            raise ValueError('HTTP response is not JSON: Content-Type: {}'.format(content_type))

        return response.json()

    @staticmethod
    def stream(url, **kwargs):
        """Create a HTTP GET stream to a remote file based on url.

        Args:
            url (str): File URL

            **kwargs (dict): Extra parameters to the `requests.request` function.

        Returns:
            requests.Response: Opened file stream

        Raises:
            HTTPError: If an HTTP error occurs.
        """
        response = requests.request('get', url, stream=True, **kwargs)
        response.raise_for_status()

        return response

    @staticmethod
    def render_html(template_name, **kwargs):  # pragma: no cover
        """Render Jinja2 HTML template."""
        template = _template_env.get_template(template_name)
        return template.render(**kwargs)
