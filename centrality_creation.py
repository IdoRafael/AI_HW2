from ways.graph import load_map_from_csv
from ways import tools
import random
from ways.tools import dbopen

@tools.timed
def create_centrality_csv(paths_number: int):
    roads = load_map_from_csv().junctions()
    random.seed()
    lines = [[i, 0] for i in range(0, len(roads))]

    for i in range(0, paths_number):
        random_path(0.99, roads, lines)

    #sort lines by centrality column

    from operator import itemgetter
    lines.sort(key=itemgetter(1), reverse=True)

    #write to file
    with dbopen('centrality.csv', 'w') as f:
        for line in lines:
            f.write((','.join(map(str, line)) + '\n'))


def random_path(p, roads, lines):
    #generate random junction from roads
    current_junction = random.choice(roads)
    current_index = current_junction.index
    lines[current_index][1] += 1

    # update lines with new junction visit
    while random.uniform(0, 1) <= p:
        try:
            # choose random neighbour of current junction
            current_index = random.choice(current_junction.links).target
            current_junction = roads[current_index]

            # update lines with new junction visit
            lines[current_index][1] += 1
        except IndexError:
            # if none exists finish
            break


if __name__ == '__main__':
    create_centrality_csv(500000)
