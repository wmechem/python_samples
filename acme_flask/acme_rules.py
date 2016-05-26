'''
Created on Tue Apr  5 10:07:05 2016

@author: will mechem

module to configure active rules

Validation rules:
1) No wine can ship to New Jersey, Connecticut, Pennsylvania, Massachusetts,
Illinois, Idaho or Oregon
2) Valid zip codes must be 5 or 9 digits
3) Everyone ordering must be 21 or older
4) Email address must be valid
5) The sum of digits in a zip code may not exceed 20 ("90210": 9+0+2+1+0 = 12)



7) *validated in process.processWorkFile()

If the state and zip code of the following record is the same as the
current record, it automatically passes.

pylint 5/8/2016
pyflakes 5/8/2016
flake8
'''


# legal age rule #3
def legal_age():
    ''' minimum age we will sell to '''

    legal_age_min = 21
    return legal_age_min


# rule messages are appended to each imported row as validation errors
def rules_messages():
    ''' list of order validation messages '''

    rules_message_dict = {}

    rules_message_dict['AllowedStates'] = "We do not ship to this state"
    rules_message_dict['InvalidZipCode'] = "Valid zipcodes are 5 or 9 digits"
    rules_message_dict['_Not21'] = "Everyone ordering must be 21 or older"
    rules_message_dict['InvalidEmail'] = "Email address must be valid"

    rules_message_dict['ZipSum'] = "The sum of digits in a zip code \
                                    may not exceed 20"

    rules_message_dict['InvalidNYEmail'] = "Customers from NY may not have \
                                          .net email addresses"

    return rules_message_dict


# rule 5) The sum of digits in a zip code may not exceed 20
# ("90210": 9+0+2+1+0 = 12)
def zip_sum_max():
    ''' maximum sum of digits in zipcode '''
    return 20


# rule 1) No wine can ship to New Jersey, Connecticut,
# Pennsylvania, Massachusetts, Illinois, Idaho or Oregon
def banned_states():
    ''' list banned states '''
    do_not_ship = [('new jersey', 'nj'),
                   ('connecticut', 'ct'),
                   ('pennsylvania', 'pa'),
                   ('massachusetts', 'ma'),
                   ('illinois', 'il'),
                   ('idaho', 'id'),
                   ('oregon', 'or')]

    return do_not_ship


def active_rules_list():
    ''' list active rules '''
    active_rules = [
    'checkStates',
    'checkZipLength',
    'checkAge',
    'checkValidEmail',
    'checkZipSum'
    ]
    return active_rules
