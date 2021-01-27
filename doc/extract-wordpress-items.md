# `extract-wordpress-items`

This Python3 script scans a WordPress page or post archive, and splits it up into files, one file per page.

It is intended for use in conjunction with a tool like Flywheel `local`, when you want to make massive regular changes to the content of a WordPress site, remove Divi tags, etc.

## Command Line Syntax

`extract-wordpress-items` takes the following basic command line.

```bash
python3 {switches} extract-wordpress-items.py input-file-name output-dir
```

`input-file-name` is the name of the file to be read. It should be a WordPress export archive of pages or posts. It should be more or less correct.

`output-dir` is the name of the directory where the output files are to be written. It must already exist. The filename will be either  _`prefix.#.post_name.xml`_, if a non-empty `<wp:post_name>` element is found; or  _`prefix.#.xml`_ otherwise. In any case _`#`_ will be changed to the post_id from the input file.

Recognized switches:

Switch | Function
-------|----------
 `-v`, `--verbose` | Print progress messages.
 `-h`, `--help`    | Print help summary.
 `--strip-divi-meta` | Remove Divi theme attributes; see [below](#advanced-use) for more info.

## Typical use

Export the pages of your side using the WordPress wp-admin `Tools>Export` menu. (We've only tested with a subset export of pages; it should also work with an export of posts.) Let's say you downloaded it to `~/Downloads/myPages.xml`.

For purposes of example, let's say your site has 3 pages; one named `about`, the second named `contact`, and the third with a blank name. Your run will look something like this:

```console
$ mkdir /tmp/myPages
$ python3 extract-wordpress-items.py mysite.WordPress.2020-01-23.xml /tmp/myPages/ --verbose
Input: 3 items

Output 0: /tmp/myPages/page-17.about.xml
Output 1: /tmp/myPages/page-131.contact.xml
Output 2: /tmp/myPages/page-4.xml
$ ls /tmp/myPages
Header.xml page-131.about.xml  page-17.contact.xml  page-4.xml
$
```

## Advanced use

The `--strip-divi-meta` switch will cause the extraction process to remove the Divi `wp:postmeta` tags from the database XML (not the embedded, square-bracketed tags; that's a separate problem).

## Meta

### Prerequisites

Tested with python3 v3.6.9 and python3-lxml version 4.2.1.

### License

Released under MIT license.
