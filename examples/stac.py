from examples._utils import Utils

from examples.catalog import Catalog
from examples.collection import Collection
from examples.item import Item
from examples.service import Service
from examples.resource_factory import ResourceFactory


ResourceFactory.register('Catalog', Catalog)
ResourceFactory.register('Collection', Collection)
ResourceFactory.register('Item', Item)


class stac:

    @staticmethod
    def service(url):
        return Service(url)

    @staticmethod
    def catalog(url):
        data = Utils.get(url)
        return Catalog(data)

    @staticmethod
    def collection(url):
        data = Utils.get(url)
        return Collection(data)

    @staticmethod
    def item(url):
        data = Utils.get(url)
        return Item(data)
