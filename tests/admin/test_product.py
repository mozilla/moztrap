from django.core.urlresolvers import reverse

from django_webtest import WebTest

from ..builders import create_user, create_product



class ProductAdminTest(WebTest):
    def setUp(self):
        self.user = create_user(is_staff=True, is_superuser=True)


    def test_changelist(self):
        url = reverse('admin:core_product_changelist')
        create_product(name="Firefox")

        res = self.app.get(url, user=self.user)

        res.mustcontain("Firefox")
