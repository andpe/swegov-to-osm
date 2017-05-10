""" Translation and postprocesing module for this project. """
import re

translation_map = [
    (re.compile('.*NVDB_DKGatunamn.*'), 'nvdb.py'),
    (re.compile('.*NVDB.*'), 'nvdb.py'),
    (re.compile('.*vgR.*'), 'nvdb.py'),
    (re.compile('.*riks.*'), 'lantmateriet.py'),
    (re.compile('.*Kommun.*'), 'scb.py'),
    (re.compile('.*Lan.*'), 'scb.py'),
    (re.compile('.*ShapeVIS.*'), 'shapevis.py')
]


# ogr2osm will not add relations automatically for some large ways (it seems)
# so we'll have to do that by hand here instead.
def add_missing_rels(f):
    """ Add missing relations to the osm file. """

    import bs4
    with open(f, 'r+') as fi:
        # This is going to take forever.
        b = bs4.BeautifulSoup(fi, "xml")
        ways = b.find_all('way')
        relations = b.find_all('relation')
        max_id = max(relations, key=lambda r: int(r.attrs['id']))
        _id = int(max_id.attrs['id'])+1


        # Find a way that does not have a relation
        for way in ways:
            tag = way.find('tag', {'k': 'name'})
            if tag is not None:
                print(way)
                name = tag.attrs['v']
                # place = way.find('tag', {'k': 'place'}).attrs['v']
                adm = way.find('tag', {'k': 'admin_level'}).attrs['v']
                ref = way.find('tag', {'k': 'ref'}).attrs['v']
                refscbr = way.find('tag', {'k': 'ref:se:scb'})
                refscb = None
                if refscbr:
                    refscb = refscbr.attrs['v']

                tags = way.find_all('tag')

                found = False
                for rel in relations:
                    if rel.find('tag', {'v': name}):
                        found = True
                        print("Found!")
                        break

                if not found:
                    import time
                    # Create a new relation with all that we need
                    r = b.new_tag('relation')
                    r.attrs['id'] = _id
                    r.attrs['version'] = '1'
                    r.attrs['visible'] = 'true'
                    r.attrs['timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%SZ")

                    r.append(
                        b.new_tag(
                            'member', ref=way.attrs['id'],
                            role='outer', type='way'
                        )
                    )
                    #r.append(b.new_tag('tag', k='type', v='boundary'))
                    # r.append(b.new_tag('tag', k='place', v=place))
                    #r.append(b.new_tag('tag', k='name', v=name))
                    #r.append(b.new_tag('tag', k='admin_level', v=adm))
                    #r.append(b.new_tag('tag', k='ref', v=ref))
                    #if refscb:
                    #    r.append(b.new_tag('tag', k='ref:se:scb', v=refscb))
                    for tag in tags:
                        r.append(tag)
                    print(r)
                    b.osm.append(r)
                    b.osm.append("\n")
                    _id += 1
                    # print(r)
                    # print(place)
                    # print("Created new relation for way %s" % name)
        # Rewind and fix stuff
        fi.seek(0)
        fi.write(str(b))
        fi.flush()

# Fix missing relations for municipality data and county data.
postprocess = [
    (re.compile('.*Kommun.*'), add_missing_rels),
    (re.compile('.*Lan.*'), add_missing_rels),
]
