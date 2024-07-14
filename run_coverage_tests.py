import os
import unittest
import coverage

def set_test_environment():
    # Set the environment variable to determine the app configuration
    os.environ['CONFIG'] = 'TESTING'

def run_coverage_tests():
    # Set the test environment
    set_test_environment()

    # Start coverage collection
    cov = coverage.Coverage(omit=["tests/*"])
    cov.start()

    # Discover and run tests
    loader = unittest.TestLoader()
    tests = loader.discover('tests')  # Assuming your tests are in a 'tests' directory
    testRunner = unittest.TextTestRunner(verbosity=2)
    result = testRunner.run(tests)

    # Stop coverage collection
    cov.stop()
    cov.save()

    # Report coverage
    print("\nCoverage Report:\n")
    cov.report()
    cov.html_report(directory='coverage_html_report')
    cov.xml_report(outfile='coverage.xml')

    # Exit with appropriate code
    if result.wasSuccessful():
        exit(0)
    else:
        exit(1)

# Run the coverage tests
if __name__ == '__main__':
    run_coverage_tests()
