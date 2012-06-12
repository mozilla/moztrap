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
                u"resource_uri": unicode(self.get_detail_uri("productversion",pv.id)),
                u"version": u"3.2",
                }],
            u"id": unicode(p.id),
            u"resource_uri": unicode(self.get_detail_uri("product",p.id)),
            })

        self.maxDiff = None
        self.assertEqual(exp_objects, act_objects)



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
            u"resource_uri": unicode(self.get_detail_uri("productversion",pv.id)),
            u"version": u"3.2",
            })

        self.maxDiff = None
        self.assertEqual(exp_objects, act_objects)



class ProductVersionEnvironmentsResourceTest(case.api.ApiTestCase):

    @property
    def factory(self):
        """The model factory for this object."""
        return self.F.ProductVersionFactory


    @property
    def resource_name(self):
        return "productversionenvironments"


    def test_productversionenvironments_list(self):
        """Get a list of existing productversions"""
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
            u'environments': [{
                u'elements': [{
                    u'category': {
                        u'id': unicode(category.id),
                        u'name': u'OS',
                        u'resource_uri': unicode(self.get_detail_uri(
                            "category",
                            category.id,
                            )),
                        },
                    u'id': unicode(element.id),
                    u'name': u'OS X',
                    u'resource_uri': unicode(self.get_detail_uri(
                        "element",
                        element.id,
                        )),
                    }],
                u'id': unicode(envs[0].id),
                u'resource_uri': unicode(self.get_detail_uri(
                    "environment",
                    envs[0].id,
                    )),
                }],
            u"id": unicode(pv.id),
            u"resource_uri": unicode(self.get_detail_uri(
                "productversionenvironments",
                pv.id,
                )),
            u"version": u"3.2",
            })

        self.maxDiff = None
        self.assertEqual(exp_objects, act_objects)
