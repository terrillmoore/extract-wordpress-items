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


### the top-level function
def Main():
    global gVerbose
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

        fname = args.hDirOutput / (posttype_value + "-" + postid_value + postname_part + ".xml")

        DropDuplicateWpMetaEntries(item)

        if gVerbose:
            print("Output " + str(itemIndex) + ": " + fname)
        with open(fname, "w") as f:
            # write the file; method xml needed to ensure CDATA goes out as such
            # encoding unicode needed to ensure this is a string rather than a sequence of bytes
            f.write(ET.tostring(item, encoding="unicode", method="xml").rstrip())
            f.close()
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
