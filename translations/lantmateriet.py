
def filterTags(attrs):
    res = {}

    if 'NAMN' in attrs:
        res['name'] = attrs['NAMN']

    if 'TATNR' in attrs:
        res['ref:se:scb'] = attrs['TATNR']

    if attrs.get('BEF') is not None:
        bef = int(attrs.get('BEF'))

        # This is an approximation based on http://wiki.openstreetmap.org/wiki/Key:place
        # and the observed values of nodes in OpenStreetMap itself for cities and towns
        # aroudn Sweden.

        # This seems to be around where OSM sets city status for Sweden
        if bef >= 30000:
            res['place'] = 'city'
        elif bef >= 6000:
            res['place'] = 'town'
        elif bef >= 200:
            res['place'] = 'village'

    return res
