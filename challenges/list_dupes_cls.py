# -*- coding: utf-8 -*-
"""
Created on Sun Apr  3 18:48:08 2016

@author: will


Write a method that accepts a list argument and efficiently finds and returns
a distinct list of any duplicate numbers in the list.
Include unit tests to verify correct output for a few test lists.

pylint 5/26/2016
flake8 5/26/2016

"""
import unittest


class TestNoAlphaDupesFoundCase1(unittest.TestCase):
    """ Test ignore non numeric. """
    def setUp(self):
        """ Setup test. """
        self.test_list = ['a', .001, 3002, 433, 987, 'alfredo',
            'bard o the night', 'alfredo', 89, .001]
        self.results_list = [.001]

    def test_dupes(self):
        """ Assert equal test """
        self.assertEqual(self.results_list,
            test_find_num_dupes(self.test_list))


class TestNoAlphaDupesFoundCase2(unittest.TestCase):
    """ Test ignore non numeric. """
    def setUp(self):
        """ Setup test. """
        self.test_list = ['a', .001, 3002, 433, 987, 'alfredo',
            'bard o the night', 'alfredo', 89, .001]
        self.results_list = ['alfredo', 'alfredo']

    def test_dupes(self):
        """ Assert NOT equal test """
        self.assertNotEqual(self.results_list,
            test_find_num_dupes(self.test_list))


class FindNumericDupes(object):
    """ Find numeric duplicates in string. """
    def __init__(self):
        self.test_list = None
        self.out_list = []

    def remove_non_numeric(self, test_list):
        """ Remove non numeric characters first. """
        self.out_list = []
        self.test_list = test_list

        for item in self.test_list:
            if isinstance(item, basestring):
                pass
            else:
                self.out_list.append(item)
        return self.out_list

    def find_num_dupes(self, test_list=None):
        """ Find numeric suplicates """
        self.test_list = test_list
        num_list = self.remove_non_numeric(self.test_list)
        dup_set = set([num for num in num_list if num_list.count(num) > 1])
        self.out_list = sorted(list(dup_set))

        return self.out_list


def test_find_num_dupes(test_list):
    """ Create object instance and execute method on test_list. """
    test = FindNumericDupes()
    results = test.find_num_dupes(test_list)
    return results

if __name__ == '__main__':
    unittest.main()
