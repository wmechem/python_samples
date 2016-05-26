# -*- coding: utf-8 -*-
"""
Created on Sun Apr  3 19:59:11 2016

@author: will

Write a method that converts its argument from integer to roman numeral i
f a numeric value is passed, or from roman numeral to an integer
if a roman numeral is passed.

Your solution should rely on the parameter's class to determine its type
and if a non-roman numeral character is passed (i.e. 'M3I',)
the method should raise a BadRomanNumeral exception.

The solution should be a single method that accepts
a single argument and return the converted value.

Additionally, your solution should demonstrate your mastery of
Python's exception handling capabilities.

Include unit tests to verify correct conversion of both types of input,
and verify exception output with bad input.

Convert to and from Roman numerals
Adapted from:

Mark Pilgrim
version 1.4
date  8 August 2001


pylint 5/26/2016
flake8 5/26/2016


"""

import re
import unittest
#Define exceptions


class RomanError(Exception):
    """ Roman error. """
    pass


class OutOfRangeError(RomanError):
    """ Out of range error. """
    pass


class NotIntegerError(RomanError):
    """ Not integer error. """
    pass


class BadRomanNumeralError(RomanError):
    """ Bad Roman numeral error. """
    pass

#Define digit mapping
ROMAN_NUMERAL_MAP = (('M', 1000),
                   ('CM', 900),
                   ('D', 500),
                   ('CD', 400),
                   ('C', 100),
                   ('XC', 90),
                   ('L', 50),
                   ('XL', 40),
                   ('X', 10),
                   ('IX', 9),
                   ('V', 5),
                   ('IV', 4),
                   ('I', 1))


#Define pattern to detect valid Roman numerals
ROMAN_NUMERAL_PATTERN = re.compile("""
    ^                   # beginning of string
    M{0,4}              # thousands - 0 to 4 M's
    (CM|CD|D?C{0,3})    # hundreds - 900 (CM), 400 (CD), 0-300 (0 to 3 C's),
                        #            or 500-800 (D, followed by 0 to 3 C's)
    (XC|XL|L?X{0,3})    # tens - 90 (XC), 40 (XL), 0-30 (0 to 3 X's),
                        #        or 50-80 (L, followed by 0 to 3 X's)
    (IX|IV|V?I{0,3})    # ones - 9 (IX), 4 (IV), 0-3 (0 to 3 I's),
                        #        or 5-8 (V, followed by 0 to 3 I's)
    $                   # end of string
    """, re.VERBOSE)


class SwapRoman(object):
    # pylint: disable=too-few-public-methods
    """ Convert to and from Roman numerals. """
    def __init__(self):
        self.in_string = None
        self.num = None

    def convert(self, in_string=''):
        """ Convert in_string to and from Roman numerals. """
        self.in_string = in_string
        if not self.in_string:
            raise BadRomanNumeralError('Input can not be blank')

        if isinstance(self.in_string, int):
            self.num = in_string
            if not 0 < self.num < 5000:
                raise OutOfRangeError("number out of range (must be 1..4999)")
            if int(self.num) != self.num:
                raise NotIntegerError("decimals can not be converted")

            result = ""
            for numeral, integer in ROMAN_NUMERAL_MAP:
                while self.num >= integer:
                    result += numeral
                    self.num -= integer

            return result
        else:
            if not ROMAN_NUMERAL_PATTERN.search(self.in_string):
                raise BadRomanNumeralError('Invalid Roman numeral: %s'
                    % self.in_string)
            result = 0
            index = 0
            for numeral, integer in ROMAN_NUMERAL_MAP:
                while self.in_string[index:index + len(numeral)] == numeral:
                    result += integer
                    index += len(numeral)
            return result


def test_conversion(test):
    """ Test function.  Create instance and execute method. """
    temp = SwapRoman()
    return temp.convert(test)


class TestToRoman(unittest.TestCase):
    # pylint: disable=R0904
    """ Test from int to Roman assert equal. """

    def setUp(self):
        self.test = 1963
        self.results = 'MCMLXIII'

    def test_converts(self):
        """  Test from int to Roman assert equal.  """
        self.assertEqual(self.results, test_conversion(self.test))


class TestToInteger(unittest.TestCase):
    # pylint: disable=R0904
    """ Test from Roman to int assert equal. """

    def setUp(self):
        self.test = 'MCMLXIII'
        self.results = 1963

    def test_converts(self):
        """ Test from Roman to int assert equal. """
        self.assertEqual(self.results, test_conversion(self.test))


class TestBadRoman(unittest.TestCase):
    # pylint: disable=R0904
    """  Test invalid Roman numeral. """

    def setUp(self):
        self.test = 'MMXM'

    def test_bad_roman(self):
        """  Test invalid Roman numeral. """
        self.assertRaises(BadRomanNumeralError, test_conversion, self.test)


if __name__ == '__main__':
    unittest.main()
