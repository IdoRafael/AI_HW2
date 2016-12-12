from ways.graph import current_speed


def expected_time(link):
    if link is None or current_speed(link) == 0:
        raise ValueError('Link is None')
    else:
        current_average_speed = current_speed(link)
        if current_average_speed == 0:
            raise ValueError('Current average speed is 0')
        else:
            return (link.distance / current_average_speed) / 1000
