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
    res = {
        'admin_level': '7',
        'boundary': 'administrative',
        'type': 'boundary',
    }

    res['name'] = attrs['KnNamn'] if attrs.get('KnNamn') else attrs.get('LnNamn')
    res['admin_level'] = '7' if attrs.get('KnKod') else '4'
    res['ref'] = attrs['KnKod'] if attrs.get('KnKod') else countyToLetter(attrs.get('LnKod'))

    if attrs.get('LnKod'):
        res['ref:se:scb'] = attrs.get('LnKod')

    return res
