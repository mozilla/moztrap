"""
Tests for EnvironmentResource api.

"""

from tests import case



class CategoryResourceTest(case.api.ApiTestCase):

    @property
    def factory(self):
        """The model factory for this object."""
        return self.F.CategoryFactory


    @property
    def resource_name(self):
        return "category"


    def test_category_list(self):
        """Get a list of existing categories"""
        category = self.factory.create(name="OS")

        res = self.get_list()

        act_meta = res.json["meta"]
        exp_meta = {
            "limit": 20,
            "next": None,
            "offset": 0,
            "previous": None,
            "total_count": 1,
            }

        self.assertEquals(act_meta, exp_meta)

        act_objects = res.json["objects"]
        exp_objects = []

        exp_objects.append({
            u'id': unicode(category.id),
            u'name': u'OS',
            u'resource_uri': unicode(self.get_detail_url(
                "category",
                category.id,
                )),
            })

        self.maxDiff = None
        self.assertEqual(exp_objects, act_objects)
