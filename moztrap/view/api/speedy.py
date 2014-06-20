# Some endpoints in the API need to be really really fast such that we
# are ready to forego the flexibility of the Tastypie API and just write
# our own view functions straight up

import json
from collections import defaultdict

from django.http import HttpResponse, HttpResponseBadRequest

from moztrap.model.library.models import CaseVersion


def caseselection(request):
    """This is a speedy version of existing Tastypie API functionality
    with the major difference in that it's much much dumber but also
    much much faster.

    This view function is about 10 faster on an average workload compared
    to the Tastpie version but it also has much fewer filtering options
    and it returns less data.
    """
    if not request.GET.get("productversion__product"):
        return HttpResponseBadRequest("productversion__product is required")
    product_id = request.GET["productversion__product"]
    not_in_case = request.GET.get("case__suites__ne", None)
    in_case = request.GET.get("case__suites", None)
    order_by = request.GET.get("order_by", "case__id")
    limit = int(request.GET.get("limit", 0))
    offset = int(request.GET.get("offset", 0))

    caseversions = (
        CaseVersion.objects
        .filter(latest=True)
        .filter(productversion__product_id=product_id)
        .select_related("case", "created_by")
        .order_by(order_by)
    )
    if not_in_case:
        caseversions = caseversions.exclude(case__suites=not_in_case)
    elif in_case:
        caseversions = caseversions.filter(case__suites=in_case)

    count = caseversions.count()
    if limit:
        caseversions = caseversions[offset:limit + offset]
    meta = {
        "count": count,
        "limit": limit,
        "offset": offset
    }
    # Because CaseVersion.tags is a ManyToMany field the only way to
    # effectively include those in the CaseVersion query is to use a
    # prefetch_related().
    # However, what that does is that it makes a list of tag ids and
    # the rather naively re-maps that back into the queryset.
    # Instead we're going to go through the mapping table
    # (CaseVersion.tags.through) and make a dict that maps each
    # caseversion ID to a list of tag IDs.
    tags = (
        CaseVersion.tags.through.objects
        .filter(tag__deleted_on__isnull=True)
        .filter(caseversion__latest=True)
        .filter(caseversion__productversion__product_id=product_id)
        .select_related("tags")
    )
    tags_map = defaultdict(list)
    for t in tags.values("caseversion_id", "tag__name", "tag__description"):
        tags_map[t["caseversion_id"]].append({
            "name": t["tag__name"],
            "description": t["tag__description"],
        })

    objects = []
    for each in caseversions:
        item = {
            "id": unicode(each.id),
            "case_id": unicode(each.case_id),
            "name": each.name,
            "priority": unicode(each.case.priority),
            "created_by": {},
            "tags": [],
        }
        if each.created_by:
            item["created_by"] = {
                "id": unicode(each.created_by.id),
                "username": unicode(each.created_by.username)
            }
        item["tags"] = tags_map[each.id]
        objects.append(item)

    context = {"objects": objects, "meta": meta}
    return HttpResponse(
        json.dumps(context, indent=2),
        content_type="application/json"
    )
