#!/usr/bin/env python3

import argparse
from lxml import etree as ET

### parse the command line to args.
def ParseCommandArgs():
    parser = argparse.ArgumentParser(description="split up Word Press page or post archive")
    parser.add_argument("hInput", metavar="{inputFile}", type=argparse.FileType('r'))
    parser.add_argument("sPfxOutput", metavar="{outputPrefix}")
    return parser.parse_args()

### read the file
def ParseFile(hInput):
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
    root = ParseFile(args.hInput)

    ### create a table t with one entry per <item>
    t = [p for p in root.findall("channel/item")]

    print("Input: " + str(len(t)) + " items\n")

    ### create separate files for each item
    itemIndex = 0
    for item in t:
        fname = args.sPfxOutput + str(itemIndex) + ".xml"
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
