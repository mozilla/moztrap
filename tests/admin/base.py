from django.core.urlresolvers import reverse

from django_webtest import WebTest

from ..builders import create_user



class AdminTestCase(WebTest):
    model_name = None
    app_label = None


    def setUp(self):
        self.user = create_user(is_staff=True, is_superuser=True)


    @property
    def changelist_url(self):
        return reverse(
            'admin:%s_%s_changelist' % (self.app_label, self.model_name)
            )


    def change_url(self, obj):
        return reverse(
            'admin:%s_%s_change' % (self.app_label, self.model_name),
            args=[obj.id]
            )


    def get(self, url):
        return self.app.get(url, user=self.user)
