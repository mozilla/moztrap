from unittest2 import TestCase



class Error(object):
    def __init__(self, response_error):
        self.response_error = response_error



class ErrorMessageAndFieldsTest(TestCase):
    def assert_results(self, obj, err, ret):
        from tcmui.core.errors import error_message_and_fields
        self.assertEqual(error_message_and_fields(obj, Error(err)), ret)


    def test_simple(self):
        self.assert_results(
            object(), "duplicate.name",
            ("This name is already in use.", ["name"]))


    def test_name_interpolation(self):
        class TestSuite(object):
            def __unicode__(self):
                return "thinger"

        self.assert_results(
            TestSuite(), "changing.used.entity",
            ("The thinger is in use and cannot be modified.", []))


    def test_classname_lookup(self):
        class TestSuite(object):
            pass

        class TestRun(object):
            pass

        self.assert_results(
            TestSuite(), "activating.incomplete.entity",
            ("Test suite is empty; add some test cases.", []))

        self.assert_results(
            TestRun(), "activating.incomplete.entity",
            ("Activate or unlock parent test cycle first.", []))


    def test_bad_error_code(self):
        self.assert_results(
            object(), "some.wierd.error",
            ('Unknown conflict "some.wierd.error"; please correct and try again.',
             []))


class ErrorMessageTest(ErrorMessageAndFieldsTest):
    """
    ``error_message`` should always return the first element of the return
    value of ``error_message_and_fields``.

    """
    def assert_results(self, obj, err, ret):
        from tcmui.core.errors import error_message
        self.assertEqual(error_message(obj, Error(err)), ret[0])
