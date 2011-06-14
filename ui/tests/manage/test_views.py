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
        res = self.get("/manage/")

        self.assertEqual(res.status_code, 302)
        self.assertEqual(
            res["Location"], "/manage/testcycles/?finder=1")
