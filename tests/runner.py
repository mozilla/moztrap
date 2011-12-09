from django.conf import settings
from django.test.simple import DjangoTestSuiteRunner, reorder_suite
from django.utils.unittest import TestCase
from django.utils.unittest.loader import defaultTestLoader



class DiscoveryDjangoTestSuiteRunner(DjangoTestSuiteRunner):
    def build_suite(self, test_labels, extra_tests=None, **kwargs):
        if test_labels:
            suite = defaultTestLoader.loadTestsFromNames(test_labels)
        else:
            suite = defaultTestLoader.discover(settings.TEST_DISCOVERY_ROOT)

        if extra_tests:
            for test in extra_tests:
                suite.addTest(test)

        return reorder_suite(suite, (TestCase,))
