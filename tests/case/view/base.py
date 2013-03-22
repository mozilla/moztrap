"""
Utility base TestCase classes for testing views.

"""
from django.conf import settings
from django.core.urlresolvers import reverse

from BeautifulSoup import BeautifulSoup
import django_webtest
import django_webtest.backends

from moztrap import model

from ...utils import Url
from ..base import DBMixin



class WebtestUserBackend(django_webtest.backends.WebtestUserBackend):
    """A version of WebtestUserBackend that returns our proxy User model."""
    def authenticate(self, django_webtest_user):
        """
        The username passed as ``remote_user`` is considered trusted.  This
        method simply returns the ``User`` object with the given username,
        creating a new ``User`` object if ``create_unknown_user`` is ``True``.

        Returns None if ``create_unknown_user`` is ``False`` and a ``User``
        object with the given username is not found in the database.
        """
        if not django_webtest_user:
            return
        user = None
        username = self.clean_username(django_webtest_user)

        # Note that this could be accomplished in one try-except clause, but
        # instead we use get_or_create when creating unknown users since it has
        # built-in safeguards for multiple threads.
        if self.create_unknown_user:
            user, created = model.User.objects.get_or_create(username=username)
            if created:
                user = self.configure_user(user)
        else:
            try:
                user = model.User.objects.get(username=username)
            except model.User.DoesNotExist:
                pass
        return user


    def get_user(self, user_id):
        """Return instances of our User model."""
        try:
            return model.User.objects.get(pk=user_id)
        except model.User.DoesNotExist:
            return None




class WebTest(DBMixin, django_webtest.WebTest):
    """Fix WebTest so it works with django-session-csrf, mixin db utilities."""
    def _setup_auth_backend(self):
        """Use our subclass of the remote user backend."""
        backend_name = 'tests.case.view.base.WebtestUserBackend'
        settings.AUTHENTICATION_BACKENDS.insert(0, backend_name)


    def _setup_auth_middleware(self):
        """
        Monkeypatch remote-user-auth middleware into MIDDLEWARE_CLASSES.

        Places remote-user-auth middleware before session-csrf middleware, so
        session-csrf sees the authenticated user.

        """
        auth_middleware = "django_webtest.middleware.WebtestUserMiddleware"
        session_csrf_middleware = "session_csrf.CsrfMiddleware"
        index = settings.MIDDLEWARE_CLASSES.index(session_csrf_middleware)
        settings.MIDDLEWARE_CLASSES.insert(index, auth_middleware)



class ViewTestCase(WebTest):
    """Add some utility assertions and methods."""
    # subclasses should provide a url property
    url = None


    def assertRedirects(self, response, path, status_code=302):
        """An assertRedirects that works with WebTest."""
        self.assertEqual(response.status_int, status_code)

        self.assertEqual(
            Url(response.headers["Location"]),
            Url("http://localhost:80" + path)
            )


    def assertElement(self, html, element, *args, **kwargs):
        """
        Assert that an element is in an HTML snippet some number of times.

        ``html`` is either an HTML string or a BeautifulSoup object.

        ``element`` is the HTML tag name; extra arguments and keyword arguments
        are passed on to BeautifulSoup as attribute selectors.

        ``count`` keyword arg specifies the number of elements matching the
        spec that are expected to be found; defaults to 1.

        """
        count = kwargs.pop("count", 1)
        if isinstance(html, basestring):
            html = BeautifulSoup(html)
        actual = len(html.findAll(element, *args, **kwargs))
        self.assertEqual(
            actual,
            count,
            "Element {0}({1}, {2}) is present {3} times, not {4}. "
            "Full HTML: {5}".format(
                element, args, kwargs, actual, count, html)
            )


    def get(self, **kwargs):
        """Shortcut for getting url; supports `ajax` boolean kwarg."""
        if kwargs.pop("ajax", False):
            kwargs.setdefault("headers", {}).setdefault(
                "X-Requested-With", "XMLHttpRequest")
        return self.app.get(self.url, **kwargs)



