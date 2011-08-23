from itertools import islice, dropwhile

from django.shortcuts import render

from .apilog import get_records, formatter



def apilog(request):
    records = get_records()

    template_name = "debug/apilog/viewer.html"

    if request.is_ajax():
        template_name = "debug/apilog/_records.html"
        last = int(request.GET.get("last", 0))
        if last:
            records = dropwhile(lambda (i, r): i >= last, records)

    records = ((i, formatter.format(r)) for i, r in records)

    return render(
        request,
        template_name,
        {
            "records": islice(records, 20)
            }
        )
