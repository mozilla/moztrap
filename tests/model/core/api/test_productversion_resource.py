"""
Tests for ProductResource api.

"""

from tests import case



class ProductVersionResourceTest(case.api.ApiTestCase):

    @property
    def factory(self):
        """The model factory for this object."""
        return self.F.ProductVersionFactory


    @property
    def resource_name(self):
        return "productversion"


    def test_productversion_list(self):
        """Get a list of existing productversions"""

        pv = self.F.ProductVersionFactory.create(
            version="3.2",
            codename="enigma"
        )

        res = self.get_list()

        act_meta = res.json["meta"]
        exp_meta = {
            "limit" : 20,
            "next" : None,
            "offset" : 0,
            "previous" : None,
            "total_count" : 1,
            }

        self.assertEquals(act_meta, exp_meta)

        act_objects = res.json["objects"]
        exp_objects = []

        exp_objects.append({
            u"codename": unicode(pv.codename),
            u"id": unicode(pv.id),
            u"resource_uri": unicode(self.get_detail_url("productversion",pv.id)),
            u"version": u"3.2",
            })

        self.maxDiff = None
        self.assertEqual(exp_objects, act_objects)
