# -*- coding: utf-8 -*-
"""
Created on Sun Apr  3 17:59:22 2016

@author: will

Write a method which will remove any given character from a target string.
Don't use the String.replace() method in your solution.
If the given character is not found in the target string,
your method should raise a CharacterNotFound exception.

#example
test = removeCharacter()
test_char = 'q'
target_string = 'quitters never win and winners never quite quit'
results = test.rmchar(test_char,target_string)
print results # >> 'uitters never win and winners never uite uit'

pylint 5/26/2016
flake8 5/26/2016

"""


class CharacterNotFound(Exception):
    """ Raise error on character not found """
    pass


class RemoveCharacter(object):
    """ Remove specified character from string. """
    def __init__(self):
        self.target_string = None
        self.test_char = None
        self.interim_list = None
        self.out_string = None

    def rmchar(self, test_char='', target_string=''):
        """ Remove a given character 'char' from 'target_string'.
        First test target string is basestring type.
        Could convert to string but that would introduce assumptions
        """
        self.target_string = target_string
        self.test_char = test_char
        try:

            test_string = isinstance(self.target_string, basestring)
            if not test_string:
                raise ValueError

        except ValueError:
            print "Input string is wrong type: %s - try quotes " % str(
                type(target_string))

            return

        try:  # test char exists in target string
            exists = self.target_string.find(self.test_char)
            if exists == -1:
                raise CharacterNotFound

        except CharacterNotFound:
            print "Chracter not found in target string"
            return

        try:
            self.interim_list = self.target_string.split(self.test_char)
            self.out_string = ''.join(self.interim_list)
            return self.out_string

        except Exception as error:
            print "Another error occured: %s" % str(error)
            return
