from django.core.exceptions import MiddlewareNotUsed

from django.test.utils import override_settings
from mock import patch, Mock

from tests import case



class AjaxTracebackMiddlewareTest(case.TestCase):
    @property
    def middleware(self):
        from moztrap.debug.middleware import AjaxTracebackMiddleware
        return AjaxTracebackMiddleware


    @override_settings(DEBUG=True)
    def test_used_in_DEBUG(self):
        self.middleware()


    @override_settings(DEBUG=False)
    def test_not_used_when_DEBUG_off(self):
        with self.assertRaises(MiddlewareNotUsed):
            self.middleware()


    @override_settings(DEBUG=True)
    def test_process_exception(self):
        """
        process_exception ajax response: traceback with <br>s inserted.

        """
        m = self.middleware()

        request = Mock()
        request.is_ajax.return_value = True

        with patch("traceback.format_exc") as format_exc:
            format_exc.return_value = "some\ntraceback"
            response = m.process_exception(request)

        self.assertEqual(response.content, "some<br>\ntraceback")


    @override_settings(DEBUG=True)
    def test_process_exception_non_ajax(self):
        """
        process_exception does nothing for non-ajax requests.

        """
        m = self.middleware()

        request = Mock()
        request.is_ajax.return_value = False

        self.assertIs(m.process_exception(request), None)
