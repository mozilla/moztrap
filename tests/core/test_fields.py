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
import datetime

from mock import patch
from unittest2 import TestCase

from ..builder import ListBuilder
from ..responses import (
    response, make_identity, make_boolean, make_locator, make_timeline)
from ..utils import AuthTestCase, fill_cache, Url



class BaseFieldTests(TestCase):
    @property
    def field_cls(self):
        from ccui.core.fields import Field
        return Field


    @property
    def cls(self):
        class Bag(object):
            def __init__(self, **kw):
                for k, v in kw.items():
                    setattr(self, k, v)


            @classmethod
            def get(cls, *args, **kwargs):
                return cls(*args, **kwargs)

        return Bag


    def field_and_cls(self, *args, **kwargs):
        f = self.field_cls(*(self.prepend_args + args), **kwargs)
        cls = self.cls
        setattr(cls, "attname", f)
        f.install("attname", cls)
        return f, cls


    def field(self, *args, **kwargs):
        return self.field_and_cls(*args, **kwargs)[0]


    @property
    def prepend_args(self):
        return ()


    def test_default_names(self):
        f = self.field()

        self.assertEqual(f.api_name, "ns1.attname")
        self.assertEqual(f.api_filter_name, "attname")
        self.assertEqual(f.api_submit_name, "attname")


    def test_set_api_name(self):
        f = self.field(api_name="apiname")

        self.assertEqual(f.api_name, "ns1.apiname")
        self.assertEqual(f.api_filter_name, "apiname")
        self.assertEqual(f.api_submit_name, "apiname")


    def test_set_api_submit_name(self):
        f = self.field(api_submit_name="apisubmitname")

        self.assertEqual(f.api_name, "ns1.attname")
        self.assertEqual(f.api_filter_name, "attname")
        self.assertEqual(f.api_submit_name, "apisubmitname")


    def test_set_api_name_and_api_submit_name(self):
        f = self.field(api_name="apiname", api_submit_name="apisubmitname")

        self.assertEqual(f.api_name, "ns1.apiname")
        self.assertEqual(f.api_filter_name, "apiname")
        self.assertEqual(f.api_submit_name, "apisubmitname")


    def test_decode_nil(self):
        f = self.field()
        self.assertEqual(f.decode({"@xsi.nil": "true"}), None)


    def test_decode(self):
        f = self.field()
        self.assertEqual(f.decode("blah"), "blah")


    def test_encode(self):
        f = self.field()
        self.assertEqual(f.encode("blah"), "blah")


    def test_no_submit_data(self):
        f, cls = self.field_and_cls(api_submit_name=False)
        self.assertEqual(f.submit_data(cls()), {})


    def test_submit_none(self):
        f, cls = self.field_and_cls()
        self.assertEqual(f.submit_data(cls(attname=None)), {})


    def test_submit(self):
        f, cls = self.field_and_cls()
        self.assertEqual(
            f.submit_data(cls(attname="blah")), {"attname": "blah"})


    def test_non_filterable(self):
        class NonFilterableField(self.field_cls):
            api_filter_name = False

        f = NonFilterableField(*self.prepend_args)
        f.install("attname", self.cls)

        self.assertEqual(f.api_filter_name, False)



class FieldTest(BaseFieldTests):
    def test_encode_returns_dict(self):
        class ComplexField(self.field_cls):
            def encode(self, value):
                return {
                    "%s_part1" % self.api_submit_name: value[0],
                    "%s_part2" % self.api_submit_name: value[1],
                    }

        f = ComplexField()
        cls = self.cls
        f.install("attname", cls)

        self.assertEqual(
            f.submit_data(cls(attname=["one", "two"])),
            {"attname_part1": "one", "attname_part2": "two"})


    def test_submit_dict(self):
        f, cls = self.field_and_cls()
        self.assertEqual(
            f.submit_data(cls(attname={"a": 1})), {"attname": {"a": 1}})



