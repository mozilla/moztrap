from mock import patch

from ..testexecution.builders import testcycles
from ..utils import ViewTestCase



@patch("tcmui.core.api.userAgent")
class DefaultManageViewTest(ViewTestCase):
    @property
    def view(self):
        from tcmui.manage.views import home
        return home


    def test_redirect(self, http):
        self.setup_responses(http)
        res = self.app.get("/manage/")

        self.assertEqual(res.status_int, 302)
        self.assertEqual(
            res.headers["location"],
            "http://localhost:80/manage/testcycles/")
