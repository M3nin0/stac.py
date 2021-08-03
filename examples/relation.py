from enum import Enum


class RelationType(Enum):
    """
    For information on the possible relationship types, please, see:

        - https://github.com/radiantearth/stac-spec/blob/v1.0.0/catalog-spec/catalog-spec.md#relation-types

        - https://github.com/radiantearth/stac-spec/blob/v1.0.0/collection-spec/collection-spec.md#relation-types
    """

    ALTERNATE = 'alternate'
    CANONICAL = 'canonical'
    CHILD = 'child'
    COLLECTION = 'collection'
    CONFORMANCE = 'conformance'
    DATA = 'data'
    DERIVED_FROM = 'derived_from'
    DOCS = 'docs'
    ITEM = 'item'
    LICENSE = 'license'
    NEXT = 'next'
    PARENT = 'parent'
    PREV = 'prev'
    PREVIEW = 'preview'
    ROOT = 'root'
    SEARCH = 'search'
    SELF = 'self'
    VIA = 'via'


    def __str__(self):
        return self.value
