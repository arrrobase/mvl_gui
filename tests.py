import unittest
import numpy as np
from money import Money


class MoneyTest(unittest.TestCase):
    """
    Test proper implementation of math operations for Money, and handling of np.NAN scenarios.
    """
    def setUp(self):
        self.mn5 = Money(-5)
        self.m0 = Money(0)
        self.m3 = Money(3)
        self.m5 = Money(5)
        self.m10 = Money(10)
        self.m15 = Money(15)
        self.nan = Money(np.NAN)

    def test_eq(self):
        self.assertTrue(self.m5 == Money(5))
        self.assertTrue(self.m5 == 5)
        self.assertTrue(self.nan == self.nan)

        self.assertFalse(self.m5 == self.m10)
        self.assertFalse(self.m5 == 10)
        self.assertFalse(self.m5 == self.nan)

    def test_add(self):
        self.assertTrue(self.m5 + self.m10 == self.m15)
        self.assertTrue(5 + self.m10 == self.m15)
        self.assertTrue(self.m5 + 10 == self.m15)

        self.assertTrue(self.m5 + self.nan == self.m5)
        self.assertTrue(self.nan + self.m5 == self.m5)
        self.assertTrue(np.isnan((self.nan + self.nan).amount))

    def test_sub(self):
        self.assertTrue(self.m15 - self.m10 == self.m5)
        self.assertTrue(15 - self.m10 == self.m5)
        self.assertTrue(self.m15 - 10 == self.m5)

        self.assertTrue(self.m5 - self.nan == self.m5)
        self.assertTrue(self.nan - self.m5 == self.mn5)
        self.assertTrue(np.isnan((self.nan - self.nan).amount))

    def test_truediv(self):
        self.assertTrue(self.m15 / self.m5 == self.m3)
        self.assertTrue(self.m15 / 5 == self.m3)
        # self.assertTrue(15 / self.m5 == self.m3)

        self.assertTrue(self.nan / self.nan == self.nan)
        self.assertTrue(self.nan / self.m10 == self.nan)
        self.assertTrue(self.m10 / self.nan == self.nan)
        self.assertTrue(10 / self.nan == self.nan)
        self.assertTrue(self.nan / 10 == self.nan)

        with self.assertRaises(ZeroDivisionError):
            self.m10 / 0

    def test_floordiv(self):
        self.assertTrue(self.m10 // self.m3 == self.m3)
        self.assertTrue(self.m10 // 3 == self.m3)
        # self.assertTrue(10 // self.m3 == self.m3)

        self.assertTrue(self.nan // self.nan == self.nan)
        self.assertTrue(self.nan // self.m10 == self.nan)
        self.assertTrue(self.m10 // self.nan == self.nan)
        self.assertTrue(10 // self.nan == self.nan)
        self.assertTrue(self.nan // 10 == self.nan)

        with self.assertRaises(ZeroDivisionError):
            self.m10 / 0

    def test_mul(self):
        self.assertTrue(self.m3 * self.m5 == self.m15)
        self.assertTrue(self.m3 * 5 == self.m15)
        self.assertTrue(3 * self.m5 == self.m15)

        self.assertTrue(self.nan * self.nan == self.nan)
        self.assertTrue(self.nan * self.m10 == self.nan)
        self.assertTrue(self.m10 * self.nan == self.nan)
        self.assertTrue(10 * self.nan == self.nan)
        self.assertTrue(self.nan * 10 == self.nan)

    def test_lt(self):
        self.assertTrue(self.m5 < self.m10)
        self.assertTrue(self.m5 < 10)
        self.assertTrue(5 < self.m10)

        self.assertFalse(self.m10 < self.m5)
        self.assertFalse(10 < self.m5)
        self.assertFalse(self.m10 < self.m5)

        self.assertFalse(self.nan < self.nan)
        self.assertFalse(self.nan < self.m5)
        self.assertFalse(self.m5 < self.nan)
        self.assertFalse(self.nan < 5)
        self.assertFalse(5 < self.nan)

    def test_le(self):
        self.assertTrue(self.m5 <= self.m10)
        self.assertTrue(self.m5 <= 10)
        self.assertTrue(5 <= self.m10)
        self.assertTrue(self.m5 <= self.m5)
        self.assertTrue(self.nan <= self.nan)

        self.assertFalse(self.m10 <= self.m5)
        self.assertFalse(10 <= self.m5)
        self.assertFalse(self.m10 <= self.m5)

        self.assertFalse(self.nan <= self.m5)
        self.assertFalse(self.m5 <= self.nan)
        self.assertFalse(self.nan <= 5)
        # self.assertFalse(5 <= self.nan)

    def test_gt(self):
        self.assertFalse(self.m5 > self.m10)
        self.assertFalse(self.m5 > 10)
        self.assertFalse(5 > self.m10)

        self.assertTrue(self.m10 > self.m5)
        self.assertTrue(10 > self.m5)
        self.assertTrue(self.m10 > self.m5)
        self.assertTrue(self.m5 >= self.m5)

        self.assertFalse(self.nan < self.nan)
        self.assertFalse(self.nan < self.m5)
        self.assertFalse(self.m5 < self.nan)
        self.assertFalse(self.nan < 5)
        self.assertFalse(5 < self.nan)

    def test_ge(self):
        self.assertFalse(self.m5 >= self.m10)
        self.assertFalse(self.m5 >= 10)
        self.assertFalse(5 >= self.m10)

        self.assertTrue(self.m10 >= self.m5)
        self.assertTrue(10 >= self.m5)
        self.assertTrue(self.m10 >= self.m5)
        self.assertTrue(self.nan <= self.nan)

        self.assertFalse(self.nan <= self.m5)
        self.assertFalse(self.m5 <= self.nan)
        self.assertFalse(self.nan <= 5)
        # self.assertFalse(5 <= self.nan)
