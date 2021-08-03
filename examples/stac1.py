from examples.stac import stac


if __name__ == '__main__':

    #
    # Padrão de acesso a um serviço STAC a partir de uma URL base
    #
    urls = [
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        'https://earth-search.aws.element84.com/v0/',
        'https://brazildatacube.dpi.inpe.br/stac/',
        'https://sentinel-stac.s3.amazonaws.com/catalog.json',
        'https://landsatlook.usgs.gov/sat-api/stac'
    ]

    for url in urls:
        service = stac.service(url)

        catalog = service.catalog()

        print('Catalog\n=======\n')
        print('\tLinks:')

        for link in catalog.links():
            print('\t\t', link)

        print('\tChildren:')

        for collection in catalog.children:
            print('\t\t', type(collection), collection)


        # print(catalog.links)


    # print(cat._repr_html_())

    # print(cat.links._repr_html_())
    #
    # links = cat.links
    #
    # for l in links:
    #     print(l)
    #     print(type(l))
    #
    # print(links[1:])
    # print(type(links[1:]))
    #
    # from pprint import pprint
    #
    # print("URL")
    # pprint(cat.url)
    #
    # print("Parent")
    # pprint(cat.parent)
    #
    # print("root")
    # pprint(cat.root)
    #
    # print("Children")
    # for child in cat.children:
    #     pprint(child)
    #
    # print("Items")
    # for item in cat.items:
    #     pprint(item)
    #
    # service = stac.service('url')

# TODO:
# - 01: possibilitar a validação de entidades contra o JSONSchema
#
#