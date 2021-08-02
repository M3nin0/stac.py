class ResourceFactory:

    _factories = {}

    @classmethod
    def register(cls, name, factory):
        cls._factories[name] = factory

    @classmethod
    def exists(cls, name):
        return name in cls._factories

    @classmethod
    def make(cls, data):
        if ('type' in data) and cls.exists(data['type']):
            return cls._factories[data['type']](data)
        else:
            # try to figure out the data object
            if {'extent', 'providers', 'properties'} & set(data.keys()):
                return cls._factories['Collection'](data)
            elif {'stac_version', 'description', 'links'}.issubset(set(data.keys())):
                return cls._factories['Catalog'](data)

        return data
