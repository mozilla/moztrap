from ..builder import ListBuilder


companies = ListBuilder(
    "company",
    "companies",
    "Company",
    {
        "name": "Default company name",
        "address": "Default company address",
        "city": "Default company city",
        "country": 239,
        "phone": "123-456-7890",
        "url": "www.example.com",
        "zip": "12345",
        })



cvis = ListBuilder(
    "CategoryValueInfo",
    None,
    "CategoryValueInfo",
    {
        "categoryName": 1,
        "categoryValue": 1,
        },
    add_identity=False,
    add_timeline=False)
