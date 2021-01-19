# extract-wordpress-items

This simple Python3 script scans a WordPress page or post archive, and splits it up into files, one file per page.

It takes the following command line.

```bash
python3 extract-wordpress-items.py input-file-name output-file-prefix
```

`input-file-name` is the name of the file to be read. It should be a WordPress export archive of pages or posts. It should be more or less correct.

`output-file-prefix` is prepended to each output file name. The filename will be either  _`prefix.#.post_name.xml`_, if a non-empty `<wp:post_name>` element if found; or  _`prefix.#.xml`_ otherwise. In any case _`#`_ will be changed to the zero-origin index of the resulting file.

## Prerequisites

Tested with python3 v3.6.9 and python3-lxml version 4.2.1.

## Meta

O