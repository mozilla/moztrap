"""
Tests for ProductResource api.

"""

from tests import case



class ProductResourceTest(case.api.ApiTestCase):

    @property
    def factory(self):
        """The model factory for this object."""
        return self.F.ProductFactory


    @property
    def resource_name(self):
        return "product"


    def test_product_list(self):
        """Get a list of existing products and their versions"""
        p = self.factory.create(name="ProductA", description="descrumptious")

        pv = self.F.ProductVersionFactory.create(
            product=p,
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
            u"name": unicode(p.name),
            u"description": unicode(p.description),
            u"productversions": [{
                u"codename": unicode(pv.codename),
                u"id": unicode(pv.id),
                u"product": unicode(self.get_detail_url("product",pv.product.id)),
                u"resource_uri": unicode(self.get_detail_url("productversion",pv.id)),
                u"version": u"3.2",
                }],
            u"id": unicode(p.id),
            u"resource_uri": unicode(self.get_detail_url("product",p.id)),
            })

        self.maxDiff = None
        self.assertEqual(exp_objects, act_objects)
