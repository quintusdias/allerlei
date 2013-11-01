import unittest

def foo(f):
    def wrapper():
        pass
    return wrapper

class MainTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @foo
    def test_base(self):
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()

