'''
This file should be runnable to print map_statistics using 
$ python stats.py
'''

from collections import namedtuple
from collections import Counter
from ways import load_map_from_csv


def map_statistics(roads):
    '''return a dictionary containing the desired information
    You can edit this function as you wish'''

    Stat = namedtuple('Stat', ['max', 'min', 'avg'])

    number_of_links = sum(1 for link in roads.iterlinks())
    number_of_junctions = len(roads.junctions())

    return {
        'Number of junctions': number_of_junctions,
        'Number of links': number_of_links,
        'Outgoing branching factor': Stat(max(len(junction.links) for junction in roads.junctions()),
                                          min(len(junction.links) for junction in roads.junctions()),
                                          sum(len(junction.links) for junction in roads.junctions())
                                          / max(1, number_of_junctions)),
        'Link distance': Stat(max(link.distance for link in roads.iterlinks()),
                              min(link.distance for link in roads.iterlinks()),
                              sum(link.distance for link in roads.iterlinks()) / max(1, number_of_links)),
        'Link type histogram': dict(Counter(link.highway_type for link in roads.iterlinks())),
    }


def print_stats():
    for k, v in map_statistics(load_map_from_csv()).items():
        print('{}: {}'.format(k, v))

        
if __name__ == '__main__':
    from sys import argv
    assert len(argv) == 1
    print_stats()
