

        import unittest
        from unittest.mock import Mock, patch
        from io import StringIO
        from junorunner.extended_runner import TextTestResult

        class TestPrintSingleError(unittest.TestCase):

            def setUp(self):
                self.stream = StringIO()
                self.result = TextTestResult(self.stream, descriptions=False, verbosity=2, total_tests=1)
                self.test = Mock()
                self.test.shortDescription.return_value = None
                self.test.__str__.return_value = "test_method"

            def test_print_single_error_with_tuple(self):
                err = (TypeError, TypeError("foo"), None)
                self.result.printSingleError("ERROR", self.test, err)
                output = self.stream.getvalue()
                self.assertIn("ERROR: test_method", output)
                self.assertIn("TypeError: foo", output)

            def test_print_single_error_with_string(self):
                err = "Something went wrong"
                self.result.printSingleError("ERROR", self.test, err)
                output = self.stream.getvalue()
                self.assertIn("ERROR: test_method", output)
                self.assertIn("Something went wrong", output)

            def test_printSingleError_no_traceback(self):
                err = "This is an error message."
                with patch('sys.stdout', new=StringIO()) as mocked_stdout:
                    self.result.printSingleError("ERROR", self.test, err)
                    output = mocked_stdout.getvalue()
                self.assertEqual(output, "======================================================================\nERROR: test_method\n----------------------------------------------------------------------\nThis is an error message.\n")

            def test_printSingleError_empty_error(self):
                err = ""
                with patch('sys.stdout', new=StringIO()) as mocked_stdout:
                    self.result.printSingleError("ERROR", self.test, err)
                    output = mocked_stdout.getvalue()
                self.assertEqual(output, "======================================================================\nERROR: test_method\n----------------------------------------------------------------------\n\n")

            def test_printSingleError_empty_traceback(self):
                err = (TypeError, TypeError("foo"), None)
                with patch('sys.stdout', new=StringIO()) as mocked_stdout:
                    self.result.printSingleError("ERROR", self.test, err)
                    output = mocked_stdout.getvalue()
                self.assertEqual(output, "======================================================================\nERROR: test_method\n----------------------------------------------------------------------\nTypeError: foo\n")


            def test_printSingleError_with_traceback(self):
                err = (TypeError, TypeError("foo"), Mock())
                err[2].format_exception.return_value = [
                    "Traceback (most recent call last):\n",
                    "  File \"some_file.py\", line 1, in <module>\n",
                    "    1/0\n",
                    "ZeroDivisionError: division by zero\n"
                ]
                with patch('sys.stdout', new=StringIO()) as mocked_stdout:
                    self.result.printSingleError("ERROR", self.test, err)
                    output = mocked_stdout.getvalue()
                self.assertIn("ERROR: test_method", output)
                self.assertIn("TypeError: foo", output)
                self.assertIn("Traceback (most recent call last):", output)
                self.assertIn("ZeroDivisionError: division by zero", output)

        