class DateFieldTest(BaseFieldTests):
    @property
    def field_cls(self):
        from ccui.core.fields import Date
        return Date


    def test_decode(self):
        f = self.field_cls()

        self.assertEqual(
            f.decode("2011-04-28T00:46:00Z"), datetime.date(2011, 4, 28))


    def test_encode(self):
        f = self.field()

        self.assertEqual(
            f.encode(datetime.date(2011, 4, 28)), "2011/04/28")


    def test_encode_string(self):
        f = self.field()

        self.assertEqual(f.encode("2011/04/28"), "2011/04/28")


    def test_submit(self):
        f, cls = self.field_and_cls()

        self.assertEqual(
            f.submit_data(cls(attname=datetime.date(2011, 4, 28))),
            {"attname": "2011/04/28"})



class LocatorFieldTest(BaseFieldTests):
    @property
    def field_cls(self):
        from ccui.core.fields import Locator
        return Locator


    @property
    def target_cls(self):
        return self.cls


    def field_cls_and_target(self, *args, **kwargs):
        target = self.target_cls
        f = self.field_cls(target, *args, **kwargs)
        cls = self.cls
        setattr(cls, "attname", f)
        f.install("attname", cls)
        return f, cls, target


    @property
    def prepend_args(self):
        return (self.target_cls,)


    def field_and_cls(self, *args, **kwargs):
        return self.field_cls_and_target(*args, **kwargs)[:2]


    def test_default_names(self):
        f = self.field()

        self.assertEqual(f.api_name, "ns1.attnameLocator")
        self.assertEqual(f.api_filter_name, "attnameId")
        self.assertEqual(f.api_submit_name, "attnameId")


    def test_set_api_name(self):
        f = self.field(api_name="apiname")

        self.assertEqual(f.api_name, "ns1.apiname")
        self.assertEqual(f.api_filter_name, "apinameId")
        self.assertEqual(f.api_submit_name, "apinameId")


    def test_set_api_submit_name(self):
        f = self.field(api_submit_name="apisubmitname")

        self.assertEqual(f.api_name, "ns1.attnameLocator")
        self.assertEqual(f.api_filter_name, "attnameId")
        self.assertEqual(f.api_submit_name, "apisubmitname")


    def test_set_api_name_and_api_submit_name(self):
        f = self.field(api_name="apiname", api_submit_name="apisubmitname")

        self.assertEqual(f.api_name, "ns1.apiname")
        self.assertEqual(f.api_filter_name, "apinameId")
        self.assertEqual(f.api_submit_name, "apisubmitname")


    def test_encode(self):
        f, cls, target_cls = self.field_cls_and_target()
        self.assertEqual(f.encode(target_cls(identity={"@id": 1})), 1)


    def test_encode_string(self):
        f, cls, target_cls = self.field_cls_and_target()
        self.assertEqual(f.encode("1"), 1)


    def test_encode_int(self):
        f, cls, target_cls = self.field_cls_and_target()
        self.assertEqual(f.encode(1), 1)


    def test_submit(self):
        f, cls, target_cls = self.field_cls_and_target()
        self.assertEqual(
            f.submit_data(cls(attname=target_cls(identity={"@id": 1}))),
            {"attnameId": 1})


    def test_descriptor_class_access(self):
        f, cls = self.field_and_cls()
        self.assertIs(cls.attname, f)



