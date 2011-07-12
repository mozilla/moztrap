from django.template import Library



register = Library()



@register.filter
def child_query_url(finder, obj):
    return finder.child_query_url(obj)


@register.filter
def sub_name(finder, obj):
    return finder.child_column_for_obj(obj)


@register.filter
def goto_url(finder, obj):
    return finder.goto_url(obj)
