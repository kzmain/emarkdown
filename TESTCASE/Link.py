import unittest

from emarkdown import tt


class SimpleTest(unittest.TestCase):

    # Returns True or False.
    def test(self):
        self.assertEqual(tt.a(), 1)

    # Returns True or False.
    def test2(self):
        self.assertEqual(tt.b(), 2)


if __name__ == '__main__':
    unittest.main()
