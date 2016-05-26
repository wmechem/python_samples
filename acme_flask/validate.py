"""
Created on Tue Apr  5 10:07:05 2016

@author: will mechem

module that processes validation rules

pylint 9.72/10 2016/05/14
(Catching too general exception Exception (broad-except)
flake8 2016/05/14 continuation line over-indented for hanging indent
"""
import unittest

from datetime import datetime, date

from dateutil.relativedelta import relativedelta

from acme_rules import \
            banned_states, \
            active_rules_list, \
            rules_messages, \
            zip_sum_max, \
            legal_age

BANNED_STATES = banned_states()

ACTIVE = active_rules_list()

RULES_MESSAGES = rules_messages()

ZIP_SUM_MAX = zip_sum_max()

LEGAL_AGE_MIN = legal_age()


def parse_row(row):
    """ Parse row into component variables """

    order_id, name, email, state, zipcode, birthday, \
        valid_flag, validation_errors = row

    return order_id, name, email, state, zipcode, birthday, \
        valid_flag, validation_errors


def validate_order(row):
    """ Process validation rules from ACTIVE_RULES. """

    try:
        results = {}
        # receives row from process.processWorkFile()

        valid_flag = 'true'

        # process rules that are included in ACTIVE_RULES list in rule module
        for key_, func_ in ACTIVE_RULES:
            print key_
            v_flag, results[key_] = func_(row)

            # set valid_flag to false if errors returned from rule and
            # not already 'false'
            if valid_flag == 'true':
                valid_flag = v_flag

        validation_errors = results  # dict
        validation_errors = str(validation_errors)

        row[6] = valid_flag
        row[7] = validation_errors

        print row
        return row

    except Exception as error:
        results = "Error validating order %s " % str(error)
        return results


def check_age(row):
    """ Ensure birthday indicates purchaser is at least LEGAL_AGE. """

    data = parse_row(row)
    birthday = data[5]

    # Ex: datetime.strptime('Jun 1, 2005 ', '%b %d, %Y')
    # Ex: birthday = Feb 27, 1963
    try:
        today = date.today()
        born = datetime.strptime(birthday, '%b %d, %Y')
        age = relativedelta(today, born)
        years = age.years

        if years < LEGAL_AGE_MIN:
            valid_flag = 'false'
            validation_error = {'Not21': RULES_MESSAGES['Not21']}

            return valid_flag, validation_error

        else:
            valid_flag = 'true'
            validation_error = None

            return valid_flag, validation_error

    except Exception as error:

        valid_flag = 'false'
        validation_error = "Error checking age: %s " % str(error)

        return valid_flag, validation_error


def check_states(row):
    """ Check state not in BANNED_STATES. """

    data = parse_row(row)
    state = data[3]

    try:
        for state_, abbr in BANNED_STATES:
            if state.lower() == state_ or state.lower() == abbr:
                valid_flag = 'false'
                validation_error = (
                    {'AllowedStates': RULES_MESSAGES['AllowedStates']})

                return valid_flag, validation_error

            else:
                valid_flag = 'true'
                validation_error = None

                return valid_flag, validation_error

    except Exception as error:

        valid_flag = 'false'
        validation_error = "Error checking state: %s " % str(error)
        return valid_flag, validation_error


def check_zip_length(row):
    """ Check length of zipcode is 5 (+ 4) digits. """
    data = parse_row(row)
    zipcode = data[4]

    try:
        zip_parts = zipcode.split('-')  # split if 5 + 4 zip format

        if len(zip_parts[0]) != 5:
            valid_flag = 'false'
            validation_error = (
                {'InvalidZipCode': RULES_MESSAGES['InvalidZipCode']})

            return valid_flag, validation_error

        else:
            if len(zip_parts) > 1:
                print len(zip_parts)
                if len(zip_parts[1]) != 4:
                    print len(zip_parts[1])
                    valid_flag = 'false'
                    validation_error = (
                        {'InvalidZipCode': RULES_MESSAGES['InvalidZipCode']})

                    return valid_flag, validation_error

        valid_flag = 'true'
        validation_error = None

        return valid_flag, validation_error

    except Exception as error:

        valid_flag = 'false'
        validation_error = "Error checking zipcode length: %s " % str(error)
        return valid_flag, validation_error


