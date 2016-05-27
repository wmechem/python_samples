"""
Flyweight pattern

Note: Python 3

reference:
Mastering Python Design Patterns
by Sakis Kasampalis
Published by Packt Publishing, 2015

pylint 5/27/2016
flake8 5/27/2016

"""

import random
from enum import Enum

SPECIES = Enum('SpeciesType', 'sapiens neandertalensis denisova')


class Species(object):
    """ Create object to register type in pool """

    pool = dict()

    def __new__(cls, species_type):
        """ Create new object only if not already present. """
        obj = cls.pool.get(species_type, None)
        if not obj:
            obj = object.__new__(cls)
            cls.pool[species_type] = obj
            obj.species_type = species_type
        return obj

    def render(self, age):
        """ Demonstrate using render method. """
        print('create a human of type {} and age {})'.format(self.species_type,
                 age))


def main():
    """ Demo Flyweight pattern renders same objects """
    rnd = random.Random()
    age_min, age_max = 1, 30    # in years
    human_counter = 0

    for _ in range(10):
        human_1 = Species(SPECIES.sapiens)
        human_1.render(rnd.randint(age_min, age_max))
        human_counter += 1

    for _ in range(3):
        human_2 = Species(SPECIES.neandertalensis)
        human_2.render(rnd.randint(age_min, age_max))
        human_counter += 1

    for _ in range(5):
        human_3 = Species(SPECIES.denisova)
        human_3.render(rnd.randint(age_min, age_max))
        human_counter += 1

    print('Humans rendered: {}'.format(human_counter))
    print('Humans actually created: {}'.format(len(Species.pool)))

    human_4 = Species(SPECIES.neandertalensis)
    human_5 = Species(SPECIES.denisova)
    human_6 = Species(SPECIES.sapiens)
    print('{} == {}? {}'.format(id(human_4),
        id(human_5), id(human_4) == id(human_5)))
    print('{} == {}? {}'.format(id(human_5),
        id(human_6), id(human_5) == id(human_6)))

if __name__ == '__main__':
    main()
