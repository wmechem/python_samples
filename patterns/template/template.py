""" Template pattern
reference:
Mastering Python Design Patterns
by Sakis Kasampalis
Published by Packt Publishing, 2015


pylint 6/7/2016
flake8 6/7/2016

"""

def dots_style(msg):
    """ Print 10 dots (.) before and after words. """
    msg = msg.capitalize()
    msg = '.' * 10 + msg + '.' * 10
    return msg

def admire_style(msg):
    """ Print '!' between words. """
    msg = msg.upper()
    return '!'.join(msg)

def generate_banner(msg, style=dots_style):
    """ Print before and after start of banner text. """
    print('-- start of banner --')
    print(style(msg))
    print('-- end of banner --\n\n')

def main():
    """ Cycle through each template. """
    msg = 'happy coding'
    [generate_banner(msg, style) for style in (dots_style, admire_style)]

if __name__ == '__main__':
    main()
