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
from lxml import etree as ET
from pathlib import Path
import re
import sys

### Initialize our name spaces
global gNS
gNS = { "wp": "http://wordpress.org/export/1.2/",
        "content": "http://purl.org/rss/1.0/modules/content/",
        "excerpt": "http://wordpress.org/export/1.2/excerpt/" }
global gVerbose
gVerbose = False
global gHeaderName
gHeaderName = "Header.xml"
global gSplitHtml
gSplitHtml = True

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
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="verbose output",
        default=False
        )
    parser.add_argument(
        "--include", "-i",
        metavar="{item}",
        action="append",
        help="<item> types to be included in output; if empty, all are",
        default=[]
        )
    parser.add_argument(
        "--combined-xml-html", "-c",
        action="store_true",
        help="use older 'lots of xml files' approach",
        default=False
        )
    args = parser.parse_args()
    return args

### read a file
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
        pValue.text = ET.CDATA(value)
        return True
    else:
        print(f"couldn't find {key} to insert {value}")
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

### get XML and HTML in the combo form
def getXmlAndHtmlCombined(filepath):
    with open(filepath, "r") as f:
        # parse the file
        item = ParseXmlFileKeepCDATA(f)
        f.close()
        return item

### get XML and HTML from separate files
def getXmlAndHtmlSplit(filepath):
    global gVerbose
    item = None
    with open(filepath, "r") as f:
        # parse the file
        item = ParseXmlFileKeepCDATA(f)
        f.close()

    htmlContentFile = re.sub(r"\bxml/", r"html/", re.sub(r"\.xml$", r'-content.html', str(filepath)))
    f = None
    try:
        f = open(htmlContentFile, "r")
    except:
        if gVerbose:
            print(f"could not find: {htmlContentFile} (XML: {str(filepath)})")
        pass

    if f != None:
        htmlContents = f.read()
        SetItemValue(item, "content:encoded", htmlContents)
        f.close()
        f = None

    htmlExcerptFile = re.sub(r"\bxml/", r"html/", re.sub(r"\.xml$", r'-excerpt.html', str(filepath)))
    try:
        f = open(htmlExcerptFile, "r")
    except:
        pass

    if f != None:
        htmlExceprt = f.read()
        SetItemValue(item, "excerpt:encoded", htmlExceprt)
        f.close()

    return item

### get Xml and Html
def getXmlAndHtml(filepath):
    if gSplitHtml:
        return getXmlAndHtmlSplit(filepath)
    else:
        return getXmlAndHtmlCombined(filepath)

### the top-level function
def Main():
    global gVerbose
    global gSplitHtml

    # parse the command line args
    args = ParseCommandArgs()
    gVerbose = args.verbose
    gSplitHtml = not args.combined_xml_html

    # check whether we have a header file
    inDir = args.hInputDir

    # open and parse the header file
    with open(inDir / gHeaderName, "r") as f:
        root = ParseXmlFileKeepCDATA(f)
        f.close()

    ### create a sorted table of file names. These are assumed
    ### to be of the form {type}-{post_id}[.suffix].xml
    ### We create a key of the form {type}-00..{post-id},
    ### where enough zeroes are inserted to make a 10-digit field.
    def wpKey(path):
        t = list(path.stem.partition('-'))
        u = list(t[2].partition('.'))
        u[0] = u[0].rjust(10, '0')
        t[2] = "".join(u)
        return "".join(t)

    t = None
    if not gSplitHtml:
        t = sorted(inDir.glob("*-*.xml"), key=wpKey)
    else:
        inXmlDir = inDir / "xml"
        t = sorted(inXmlDir.glob("*-*.xml"), key=wpKey)

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

        item = getXmlAndHtml(filepath)
        sPostType = GetItemValue(item, "wp:post_type")

        if len(args.include) == 0 or sPostType in args.include:
            DropDuplicateWpMetaEntries(item)
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
