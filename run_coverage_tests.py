import os
import unittest
import coverage

def set_test_environment():
    # Set the environment variable to determine the app configuration
    os.environ['CONFIG'] = 'TESTING'

def run_tests():
    # Set the test environment
    set_test_environment()

    # Start coverage
    cov = coverage.Coverage(omit=["tests/*"])
    cov.start()

    # Discover and run tests
    loader = unittest.TestLoader()
    tests = loader.discover('tests')  # Assuming your tests are in a 'tests' directory
    testRunner = unittest.TextTestRunner()
    testRunner.run(tests)

    # Stop coverage and save results
    cov.stop()
    cov.save()

    # Report coverage
    print("\nCoverage Report:")
    cov.report()

    # Optionally, generate HTML report
    cov.html_report(directory='coverage_html_report')

    # Optionally, generate XML report
    cov.xml_report(outfile='coverage.xml')

# Run the tests
if __name__ == '__main__':
    run_tests()