@patch("ccui.core.api.userAgent")
class LocatorFunctionalTest(AuthTestCase):
    @property
    def subject_and_target(self):
        from ccui.core.api import RemoteObject
        from ccui.core.fields import Field, Locator

        class TheTarget(RemoteObject):
            nickname = Field()

            name_field = "nickname"

        class TheSubject(RemoteObject):
            target = Locator(TheTarget)

        return TheSubject, TheTarget


    @property
    def subjects(self):
        return ListBuilder(
            "thesubject",
            "thesubjects",
            "Thesubject",
            {
                "targetLocator": make_locator(
                    id=1, url="thetargets/1", name="The Target")
                }
            )


    def test_descriptor_lookup(self, http):
        TheSubject, TheTarget = self.subject_and_target

        target_data = {
            "@url": "http://some.base/thetargets/1",
            "@id": "1",
            "@name": "The Target"}
        http.request.return_value = response(
            self.subjects.one(targetLocator=target_data))

        subj = TheSubject.get("thesubjects/1", auth=self.auth)

        target = subj.target

        self.assertIsInstance(target, TheTarget)
        self.assertEqual(target.auth, self.auth)
        self.assertEqual(target.id, "1")
        self.assertEqual(target._location, "http://some.base/thetargets/1")
        self.assertEqual(target.nickname, "The Target")
        # getting target id, nickname, location didn't trigger delivery
        self.assertFalse(target._delivered)

        # accessing attribute a second time returns cached instance
        self.assertIs(target, subj.target)


    def test_descriptor_lookup_none(self, http):
        TheSubject, TheTarget = self.subject_and_target

        http.request.return_value = response(
            self.subjects.one(targetLocator={"@xsi.nil":"true"}))

        subj = TheSubject.get("thesubjects/1")

        target = subj.target

        self.assertEqual(target, None)


    def test_descriptor_lookup_no_url(self, http):
        TheSubject, TheTarget = self.subject_and_target

        target_data = {
            "@id": "1"}
        http.request.return_value = response(
            self.subjects.one(targetLocator=target_data))

        subj = TheSubject.get("thesubjects/1")

        self.assertEqual(subj.target, target_data)


    def test_descriptor_lookup_no_id(self, http):
        TheSubject, TheTarget = self.subject_and_target

        target_data = {
            "@url": "http://some.base/thetargets/1",
            }
        http.request.return_value = response(
            self.subjects.one(targetLocator=target_data))

        subj = TheSubject.get("thesubjects/1")

        self.assertEqual(subj.target, None)



class ResourceIdentityFieldTest(BaseFieldTests):
    @property
    def field_cls(self):
        from ccui.core.fields import ResourceIdentity
        return ResourceIdentity


    def test_default_names(self):
        f = self.field()

        self.assertEqual(f.api_name, "ns1.resourceIdentity")
        self.assertEqual(f.api_filter_name, False)
        self.assertEqual(f.api_submit_name, "resourceIdentity")


    def test_set_api_name(self):
        with self.assertRaises(TypeError):
            self.field(api_name="apiname")


    def test_set_api_submit_name(self):
        with self.assertRaises(TypeError):
            self.field(api_submit_name="apisubmitname")


    def test_set_api_name_and_api_submit_name(self):
        with self.assertRaises(TypeError):
            self.field(api_name="apiname", api_submit_name="apisubmitname")


    def test_encode(self):
        f = self.field()
        self.assertEqual(
            f.encode({"@version": "2"}), {"originalVersionId": "2"})


    def test_encode_no_version(self):
        f = self.field()
        self.assertEqual(
            f.encode("blah"), {})


    def test_no_submit_data(self):
        with self.assertRaises(TypeError):
            self.field_and_cls(api_submit_name=False)


    def test_submit(self):
        f, cls = self.field_and_cls()
        self.assertEqual(
            f.submit_data(
                cls(attname={"@version": "3"})), {"originalVersionId": "3"})



@patch("ccui.core.api.userAgent")
class UserIDFunctionalTest(AuthTestCase):
    @property
    def subject_and_user(self):
        from ccui.core.api import RemoteObject
        from ccui.core.fields import UserID

        class User(RemoteObject):
            pass

        class TheSubject(RemoteObject):
            user = UserID()

        return TheSubject, User


    @property
    def subjects(self):
        return ListBuilder(
            "thesubject",
            "thesubjects",
            "Thesubject",
            {
                "user": "1"
                }
            )


    def test_descriptor_lookup(self, http):
        from ccui.core.auth import admin
        TheSubject, User = self.subject_and_user

        http.request.return_value = response(
            self.subjects.one(user="4"))

        subj = TheSubject.get("thesubjects/1", auth=self.auth)

        user = subj.user

        self.assertIsInstance(user, User)

        # @@@ uses admin auth for now since user view perms don't work
        self.assertEqual(user.auth, admin)
        self.assertEqual(user._location, "users/4")

        # accessing attribute a second time returns cached instance
        self.assertIs(user, subj.user)


    def test_descriptor_lookup_invalid(self, http):
        TheSubject, User = self.subject_and_user

        http.request.return_value = response(
            self.subjects.one(user="blah"))

        subj = TheSubject.get("thesubjects/1", auth=self.auth)

        user = subj.user

        self.assertEqual(user, "blah")


    def test_descriptor_class_access(self, http):
        TheSubject, User = self.subject_and_user
        self.assertIs(TheSubject.user, TheSubject.__dict__["user"])