class AuthenticatedViewTestCase(ViewTestCase):
    """Base test case for authenticated views."""
    def setUp(self):
        """Set-up for authenticated view test cases; create a user."""
        self.user = self.F.UserFactory.create()


    def get(self, **kwargs):
        """Shortcut for getting url, authenticated."""
        kwargs.setdefault("user", self.user)
        return super(AuthenticatedViewTestCase, self).get(**kwargs)


    def post(self, data, **kwargs):
        """Shortcut for posting to url, authenticated."""
        kwargs.setdefault("user", self.user)
        return self.app.post(self.url, data, **kwargs)


    def add_perm(self, codename):
        """Add named permission to user."""
        perm = self.model.Permission.objects.get(codename=codename)
        self.user.user_permissions.add(perm)


    def test_login_required(self):
        """Requires login."""
        res = self.app.get(self.url, status=302)

        self.assertRedirects(res, reverse("auth_login") + "?next=" + self.url)



class FormViewTestCase(AuthenticatedViewTestCase):
    """Base class for testing any authenticated view with a form."""
    # subclasses should override
    form_id = None


    def get_form(self, *args, **kwargs):
        """Get the manage list form; passes args/kwargs on to self.get()."""
        return self.get(*args, **kwargs).forms[self.form_id]



class ListViewTestCase(AuthenticatedViewTestCase):
    """Base class for testing list views."""
    # subclasses should specify these:
    factory = None       # factory for creating objects in this list
    name_attr = "name"   # char attribute that should appear in list


    def soup(self, response):
        """
        Given an HTML or JSON response, return a BeautifulSoup object.

        If the response is JSON, looks for the "html" key.

        """
        if "html" in response.content_type:
            html = response.html
        elif "json" in response.content_type:
            html = BeautifulSoup(response.json["html"])
        else:
            self.fail(
                "Response content-type {0} is neither JSON nor HTML.".format(
                    response.content_type)
                )

        return html


    def assertInList(self, response, name, count=1):
        """Assert that item ``name`` is in the list ``count`` times."""
        soup = self.soup(response)
        itemlist = soup.find(True, "itemlist")
        if itemlist is None:
            self.fail("itemlist not found in: {0}".format(soup))
        self.assertElement(
            itemlist,
            "h3",
            title=name,
            count=count
            )


    def assertIdInList(self, response, id, count=1):
        """Assert that article's ``id`` is in the list ``count`` times."""
        soup = self.soup(response)
        itemlist = soup.find(True, "itemlist")
        if itemlist is None:
            self.fail("itemlist not found in: {0}".format(soup))
        self.assertElement(
            itemlist,
            "article",
            id=id,
            count=count
        )


    def assertNotInList(self, response, name):
        """Assert that item ``name`` is not in the list."""
        self.assertInList(response, name, 0)


    def assertIdNotInList(self, response, id):
        """Assert that item ``name`` is not in the list."""
        self.assertIdInList(response, id, 0)


    def assertOrderInList(self, response, *names):
        """Assert that ``names`` appear in list in given order."""
        soup = self.soup(response)

        all_names = [el.text for el in soup.findAll("h3", title=True)]

        indices = []

        for name in names:
            try:
                indices.append((all_names.index(name), name))
            except ValueError:
                self.fail("{0} does not appear in list.".format(name))

        actual_order = sorted(indices, key=lambda t: t[0])

        self.assertEqual(
            [t[1] for t in actual_order],
            [t[1] for t in indices],
            )


    def test_list(self):
        """Displays a list of objects."""
        self.factory(**{self.name_attr: "Foo Bar"})

        res = self.get()

        self.assertInList(res, "Foo Bar")



class ListFinderTests(object):
    """Extra tests for manage lists with finder."""
    def test_finder(self):
        """Finder is present in context with list of products."""
        p = self.F.ProductFactory.create(name="Foo Product")

        res = self.get()

        res.mustcontain("Foo Product")
        res.mustcontain(
            "data-sub-url="
            '"?finder=1&amp;col=productversions&amp;id={0}"'.format(p.id))


    def test_finder_ajax(self):
        """Finder intercepts its ajax requests to return child obj lists."""
        pv = self.F.ProductVersionFactory.create(version="1.0.1")

        res = self.get(
            params={
                "finder": "1",
                "col": "productversions",
                "id": str(pv.product.id)
                },
            headers={"X-Requested-With": "XMLHttpRequest"},
            )

        self.assertIn("1.0.1", res.json["html"])
        self.assertIn(
            'data-sub-url="?finder=1&amp;col=runs&amp;id={0}"'.format(pv.id),
            res.json["html"]
            )



class NoCacheTest(object):
    """Test that a given view marks it's responses as uncacheable."""
    def test_never_cache(self):
        res = self.get()

        self.assertEqual(res.headers["Cache-Control"], "max-age=0")
