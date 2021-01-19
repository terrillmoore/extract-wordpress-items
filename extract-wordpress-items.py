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
global gVerbose
gVerbose = False

### parse the command line to args.
def ParseCommandArgs():
    parser = argparse.ArgumentParser(description="split up Wor Press archive of pages or posts")
    parser.add_argument("hInput", metavar="{inputXmlFile}", type=argparse.FileType('r'),
                        help="Input XML file")
    parser.add_argument("sPfxOutput", metavar="{outputFilePrefix}",
                        help="Prefix for names of generated output files")
    parser.add_argument("--strip-divi-meta", action="store_true",
                        help="remove Divi wp:postmeta entries",
                        default=False)
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="verbose output",
                        default=False)
    return parser.parse_args()

### read the file
def ParseXmlFileKeepCDATA(hInput):
    # make sure we keep comments and CDATA marked as such.
    ETparse = ET.ETCompatXMLParser(remove_comments=False, strip_cdata=False)
    ET.set_default_parser(ETparse)
    # parse the input
    doc = ET.parse(hInput)
    return doc.getroot()

### remove Divi WpMeta tags
def StripDiviWpMeta(tree):
    for wpMeta in tree.findall("wp:postmeta", gNS):
        wpMetaKey = wpMeta.find("wp:meta_key", gNS)
        if wpMetaKey != None:
            wpMetaKeyName = wpMetaKey.text
            if wpMetaKeyName.startswith("_et_") or wpMetaKeyName.startswith("et_"):
                # we found one we don't like
                tree.remove(wpMeta)
                if gVerbose:
                    print("removed: {:s}".format(wpMetaKeyName))
    return tree

### the top-level function
def Main():
    # parse the command line args
    args = ParseCommandArgs()
    gVerbose = args.verbose

    # read the input file
    root = ParseXmlFileKeepCDATA(args.hInput)

    ### create a table t with one entry per <item>
    t = [p for p in root.findall("channel/item")]

    if gVerbose:
        print("Input: " + str(len(t)) + " items\n")

    if args.strip_divi_meta:
        for item in t:
            StripDiviWpMeta(item)

    ### create separate files for each item
    itemIndex = 0
    for item in t:
        postname_item = item.find("wp:post_name", gNS)
        postname_part = ""
        if postname_item != None and postname_item.text != "":
            postname_part = "." + postname_item.text

        fname = args.sPfxOutput + "{:03d}".format(itemIndex) + postname_part + ".xml"
        if gVerbose:
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