def check_zip_sum(row):
    """ Check sum of 5 (+4) zipcode digits is not greater than ZIP_SUM_MAX. """

    zip_sum = 0
    data = parse_row(row)
    zipcode = data[4]

    try:
        zipcode = zipcode.replace("-", "")
        for digit in zipcode:
            zip_sum += int(digit)

        if zip_sum > ZIP_SUM_MAX:
            valid_flag = 'false'
            validation_error = {'ZipSum': RULES_MESSAGES['ZipSum']}

            return valid_flag, validation_error

        else:
            valid_flag = 'true'
            validation_error = None

            return valid_flag, validation_error

    except Exception as error:

        valid_flag = 'false'
        validation_error = "Error checking zipcode sum: %s " % str(error)
        return valid_flag, validation_error


def check_valid_email(row):
    """ Check name is at least two characters and tld is
    at least two character and if state is NY then tld is not '.net'. """
    data = parse_row(row)
    email = data[2]
    state = data[3]
    # test tld >1 char
    try:
        email_parts = email.split(".")
        name = email_parts[0].split("@")

        if len(email_parts) < 2:
            # no tld (.com etc.)

            valid_flag = 'false'
            validation_error = {'InvalidEmail': RULES_MESSAGES['InvalidEmail']}

            return valid_flag, validation_error

        elif len(email_parts[-1]) < 2:
            # tld too short must be at least two characters for a country

            valid_flag = 'false'
            validation_error = {'InvalidEmail': RULES_MESSAGES['InvalidEmail']}

            return valid_flag, validation_error

        elif len(name) < 2:
            # no name i.e., wmechem @

            valid_flag = 'false'
            validation_error = (
                {'InvalidEmail': RULES_MESSAGES['InvalidEmail']})

            return valid_flag, validation_error

        elif (state.lower() == 'ny' or state.lower() == 'new york') and (
                email_parts[-1] == 'net'):

            valid_flag = 'false'
            validation_error = (
                {'InvalidNYEmail': RULES_MESSAGES['InvalidNYEmail']})

            return valid_flag, validation_error

        else:
            valid_flag = 'true'
            validation_error = None

            return valid_flag, validation_error

    except Exception as error:

        valid_flag = 'false'
        validation_error = "Error checking valid email: %s " % str(error)
        return valid_flag, validation_error

#RULES here to not throw error for missing function in rules module
RULES = [
    ('check_states', check_states),
    ('check_zip_length', check_zip_length),
    ('check_age', check_age),
    ('check_valid_email', check_valid_email),
    ('check_zip_sum', check_zip_sum)
    ]

ACTIVE_RULES = [(key, func) for key, func in RULES for rule in ACTIVE if (
    key == rule)]


#tests
class TestCheckAgeNot21(unittest.TestCase):
    """ Unittest """
    # pylint: disable=R0904
    def setUp(self):
        """ setup test """
        self.results = ('false', {'Not21': RULES_MESSAGES['Not21']})
        self.row = '3572', 'Davis Walters', 'euismod@sit.edu', 'PA', \
            '67102', 'Mar 21, 2012', 'false', 'not validated'

    def test_age(self):
        """ test """
        self.assertEqual(self.results, check_age(self.row))


class TestCheckAge21(unittest.TestCase):
    """ Unittest """
    # pylint: disable=R0904
    def setUp(self):
        """ setup test """
        self.results = ('true', None)
        self.row = '3572', 'Davis Walters', 'euismod@sit.edu', 'PA', \
            '67102', 'Mar 21, 1976', 'false', 'not validated'

    def test_age(self):
        """ test """
        self.assertEqual(self.results, check_age(self.row))


class TestCheckStatesNotOK(unittest.TestCase):
    """ Unittest """
    # pylint: disable=R0904
    def setUp(self):
        """ setup test """
        self.results = (
            'false', {'AllowedStates': RULES_MESSAGES['AllowedStates']})
        self.row = '3572', 'Davis Walters', 'euismod@sit.edu', 'NJ', \
            '67102', 'Mar 21, 2012', 'false', 'not validated'

    def test_state(self):
        """ test """
        self.assertEqual(self.results, check_states(self.row))


class TestCheckStatesOK(unittest.TestCase):
    """ Unittest """
    # pylint: disable=R0904
    def setUp(self):
        """ setup test """
        self.results = ('true', None)
        self.row = '3572', 'Davis Walters', 'euismod@sit.edu', 'OH', \
            '67102', 'Mar 21, 1976', 'false', 'not validated'

    def test_state(self):
        """ test """
        self.assertEqual(self.results, check_states(self.row))


