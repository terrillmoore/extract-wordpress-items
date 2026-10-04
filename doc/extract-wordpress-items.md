# `extract-wordpress-items`

This Python3 script scans a WordPress page or post archive, and splits it up into files, one file per page.

It is intended for use in conjunction with a tool like Flywheel `local`, when you want to make massive regular changes to the content of a WordPress site, remove Divi tags, etc.

## Command Line Syntax

`extract-wordpress-items` takes the following basic command line.

```bash
python3 extract-wordpress-items.py {switches} input-file-name output-dir
```

`input-file-name` is the name of the file to be read. It should be a WordPress export archive of pages or posts. It should be more or less correct.

`output-dir` is the name of the directory where the output files are to be written. It must already exist. The script writes `Header.xml` (the archive with all items removed) in `output-dir`, and one set of files for each item:

- `output-dir/xml/`_`type-#.post_name.xml`_ holds the item, with the `<content:encoded>` and `<excerpt:encoded>` elements emptied.
- `output-dir/html/`_`type-#.post_name-content.html`_ holds the contents of `<content:encoded>`.
- `output-dir/html/`_`type-#.post_name-excerpt.html`_ holds the contents of `<excerpt:encoded>`.

The script creates the `xml` and `html` subdirectories if needed. _`type`_ is the item's `<wp:post_type>` and _`#`_ is its `<wp:post_id>`. If `<wp:post_name>` is missing or empty, the script leaves out _`.post_name`_. The script skips items with no `<wp:post_id>`.

With `--combined-xml-html`, the script instead writes each item, HTML included, as _`type-#.post_name.xml`_ directly in `output-dir`.

Recognized switches:

Switch | Function
-------|----------
 `-v`, `--verbose` | Print progress messages.
 `-h`, `--help`    | Print help summary.
 `--strip-divi-meta` | Remove Divi theme attributes; see [below](#advanced-use) for more info.
 `-c`, `--combined-xml-html` | Use the older layout: one XML file per item, HTML included, no `xml` or `html` subdirectory.

## Typical use

Export the pages of your side using the WordPress wp-admin `Tools>Export` menu. (We've only tested with a subset export of pages; it should also work with an export of posts.) Let's say you downloaded it to `~/Downloads/myPages.xml`.

For purposes of example, let's say your site has 3 pages; one named `about`, the second named `contact`, and the third with a blank name. Your run will look something like this:

```console
$ mkdir /tmp/myPages
$ python3 extract-wordpress-items.py --verbose ~/Downloads/myPages.xml /tmp/myPages
Input: 3 items

Output 0: /tmp/myPages/xml/page-17.about.xml, /tmp/myPages/html/page-17.about-content.html, /tmp/myPages/html/page-17.about-excerpt.html
Output 1: /tmp/myPages/xml/page-131.contact.xml, /tmp/myPages/html/page-131.contact-content.html, /tmp/myPages/html/page-131.contact-excerpt.html
Output 2: /tmp/myPages/xml/page-4.xml, /tmp/myPages/html/page-4-content.html, /tmp/myPages/html/page-4-excerpt.html
$ ls /tmp/myPages /tmp/myPages/xml
/tmp/myPages:
Header.xml  html  xml

/tmp/myPages/xml:
page-131.contact.xml  page-17.about.xml  page-4.xml
$
```

## Advanced use

The `--strip-divi-meta` switch will cause the extraction process to remove the Divi `wp:postmeta` tags from the database XML (not the embedded, square-bracketed tags; that's a separate problem).

## Meta

### Prerequisites

Tested with python3 v3.6.9 and python3-lxml version 4.2.1.

### License

Released under MIT license.
