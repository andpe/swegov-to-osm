#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" A translation function for Trafikverket-NVDB to OSM. """
import sys

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
    """ Filter and change some tags for street names and whatnot. """

    result = {
        'highway': 'residential'
    }

    # Namn will always contain the name if it has one.
    if 'NAMN' in attrs and attrs['NAMN']:
        result['name'] = attrs['NAMN']

    hasPrefix = False

    # Assign the highway tag as a best effort based on the data from
    # trafikverket + nvdb
    if 'KLASS' in attrs and attrs['KLASS']:
        klass = int(attrs['KLASS'])
        if klass == 0:
            result['highway'] = 'motorway'
        elif klass == 1:
            result['highway'] = 'trunk'
        elif klass > 1 and klass < 4:
            result['highway'] = 'primary'
        elif klass == 4:
            result['highway'] = 'secondary'
            hasPrefix = True
        elif klass == 5:
            result['highway'] = 'tertiary'
            hasPrefix = True
        elif klass > 6:
            result['highway'] = 'residential'
        else:
            result['highway'] = 'unclassified'

    if 'HUVUDNR' in attrs and attrs['HUVUDNR']:
        prefix = ''
        if hasPrefix:
            prefix = countyToLetter(attrs['LÄN'])

        result['ref'] = prefix + attrs['HUVUDNR']

    return result
