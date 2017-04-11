# swegov-to-osm
Conversion tools for going from Swedish government data to (mostly) OSM-compatible data. The purpose of this project was to make government data possible to use together with [pbflookup](https://github.com/thomasfischer-his/pbflookup) without having to update the C++ code.

## Dependencies
This project depends on the following projects:

* [ogr2osm](https://github.com/pnorman/ogr2osm) for converting the Shapefiles to OSM
* [osmosis](https://github.com/openstreetmap/osmosis) for converting the OSM files into osm.pbf

## Examples

To run the conversion chain on a folder of government data from Sweden this command line can be used.
```bash
$ python3 convert.py -i /mnt/hgfs/shapes/ -o /home/andpe/out -p '(vgR|Kommun|Lan|bt_riks|mb_riks_centroid).*shp$' default_ruleset.py
```
This combination of parameters uses ```/mnt/hgfs/shapes``` as the input directory and ```/home/andpe/out``` as the output directory. The input folder is then filtered looking for files that match the pattern in ```-p``` and converts the files from the SHP attributes to OSM attributes using the ruleset specified in default_ruleset.py