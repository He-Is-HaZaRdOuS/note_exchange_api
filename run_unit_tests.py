import os
import unittest

def set_test_environment():
    # Set the environment variable to determine the app configuration
    os.environ['CONFIG'] = 'TESTING'

def run_tests():
    # Set the test environment
    set_test_environment()

    # Discover and run tests
    loader = unittest.TestLoader()
    tests = loader.discover('unit_tests')
    testRunner = unittest.TextTestRunner(verbosity=2)
    result = testRunner.run(tests)

    # Exit with appropriate code
    if result.wasSuccessful():
        exit(0)
    else:
        exit(1)

# Run the tests
if __name__ == '__main__':
    run_tests()
