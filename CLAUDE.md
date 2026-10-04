# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Two Python 3 scripts that convert a WordPress export (WXR XML) archive to a tree of files under git and back again, so site content can be edited with ordinary text tools and then re-imported. Both scripts use `lxml` and nothing else outside the standard library. There is no package, build step, linter configuration, or test suite.

- `extract-wordpress-items.py {archive.xml} {outdir}`: split an archive into one file per `<item>`.
- `compose-wordpress-items.py {indir} [{out.xml}]`: rebuild an archive from that tree (stdout if no output file).

Run them directly with `python3`. To check a change, extract a real export into a scratch directory, compose it again, and diff the result against the original archive. `.vscode/launch.json` holds the debug arguments the author uses for the extract script.

## Directory layout produced by extract

The default ("split") layout:

```
{outdir}/Header.xml                               archive with all <item>s removed
{outdir}/xml/{type}-{post_id}[.{post_name}].xml   one <item>, with content:encoded and excerpt:encoded emptied
{outdir}/html/{type}-{post_id}[.{post_name}]-content.html
{outdir}/html/{type}-{post_id}[.{post_name}]-excerpt.html
```

`-c` / `--combined-xml-html` selects the older layout: every item as one `.xml` file directly in `{outdir}`, HTML left inside the CDATA. Pass the same flag to both scripts.

`{outdir}` must exist; in split mode the extract script creates `xml/` and `html/` under it.

## How the round trip works

- `Header.xml` keeps the `<rss>`/`<channel>` wrapper and ends the channel with the comment `extract-wordpress-items.py: insert items here`. Compose parses it and appends each item to the end of `<channel>`.
- Compose finds the paired HTML files by rewriting the XML path: `.xml` becomes `-content.html` / `-excerpt.html`, and the path component `xml/` becomes `html/`. A missing HTML file leaves that element empty. It writes the HTML back as `ET.CDATA`.
- Compose sorts items by a key that zero-pads the post_id to 10 digits (`wpKey`), so items come out in `{type}`, then numeric post_id order.
- Both scripts parse with `ETCompatXMLParser(strip_cdata=False, remove_comments=False, resolve_entities=False)` and serialize with `ET.tostring(..., encoding="unicode", method="xml")`. These settings keep CDATA sections and comments intact; changing them breaks the round trip.
- Both scripts drop duplicate `wp:postmeta` entries (same `wp:meta_key`) and postmeta with no key (`DropDuplicateWpMetaEntries`, duplicated in each file). Extract's `--strip-divi-meta` also removes postmeta whose key starts with `_et_` or `et_`.
- `compose --include {type}` (repeatable) limits output to items with that `wp:post_type`.

The namespace map `gNS` (`wp`, `content`, `excerpt`) and the helpers `ParseXmlFileKeepCDATA`, `GetItemValue`, `SetItemValue` are copied in both scripts rather than shared. Keep the copies in step when changing one. Note that `SetItemValue` differs: extract assigns plain text, compose wraps it in `ET.CDATA`.

## Re-importing into WordPress

Import needs the WordPress Importer plugin plus `wordpress-import-update.php` (https://gist.github.com/terrillmoore/70f7fefde462dc632515db28cc78a07a) in `wp-content/mu-plugins`; without that plugin the importer skips items that already exist. The author's workflow uses a Flywheel `local` copy of the site.

## Conventions

- File header block: `Module:`, `Function:`, `Copyright and License:` (MCCI Corporation, MIT, see `LICENSE.md`), `Author:`.
- Style: module-level globals with `g` prefix (`gVerbose`, `gSplitHtml`), CapWords function names for the original functions, `### comment` before each function, script ends with a bare `Main()` call.
