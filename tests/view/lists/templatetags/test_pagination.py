# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-12 Mozilla
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
"""
Tests for pagination template tags and filters.

"""
from mock import Mock

from django import template
from django.test import TestCase

from .... import factories as F



class PaginateTest(TestCase):
    """Tests for paginate template tag."""
    def test_paginate(self):
        """Places Pager object in context with size/num from request."""
        from cc.model.tags.models import Tag

        tpl = template.Template(
            "{% load pagination %}{% paginate queryset as pager %}"
            "{% for obj in pager.objects %}{{ obj }} {% endfor %}")

        request = Mock()
        request.GET = {"pagesize": 3, "pagenumber": 2}

        for i in range(1, 7):
            F.TagFactory.create(name=str(i))
        qs = Tag.objects.all()

        output = tpl.render(
            template.Context({"request": request, "queryset": qs}))

        self.assertEqual(output, "4 5 6 ")


class FilterTest(TestCase):
    """Tests for template filters."""
    def test_pagenumber_url(self):
        """``pagenumber_url`` filter updates pagenumber in URL."""
        from cc.view.lists.templatetags.pagination import pagenumber_url
        request = Mock()
        request.get_full_path.return_value = (
            "http://localhost/?pagenumber=2&pagesize=10")
        self.assertEqual(
            pagenumber_url(request, 1),
            "http://localhost/?pagenumber=1&pagesize=10")


    def test_pagesize_url(self):
        """``pagesize_url`` updates pagesize in URL (and jumps to page 1)."""
        from cc.view.lists.templatetags.pagination import pagesize_url
        request = Mock()
        request.get_full_path.return_value = (
            "http://localhost/?pagenumber=2&pagesize=10")
        self.assertEqual(
            pagesize_url(request, 20),
            "http://localhost/?pagenumber=1&pagesize=20")


    def test_pagenumber(self):
        """``pagenumber`` gets the pagenumber from the request."""
        from cc.view.lists.templatetags.pagination import pagenumber
        request = Mock()
        request.GET = {"pagenumber": 2, "pagesize": 10}
        self.assertEqual(pagenumber(request), 2)


    def test_pagesize(self):
        """``pagenumber`` gets the pagenumber from the request."""
        from cc.view.lists.templatetags.pagination import pagesize
        request = Mock()
        request.GET = {"pagenumber": 2, "pagesize": 10}
        self.assertEqual(pagesize(request), 10)
