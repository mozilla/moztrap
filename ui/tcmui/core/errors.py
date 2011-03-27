# maps a message id to a tuple of (error message, fields), where fields is a
# list of field names this message is likely related to.
MESSAGES = {
    "duplicate.name": ("This name is already in use.", ["name"]),
    "changing.used.entity": (
        "The %(name)s is in use and cannot be modified.", []),
    "deleting.used.entity": (
        "The %(name)s is in use and cannot be deleted.", [])
    }


def error_message_and_fields(err, obj_name):
    """
    Given an exception and the name of an object that caused it, return a tuple
    of (error-message, fields), where fields is a list of field names this
    message is likely related to.

    """
    if err.response_error in MESSAGES:
        return MESSAGES[err.response_error] % {"name": obj_name}
    else:
        return (
            'Unknown conflict "%s"; please correct and try again.'
            % err.response_error,
            [])


def error_message(err, obj_name):
    return error_message_and_fields(err, obj_name)[0]
