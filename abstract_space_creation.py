from ways.graph import load_map_from_csv
import pickle
from search import make_abstract_junction
from ways.tools import timed, dbopen

@timed
def make_abstract_space(k, m, roads_junctions):
    amount_of_centers = int(len(roads_junctions) * k)
    amount_of_neighbours = int(amount_of_centers * m)
    import csv
    from itertools import islice
    with dbopen('centrality.csv', 'r') as f:
        it = islice(f, 0, amount_of_centers)
        centers = {int(row[0]) for row in csv.reader(it)}

    with dbopen('abstractSpace_{}.pkl'.format(k), 'wb') as f:
        abstract_space = {source: make_abstract_junction(source, roads_junctions, centers, amount_of_neighbours)
                          for source in centers}
        pickle.dump(abstract_space, f)


def make_all_abstract_spaces():
    road_junctions = load_map_from_csv().junctions()
    for k in {0.0025, 0.005, 0.01, 0.05}:
        make_abstract_space(k, 0.1, road_junctions)


if __name__ == '__main__':
    make_all_abstract_spaces()
