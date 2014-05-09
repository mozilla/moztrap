"""
Tests for transforming a filterset class (with `filters` list as a class
attribute) into a blob of JSON.
"""

import json

from django.template import Template, Context

from moztrap import model
from moztrap.view.lists import filters
from tests import case


class FiltersetToJSONTests(case.DBTestCase):

    def test_empty_filterset_to_json(self):
        t = Template("{% load filterset %}{% filterset_to_json filterset %}")
        filterset = []
        output = t.render(Context({"filterset": filterset}))
        struct = json.loads(output)
        self.assertEqual(struct, {"fields": [], "options": {}})

    def test_empty_filterset_with_options_to_json(self):
        t = Template("""
            {% load filterset %}
            {% filterset_to_json filterset with foo="bar" one=1 advanced %}
        """)
        filterset = []
        output = t.render(Context({"filterset": filterset}))
        struct = json.loads(output)
        self.assertEqual(struct["fields"], [])
        self.assertEqual(struct["options"], {
            "foo": "bar",
            "one": 1,
            "advanced": None
        })

    def test_basic_filterset_to_json(self):
        t = Template("{% load filterset %}{% filterset_to_json filterset %}")
        class SampleFilterset(filters.FilterSet):
            filters = [
                filters.KeywordFilter("name"),
                filters.ModelFilter(
                    "creator",
                    lookup="created_by",
                    queryset=model.User.objects.all().order_by("username")),
                filters.ModelFilter(
                    "product",
                    queryset=model.Product.objects.all().order_by("name")
                    ),
            ]
        product1 = model.Product.objects.create(
            name="Bee", description="A nice description",
        )
        product2 = model.Product.objects.create(
            name="Aaa", description="Another nice description",
        )
        assert not model.User.objects.all().count()
        assert model.Product.objects.all().count()

        f = SampleFilterset().bind({})
        output = t.render(Context({"filterset": f}))
        struct = json.loads(output)

        field1, field2, field3 = struct["fields"]
        # field1
        self.assertEqual(field1["key"], "name")
        self.assertEqual(field1["name"], "name")
        self.assertEqual(field1["cls"], "keyword")
        self.assertEqual(field1["is_default_and"], True)
        self.assertEqual(field1["switchable"], True)
        self.assertEqual(field1["options"], [])

        # field2
        self.assertEqual(field2["key"], "creator")
        self.assertEqual(field2["name"], "creator")
        self.assertEqual(field2["cls"], "")
        self.assertEqual(field2["is_default_and"], False)
        self.assertEqual(field2["switchable"], False)
        self.assertEqual(field2["options"], [])

        # field3
        self.assertEqual(field3["key"], "product")
        self.assertEqual(field3["name"], "product")
        self.assertEqual(field3["cls"], "")
        self.assertEqual(field3["is_default_and"], False)
        self.assertEqual(field3["switchable"], False)
        self.assertEqual(field3["options"], [
            ["Aaa", False, product2.pk],
            ["Bee", False, product1.pk]
        ])
