#!/usr/bin/env python3

##############################################################################
#
# Module:  extract-wordpress-items.py
#
# Function:
#   Extract Word Press <item> entries from a Word Press archive file.
#
# Copyright and License:
#   Copyright (C) 2021, MCCI Corporation. See accompanying LICENSE file
#
# Author:
#   Terry Moore, MCCI   January, 20201
#
##############################################################################

import argparse
from lxml import etree as ET

### Initialize our name spaces
global gNS
gNS = { "wp": "http://wordpress.org/export/1.2/",
        "content": "http://purl.org/rss/1.0/modules/content/",
        "excerpt": "http://wordpress.org/export/1.2/excerpt/" }

### parse the command line to args.
def ParseCommandArgs():
    parser = argparse.ArgumentParser(description="split up Word Press archive of pages or posts")
    parser.add_argument("hInput", metavar="{inputXmlFile}", type=argparse.FileType('r'))
    parser.add_argument("sPfxOutput", metavar="{outputFilePrefix}")
    return parser.parse_args()

### read the file
def ParseXmlFileKeepCDATA(hInput):
    # make sure we keep comments and CDATA marked as such.
    ETparse = ET.ETCompatXMLParser(remove_comments=False, strip_cdata=False)
    ET.set_default_parser(ETparse)
    # parse the input
    doc = ET.parse(hInput)
    return doc.getroot()

### the top-level function
def Main():
    # parse the command line args
    args = ParseCommandArgs()

    # read the input file
    root = ParseXmlFileKeepCDATA(args.hInput)

    ### create a table t with one entry per <item>
    t = [p for p in root.findall("channel/item")]

    print("Input: " + str(len(t)) + " items\n")

    ### create separate files for each item
    itemIndex = 0
    for item in t:
        postname_item = item.find("wp:post_name", gNS)
        postname_part = ""
        if postname_item != None and postname_item.text != "":
            postname_part = "." + postname_item.text

        fname = args.sPfxOutput + str(itemIndex) + postname_part + ".xml"
        print("Output " + str(itemIndex) + ": " + fname)
        with open(fname, "w") as f:
            # write the file; method xml needed to ensure CDATA goes out as such
            # encoding unicode needed to ensure this is a string rather than a sequence of bytes
            f.write(ET.tostring(item, encoding="unicode", method="xml"))
            f.close()
        itemIndex += 1

### do the work.
Main()

### end
