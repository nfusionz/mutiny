import unittest


class MyTestCase(unittest.TestCase):

    @unittest.skip
    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
