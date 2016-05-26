"""
Demo API classes for api_Adapter.py module

"""




class Api_1(object):
    """ API Class """
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return 'api {} '.format(self.name)

    def link(self):
        return 'connected'

    def echo(self):
        return 'ping'

    def slots(self):
        return '10 of 20 available'

    def util(self):
        return '75 pct utilization'

class Api_2(object):
    """ API Class """
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return 'api {} '.format(self.name)

    def pair(self):
        return 'paired'

    def repeat(self):
        return 'ping'

    def avail(self):
        return '12 slots'

    def busy(self):
        return 'Less than 50 pct utilized'


class Api_3(object):
    """ API Class """
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return 'api {} '.format(self.name)

    def chat(self):
        return 'Hello'

    def ack(self):
        return 'ack'

    def mem(self):
        return '126gb available'

    def free(self):
        return '25 pct available'
