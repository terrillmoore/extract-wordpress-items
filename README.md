# Extract and Compose WordPress Archives

These tools allow simple roundtrippig of data between a WordPress content database and git-controlled files on the local machine.

## Motivation

HTML stored in a WordPress database may have a variety of problems (typos, out-of-date '™' versus '&reg;' references, outdated company names, and so forth. It's much easier to fix such things using text processing tools, but hard to turn such tools loose against the database. Furthermore, a text processing flow allows the use of git, which in turn allows careful step-by-step review and collaboration.

Although it's technically possible to edit a WordPress XML archive directly, it's quite unpleasant.

This package therefore has two tools. The first tool expands an XML archive into a directory containg the archive contents, split up by page, post or other item type.

The second tool reverses this process, creating an XML archive that can be imported into WordPress.

The tools use Python's `lxml` library, and therefore are aware of the structure of what they're processing.

## `extract-wordpress-items`

This Python3 script scans a WordPress archive, and splits it up into files, one file per item. It will optionally remove some Divi-specific tags as it creates the files.

It is intended for use in conjunction with a tool like Flywheel `local`, when you want to make massive regular changes to the content of a WordPress site, remove Divi tags, etc.

Documntation is [here](doc/extract-wordpress-items.md)

## `compose-wordpress-items`

This python3 script takes a collection of XML files (typically as generated by [`extract-wp-items`](#extract-wordpress-items), and puts them together into an archive that can subsequently be imported.

Documentation is [here](doc/compose-wordpress-items.md).

To use this, you must make two changes in your WordPress set up.

1. You must install the [WordPress Importer](https://wordpress.org/plugins/wordpress-importer/).
2. You must add [wordpress-import-update.php][1] to your WordPress installation's `app/public/wp-content/mu-plugins` directory. (Without this, duplicate pages are skipped).

   **Note:** If you're using Flywheel `local`, you may need to re-install this after pulling an image from the main site.

[1]: https://gist.github.com/terrillmoore/70f7fefde462dc632515db28cc78a07a

## Suggested workflow

### Getting started from scratch

1. Using Flywheel's [local](https://localwp.com/), clone your site to a Ubuntu system. (We have not tested on Mac, Windows, or other distributions. We tested on Ubuntu 18.04 LTS.)

2. Copy your local copy of [wordpress-import-update.php][1] to `~/Local Files/$SITE/app/public/wp-content/mu-plugins`.

3. Create a directory you'll use for working on the site.

4. Change to that directory, and `git init .`

### Updating your content directory from WordPress

1. Using WordPress wp-admin>Tools>Export, create a full archive from the Firefly `local` image. (You can also do a subset, but my normal workflow is the full site.)

2. Extract to your working git repository directory.

    ```bash
    cd {path-to-repo}
    python3 {path-to-script}/extract-wordpress-items.py . --strip-divi
    ```
3. Capture any changes.

    ```bash
    git add .
    git commit -m "Import from WordPress"
    ```
4. Make your local changes.

5. Create an archive.

    ```bash
    python3 {path-to-script}/compose-wordpress-items.py . /tmp/archive.xml
    ```

6. Use WordPress Tools>Import to update your Flywheel `local` image of the repo.

## Meta

### Author

Terry Moore, MCCI Corporation

### Status

2021-01-23: These tools are very much works in progress. However, I successfully used them on MCCI's website to make a number of site-wide changes, check them with Flywheel `local`, and then updated the MCCI site with the results. This was much less painful than using the on-line WordPress editor -- I could use Visual Studio Code, command-line tools like `grep` and `aspell`, etc. Since I've only used it in my use case, it's possible that there are ugly mistakes that I've not yet encountered.

### Future Directions

It is clear that it would be even more convenient to further split each `page` and `post` item so that the `<content:encoded>` `CDATA` is placed into a separate `.html` file, parallel to the item's `.xml` file. This would allow Visual Studio Code (or other editor) to apply syntax analysis to the HTML body.

### Prerequisites

Tested with python3 v3.6.9 and python3-lxml version 4.2.1.

### License

Released under MIT license.
