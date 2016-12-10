'''
 A set of utilities for using israel.csv 
 The map is extracted from the openstreetmap project
'''

from collections import namedtuple
from ways import tools
from ways import info
import sys


# define class Link
Link = namedtuple('Link',
       ['source', 'target',  #  int (junction indices)
        'distance',          #  int (in meters. You may change distance to KM units if you wish)
        'highway_type',      #  int < len(road_info.ROAD_TYPES)
       ])

# define class AbstractLink
AbstractLink = namedtuple('AbstractLink',
       ['path',     #    list or tuple of ints - the path to the target in the full graph
       #    PLEASE INCLUDE SOURCE AND TARGET JUNCTIONS IN THE PATH
       'target',  #  int
        'cost',          #  float - cost of path
        'highway_type',      #  Should ALWAYS be -1
       ])

# define class Junction
Junction = namedtuple('Junction',
           ['index',       #  int
            'lat', 'lon',  #  floats: latitude/longitude
            'links',       #  list of Link or AbstractLink
           ])


class Roads(dict):
    '''The graph is a dictionary Junction_id->Junction, with some methods to help.
    To change the generation, simply assign to it:
    g.generation = 5
    '''
    def junctions(self):
        return list(self.values())
    
    def __init__(self, junction_list):
        super(Roads, self).__init__(junction_list)
        'to change the generation, simply assign to it'
        self.generation = 0
                    
    def iterlinks(self):
        '''chain all the links in the graph. 
        use: for link in roads.iterlinks(): ... '''
        return (link for j in self.values() for link in j.links)

def _make_link(i,link_string):
    'This function is for local use only'
    types = [int, float, int]
    link_params = [_type(x) for _type,x in zip(types,link_string.split("@"))]
    return Link(i,*link_params)

def _make_junction(i_str, lat_str, lon_str, *link_row):
    'This function is for local use only'
    i, lat, lon = int(i_str), float(lat_str), float(lon_str)
    try:
        links = list(_make_link(i,lnk)
                 for lnk in link_row if not lnk=='')
        links = list(filter(lambda lnk: lnk.distance>0,links))
    except ValueError:
        links = []
    return Junction(i, lat, lon, links)

def daily_average_speed(link):
    return sum(info.SPEED_RANGES[link.highway_type])/2
               
def current_speed(link):
    lnk_speed = info.SPEED_RANGES[link.highway_type]
    return (tools.dhash(link)/0xffffffff)*(lnk_speed[1]-lnk_speed[0]) + lnk_speed[0]

@tools.timed
def load_map_from_csv(filename='tlv.csv', start=0, count=sys.maxsize):
    '''returns graph, encoded as an adjacency list
    @param slice_params can be used to cut part of the file
    example: load_map_from_csv(start=50000, count=50000))
    '''

    import csv
    from itertools import islice
    with tools.dbopen(filename, 'rt') as f:
        it = islice(f, start, min(start+count, sys.maxsize))
        lst = {int(row[0]):_make_junction(*row) for row in csv.reader(it)}
        if count < sys.maxsize:
            lst = {i:Junction(i, j.lat, j.lon, tuple(lnk for lnk in j.links if lnk.target in lst))
                              for i, j in lst.items()} 
    return Roads(lst)