# maps a message id to a tuple of (error message, fields), where fields is a
# list of field names this message is likely related to.
MESSAGES = {
    "duplicate.name": ("This name is already in use.", ["name"]),
    "changing.used.entity": (
        "The %(name)s is in use and cannot be modified.", []),
    "deleting.used.entity": (
        "The %(name)s is in use and cannot be deleted.", []),
    "invalid.user": (
        "You created this; someone else must approve or reject it.", []),
    }


def error_message_and_fields(err, obj_name="object"):
    """
    Given an exception and the name of an object that caused it, return a tuple
    of (error-message, fields), where fields is a list of field names this
    message is likely related to.

    """
    if err.response_error in MESSAGES:
        data = MESSAGES[err.response_error]
        return (data[0] % {"name": obj_name}, data[1])
    else:
        return (
            'Unknown conflict "%s"; please correct and try again.'
            % err.response_error,
            [])


def error_message(err, obj_name):
    return error_message_and_fields(err, obj_name)[0]
