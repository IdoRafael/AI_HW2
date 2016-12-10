from ways.graph import load_map_from_csv
from random import choice
from uniform_cost_search import find_dataset_neighbour
from ways.tools import dbopen


def create_dataset():
    dataset_size = 20
    roads_junctions = load_map_from_csv().junctions()

    dataset = set()
    havent_checked_yet = set(j.index for j in roads_junctions)

    while len(dataset) < dataset_size and len(havent_checked_yet) > 0:
        current = choice(tuple(havent_checked_yet))
        havent_checked_yet.remove(current)
        result = find_dataset_neighbour(current, roads_junctions)
        if result is None:
            continue
        dataset.add((current, result))
    return dataset


def create_dataset_csv():
    dataset = create_dataset()

    with dbopen('dataSet.csv', 'w') as f:
        for i, j in dataset:
            f.write('{},{}'.format(i, j) + '\n')


if __name__ == '__main__':
    create_dataset_csv()
