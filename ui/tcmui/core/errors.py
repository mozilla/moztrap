# maps a message id to a tuple of (error message, fields), where fields is a
# list of field names this message is likely related to.
MESSAGES = {
    "duplicate.name": ("This name is already in use.", ["name"]),
    "changing.used.entity": (
        "%(name)s is in use elsewhere and cannot be modified.", []),
    "deleting.used.entity": (
        "%(name)s is in use elsewhere and cannot be deleted.", []),
    "invalid.user": (
        "You created this; someone else must approve or reject it.", []),
    "activating.incomplete.entity": {
        "TestSuite": ("Test suite is empty; add some test cases.", []),
        "TestRun": ("Activate or unlock parent test cycle first.", [])
         },
    "including.not.activated.entity": (
        "Can't include a not-active test case in a test run.", []),
    "including.multiple.testcase.versions": (
        "Selected test suites contain conflicting test case versions.",
        ["suites"]
        ),
    "products.dont.match": {
        "TestSuite": (
            "Selected test case is for the wrong product.", ["cases"]),
        "TestRun": (
            "Selected test suite is for the wrong product.", ["suites"]),
        },
    }


def error_message_and_fields(obj, err):
    """
    Given an exception and the name of an object that caused it, return a tuple
    of (error-message, fields), where fields is a list of field names this
    message is likely related to.

    """
    try:
        data = MESSAGES[err.response_error]
        if isinstance(data, dict):
            data = data[obj.__class__.__name__]
        message, fields = data
        return (message % {"name": unicode(obj)}, fields)
    except KeyError:
        return (
            'Unknown conflict "%s"; please correct and try again.'
            % err.response_error,
            [])


def error_message(obj, err):
    return error_message_and_fields(obj, err)[0]
