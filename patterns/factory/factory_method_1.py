"""
Factory pattern

Note: Python 3

reference:
Mastering Python Design Patterns
by Sakis Kasampalis
Published by Packt Publishing, 2015
--- virtually unmodified ---

flake8 5/27/2016

"""

import xml.etree.ElementTree as etree
import json


class JSONConnector:
    """  Return factory object for JSON. """
    def __init__(self, filepath):
        self.data = dict()
        with open(filepath, mode='r', encoding='utf-8') as f:
            self.data = json.load(f)

    @property
    def parsed_data(self):
        return self.data


class XMLConnector:
    """  Return factory object for XML. """
    def __init__(self, filepath):
        self.tree = etree.parse(filepath)

    @property
    def parsed_data(self):
        return self.tree


def connection_factory(filepath):
    """  Return connector based on file type.  """
    if filepath.endswith('json'):
        connector = JSONConnector
    elif filepath.endswith('xml'):
        connector = XMLConnector
    else:
        raise ValueError('Cannot connect to {}'.format(filepath))
    return connector(filepath)


def connect_to(filepath):
    """  Attempt to make factory connection.  """
    factory = None
    try:
        factory = connection_factory(filepath)
    except ValueError as value_error:
        print(value_error)
    return factory


def main():
    sqlite_factory = connect_to('data/person.sq3')
    print()

    xml_factory = connect_to('data/person.xml')
    xml_data = xml_factory.parsed_data
    liars = xml_data.findall(".//person[lastName='{}']".format('Liar'))
    print('found: {} persons'.format(len(liars)))
    for liar in liars:
        print('first name: {}'.format(liar.find('firstName').text))
        print('last name: {}'.format(liar.find('lastName').text))
        [print('phone number ({}):'.format(phone.attrib['type']),
            phone.text) for phone in liar.find('phoneNumbers')]
    print()

    json_factory = connect_to('data/donut.json')
    json_data = json_factory.parsed_data
    print('found: {} donuts'.format(len(json_data)))
    for donut in json_data:
        print('name: {}'.format(donut['name']))
        print('price: ${}'.format(donut['ppu']))
        [print('topping: {} {}'.format(topping['id'], topping['type']))
            for topping in donut['topping']]

if __name__ == '__main__':
    main()
