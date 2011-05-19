from ..builder import ListBuilder
from ..responses import make_locator, make_boolean



testcases = ListBuilder(
    "testcase",
    "testcases",
    "Testcase",
    {
        "companyId": 1,
        "companyLocator": make_locator(id=1, url="companies/1"),
        "maxAttachmentSizeInMbytes": 0,
        "maxNumberOfAttachments": 0,
        "name": "Default Test Case",
        "productId": 1,
        "productLocator": make_locator(id=1, url="products/1"),
        "testCycleId": make_boolean(None),
        "testCycleLocator": make_boolean(None),
        })



testcaseversions = ListBuilder(
    "testcaseversion",
    "testcaseversions",
    "Testcaseversion",
    {
        "approvalStatusId": 1,
        "approvedBy": make_boolean(None),
        "approvedByLocator": make_boolean(None),
        "companyId": 1,
        "companyLocator": make_locator(id=1, url="companies/1"),
        "description": "",
        "latestVersion": True,
        "majorVersion": 0,
        "minorVersion": 1,
        "maxAttachmentSizeInMbytes": 0,
        "maxNumberOfAttachments": 0,
        "name": "Default Test Case Version",
        "productId": 1,
        "productLocator": make_locator(id=1, url="products/1"),
        "testCaseId": 1,
        "testCaseStatusId": 1,
        "testCycleId": make_boolean(None),
        "testCycleLocator": make_boolean(None),
        })
