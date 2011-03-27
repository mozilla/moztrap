# maps a message id to a tuple of (error message, fields), where fields is a
# list of field names this message is likely related to.
MESSAGES = {
    "duplicate.name": ("This name is already in use.", ["name"]),
    "changing.used.entity": (
        "This object is in use and cannot be modified.", []),
    }


def error_message_and_fields(self, err):
    """
    Given an exception, return a tuple of (error-message, fields), where fields
    is a list of field names this message is likely related to.

    """
    if err.response_error in MESSAGES:
        return MESSAGES[err.response_error]
    else:
        return (
            'Unknown conflict "%s"; please correct and try again.'
            % err.response_error,
            [])


