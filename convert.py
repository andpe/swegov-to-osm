"""
Conversion chain for ESRI SHP to OSM for a thesis in informatics.

This file runs ogr2osm.py first to convert shape files to OpenStreetMap XML
which then gets passed to osmosis to be merged into a single file and saved
as a OSM-PBF file.

"""

import optparse
import subprocess
import sys
import os
from os.path import exists
import logging
import re
import uuid

DEBUG = True

# Global variable to determine where to save the running ID
batch_id_file = '/tmp/' + str(uuid.uuid4())

# Set up logging for the module
logging.basicConfig()
logger = logging.getLogger('converter')
logger.setLevel(logging.DEBUG)

# Set up an options parser
op = optparse.OptionParser(usage="""
    %prog [options] <translation_mapping_file>
""")
op.add_option("-i", "--input-directory", dest="input_dir", help="Source directory to convert to OSM")
op.add_option(
    "-o", "--output-directory",
    dest="output_dir", help="Output directory for the converted files")
op.add_option(
    "-p", "--pattern",
    dest="filepattern", help="Regex to match files in the source directory against")

(options, args) = op.parse_args()
print(args)

# If no arguments were provided, print the help text and exit cleanly
if len(args) < 1:
    op.print_help()
    sys.exit(0)

# TODO: Load the translation_mapping_file so that translation files
#       can be applied to files running through ogr2osm.py.

# If the translation mapping file doesn't exist then we simply bail out here
# since proceeding could be a waste of time.
if len(args) < 1 or not exists(args[0]):
    logger.fatal("Translation mapping file not provided or non-existent, bailing")
    sys.exit(2)

# Load the translation mapping file by executing it.
f = open(args[0], 'r')
exec(f.read())

# Some minor sanity checks before we proceed, ogr2osm and osmosis have to be
# in PATH before we can proceed. If either of them is missing then exit
# with error code 2.
with open(os.devnull, 'w') as fnull:
    r = subprocess.Popen("ogr2osm.py", shell=True, stdout=fnull, stderr=fnull)
    code = r.wait()
    if code == 127:
        print("ogr2osm.py must be in path", file=sys.stderr)
        sys.exit(2)
    else:
        logger.debug("ogr2osm.py in path, proceeding")

    r = subprocess.Popen("osmosis", shell=True, stdout=fnull, stderr=fnull)
    code = r.wait()
    if code == 127:
        print("osmosis must be in path", file=sys.stderr)
        sys.exit(2)

# Input directory must exist, otherwise error code 20 is raised
if not exists(options.input_dir):
    logger.fatal("Input directory does not exist, bailing")
    sys.exit(20)

shp_files = []

# Recursively look for shp files in the input directory
for root, subf, files in os.walk(options.input_dir):
    for filename in files:
        if (options.filepattern is None and filename.endswith(".shp")) or re.match(options.filepattern, filename) is not None:
            logger.debug("Found %s in %s", filename, root)
            shp_files.append(os.path.join(root, filename))

logger.info("Found %d files to convert in %s", len(shp_files), options.input_dir)

# Write a 0 to the batch id file.
with open(batch_id_file, 'w') as f:
    f.write('0')
    f.flush()

# Convert the files to OSM format by using ogr2osm.py.
run = 0
for shp in shp_files:
    logger.info("Converting %s", shp)
    translation_file = None

    for reg, f in translation_map:
        if reg.match(shp) is not None:
            translation_file = f
            break

    # Open the log files to have somewhere to log.
    with open('stderr-%d.err' % run, 'w') as err, open('stdout-%d.log' % run, 'w') as std:
        args = "ogr2osm.py --positive-id --add-timestamp --add-version --idfile=%s --saveid=%s --debug-tags --verbose" % (batch_id_file, batch_id_file)
        if translation_file is not None:
            args += ' -t %s' % translation_file
            logger.info("Using %s as translation file", translation_file)

        # Finish building the command line we're going to execute and then run it.
        args += " '%s'" % shp
        logger.debug("Running %s", args)
        p = subprocess.Popen(
            args,
            shell=True,
            stderr=err,
            stdout=std
        )

        retcode = p.wait()
        if retcode != 0:
            logger.warning("Conversion of %s might have failed, check stderr-%d.err", shp, run)

    run += 1

# Change path from INPUT_DIR to OUTPUT_DIR and conver the filenames
# to their new converted names so that we can merge them using osmosis
osm_files = [
    os.path.join(
        options.output_dir,
        os.path.basename(x)
    )[:-3] + 'osm'  # Replace .shp with .osm in the filenames
    for x in shp_files
]

for osm in osm_files:
    for pattern, cb in postprocess:
        if pattern.match(osm):
            logger.info("Running post-process on %s", osm)
            cb(osm, batch_id_file)

osmosis_args = ['osmosis']
for osm in osm_files:
    osmosis_args.extend(['--rx', osm])

# Merge needs to be n-1 of the rx arguments
osmosis_args.extend(['--merge'] * (len(osm_files) - 1))
osmosis_args.append('--write-pbf merged.osm.pbf')

# Run osmosis and put the output in a log file.
with open('stderr.err', 'w') as err, open('stdout.log', 'w') as std:
    logger.debug("Running %s", ' '.join(osmosis_args))
    p = subprocess.Popen(' '.join(osmosis_args), shell=True, stderr=err, stdout=std)
    retcode = p.wait()
    if retcode != 0:
        logger.warning("Merge using osmosis might have failed, check stderr.err")
    else:
        logger.info("Done converting and merging files, result is in merged.osm.pbf")

# Cleanup
os.unlink(batch_id_file)
