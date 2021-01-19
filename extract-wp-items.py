#!/usr/bin/env python3

import argparse
# import xml.etree.ElementTree as ET
from lxml import etree as ET

### parse the command line to args.
parser = argparse.ArgumentParser(description="split up Word Press page or post archive")
parser.add_argument("hInput", metavar="{inputFile}", type=argparse.FileType('r'))
parser.add_argument("sPfxOutput", metavar="{outputPrefix}")
args = parser.parse_args()

### read the file
ETparse = ET.ETCompatXMLParser(remove_comments=False, strip_cdata=False)
ET.set_default_parser(ETparse)
doc = ET.parse(args.hInput)
root = doc.getroot()

### create a table t with one entry per item
t = [p for p in root.findall("channel/item")]

print("Input: " + str(len(t)) + " items\n")

### create separate files
itemIndex = 0
for item in t:
    fname = args.sPfxOutput + str(itemIndex) + ".xml"
    print("Output " + str(itemIndex) + ": " + fname)
    #for content in item.findall("encoded"):
    #    content.text = ET.CDATA(content.text)
    with open(fname, "w") as f:
        f.write(ET.tostring(item, encoding="unicode", method="xml"))
        f.close()
    itemIndex += 1

### end
