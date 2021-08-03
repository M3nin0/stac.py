"""This module introduces a class that represent an asset
according to the STAC specification."""

import collections.abc
import os
from collections import UserDict

from tqdm import tqdm

from examples._utils import Utils


class Asset(UserDict):
    """A class for representing assets."""

    def __init__(self, data):
        """Initialize the instance with dictionary data.

        Args:
            data (dict): Dict with Link metadata.
        """
        if not isinstance(data, collections.abc.Mapping):
            raise ValueError('data parameter must be a mapping.')

        super(Asset, self).__init__(data or {})

    @property
    def href(self):
        """URL associated to the Asset."""
        return self['href']

    @property
    def title(self):
        """A human readable title to be used in rendered displays of the Asset."""
        return self.get('title')

    @property
    def description(self):
        """Detailed multi-line description to fully explain the Asset.

        Returns:
            str: The Asset description.

        Note:
            CommonMark 0.29 syntax MAY be used for rich text representation.
        """
        return self.get('description')

    @property
    def type(self):
        """Media type of the Asset object."""
        return self.get('type')

    @property
    def roles(self):
        """The semantic roles of the asset."""
        return self.get('roles', [])

    def _repr_html_(self):  # pragma: no cover
        """Display the Asset as HTML for a rich display in IPython."""
        return Utils.render_html('link.html', asset=self)

    def download(self, output_dir=None):  # pragma: no cover
        """Download the asset to an indicated folder.

        Args:
            output_dir (str): Directory path to download the asset, if left None, the asset will be
                              downloaded to the current working directory.

        Returns:
            str: path to downloaded file.
        """
        filename = os.path.basename(self['href'])

        if output_dir:
            filename = os.path.join(output_dir, filename)
            os.makedirs(os.path.dirname(filename), exist_ok=True)

        response = Utils.stream(self['href'])

        with open(filename, 'wb') as target_file:
            with tqdm.wrapattr(target_file, 'write', miniters=1,
                               total=int(response.headers.get('content-length', 0)),
                               desc=filename) as fout:
                for chunk in response.iter_content(chunk_size=4096):
                    fout.write(chunk)

        return filename
