# Case Conductor is a Test Case Management system.
# Copyright (C) 2011 uTest Inc.
# 
# This file is part of Case Conductor.
# 
# Case Conductor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Case Conductor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Case Conductor.  If not, see <http://www.gnu.org/licenses/>.
import posixpath

from django.core.urlresolvers import reverse



class Finder(object):
    template_base = ""
    columns = []


    def __init__(self, auth=None):
        self.auth = auth
        self.columns_by_name = dict((c.name, c) for c in self.columns)
        self.parent_columns = dict(
            zip([c.name for c in self.columns[1:]], self.columns[:-1])
            )
        self.child_columns = dict(
            zip([c.name for c in self.columns[:-1]], self.columns[1:])
            )
        self.columns_by_model = dict((c.model, c) for c in self.columns)


    def column_template(self, column_name):
        """
        Returns the template to use for rendering a list of objects in a given
        column.

        """
        col = self._get_column_by_name(column_name)
        return posixpath.join(self.template_base, col.template_name)


    def goto_url(self, obj):
        """
        Given an object, return its "Goto" url, or None.

        """
        try:
            col = self.columns_by_model[obj.__class__]
        except KeyError:
            return None

        if col.goto is not None:
            return reverse(col.goto) + "?%s=%s" % (col.attr, obj.id)

        return None


    def child_column_for_obj(self, obj):
        """
        Given an object, return the column name of its child column, or None if
        there is none.

        """
        try:
            col = self.columns_by_model[obj.__class__]
            return self.child_columns[col.name].name
        except KeyError:
            return None


    def child_query_url(self, obj):
        """
        Given an object, return the URL for an ajax query to fetch child
        objects.

        """
        child_col = self.child_column_for_obj(obj)
        if child_col is not None:
            return "?finder=1&col=%s&id=%s" % (child_col, obj.id)
        return None


    def objects(self, column_name, parent_id=None):
        """
        Given a column name, return the list of objects.

        If a parent_id is given and there is a parent column, filter the list
        by that parent id.

        """
        col = self._get_column_by_name(column_name)
        ret = col.objects(auth=self.auth)
        if parent_id is not None:
            try:
                parent = self.parent_columns[col.name]
            except KeyError:
                raise ValueError(
                    "Column %r has no parent; cannot use parent_id."
                    % column_name)
            else:
                return ret.filter(**{parent.attr: parent_id})
        return ret


    def _get_column_by_name(self, column_name):
        try:
            return self.columns_by_name[column_name]
        except KeyError:
            raise ValueError("Column %r does not exist." % column_name)




class Column(object):
    def __init__(self, name, template_name, list_model, attr,
                 goto=None, sort=("name", "asc"), **filters):
        self.name = name
        self.template_name = template_name
        self.list_model = list_model
        self.model = self.list_model.entryclass
        self.attr = attr
        self.filters = filters
        self.sort = sort
        self.goto = goto


    def objects(self, auth):
        return self.list_model.ours(auth=auth).filter(
            **self.filters).sort(*self.sort)
