import numpy as np
from decimal import Decimal
from functools import total_ordering


@total_ordering
class Money:
    """
    Class to represent money, either as dollar amounts or number of quarters, and from weights

    All the checks for instance of decimal are to prevent errors, because numpy can't check decimal types without
    throwing type error
    TODO: implement rest of class numerical methods
    """
    def __init__(self, amount=None):
        if amount is None:
            self._amount = np.NAN

        else:
            if not isinstance(amount, Decimal) and np.isnan(amount):
                self._amount = amount
            else:
                self._amount = Decimal(amount)

    @property
    def amount(self):
        return self._amount

    def __str__(self):
        if not isinstance(self.amount, Decimal) and np.isnan(self.amount):
            return 'NaN'

        return '${:03.2f}'.format(self.amount)

    def __repr__(self):
        if not isinstance(self.amount, Decimal) and np.isnan(self.amount):
            return 'NaN'

        return 'Money ' + self.__str__()

    def __float__(self):
        return float(self.amount)

    def __int__(self):
        return int(self.amount)*4

    def __add__(self, other):
        amount = self._amount
        if isinstance(other, Money):
            other = other.amount

        # if both are nan, return nan, else set whichever is nan to 0
        if not isinstance(amount, Decimal) and np.isnan(amount):
            amount = 0

            if not isinstance(other, Decimal) and np.isnan(other):
                return Money(np.NAN)

        elif not isinstance(other, Decimal) and np.isnan(other):
            other = 0

        return Money(amount + other)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        amount = self._amount
        if isinstance(other, Money):
            other = other.amount

        # if both are nan, return nan, else set whichever is nan to 0
        if not isinstance(amount, Decimal) and np.isnan(amount):
            amount = 0

            if not isinstance(other, Decimal) and np.isnan(other):
                return Money(np.NAN)

        elif not isinstance(other, Decimal) and np.isnan(other):
            other = 0

        return Money(amount - other)

    def __rsub__(self, other):
        return (-self).__add__(other)

    def __neg__(self):
        return Money(-self.amount)

    # python 2 support
    def __div__(self, other):
        return self.__truediv__(other)

    def __truediv__(self, other):
        amount = self._amount
        if isinstance(other, Money):
            other = other.amount

        # check if either are nan and return nan
        if not isinstance(amount, Decimal) and np.isnan(amount):
            return Money(np.NAN)
        if not isinstance(other, Decimal) and np.isnan(other):
            return Money(np.NAN)

        if other == 0:
            raise ZeroDivisionError()

        return Money(amount / other)

    def __rtruediv__(self, other):
        return self.__truediv__(other)

    def __floordiv__(self, other):
        amount = self._amount
        if isinstance(other, Money):
            other = other.amount

        # check if either are nan and return nan
        if not isinstance(amount, Decimal) and np.isnan(amount):
            return Money(np.NAN)
        if not isinstance(other, Decimal) and np.isnan(other):
            return Money(np.NAN)

        if other == 0:
            raise ZeroDivisionError()

        return Money(amount // other)

    def __rfloordiv__(self, other):
        return self.__floordiv__(other)

    def __mul__(self, other):
        amount = self._amount
        if isinstance(other, Money):
            other = other.amount

        # check if either are nan and return nan
        if not isinstance(amount, Decimal) and np.isnan(amount):
            return Money(np.NAN)
        if not isinstance(other, Decimal) and np.isnan(other):
            return Money(np.NAN)

        elif not isinstance(other, Decimal) and np.isnan(other):
            return ZeroDivisionError

        return Money(amount * other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __lt__(self, other):
        amount = self._amount
        if isinstance(other, Money):
            other = other.amount

        # check if either are nan and return false
        if not isinstance(amount, Decimal) and np.isnan(amount):
            return False
        if not isinstance(other, Decimal) and np.isnan(other):
            return False

        return amount < other

    def __gt__(self, other):
        amount = self._amount
        if isinstance(other, Money):
            other = other.amount

        # check if either are nan and return false
        if not isinstance(amount, Decimal) and np.isnan(amount):
            return False
        if not isinstance(other, Decimal) and np.isnan(other):
            return False

        return amount > other

    def __eq__(self, other):
        amount = self._amount
        if isinstance(other, Money):
            other = other.amount

        # if both are nan, return True
        if not isinstance(amount, Decimal) and np.isnan(amount):
            if not isinstance(other, Decimal) and np.isnan(other):
                return True

        return amount == other

    @staticmethod
    def quarter_round(x):
        return round(x*4)/4

    @classmethod
    def from_quarters(cls, quarters):
        return cls(quarters/4)

    @classmethod
    def from_oz(cls, oz):
        return cls(cls.quarter_round(oz*1.25))

    @classmethod
    def from_weight(cls, lb_oz):
        lb_oz = lb_oz.strip()
        if lb_oz:
            try:
                weight = list(map(float, lb_oz.split(' ')))
            except ValueError:
                print(lb_oz)
                raise

            try:
                weight = weight[0] * 16 + weight[1]
            except IndexError:
                weight = weight[0]

            return cls.from_oz(weight)
        else:
            return Money(np.NAN)