from algorithms import base_with_information_and_already_loaded,\
    bw_with_information_and_already_loaded, a_star_with_information_and_already_loaded,\
    a_star_exp3_with_information_and_already_loaded
from ways.tools import dbopen
import pickle
from ways.graph import load_map_from_csv
from ways.tools import timed


def base_experiment(i, j, roads_junctions):
    path, num_closed, cost = base_with_information_and_already_loaded(
        i, j, roads_junctions)
    return num_closed, cost


def bw_experiment(i, j, abstract_map, roads_junctions):
    path, num_closed, cost = bw_with_information_and_already_loaded(
        i, j, abstract_map, roads_junctions)
    return num_closed, cost

def a_star_experiment(i, j, roads_junctions):
    path, num_closed, cost = a_star_with_information_and_already_loaded(
        i, j, roads_junctions)
    return num_closed, cost

def a_star_exp3_experiment(i, j, abstract_map, roads_junctions):
    path, num_closed, cost = a_star_exp3_with_information_and_already_loaded(
        i, j, abstract_map, roads_junctions)
    return num_closed, cost


@timed
def create_experiment_csv():
    roads_junctions = load_map_from_csv().junctions()
    K = [0.0025, 0.005, 0.01, 0.05]
    abstract_map_name = {k: 'abstractSpace_{}.pkl'.format(k) for k in K}
    import csv
    with dbopen('dataSet.csv', 'rt') as f:
        dataset = [(int(row[0]), int(row[1])) for row in csv.reader(f)]

    line = {}
    for i, j in dataset:
        num_closed, cost = base_experiment(i, j, roads_junctions)
        line[i, j] = [i, j, num_closed, cost]

    for k in K:
        with dbopen(abstract_map_name[k], 'rb') as f:
            abstract_map = pickle.load(f)
        for i, j in dataset:
            num_closed, cost = bw_experiment(i, j, abstract_map, roads_junctions)
            line[i, j] += [num_closed, cost]

    with dbopen('experiment.csv', 'wt') as f:
        for i, j in dataset:
            f.write((','.join(map(str, line[i, j])) + '\n'))


@timed
def create_experiment2_csv():
    roads_junctions = load_map_from_csv().junctions()
    K = [0.0025, 0.005, 0.01, 0.05]
    abstract_map_name = {k: 'abstractSpace_{}.pkl'.format(k) for k in K}
    import csv
    with dbopen('dataSet.csv', 'rt') as f:
        dataset = [(int(row[0]), int(row[1])) for row in csv.reader(f)]

    line = {}
    for i, j in dataset:
        num_closed, cost = base_experiment(i, j, roads_junctions)
        line[i, j] = [i, j, num_closed, cost]
        num_closed, cost = a_star_experiment(i, j, roads_junctions)
        line[i, j] += [num_closed, cost]

    for k in K:
        with dbopen(abstract_map_name[k], 'rb') as f:
            abstract_map = pickle.load(f)
        for i, j in dataset:
            num_closed, cost = bw_experiment(i, j, abstract_map, roads_junctions)
            line[i, j] += [num_closed, cost]
            num_closed, cost = a_star_exp3_experiment(i, j, abstract_map, roads_junctions)
            line[i, j] += [num_closed, cost]

    with dbopen('experiment2.csv', 'wt') as f:
        for i, j in dataset:
            f.write((','.join(map(str, line[i, j])) + '\n'))


if __name__ == '__main__':
    create_experiment_csv()
    create_experiment2_csv()
