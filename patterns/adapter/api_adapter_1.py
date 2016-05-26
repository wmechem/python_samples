""" Adapter pattern
reference:
Mastering Python Design Patterns
by Sakis Kasampalis
Published by Packt Publishing, 2015


pylint 5/26/2016
flake8 5/26/2016

"""

from apis import Api_1, Api_2, Api_3


class Adapter(object):
    """ Provide Adapter dictionary for methods.  """
    def __init__(self, obj, adapted_methods):
        self.obj = obj
        self.__dict__.update(adapted_methods)

    def __str__(self):
        return str(self.obj)


def demo(mapping):
    """ Demonstrate calls to individual APIs. """
    for api in mapping:
        print('{} {}'.format(str(api), api.connect()))
        print('{} {}'.format(str(api), api.ping()))
        print('{} {}'.format(str(api), api.capacity()))
        print('{} {}'.format(str(api), api.utilization()))


def main():
    """ Map standard API methods to APIs individual methods.  """
    mapping = []
    api1 = Api_1('Unix')
    mapping.append(Adapter(api1, dict(connect=api1.link, ping=api1.echo,
        capacity=api1.slots, utilization=api1.util)))

    api2 = Api_2('Linux')
    mapping.append(Adapter(api2, dict(connect=api2.pair, ping=api2.repeat,
        capacity=api2.avail, utilization=api2.busy)))

    api3 = Api_3('OSX')
    mapping.append(Adapter(api3, dict(connect=api3.chat, ping=api3.ack,
        capacity=api3.mem, utilization=api3.free)))

    demo(mapping)


if __name__ == "__main__":
    main()
