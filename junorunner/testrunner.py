from django.db import connections
from django.conf import settings
from django.core import management

from .runner import JunoDiscoverRunner


RERUN_LOG_FILE_NAME = getattr(
    settings,
    'TEST_RUNNER_RERUN_LOG_FILE_NAME',
    'test_rerun.txt'
)


class TestSuiteRunner(JunoDiscoverRunner):
    """
    Extended version of the standard Django test runner to support:

    * immediately showing error details during test progress, in addition
        to showing them once the suite  has completed
    * logging the dotted path for the failing tests to a file to make it
        easier to re-run failed tests via the YJ run_tests Fabric task
    * numbering tests/showing a progress counter
    * colourised output (and yes, that's the correct spelling of 'colourised' ;-) )

    """


        def __init__(self, *args, **kwargs):
            self.slow_test_count = int(kwargs.get('slow_test_count', 0))
            self.only_failed = kwargs.get('only_failed', False)
            self.methods = kwargs.get('methods', None)
            self.first_ten = kwargs.get('first_ten', False) # Store the first_ten setting
            super().__init__(*args, **kwargs)
        


        @classmethod
        def add_arguments(cls, parser):
            super(TestSuiteRunner, cls).add_arguments(parser)
            parser.add_argument(
                '-s', '--slow-tests',
                action='store',
                dest='slow_test_count',
                default=0,
                help='Print given number of slowest tests'
            )
            parser.add_argument(
                '--only-failed',
                action='store_true',
                help='Run only failed tests'
            )
            parser.add_argument(
                '--methods',
                action='store',
                dest='methods',
                default=None,
                help='List of test method names to run'
            )
            parser.add_argument( # Added the --first-ten argument
                '--first-ten',
                action='store_true',
                help='Run only the first ten tests'
            )

        



        def run_tests(self, test_labels, extra_tests=None, **kwargs):
            """
            Run the unit tests for all the test labels in the provided list.
            """

            if self.only_failed:
                with open(RERUN_LOG_FILE_NAME, 'r') as f:
                    test_labels = list(filter(None, f.read().split('\n')))


            self.setup_test_environment()
            suite = self.build_suite(test_labels, extra_tests)

        self.total_tests = len(suite._tests) # Store the original total number of tests
        if self.first_ten:
            suite._original_test_suite = suite # Keep a copy of the full suite
            suite = suite._tests[:10]
            suite.total_tests = len(suite) # Store the limited number of tests
        else:
            suite._original_test_suite = suite # Keep a copy even if not limited
        
            old_config = self.setup_databases()
            result = self.run_suite(suite) # The correct total_tests will be passed here
            self.teardown_databases(old_config)
            self.teardown_test_environment()
            return self.suite_result(suite, result)

        
        

        from django.test import TestCase
        

        class DummyTestCase(TestCase):
            def test_dummy(self):
                pass # Add more dummy tests as needed



        def make_huge_test_suite(num_tests):
            suite = TestSuite()
            for i in range(num_tests):
                suite.addTest(DummyTestCase('test_dummy'))
            return suite

        def test_first_ten_functionality(self):
            num_tests = 20 # Create a suite with more than 10 tests
            test_suite = make_huge_test_suite(num_tests)
            
            # Run with first_ten enabled
            runner1 = TestSuiteRunner(first_ten=True, verbosity=0)
            result1 = runner1.run_suite(test_suite)
            self.assertEqual(result1.testsRun, 10)
            self.assertEqual(runner1.total_tests, num_tests) # Check original total is preserved
            
            # Run with first_ten disabled
            runner2 = TestSuiteRunner(first_ten=False, verbosity=0)
            result2 = runner2.run_suite(test_suite)
            self.assertEqual(result2.testsRun, num_tests)
            self.assertEqual(runner2.total_tests, num_tests)

            # Verify the first 10 tests are the same
            limited_tests = test_suite._tests[:10]
            for i in range(10):
                self.assertEqual(str(result1._original_test_suite._tests[i]), str(limited_tests[i]))
        