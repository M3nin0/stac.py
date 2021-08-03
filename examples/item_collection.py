class ItemCollection(dict):

    def __init__(self, data=None, validate=False):
        """Initialize instance with dictionary data.

        :param data: Dict with catalog metadata.
        :param validate: true if the Catalog should be validate using its jsonschema. Default is False.
        """
        self._validate = validate
        super(ItemCollection, self).__init__(data or {})