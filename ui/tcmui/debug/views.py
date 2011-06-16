from itertools import islice

from django.shortcuts import render

from .apilog import get_records, formatter



def apilog(request):
    records = (
        (i, r) for i, r in enumerate(get_records())
        if not r.args.get("url", "").startswith("/debug/")
        )

    if request.GET.get("nocached"):
        records = ((i, r) for i, r in records if not r.args.get("cache_key"))

    template_name = "debug/apilog/viewer.html"

    if request.is_ajax():
        template_name = "debug/apilog/_records.html"
        start = int(request.GET.get("start", 0))
        if start:
            records = islice(records, start, None)

    records = ((i, formatter.format(r)) for i, r in records)

    return render(
        request,
        template_name,
        {
            "records": islice(records, 20)
            }
        )
