"""
Tests for ProductVersionEnvironmentsResource api.

"""

from tests import case



class ProductVersionEnvironmentsResourceTest(case.api.ApiTestCase):

    @property
    def factory(self):
        """The model factory for this object."""
        return self.F.ProductVersionFactory


    @property
    def resource_name(self):
        return "productversionenvironments"


    def test_productversionenvironments_list(self):
        """Get a list of existing productversions with full environment data"""
        envs = self.F.EnvironmentFactory.create_full_set(
                {"OS": ["OS X"]})
        element = envs[0].elements.get()
        category = element.category

        pv = self.F.ProductVersionFactory.create(
            version="3.2",
            codename="enigma",
            environments=envs,
            )

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
            u"codename": unicode(pv.codename),
            u'environments': [{
                u'elements': [{
                    u'category': {
                        u'id': unicode(category.id),
                        u'name': u'OS',
                        u'resource_uri': unicode(self.get_detail_url(
                            "category",
                            category.id,
                            )),
                        },
                    u'id': unicode(element.id),
                    u'name': u'OS X',
                    u'resource_uri': unicode(self.get_detail_url(
                        "element",
                        element.id,
                        )),
                    }],
                u'id': unicode(envs[0].id),
                u'resource_uri': unicode(self.get_detail_url(
                    "environment",
                    envs[0].id,
                    )),
                }],
            u"id": unicode(pv.id),
            u"resource_uri": unicode(self.get_detail_url(
                "productversionenvironments",
                pv.id,
                )),
            u"version": u"3.2",
            })

        self.maxDiff = None
        self.assertEqual(exp_objects, act_objects)
