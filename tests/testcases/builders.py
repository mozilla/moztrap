from ..builder import ListBuilder
from ..responses import make_locator, make_boolean



testsuites = ListBuilder(
    "testsuite",
    "testsuites",
    "Testsuite",
    {
        "companyId": 1,
        "companyLocator": make_locator(id=1, url="companies/1"),
        "description": "the default test suite",
        "name": "Default Test Suite",
        "productId": 1,
        "productLocator": make_locator(id=1, url="products/1"),
        "testSuiteStatusId": 1,
        "useLatestVersions": False,
        }
    )



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


testcasesteps = ListBuilder(
    "testcasestep",
    "testcasesteps",
    "Testcasestep",
    {
        "name": "Default Test Case Step",
        "testCaseVersionId": 1,
        "testCaseVersionLocator":
            make_locator(id=1, url="testcases/versions/1"),
        "stepNumber": 1,
        "instruction": "default instruction",
        "expectedResult": "default expected result",
        "estimatedTimeInMin": 3,
        })



testsuiteincludedtestcases = ListBuilder(
    "includedtestcase",
    "includedtestcases",
    "Includedtestcase",
    {
        "blocking": False,
        "runOrder": 0,
        "testCaseId": 1,
        "testCaseLocator": make_locator(id=1, url="testcases/1"),
        "testCaseVersionId": 1,
        "testCaseVersionLocator":
            make_locator(id=1, url="testcases/versions/1"),
        "testSuiteId": 1,
        "testSuiteLocator": make_locator(id=1, url="testsuites/1"),
        # @@@ these values are not used
        "testCycleId": make_boolean(None),
        "testCycleLocator": make_boolean(None),
        "testRunId": make_boolean(None),
        "testRunLocator": make_boolean(None),
        # @@@ below values probably indicate a platform bug
        "companyId": make_boolean(None),
        "companyLocator": make_boolean(None),
        "productId": make_boolean(None),
        "productLocator": make_boolean(None),
        })
