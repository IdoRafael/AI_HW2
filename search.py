from heapq import heappop, heappush
from ways.graph import load_map_from_csv, Junction, Link, AbstractLink


class Node:
    def __init__(self, state, parent, cost, parent_link = None, h = 0):
        self.state = state
        self.parent = parent
        self.cost = cost
        self.parent_link = parent_link
        self.h = h

    def __lt__(self, other):
        return self.cost + self.h < other.cost + other.h

    def __eq__(self, other):
        return self.state == other.state

    def __hash__(self):
        return hash(self.state)


def _expand(state, roads_junctions):
    for link in roads_junctions[state].links:
        yield link


def _path(node: Node):
    path = []
    current = node
    while current is not None:
        path.insert(0, current.state)
        current = current.parent
    return path


def _abstract_path(node: None):
    path = node.parent_link if node.parent_link is not None else []
    current = node.parent
    while current is not None:
        if current.parent_link is not None:
            path = current.parent_link + path[1:]
            current = current.parent
        else:
            break

    return path


# From heapq.py, since _siftdown is not meant to be used.
# Used for performance reasons
def _siftdown(heap, start_position, position):
    new_item = heap[position]
    # Follow the path to the root, moving parents down until finding a place
    # newitem fits.
    while position > start_position:
        parent_position = (position - 1) >> 1
        parent = heap[parent_position]
        if new_item < parent:
            heap[position] = parent
            position = parent_position
            continue
        break
    heap[position] = new_item


def _decrease_key(heap, index, new_key):
    heap[index].cost = new_key
    _siftdown(heap, 0, index)


def _a_star_search_aux(source, roads_junctions, result_function, result_item, heuristic_function,
                       cost_function, goal_test, centers=None, target=None, solution_limit=1):
    open_heapq = [Node(source, None, 0, None, heuristic_function(source, target, roads_junctions))]
    open_set = {source}
    closed = dict()
    result_list = []
    num_closed = 0

    while open_heapq:
        next = heappop(open_heapq)
        open_set.discard(next.state)
        closed[next.state] = next
        num_closed += 1

        if goal_test(next, centers, source, target):
            result_list.append(result_item(next))
            if len(result_list) >= solution_limit:
                break
            else:
                continue

        for link in _expand(next.state, roads_junctions):
            new_cost = next.cost + cost_function(link)

            if link.target in open_set:  # A node with state link.target exists in OPEN
                old_node_index = open_heapq.index(Node(link.target, None, None))
                old_node = open_heapq[old_node_index]
                if old_node.cost > new_cost:  # If new parent is better
                    old_node.parent = next
                    old_node.parent_link = link.path if type(link) is AbstractLink else None
                    _decrease_key(open_heapq, old_node_index, new_cost)

            else:  # State not in OPEN. Maybe in CLOSED
                old_node = closed.get(link.target, None)
                if old_node is not None:  # A node with state link.target exists in CLOSED
                    if old_node.cost > new_cost:  # If new parent is better
                        old_node.parent = next
                        old_node.parent_link = link.path if type(link) is AbstractLink else None
                        old_node.cost = new_cost
                        del closed[link.target]
                        heappush(open_heapq, old_node)
                        open_set.add(link.target)
                else:
                    heappush(open_heapq, Node(link.target, next, new_cost,
                                              link.path if type(link) is AbstractLink else None,
                                              heuristic_function(link.target, target, roads_junctions)))
                    open_set.add(link.target)
    return result_function(source, result_list, roads_junctions, closed, num_closed)


def _uniform_cost_search_aux(source, roads_junctions, result_function, result_item, cost_function,
                             goal_test, centers=None, target=None, solution_limit=1):
    def heuristic_function(source, target, roads_junctions):
        return 0

    def result_function_astar(source, result_list, roads_junctions, closed, num_closed):
        return result_function(source, result_list, roads_junctions, closed)

    return _a_star_search_aux(source, roads_junctions, result_function_astar, result_item, heuristic_function,
                              cost_function, goal_test, centers, target, solution_limit)


