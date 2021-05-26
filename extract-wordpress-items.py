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
#   Terry Moore, MCCI   January, 2021
#
##############################################################################

import argparse
from lxml import etree as ET
from pathlib import Path

### Initialize our name spaces
global gNS
gNS = { "wp": "http://wordpress.org/export/1.2/",
        "content": "http://purl.org/rss/1.0/modules/content/",
        "excerpt": "http://wordpress.org/export/1.2/excerpt/" }
global gVerbose
gVerbose = False
global gSplitHtml
gSplitHtml = True

### parse the command line to args.
def ParseCommandArgs():
    def checkPath(s):
        result = Path(s)
        if not result.is_dir():
            raise ValueError("not a directory")

        return result

    parser = argparse.ArgumentParser(description="split up WordPress archive of pages or posts")
    parser.add_argument(
        "hInput",
        metavar="{inputXmlFile}",
        type=argparse.FileType('r'),
        help="Input XML file"
        )
    parser.add_argument(
        "hDirOutput", metavar="{outputDirectory}",
        type=checkPath,
        help="Where to put generated output files"
        )
    parser.add_argument(
        "--strip-divi-meta",
        action="store_true",
        help="remove Divi wp:postmeta entries",
        default=False
        )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="verbose output",
        default=False
        )
    parser.add_argument(
        "--combined-xml-html", "-c",
        action="store_true",
        help="use older 'lots of xml files' approach",
        default=False
        )
    return parser.parse_args()

### read the file
def ParseXmlFileKeepCDATA(hInput):
    # make sure we keep comments and CDATA marked as such.
    ETparse = ET.ETCompatXMLParser(
                remove_comments=False,
                strip_cdata=False,
                resolve_entities=False
                )
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
                if gVerbose: # gVerbose:
                    print("removed: {:s}".format(wpMetaKeyName))
    return tree

### return the CDATA for a given key
def GetItemValue(item, key):
    global gNS
    pValue = item.find(key, gNS)
    if pValue != None:
        return pValue.text
    else:
        return None

### set the CDATA for a given key
def SetItemValue(item, key, value):
    global gNS
    pValue = item.find(key, gNS)
    if pValue != None:
        pValue.text = value
        return True
    else:
        return False

### Eliminate duplicate WP meta entries
def DropDuplicateWpMetaEntries(item):
    global gNS
    tSeenKeys = dict()
    for wpMeta in item.findall("wp:postmeta", gNS):
        wpMetaKey = wpMeta.find("wp:meta_key", gNS)
        if wpMetaKey != None:
            wpMetaKeyName = wpMetaKey.text
            if wpMetaKeyName in tSeenKeys:
                # we found one we don't like
                item.remove(wpMeta)
                if gVerbose: # gVerbose:
                    print("removed duplicate: {:s}".format(wpMetaKeyName))
            else:
                tSeenKeys[wpMetaKeyName] = True
        else:
            # we don't like not having a meta_key; remove node
            item.remove(wpMeta)

### write file as combined xml/html
def writeFileCombined(item, itemIndex, postname_part, posttype_value, postid_value, args):
    fname = args.hDirOutput / (posttype_value + "-" + postid_value + postname_part + ".xml")

    if gVerbose:
        print("Output " + str(itemIndex) + ": " + fname)
    with open(fname, "w") as f:
        # write the file; method xml needed to ensure CDATA goes out as such
        # encoding unicode needed to ensure this is a string rather than a sequence of bytes
        f.write(ET.tostring(item, encoding="unicode", method="xml").rstrip())
        f.close()

def writeFileSplit(item, itemIndex, postname_part, posttype_value, postid_value, args):
    xmlFname = args.hDirOutput / "xml" / (posttype_value + "-" + postid_value + postname_part + ".xml")
    htmlContentFname = args.hDirOutput / "html" / (posttype_value + "-" + postid_value + postname_part + "-content.html")
    htmlExcerptFname = args.hDirOutput / "html" / (posttype_value + "-" + postid_value + postname_part + "-excerpt.html")

    if gVerbose:
        print("Output " + str(itemIndex) + ": " + xmlFname + ", " + htmlExcerptFname)

    # extract the HTML cdata
    htmlContent = GetItemValue(item, "content:encoded")
    htmlExcerpt = GetItemValue(item, "excerpt:encoded")
    SetItemValue(item, "content:encoded", "")
    SetItemValue(item, "excerpt:encoded", "")

    with open(xmlFname, "w") as f:
        f.write(ET.tostring(item, encoding="unicode", method="xml").rstrip())
        f.close()

    with open(htmlContentFname, "w") as f:
        f.write(htmlContent)
        f.close()

    with open(htmlExcerptFname, "w") as f:
        f.write(htmlExcerpt)
        f.close()

### write file
def writeFile(item, itemIndex, postname_part, posttype_value, postid_value, args):
    global gSplitHtml
    if gSplitHtml:
        writeFileSplit(item, itemIndex, postname_part, posttype_value, postid_value, args)
    else:
        writeFileCombined(item, itemIndex, postname_part, posttype_value, postid_value, args)
#end writeFile

### the top-level function
def Main():
    global gVerbose
    global gSplitHtml
    # parse the command line args
    args = ParseCommandArgs()
    gVerbose = args.verbose
    gSplitHtml = not args.combined_xml_html
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
    itemSkipped = 0
    for item in t:
        postname_value = GetItemValue(item, "wp:post_name")
        posttype_value = GetItemValue(item, "wp:post_type")
        postid_value = GetItemValue(item, "wp:post_id")

        if postid_value == None:
            itemSkipped += 1
            if gVerbose:
                print("Item " + itemIndex + "skiped, no post_id")
            continue

        postname_part = ""
        if postname_value != None and postname_value != "":
            postname_part = "." + postname_value

        DropDuplicateWpMetaEntries(item)

        writeFile(item, itemIndex, postname_part, posttype_value, postid_value, args)

        itemIndex += 1

    ### remove all items
    for item in t:
        item.getparent().remove(item)

    ### find the channel item.
    channel = root.find("channel")

    ### write the resulting
    comment = ET.Comment("extract-wordpress-items.py: insert items here")
    channel.insert(len(channel), comment)   # append comment

    fname = args.hDirOutput / "Header.xml"
    with open(fname, "w") as f:
        # write the file; method xml needed to ensure CDATA goes out as such
        # encoding unicode needed to ensure this is a string rather than a sequence of bytes
        f.write(ET.tostring(root, encoding="unicode", method="xml"))
        f.close()

### end Main()

### do the work.
Main()

### end
