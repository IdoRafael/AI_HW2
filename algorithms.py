from ways.graph import load_map_from_csv
from search import uniform_cost_search, find_nearest_center,\
    uniform_cost_search_abstract, a_star_search, a_star_search_abstract
from ways.tools import compute_distance


def find_nearest_center_by_air(target, roads_junctions, centers):
    target_junction = roads_junctions[target]
    centers_with_distance = {(junc,
                              compute_distance(roads_junctions[junc].lat, roads_junctions[junc].lon,
                                               target_junction.lat, target_junction.lon))
                             for junc in centers}
    try:
        junc, distance = min(centers_with_distance, key=lambda t: t[1])
    except (ValueError, TypeError):
        return None
    return junc


def base_with_information_and_already_loaded(source, target, roads_junctions):
    # returns (path, number_closed, cost).
    # if no path found, returns (None, number_closed, None)
    return uniform_cost_search(source, target, lambda link: link.distance, roads_junctions)


def base_with_information(source, target):
    roads_junctions = load_map_from_csv().junctions()
    return base_with_information_and_already_loaded(source, target, roads_junctions)


def bw_with_information_and_already_loaded(source, target, abstractMap, roads_junctions):
    centers = {key for key, value in abstractMap.items()}
    closed_a, closed_b, closed_c = 0, 0, 0

    junc1, path_a, closed_a, cost_a = find_nearest_center(source, centers, roads_junctions)
    if junc1 is not None:
        # b:
        junc2 = find_nearest_center_by_air(target, roads_junctions, centers)
        if junc2 is not None:
            path_b, closed_b, cost_b = uniform_cost_search(
                junc2, target, lambda link: link.distance, roads_junctions)
            # c:
            if path_b is not None:
                path_c, closed_c, cost_c = uniform_cost_search_abstract(
                    junc1, junc2, lambda link: link.cost, abstractMap)
                # d:
                if path_c is not None:
                    return path_a + path_c[1:] + path_b[1:], \
                           closed_a + closed_b + closed_c, \
                           cost_a + cost_b + cost_c

    # e: if something failed:
    path, closed, cost = uniform_cost_search(
        source, target, lambda link: link.distance, roads_junctions)
    previous_closed = {closed_a, closed_b, closed_c}
    return path, closed + sum(i for i in previous_closed if i is not None), cost


def better_waze_with_information(source, target, abstractMap):
    roads_junctions = load_map_from_csv().junctions()
    return bw_with_information_and_already_loaded(source, target, abstractMap, roads_junctions)


def _heuristic_aerial_distance(source, target, roads_junctions):
    j0 = roads_junctions[source]
    j1 = roads_junctions[target]
    return compute_distance(j0.lat, j0.lon, j1.lat, j1.lon) * 1000


def a_star_with_information_and_already_loaded(source, target, roads_junctions):
    # returns (path, number_closed, cost).
    # if no path found, returns (None, number_closed, None)
    return a_star_search(source, target, lambda link: link.distance,
                         _heuristic_aerial_distance, roads_junctions)


def a_star_with_information(source, target):
    roads_junctions = load_map_from_csv().junctions()
    return a_star_with_information_and_already_loaded(source, target, roads_junctions)


def a_star_exp3_with_information_and_already_loaded(source, target, abstractMap, roads_junctions):
    centers = {key for key, value in abstractMap.items()}
    closed_a, closed_b, closed_c = 0, 0, 0

    junc1 = find_nearest_center_by_air(source, roads_junctions, centers)
    if junc1 is not None:
        path_a, closed_a, cost_a = a_star_search(source, junc1, lambda link: link.distance,
                                                 _heuristic_aerial_distance, roads_junctions)
        if path_a is not None:
            # b:
            junc2 = find_nearest_center_by_air(target, roads_junctions, centers)
            if junc2 is not None:
                path_b, closed_b, cost_b = a_star_search(junc2, target, lambda link: link.distance,
                                                         _heuristic_aerial_distance, roads_junctions)
                # c:
                if path_b is not None:
                    path_c, closed_c, cost_c = a_star_search_abstract(
                        junc1, junc2, lambda link: link.cost, _heuristic_aerial_distance, abstractMap)
                    # d:
                    if path_c is not None:
                        return path_a + path_c[1:] + path_b[1:], \
                               closed_a + closed_b + closed_c, \
                               cost_a + cost_b + cost_c

    # e: if something failed:
    path, closed, cost = a_star_search(
        source, target, lambda link: link.distance, _heuristic_aerial_distance, roads_junctions)
    previous_closed = {closed_a, closed_b, closed_c}
    return path, closed + sum(i for i in previous_closed if i is not None), cost


def a_star_exp3_with_information(source, target, abstractMap):
    roads_junctions = load_map_from_csv().junctions()
    return a_star_exp3_with_information_and_already_loaded(source, target, abstractMap, roads_junctions)


