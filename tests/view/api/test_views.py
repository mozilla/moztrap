"""
Tests for home speedy API views.

"""
import json

from django.core.urlresolvers import reverse

from tests import case


class SpeedyCaseVersionsViewTest(case.view.ViewTestCase):
    """Tests for speedy caseversions API view."""

    @property
    def url(self):
        return reverse("caseselection")

    def test_that_productversion__product_is_required(self):
        res = self.get(status=400)
        self.assertEqual(res.content, "productversion__product is required")

    def test_no_results(self):
        pv = self.F.ProductVersionFactory.create()
        res = self.get(
            params={"productversion__product": pv.product.id},
            status=200
        )
        self.assertEqual(
            json.loads(res.content),
            {
                "objects": [],
                "meta": {
                    "count": 0,
                    "limit": 0,
                    "offset": 0
                }
            }
        )

    def test_one_result(self):
        pv = self.F.ProductVersionFactory.create()
        tc = self.F.CaseFactory.create(product=pv.product)
        cv = self.F.CaseVersionFactory.create(
            case=tc, productversion=pv, status="active"
        )
        res = self.get(
            params={"productversion__product": pv.product.id},
            status=200
        )
        expect = {
            "objects": [{
                "id": cv.id,
                "case_id": tc.id,
                "created_by": {},
                "name": cv.name,
                "priority": unicode(None),
                "tags": []
            }],
            "meta": {
                "count": 1,
                "limit": 0,
                "offset": 0
            }
        }
        self.assertEqual(
            json.loads(res.content),
            expect
        )

    def test_one_fuller_result(self):
        pv = self.F.ProductVersionFactory.create()
        tc = self.F.CaseFactory.create(product=pv.product)
        u = self.F.UserFactory.create()
        cv = self.F.CaseVersionFactory.create(
            case=tc, productversion=pv, status="active", user=u
        )
        t = self.F.TagFactory.create()
        cv.tags.add(t)
        # add a tag too that is deleted
        t2 = self.F.TagFactory.create(name="Will Delete")
        t2.delete()
        assert self.refresh(t2).deleted_on
        cv.tags.add(t2)

        res = self.get(
            params={"productversion__product": pv.product.id},
            status=200
        )
        expect = {
            "objects": [{
                "id": cv.id,
                "case_id": tc.id,
                "created_by": {
                    "id": u.id,
                    "username": u.username
                },
                "name": cv.name,
                "priority": unicode(None),
                "tags": [{
                    "name": t.name,
                    "description": t.description
                }]
            }],
            "meta": {
                "count": 1,
                "limit": 0,
                "offset": 0
            }
        }
        self.assertEqual(
            json.loads(res.content),
            expect
        )

    def test_paginate_results(self):
        pv = self.F.ProductVersionFactory.create()

        for i in range(10):
            tc = self.F.CaseFactory.create(product=pv.product)
            self.F.CaseVersionFactory.create(
                case=tc, productversion=pv, status="active"
            )

        res = self.get(
            params={"productversion__product": pv.product.id},
            status=200
        )
        expect_meta = {
            "count": 10,
            "limit": 0,
            "offset": 0
        }
        self.assertEqual(
            json.loads(res.content)['meta'],
            expect_meta
        )
        self.assertEqual(
            len(json.loads(res.content)["objects"]),
            10
        )

        # this time set a limit
        res = self.get(
            params={
                "productversion__product": pv.product.id,
                "limit": 3
            },
            status=200
        )
        expect_meta = {
            "count": 10,
            "limit": 3,
            "offset": 0
        }
        self.assertEqual(
            json.loads(res.content)['meta'],
            expect_meta
        )
        self.assertEqual(
            len(json.loads(res.content)["objects"]),
            3
        )

    def test_filtered_by_suites(self):
        pv = self.F.ProductVersionFactory.create()
        tc1 = self.F.CaseFactory.create(product=pv.product)
        cv1 = self.F.CaseVersionFactory.create(
            case=tc1, productversion=pv, status="active", name="Foo"
        )
        tc2 = self.F.CaseFactory.create(product=pv.product)
        cv2 = self.F.CaseVersionFactory.create(
            case=tc2, productversion=pv, status="active", name="Bar"
        )
        assert cv1.name != cv2.name
        suite = self.F.SuiteFactory.create(product=pv.product, status="active")
        self.F.SuiteCaseFactory.create(suite=suite, case=tc1)

        suite2 = self.F.SuiteFactory.create(
            product=pv.product, status="active"
        )
        self.F.SuiteCaseFactory.create(suite=suite2, case=tc2)

        res = self.get(
            params={
                "productversion__product": pv.product.id,
                "case__suites": suite.id},
            status=200
        )
        expect_names = [cv1.name]
        self.assertEqual(
            [x["name"] for x in json.loads(res.content)["objects"]],
            expect_names
        )
        res = self.get(
            params={
                "productversion__product": pv.product.id,
                "case__suites__ne": suite.id},
            status=200
        )
        expect_names = [cv2.name]
        self.assertEqual(
            [x["name"] for x in json.loads(res.content)["objects"]],
            expect_names
        )

    def test_order_by_suites_order(self):
        pv = self.F.ProductVersionFactory.create()
        tc1 = self.F.CaseFactory.create(product=pv.product)
        cv1 = self.F.CaseVersionFactory.create(
            case=tc1, productversion=pv, status="active", name="Foo"
        )
        tc2 = self.F.CaseFactory.create(product=pv.product)
        cv2 = self.F.CaseVersionFactory.create(
            case=tc2, productversion=pv, status="active", name="Bar"
        )
        assert cv1.name != cv2.name
        suite = self.F.SuiteFactory.create(product=pv.product, status="active")
        suitecase = self.F.SuiteCaseFactory.create(
            suite=suite, case=tc1, order=3
        )

        suite2 = self.F.SuiteFactory.create(
            product=pv.product, status="active"
        )
        suitecase2 = self.F.SuiteCaseFactory.create(
            suite=suite2, case=tc2, order=2
        )

        res = self.get(
            params={
                "productversion__product": pv.product.id,
                "order_by": "case__suitecases__order"},
            status=200
        )
        # becase order=2 < order=1
        expect_names = [cv2.name, cv1.name]
        self.assertEqual(
            [x["name"] for x in json.loads(res.content)["objects"]],
            expect_names
        )
        suitecase.order = 0
        suitecase.save()

        res = self.get(
            params={
                "productversion__product": pv.product.id,
                "order_by": "case__suitecases__order"},
            status=200
        )
        # becase order=2 > order=0
        expect_names = [cv1.name, cv2.name]
        self.assertEqual(
            [x["name"] for x in json.loads(res.content)["objects"]],
            expect_names
        )
