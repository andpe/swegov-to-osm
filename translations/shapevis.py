
def filterTags(attrs):
    """ Convert some ShapeVIS attributes to OSM. """

    result = {}
    if 'HAALPLTSMN' in attrs:
        result['name'] = attrs['HAALPLTSMN']
        result['bus'] = 'yes'

        # Default
        result['public_transport'] = 'stop_position'
        if 'station' in result['name'].lower() and\
           'centrum' in result['name'].lower():
            result['public_transport'] = 'station'

    return result