class TimelineFieldTest(BaseFieldTests):
    @property
    def field_cls(self):
        from ccui.core.fields import TimelineField
        return TimelineField


    @property
    def result_cls(self):
        from ccui.core.fields import Timeline
        return Timeline


    @property
    def user_cls(self):
        from ccui.core.api import RemoteObject

        class User(RemoteObject):
            pass

        return User


    def test_default_names(self):
        f = self.field()

        self.assertEqual(f.api_name, "ns1.timeline")
        self.assertEqual(f.api_filter_name, False)
        self.assertEqual(f.api_submit_name, False)


    def test_set_api_name(self):
        with self.assertRaises(TypeError):
            self.field(api_name="apiname")


    def test_set_api_submit_name(self):
        with self.assertRaises(TypeError):
            self.field(api_submit_name="apisubmitname")


    def test_set_api_name_and_api_submit_name(self):
        with self.assertRaises(TypeError):
            self.field(api_name="apiname", api_submit_name="apisubmitname")


    def test_no_submit_data(self):
        with self.assertRaises(TypeError):
            self.field_and_cls(api_submit_name=False)


    def test_submit(self):
        f, cls = self.field_and_cls()
        self.assertEqual(
            f.submit_data(
                cls(attname="blah")), {})


    def test_decode(self):
        User = self.user_cls
        f = self.field()
        t = f.decode(
            {
                "@createDate":"2011-05-04T18:24:11Z",
                "@createdBy":"1",
                "@lastChangeDate":"2011-05-05T18:24:11Z",
                "@lastChangedBy":"2",
                "@xsi.type":"ns1:Timeline"
                }
            )
        self.assertIsInstance(t, self.result_cls)
        self.assertEqual(t.createDate, datetime.date(2011, 5, 4))
        self.assertEqual(t.lastChangeDate, datetime.date(2011, 5, 5))
        self.assertIsInstance(t.createdBy, User)
        self.assertEqual(t.createdBy._location, "users/1")
        self.assertIsInstance(t.lastChangedBy, User)
        self.assertEqual(t.lastChangedBy._location, "users/2")


    def test_descriptor_class_access(self):
        f, cls = self.field_and_cls()
        self.assertIs(cls.attname, f)



@patch("ccui.core.api.userAgent")
class TimelineFieldFunctionalTest(AuthTestCase):
    @property
    def subject_timeline_and_user(self):
        from ccui.core.api import RemoteObject
        from ccui.core.fields import TimelineField, Timeline

        class User(RemoteObject):
            pass

        class TheSubject(RemoteObject):
            timeline = TimelineField()

        return TheSubject, Timeline, User


    @property
    def subjects(self):
        return ListBuilder(
            "thesubject",
            "thesubjects",
            "Thesubject",
            {
                "timeline": make_timeline()
                }
            )


    def test_descriptor_lookup(self, http):
        TheSubject, Timeline, User = self.subject_timeline_and_user

        http.request.return_value = response(
            self.subjects.one(
                timeline={
                    "@createDate":"2011-05-04T18:24:11Z",
                    "@createdBy":"1",
                    "@lastChangeDate":"2011-05-05T18:24:11Z",
                    "@lastChangedBy":"2",
                    "@xsi.type":"ns1:Timeline"
                    }
                )
            )

        subj = TheSubject.get("thesubjects/1", auth=self.auth)

        timeline = subj.timeline

        self.assertIsInstance(timeline, Timeline)
        self.assertEqual(timeline.auth, self.auth)

        self.assertEqual(timeline.createDate, datetime.date(2011, 5, 4))
        self.assertEqual(timeline.lastChangeDate, datetime.date(2011, 5, 5))
        self.assertIsInstance(timeline.createdBy, User)
        self.assertEqual(timeline.createdBy._location, "users/1")
        self.assertIsInstance(timeline.lastChangedBy, User)
        self.assertEqual(timeline.lastChangedBy._location, "users/2")

        # accessing attribute a second time returns cached instance
        self.assertIs(timeline, subj.timeline)



