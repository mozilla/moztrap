from .util import update_querystring



DIRECTIONS = set(["asc", "desc"])
DEFAULT = "asc"



def from_request(request):
    """
    Given a request, return tuple (sortfield, sortdirection).

    """
    sortfield = request.GET.get("sortfield", None)
    sortdirection = request.GET.get("sortdirection", "asc")
    return sortfield, sortdirection



def url(url, field, direction):
    return update_querystring(url, sortfield=field, sortdirection=direction)



def toggle(direction):
    return DIRECTIONS.difference([direction]).pop()
