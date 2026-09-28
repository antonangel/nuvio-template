# nuvio-settings

Our own Nuvio + AIOMetadata setup: the collection layout the TV client shows, and the
AIO catalog config behind it. Both importable artifacts are generated from one overlay,
so the two halves can never drift apart.

Target instance: AIO profile `56dcd2e0`, addon id `aio-metadata` (AIOMetadata 3.2.3).

## Layout

```
curation.json     the overlay — art swaps, collection/folder edits, open items. EDIT THIS.
build.py          generator + gates (stdlib only, no deps)
base/             upstream kit, vendored verbatim. NEVER EDIT.
reference/        live snapshots used by the gates (AIO manifest)
addons/           live exports of the two addons as configured now (restore material)
assets/           our art library, one dir per family:
                    collections/ 68   actors/ 57   awards/ 7   discover/ 6
data/             generated: franchises-folders.json, franchises-catalogs.json, match-report.csv
tools/            match-mdblist.py — slug -> mdblist list matching, with the review table
dist/             generated. NEVER EDIT.
  nuvio-collections.json    -> Nuvio client / AIO "Import collections"
  aiometadata-setup.json    -> AIO "Import Catalog Setup"
  mapping.csv               audit: every folder, its sources and its art
```

## Franchises (68 collections)

`tools/match-mdblist.py` matches each `assets/collections/*.jpg` slug to an mdblist list and
writes `data/franchises-{folders,catalogs}.json` plus a review CSV:

```bash
python3 tools/match-mdblist.py --dry   # review table only
python3 tools/match-mdblist.py         # regenerate data/
```

- Hand-picked ids live in `OVERRIDES` (each with the reason); auto-matching scores on name
  equality and **anything under the confidence bar is printed for review, never silently trusted**.
- Override metadata is fetched **by list id** (`GET /lists/{id}`); the search endpoint is
  rate-limit-flaky and misses lists whose name differs from the slug (slug `jurassic-world` is
  the list `Jurassic Park`). Search is only used for auto-matching.
- A failed query aborts the run — a silently empty result is how a wrong catalog ships.
- `tileShape` is read from the JPEG's real aspect ratio, not assumed.


## Workflow

```bash
python3 build.py --check --manifest reference/aio-manifest-56dcd2e0.json   # validate, no writes
python3 build.py         --manifest reference/aio-manifest-56dcd2e0.json   # write dist/
python3 build.py --net                                                     # also HEAD-check every art URL
```

`build.py` applies `curation.json` to `base/`, then verifies:

- every folder has an id, a valid `tileShape` and non-empty `catalogSources`
- every source is a complete `{addonId, type, catalogId}` triple and **resolves against
  the snapshot manifest** — a dead source fails the build unless it is listed in
  `curation.json` → `pending` (a documented open decision)
- AIO catalogs have no duplicate `(type, id)` and stay `apiKeysExcluded: true`

`dist/` is committed on purpose: it is the thing you paste into a dashboard, and it makes
every change a reviewable diff.

## Importing

- `dist/nuvio-collections.json` → Nuvio client, or AIO → **Collections** → Import collections.
- `dist/aiometadata-setup.json` → AIO → **Catalogs** → Import Catalog Setup.
  This dialog **replaces the entire config** — it carries the 55 base catalogs plus
  anything in `curation.json` → `extra_catalogs`, and no API keys.

A collections file in the Catalogs dialog fails with "Invalid configuration file format",
and a full export in the Collections dialog is rejected — one file per dialog.

## Live addon configs (`addons/`)

The two addons exactly as they are configured now, exported verbatim. Restore material —
the generator does not read these.

- `aiometadata-no-collections.json` — AIOMetadata **full config export** (format version 3.2.3):
  providers, art providers, search engines, streaming list, the 46 catalogs (27 enabled) and the
  five AIO manager accounts. Collections are deliberately absent — those come from
  `dist/nuvio-collections.json`.
- `aiostreams.json` — AIOStreams config: Tamtaro partial SEL 3.0.4 + Vidhin ranked regexes,
  TorBox only, `cacheAndPlay` for usenet, "Nuvio minimal + badges" formatter.
  Credentials are stripped from `services`, **but the TorBox API key sits inside the Comet and
  StremThru preset URLs** — keep this repo private, and redact those two URLs before ever sharing
  the file.

Open item: `base/` and `dist/aiometadata-setup.json` still say `version: 1.35.2` (55 base
catalogs) while the live instance and `addons/` are on 3.2.3 — the vendored base predates the
current AIOMetadata. Re-base and regenerate, or keep the two apart, is still undecided.

## Art

`curation.json` → `art` maps a folder title to `{cover, logo, hero}`, resolved against
`art_base`. `cover` → `coverImageUrl`, `logo` → `titleLogoUrl`, `hero` → `heroBackdropUrl`.

Current source: [illiyah/Images](https://github.com/illiyah/Images/tree/main), hotlinked by
URL (no re-hosting). Filenames that do **not** follow the `<Stem>-coverimage/-titlelogo/-backdrop_1080p`
pattern:

- Apple TV's logo is `AppleTV-titleimage.webp` (`-titlelogo` 404s). It is white-on-transparent —
  correct over a hero backdrop, invisible on a light surface.
- Peacock has no `Peacock-backdrop_1080p.webp`; `PeacockPlus-backdrop_1080p.webp` is used
  (verified: Peacock UI artwork, despite the name).
- Adult Swim has no art in that repo; the kit's original cover stays.

The same repo also covers folders we have not switched over yet — swap these in when wanted:

- Discover: `newmovies`, `newseries`, `trendingmmovies` (note the double `m`), `trendingseries`,
  plus `popular`, `toprated`, `foryou`, `newreleases` sets that also ship `-backdrop`/`-titlelogo`.
- Genres: all except Nature and Mindfuck. Mystery's filename is misspelled `mysteru-coverimage.webp`.
- Nothing for the 7 Decades or the 12 franchise folders — those need our own art.

## Open items

Listed in `curation.json` → `pending` so the build stays honest about them:

1. **Streaming Services (9 folders)** — sources point at the external addon
   `pw.ers.netflix-catalog`. Either install it in the client, or add AIO's native
   `streaming.<code>` catalogs and remap.
2. **Genres/Horror** — wants `mdblist.102554` ("Must-See Modern Horror", 188 items, author
   `snoak`), which the AIO profile does not have yet.
3. **Marvel / DC Universe / Star Wars** — served by the joaogonp and tapframe addons;
   AIO cannot reproduce their chronological catalogs, so these stay external or get
   substituted.
