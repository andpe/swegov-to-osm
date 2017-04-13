""" Translation file for SCB data about municipal and county boundaries. """


def countyToLetter(countyCode):
    countyMap = {
        1: 'A',
        24: 'AC',
        25: 'BD',
        3: 'C',
        4: 'D',
        5: 'E',
        6: 'F',
        7: 'G',
        8: 'H',
        9: 'I',
        10: 'K',
        12: 'M',
        13: 'N',
        14: 'O',
        17: 'S',
        18: 'T',
        19: 'U',
        20: 'W',
        21: 'X',
        22: 'Y',
        23: 'Z'
    }

    if countyCode and len(countyCode) > 0:
        countyCode = int(countyCode)
        return countyMap[countyCode] + ' '
    else:
        return ''


def filterTags(attrs):
    """ Translate from SCB SHP files to OSM properties. """
    # Some default values.
    res = {
        'admin_level': '7',
        'boundary': 'administrative',
        'type': 'boundary',
    }

    res['name'] = attrs['KnNamn'] if attrs.get('KnNamn') else attrs.get('LnNamn')

    # According to http://wiki.openstreetmap.org/wiki/Tag:boundary%3Dadministrative#admin_level
    # admin_level should be 7 for municipalities and 4 for counties for Sweden.
    res['admin_level'] = '7' if attrs.get('KnKod') else '4'
    # The reference code is the municipality code or county code from SCB.
    res['ref'] = attrs['KnKod'] if attrs.get('KnKod') else countyToLetter(attrs.get('LnKod'))

    # Add this extra ref for the code for counties, since they will get translated into letters.
    if attrs.get('LnKod'):
        res['ref:se:scb'] = attrs.get('LnKod')

    return res
