""" Template pattern
Reference:
Adapted from:
Mastering Python Design Patterns
by Sakis Kasampalis
Published by Packt Publishing, 2015


pylint 6/7/2016
flake8 6/7/2016

"""


class Template(object):
    """ Create class instance with template methods. """

    def __init__(self, msg=None):
        self.msg = msg
        self.altered_msg = None

    def dots_style(self, msg):
        """ Print 10 dots (.) before and after words. """
        self.altered_msg = msg.capitalize()
        self.altered_msg = '.' * 10 + self.altered_msg + '.' * 10
        return self.altered_msg

    def admire_style(self, msg):
        """ Print '!' between letters. """
        self.altered_msg = msg.upper()
        return '!'.join(self.altered_msg)

    def generate_banner(self, style=dots_style):
        """ Print before and after start of banner text. """
        print('-- start of banner --')
        print(style(self.msg))
        print('-- end of banner --\n\n')


def main():
    """ Cycle through each template. """
    msg = 'Happy Coding'
    banner = Template(msg)

    output = [banner.generate_banner(style) for style in (banner.dots_style,
                                                          banner.admire_style)]
    print(output)

if __name__ == '__main__':
    main()
