"""
Finder; a multi-column hierarchical object navigator.

"""
from functools import wraps
import posixpath

from django.db import models
from django.shortcuts import render

from .filters import filter_url



def finder(finder_cls):
    """
    View decorator that takes care of everything needed to render a finder on
    the rendered page.

    """
    def decorator(view_func):
        finder = finder_cls()

        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.is_ajax() and request.GET.get("finder"):
                col_name = request.GET["col"]
                return render(
                    request,
                    finder.column_template(col_name),
                    {
                        "colname": col_name,
                        "finder": {
                            "finder": finder,
                            col_name: finder.objects(
                                col_name, request.GET["id"])
                            },
                        }
                    )
            response = view_func(request, *args, **kwargs)
            try:
                ctx = response.context_data
            except AttributeError:
                return response
            top_col = finder.columns[0]
            finder_ctx = ctx.setdefault("finder", {})
            finder_ctx.update(
                {
                    "finder": finder,
                    top_col.name: finder.objects(top_col.name)
                    }
                )
            return response

        return _wrapped_view

    return decorator



class Finder(object):
    """A multi-column hierarchical object navigator."""
    # The template directory under which templates for this finder live.
    template_base = ""
    # A list of Column instances for this finder.
    columns = []


    def __init__(self):
        """Initialize a Finder."""
        self.columns_by_name = dict((c.name, c) for c in self.columns)
        self.parent_columns = dict(
            zip([c.name for c in self.columns[1:]], self.columns[:-1])
            )
        self.child_columns = dict(
            zip([c.name for c in self.columns[:-1]], self.columns[1:])
            )
        self.columns_by_model = dict((c.model, c) for c in self.columns)


    def column_template(self, column_name):
        """Returns template name for rendering objects in given column."""
        col = self._get_column_by_name(column_name)
        return posixpath.join(self.template_base, col.template_name)


    def goto_url(self, obj):
        """Given an object, return its "Goto" url, or None."""
        try:
            col = self.columns_by_model[obj.__class__]
        except KeyError:
            return None

        return col.goto_url(obj)


    def child_column_for_obj(self, obj):
        """Given an object, return name of its child column, or None."""
        try:
            col = self.columns_by_model[obj.__class__]
            return self.child_columns[col.name].name
        except KeyError:
            return None


    def child_query_url(self, obj):
        """Given an object, return URL for ajax query to fetch child objects."""
        child_col = self.child_column_for_obj(obj)
        if child_col is not None:
            return "?finder=1&col=%s&id=%s" % (child_col, obj.id)
        return None


    def objects(self, column_name, parent=None):
        """
        Given a column name, return the list of objects.

        If a parent is given and there is a parent column, filter the list by
        that parent.

        """
        col = self._get_column_by_name(column_name)
        ret = col.objects()
        if parent is not None:
            try:
                parent_col = self.parent_columns[col.name]
            except KeyError:
                raise ValueError(
                    "Column {0} has no parent.".format(column_name))

            opts = col.model._meta

            attr = None
            for field in [
                    f for f in opts.fields if isinstance(f, models.ForeignKey)
                    ] + opts.many_to_many:
                if field.rel.to is parent_col.model:
                    attr = field.name
                    break

            if attr is None:
                try:
                    attr = [
                        r.get_accessor_name()
                        for r in opts.get_all_related_many_to_many_objects()
                        if r.model is parent_col.model
                        ][0]
                except IndexError:
                    raise ValueError(
                        "Cannot find relationship from {0} to {1}".format(
                            col.model, parent_col.model))

            ret = ret.filter(**{attr: parent})
        return ret


    def _get_column_by_name(self, column_name):
        try:
            return self.columns_by_name[column_name]
        except KeyError:
            raise ValueError("Column %r does not exist." % column_name)




class Column(object):
    def __init__(self, name, template_name, queryset, goto=None):
        self.name = name
        self.template_name = template_name
        self.model = queryset.model
        self.queryset = queryset
        self.goto = goto


    def objects(self):
        """Return objects to display in this column."""
        return self.queryset.all()


    def goto_url(self, obj):
        """Given an object, return its "Goto" url, or None."""
        if self.goto:
            return filter_url(self.goto, obj)

        return None
