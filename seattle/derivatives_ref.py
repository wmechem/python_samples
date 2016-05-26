'''
4/28 w.mechem

2) Write a Python method that takes a mathematical expression,
and returns an expression that is its first derivative.
The expression may consist of any combination of the variable X, constants,
and the operations multiplication, division, addition, subtraction and power
(power to a constant only).
For example, if the expression is X^3 + X^5, the method returns 3*X^2+5*X^4.
Notes:
Only handles simple expressions.  I.e., X^3 + X^5, 12X^9 / 7X^4, etc.
Will not produce correct results for complex expressions such as
X^3 + X^5 - 12X^9 / 7X^4, etc.  This would require another
level of parsing recursion which I did not implement.
use: python derivatives.py '12x^3/3x^7'

pylint 5/8/2016
pyflakes 5/8/2016
flake8 5/8/2016:
derivatives_ref.py:194:25: E128 continuation line under-indented for visual indent
derivatives_ref.py:194:25: W503 line break before binary operator
pep8 https://www.python.org/dev/peps/pep-0008/
" Following the tradition from mathematics usually results in more readable code:

# Yes: easy to match operators with operands
income = (gross_wages
          + taxable_interest
          + (dividends - qualified_dividends)
          - ira_deduction
          - student_loan_interest)
In Python code, it is permissible to break before or after a binary operator, 
as long as the convention is consistent locally. For new code Knuth's style is suggested."

'''

import re
import sys

OPERATORS = ['+', '-', '*', '/']
EXPONENTIATION_OPERATOR = '^'
VAR = 'X'

EXPRESSION = '12x^13/7x^4'  # default in case no command line argument


try:
    EXPRESSION = str(sys.argv[1])
except IndexError:
    EXPRESSION = EXPRESSION

EXPRESSION = EXPRESSION.upper()


def split_exp(expression=EXPRESSION):
    ''' split expressions and find operator'''

    print expression
    for operator in OPERATORS:
        expressions = expression.split(operator)

        if len(expressions) > 1:

            return expressions, operator


def get_powers():
    ''' get exponents '''

    expression_components, operator = split_exp()
    expressions = []

    for expression in expression_components:
        print expression
        if EXPONENTIATION_OPERATOR in expression:
            expression = tuple(expression.split(EXPONENTIATION_OPERATOR))
            print 'found ^'
            print expression
            expressions.append(expression)

        else:
            # substitute power = 0 here IF EXPONENTIATION_OPERATOR not found
            expression = (expression, 0)
            expressions.append(expression)

    expressions.append(operator)

    return expressions


def addition(expressions, operator):
    ''' find first derivative for addition operation'''

    print "Addition"
    first_derivative = ''
    for expression in expressions[:-1]:
        print 'exp = %s ' % str(expression)
        temp = ''
        expression = (str(expression[0]).strip(), str(expression[1]).strip())

        if len(expression[0]) > 1:
            try:
                coefficient = int(re.sub(r"\D", "", expression[0]))
            except ValueError:
                # no coefficient. Will make it 1 1X = X
                coefficient = 1
            variable = str(re.sub(r"\d", "", expression[0]))
            power = int(expression[1])

            if coefficient != 0:
                power = power * coefficient

            if power == 0:
                temp = str(coefficient)
            else:
                temp = str(power) + variable
            expression = (temp, expression[1])
        else:
            temp = str(int(expression[1]))+str(expression[0])
            expression = (temp, expression[1])

        if power == 0:
            derived_expression = str(expression[0])
        else:
            derived_expression = (
                                  str(expression[0])
                                  + "^"
                                  + str(int(expression[1])-1))

        first_derivative += derived_expression + str(operator)

    first_derivative = first_derivative.rstrip(operator)

    print "First derivative %s" % str(first_derivative)

    return


def subtraction(expressions, operator):
    ''' find first derivative for subtraction operation'''

    print "Subtraction"
    first_derivative = ''
    for expression in expressions[:-1]:
        temp = ''
        expression = (str(expression[0]).strip(), str(expression[1]).strip())

        if len(expression[0]) > 1:
            try:
                coefficient = int(re.sub(r"\D", "", expression[0]))
            except ValueError:
                coefficient = 1
            variable = str(re.sub(r"\d", "", expression[0]))
            power = int(expression[1])
            new_power = int(expression[1]) * coefficient

            if power == 0:
                temp = str(coefficient)
            else:
                temp = str(new_power) + variable
            expression = (temp, expression[1])

        else:
            temp = str(int(expression[1])) + str(expression[0])
            expression = (temp, expression[1])

        if power == 0:
            derived_expression = str(expression[0])
        else:
            derived_expression = (
                                  str(expression[0])
                                  + "^"
                                  + str(int(expression[1])-1))

        first_derivative += derived_expression + str(operator)

    first_derivative = first_derivative.rstrip(operator)

    print "First derivative %s" % str(first_derivative)
    return


def multiplication(expressions):
    ''' find first derivative for multiplication operation'''

    print 'Multiplication'
    first_derivative = ''
    simple_power = 0
    simple_multiplier = 0
    for expression in expressions[:-1]:
        print expression
        left = str(expression[0]).strip()
        right = str(expression[1]).strip()
        if right == '0':
            right = 1
        expression = (left, right)

        if len(expression[0]) > 1:
            print 'expression = %s' % str(expression[0])
            try:
                coefficient = int(re.sub(r"\D", "", expression[0]))
            except ValueError:
                coefficient = 1

            variable = str(re.sub(r"\d", "", expression[0]))
            if simple_multiplier == 0:
                simple_multiplier = coefficient
            else:
                simple_multiplier *= coefficient

        simple_power += int(expression[1])

    first_derivative = (
                        str(int(simple_multiplier)
                        * int(simple_power))
                        + str(variable)
                        + "^"
                        + str(int(simple_power)-1))

    print "First derivative %s" % str(first_derivative)
    return


def division(expressions):
    ''' find first derivative for division operation'''
    print 'Division'
    first_derivative = ''
    expressions = expressions[:-1]
    for i in xrange(len(expressions)):
        expression = expressions[i]
        try:
            coefficient = int(re.sub(r"\D", "", expression[0]))
        except ValueError:
            coefficient = 1

        variable = str(re.sub(r"\d", "", expression[0]))
        power = expression[1]

        if i == 0:
            dividend = int(coefficient)
            add_powers = int(power)

        else:
            quotient = dividend / coefficient  # assumes int not float
            add_powers = add_powers + int(power)

    # first_pass = str(quotient)+str(variable)+"^"+str(add_powers)
    first_derivative = (
                        str(int(quotient)
                        * int(add_powers))
                        + str(variable)
                        + "^"
                        + str(int(add_powers)-1))

    print "First derivative %s" % str(first_derivative)
    return


def process_rules():
    ''' get first derivative based on type of operation '''

    print 'processing rules'
    expressions = get_powers()
    operator = expressions[-1]
    print expressions

    if operator == '+':
        addition(expressions, operator)

    if operator == '-':
        subtraction(expressions, operator)

    if operator == '*':
        multiplication(expressions)

    if operator == '/':
        division(expressions)

if __name__ == "__main__":
    process_rules()