@patch("ccui.core.api.userAgent")
class LinkFunctionalTest(AuthTestCase):
    def subject_and_target(self, cache=None):
        from ccui.core.api import RemoteObject, ListObject
        from ccui.core.fields import Link, List, Object

        class TheTarget(RemoteObject):
            pass

        class TargetList(ListObject):
            entryclass = TheTarget

            entries = List(Object(TheTarget))

        kwargs = {}
        if cache is not None:
            kwargs["cache"] = cache

        class TheSubject(RemoteObject):
            targets = Link(TargetList, **kwargs)

        return TheSubject, TargetList


    @property
    def targets(self):
        return ListBuilder(
            "thetarget",
            "thetargets",
            "Thetarget",
            )


    @property
    def subjects(self):
        return ListBuilder(
            "thesubject",
            "thesubjects",
            "Thesubject",
            {
                "targets": self.targets.array({})
                }
            )


    def test_descriptor_lookup(self, http):
        TheSubject, TargetList = self.subject_and_target()

        http.request.return_value = response(self.subjects.one())

        subj = TheSubject.get("some/url", auth=self.auth)

        targets = subj.targets

        self.assertIsInstance(targets, TargetList)
        self.assertEqual(targets.auth, self.auth)
        self.assertIs(targets.linked_from, subj)
        self.assertEqual(
            targets._location, "some/url/targets")
        # getting target location didn't trigger delivery
        self.assertFalse(targets._delivered)


    def test_descriptor_lookup_cache_bucket_specified(self, http):
        TheSubject, TargetList = self.subject_and_target(cache="OtherBucket")

        http.request.return_value = response(self.subjects.one())

        subj = TheSubject.get("some/url", auth=self.auth)

        http.request.return_value = response(self.targets.array({}))

        with patch("ccui.core.cache.cache") as cache:
            fill_cache(cache, {})
            list(subj.targets)

        cache.get.assert_called_with(
            "OtherBucket-0-http://fake.base/rest/some/url/targets?_type=json")


    def test_descriptor_lookup_no_location(self, http):
        TheSubject, TargetList = self.subject_and_target()

        subj = TheSubject()

        with self.assertRaises(AttributeError):
            subj.targets


    def test_descriptor_set(self, http):
        TheSubject, TargetList = self.subject_and_target()
        TheTarget = TargetList.entryclass

        subj = TheSubject.get("some/url", auth=self.auth)

        http.request.return_value = response(make_boolean(True))

        subj.targets = [
            TheTarget(identity=make_identity(id=1)),
            TheTarget(identity=make_identity(id=2))]

        req = http.request.call_args[1]
        self.assertEqual(req["method"], "PUT")
        self.assertEqual(req["body"], "theTargetIds=1&theTargetIds=2")
        self.assertEqual(
            Url(req["uri"]),
            Url("http://fake.base/rest/some/url/targets?_type=json"))


    def test_descriptor_set_with_list(self, http):
        TheSubject, TargetList = self.subject_and_target()
        TheTarget = TargetList.entryclass

        subj = TheSubject.get("some/url", auth=self.auth)

        http.request.return_value = response(make_boolean(True))

        subj.targets = TargetList(
            entries=[
                TheTarget(identity=make_identity(id=1)),
                TheTarget(identity=make_identity(id=2))])

        req = http.request.call_args[1]
        self.assertEqual(req["method"], "PUT")
        self.assertEqual(req["body"], "theTargetIds=1&theTargetIds=2")
        self.assertEqual(
            Url(req["uri"]),
            Url("http://fake.base/rest/some/url/targets?_type=json"))
