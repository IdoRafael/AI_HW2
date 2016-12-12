from ways.graph import current_speed


def expected_time(link):
    if link is None or link.distance == 0:
        raise ValueError('Link is None or distance == 0')
    else:
        return 1000 * current_speed(link) / link.distance
