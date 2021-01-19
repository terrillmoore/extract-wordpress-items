# extract-wordpress-items

This simple Python3 script scans a WordPress page or post archive, and splits it up into files, one file per page.

It is intended for use in conjunction with a tool like Flywheel `local`, when you want to make massive regular changes to the content of a WordPress site, remove Divi tags, etc.

## Command Line Syntax

It takes the following basic command line.

```bash
python3 extract-wordpress-items.py input-file-name output-file-prefix
```

`input-file-name` is the name of the file to be read. It should be a WordPress export archive of pages or posts. It should be more or less correct.

`output-file-prefix` is prepended to each output file name. The filename will be either  _`prefix.#.post_name.xml`_, if a non-empty `<wp:post_name>` element if found; or  _`prefix.#.xml`_ otherwise. In any case _`#`_ will be changed to the zero-origin index of the resulting file.

## Typical use

Export the pages of your side using the WordPress wp-admin `Tools>Export` menu. (We've only tested with a subset export of pages; it should also work with an export of posts.) Let's say you downloaded it to `~/Downloads/myPages.xml`.

For purposes of example, let's say your site has 3 pages; one named `about`, the second named `contact`, and the third with a blank name. Your run will look something like this:

```console
$ mkdir /tmp/myPages
$ python3 extract-wordpress-items.py /tmp/myPages/ --verbose
Input: 3 items

Output 0: /tmp/myPages/000.about.xml
Output 1: /tmp/myPages/001.contact.xml
Output 2: /tmp/myPages/002.xml
$ ls /tmp/myPages
000.about.xml  001.contact.xml  002.xml
$
```

## Advanced use

The `--strip-divi-meta` switch will cause the extraction process to remove the Divi `wp:postmeta` tags from the database XML (not the embedded, square-bracketed tags; that's a separate problem).

## Prerequisites

Tested with python3 v3.6.9 and python3-lxml version 4.2.1.

## Meta

Released under MIT license.
