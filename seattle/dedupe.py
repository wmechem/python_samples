'''
3) Write a Python method that takes a string S, and returns a string
containing the characters in S with duplicates removed.
For example, if it gets 'ABA%%3', it should return 'AB%3'. *

Usage: python dedupe.py 'thestringtotest'
returns 'thesringo'

pylint 05/08/2016
pyflakes 5/8/2016
pep8 5/8/2016
flake8 5/8/2016

'''


import sys

try:
    IN_STRING = sys.argv[1]
except IndexError:
    IN_STRING = IN_STRING


IN_STRING = 'ABA%%3'  # default in case no command line argument


def dedupe_string(in_string):
    ''' main function to remove duplicates and return result '''
    in_string = in_string
    result = []
    for char in in_string:
        if char not in result:
            result.append(char)

    new_string = ''.join(result)

    return new_string


if __name__ == '__main__':

    OUT_STRING = dedupe_string(IN_STRING)
    print OUT_STRING