def uniform_cost_search(source, target, cost_function, roads_junctions):
    def result_item(next):
        return _path(next), next.cost

    def goal_test(next, centers, source, target):
        return next.state == target

    def result_function(source, result_list, roads_junctions, close):
        if len(result_list) > 0:
            return result_list[0][0], len(close), result_list[0][1]
        else:
            return None, len(close), None

    return _uniform_cost_search_aux(
        source, roads_junctions, result_function, result_item, cost_function, goal_test, target=target
    )


def make_abstract_junction(source, roads_junctions, centers, solution_limit):
    def result_item(next):
        return AbstractLink(path=_path(next), target=next.state, cost=next.cost, highway_type=-1)

    def goal_test(next, centers, source, target):
        return next.state in centers and next.state != source

    def result_function(source, result_list, roads_junctions, close):
        return Junction(
            index=source, lat=roads_junctions[source].lat, lon=roads_junctions[source].lon, links=result_list
        )

    def cost_function(link):
        return link.distance

    return _uniform_cost_search_aux(
        source, roads_junctions, result_function, result_item, cost_function,
        goal_test, centers=centers, solution_limit=solution_limit
    )


def find_dataset_neighbour(source, roads_junctions):
    def result_item(next):
        return next.state

    def goal_test(next, centers, source, target):
        return next.cost >= 200

    def result_function(source, result_list, roads_junctions, close):
        if len(result_list) > 0:
            return result_list[0]
        else:
            return None

    def cost_function(link):
        return 1

    return _uniform_cost_search_aux(
        source, roads_junctions, result_function, result_item, cost_function, goal_test
    )


def find_nearest_center(source, centers, roads_junctions):
    def result_item(next):
        return next.state, _path(next), next.cost

    def goal_test(next, centers, source, target):
        return next.state in centers

    def result_function(source, result_list, roads_junctions, close):
        if len(result_list) > 0:
            return result_list[0][0], result_list[0][1], len(close), result_list[0][2]
        else:
            return None, None, len(close), None

    def cost_function(link):
        return link.distance

    return _uniform_cost_search_aux(
        source, roads_junctions, result_function, result_item,
        cost_function, goal_test, centers=centers
    )


def uniform_cost_search_abstract(source, target, cost_function, abstract_map):
    def result_item(next):
        return _abstract_path(next), next.cost

    def goal_test(next, centers, source, target):
        return next.state == target

    def result_function(source, result_list, roads_junctions, close):
        if len(result_list) > 0:
            return result_list[0][0], len(close), result_list[0][1]
        else:
            return None, len(close), None

    return _uniform_cost_search_aux(
        source, abstract_map, result_function, result_item, cost_function, goal_test, target=target
    )


def a_star_search(source, target, cost_function, heuristic_function, roads_junctions):
    def result_item(next):
        return _path(next), next.cost

    def goal_test(next, centers, source, target):
        return next.state == target

    def result_function(source, result_list, roads_junctions, close, num_closed):
        if len(result_list) > 0:
            return result_list[0][0], num_closed, result_list[0][1]
        else:
            return None, num_closed, None

    return _a_star_search_aux(source, roads_junctions, result_function, result_item, heuristic_function,
                              cost_function, goal_test, None, target, 1)


def a_star_search_abstract(source, target, cost_function, heuristic_function, abstract_map):
    def result_item(next):
        return _abstract_path(next), next.cost

    def goal_test(next, centers, source, target):
        return next.state == target

    def result_function(source, result_list, roads_junctions, close, num_closed):
        if len(result_list) > 0:
            return result_list[0][0], num_closed, result_list[0][1]
        else:
            return None, num_closed, None

    return _a_star_search_aux(source, abstract_map, result_function, result_item,
                              heuristic_function, cost_function, goal_test, None, target, 1)

