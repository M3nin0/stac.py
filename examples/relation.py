from enum import Enum


class RelationType(Enum):

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