class TestCheckZipLengthNotOk(unittest.TestCase):
    """ Unittest """
    # pylint: disable=R0904
    def setUp(self):
        """ setup test """
        self.results = (
            'false', {'InvalidZipCode': RULES_MESSAGES['InvalidZipCode']})
        self.row = '3572', 'Davis Walters', 'euismod@sit.edu', 'NJ', \
            '671026', 'Mar 21, 2012', 'false', 'not validated'

    def test_state(self):
        """ test """
        self.assertEqual(self.results, check_zip_length(self.row))


class TestCheckZipLengthOK(unittest.TestCase):
    """ Unittest """
    # pylint: disable=R0904
    def setUp(self):
        """ setup test """
        self.results = ('true', None)
        self.row = '3572', 'Davis Walters', 'euismod@sit.edu', 'OH', \
            '67102', 'Mar 21, 1976', 'false', 'not validated'

    def test_state(self):
        """ test """
        self.assertEqual(self.results, check_zip_length(self.row))


class TestCheckZipSumNotOK(unittest.TestCase):
    """ Unittest """
    # pylint: disable=R0904
    def setUp(self):
        """ setup test """
        self.results = ('false', {'ZipSum': RULES_MESSAGES['ZipSum']})
        self.row = '3572', 'Davis Walters', 'euismod@sit.edu', 'NJ', \
            '99999-9999', 'Mar 21, 2012', 'false', 'not validated'

    def test_state(self):
        """ test """
        self.assertEqual(self.results, check_zip_sum(self.row))


class TestCheckZipSumOK(unittest.TestCase):
    """ Unittest """
    # pylint: disable=R0904
    def setUp(self):
        """ setup test """
        self.results = ('true', None)
        self.row = '3572', 'Davis Walters', 'euismod@sit.edu', 'OH', \
            '67102', 'Mar 21, 1976', 'false', 'not validated'

    def test_state(self):
        """ test """
        self.assertEqual(self.results, check_zip_sum(self.row))


class TestCheckValidEmailTldNotOK(unittest.TestCase):
    """ Unittest """
    # pylint: disable=R0904
    def setUp(self):
        """ setup test """
        self.results = (
            'false', {'InvalidEmail': RULES_MESSAGES['InvalidEmail']})
        self.row = '3572', 'Davis Walters', 'euismod@sit.x', 'NJ', \
            '99999-9999', 'Mar 21, 2012', 'false', 'not validated'

    def test_state(self):
        """ test """
        self.assertEqual(self.results, check_valid_email(self.row))


class TestCheckValidEmailNameNotOK(unittest.TestCase):
    """ Unittest """
    # pylint: disable=R0904
    def setUp(self):
        """ setup test """
        self.results = (
            'false', {'InvalidEmail': RULES_MESSAGES['InvalidEmail']})
        self.row = '3572', 'Davis Walters', 'sit.edu', 'NJ', \
            '99999-9999', 'Mar 21, 2012', 'false', 'not validated'

    def test_state(self):
        """ test """
        self.assertEqual(self.results, check_valid_email(self.row))


class TestCheckValidEmailNYnetNotOK(unittest.TestCase):
    """ Unittest """
    # pylint: disable=R0904
    def setUp(self):
        """ setup test """
        self.results = (
            'false', {'InvalidNYEmail': RULES_MESSAGES['InvalidNYEmail']})
        self.row = '3572', 'Davis Walters', 'sally@sit.net', 'NY', \
            '99999-9999', 'Mar 21, 2012', 'false', 'not validated'

    def test_state(self):
        """ test """
        self.assertEqual(self.results, check_valid_email(self.row))


class TestCheckValidEmailOK(unittest.TestCase):
    """ Unittest """
    # pylint: disable=R0904
    def setUp(self):
        """ setup test """
        self.results = ('true', None)
        self.row = '3572', 'Davis Walters', 'euismod@sit.edu', 'OH', \
            '67102', 'Mar 21, 1976', 'false', 'not validated'

    def test_state(self):
        """ test """
        self.assertEqual(self.results, check_valid_email(self.row))


if __name__ == '__main__':
    unittest.main()
