"""
Utility base TestCase for testing admin views.

"""
from django.core.urlresolvers import reverse

from .view.base import WebTest



class AdminTestCase(WebTest):
    model_name = None
    app_label = None


    def setUp(self):
        """Set-up for all admin test cases."""
        self.user = self.F.UserFactory.create(
            is_staff=True, is_superuser=True)


    @property
    def changelist_url(self):
        """The changelist URL for this model."""
        return reverse(
            'admin:%s_%s_changelist' % (self.app_label, self.model_name)
            )


    @property
    def add_url(self):
        """The add URL for the given object."""
        return reverse(
            'admin:%s_%s_add' % (self.app_label, self.model_name)
            )


    def change_url(self, obj):
        """The change URL for the given object."""
        return reverse(
            'admin:%s_%s_change' % (self.app_label, self.model_name),
            args=[obj.id]
            )


    def delete_url(self, obj):
        """The delete URL for the given object."""
        return reverse(
            'admin:%s_%s_delete' % (self.app_label, self.model_name),
            args=[obj.id]
            )


    def get(self, url):
        """Make GET request to given URL and return response."""
        return self.app.get(url, user=self.user)


    def post(self, url, data):
        """Make POST request to given URL with ``data``, return response."""
        return self.app.post(url, data, user=self.user)
