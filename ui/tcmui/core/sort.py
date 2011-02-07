from .util import add_to_querystring



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
    return add_to_querystring(url, sortfield=field, sortdirection=direction)



def toggle(direction):
    return DIRECTIONS.difference([direction]).pop()
