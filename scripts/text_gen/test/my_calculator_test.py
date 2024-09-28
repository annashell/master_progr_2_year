import unittest

from scripts.text_gen.my_calculator import calculator


# from my_calculator import calculator


class TestCalculator(unittest.TestCase):
    def test_norm(self):
        self.assertEqual(calculator("2+3"), 5)
        self.assertEqual(calculator("2*3"), 6)
        self.assertEqual(calculator("2-3"), -1)
        self.assertEqual(calculator("1+2^3^5-15*5/(5+1)"), 32756.5)
        self.assertEqual(calculator("(3+5)*(-3+2)"), -8)
