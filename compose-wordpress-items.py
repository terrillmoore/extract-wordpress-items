#!/usr/bin/env python3

##############################################################################
#
# Module:  compose-wordpress-items.py
#
# Function:
#   Compose extracted Word Press <item> entries frto form a Word Press archive file.
#
# Copyright and License:
#   Copyright (C) 2021, MCCI Corporation. See accompanying LICENSE file
#
# Author:
#   Terry Moore, MCCI   January, 2021
#
##############################################################################

import argparse
import sys
from pathlib import Path
from lxml import etree as ET

### Initialize our name spaces
global gNS
gNS = { "wp": "http://wordpress.org/export/1.2/",
        "content": "http://purl.org/rss/1.0/modules/content/",
        "excerpt": "http://wordpress.org/export/1.2/excerpt/" }
global gVerbose
gVerbose = False
global gHeaderName
gHeaderName = "Header.xml"

### parse the command line to args.
def ParseCommandArgs():
    def checkPath(s):
        result = Path(s)
        if not result.is_dir():
            raise ValueError("not a directory")
        if not (result / gHeaderName).is_file():
            raise ValueError("Header.xml not in directory")

        return result
    
    parser = argparse.ArgumentParser(description="re-compose split WordPress archive")
    parser.add_argument(
                "hInputDir",
                metavar="{inputFilePrefix}",
                type=checkPath,
                help="Directory containing input xml files to be composed"
                )
    parser.add_argument(
                "hOutputFile",
                metavar="{outputXmlFile}",
                nargs="?",
                type=argparse.FileType('w'),
                default=sys.stdout,
                help="File to be created (default: stdout)"
                )
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="verbose output",
                        default=False)
    args = parser.parse_args()
    return args

### read a file
def ParseXmlFileKeepCDATA(hInput):
    # make sure we keep comments and CDATA marked as such.
    ETparse = ET.ETCompatXMLParser(remove_comments=False, strip_cdata=False)
    ET.set_default_parser(ETparse)
    # parse the input
    doc = ET.parse(hInput)
    return doc.getroot()

### the top-level function
def Main():
    global gVerbose
    # parse the command line args
    args = ParseCommandArgs()
    gVerbose = args.verbose

    # check whether we have a header file
    inDir = args.hInputDir

    # open and parse the header file
    with open(inDir / gHeaderName, "r") as f:
        root = ParseXmlFileKeepCDATA(f)
        f.close()

    ### create a sorted table of file names
    t = sorted(inDir.glob("*.xml"))

    if gVerbose:
        print("Input: " + str(len(t)) + " files")

    ### read each item and apend
    channel = root.find("channel")

    itemIndex = 0
    for filepath in t:
        if filepath.name == gHeaderName:
            continue

        if gVerbose:
            print("Read: " + filepath.name)

        with open(filepath, "r") as f:
            # parse the file
            item = ParseXmlFileKeepCDATA(f)
            f.close()
            channel.insert(len(channel), item)

        itemIndex += 1

    ### write the resulting file
    # method xml needed to ensure CDATA goes out as such
    # encoding unicode needed to ensure this is a string rather than a sequence of bytes
    args.hOutputFile.write(ET.tostring(root, encoding="unicode", method="xml"))
    f.close()

### end Main()

### do the work.
Main()

### end
