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
addons/           the four live exports (2 addons + both AIOMetadata profiles)
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

The four exports exactly as they are configured now, dumped verbatim. Restore material — the
generator does not read these.

- `aiostreams.json` — AIOStreams, `AIOStreams (A)`: Tamtaro partial SEL 3.0.4 + Vidhin ranked
  regexes, TorBox only, `cacheAndPlay` for usenet, "Nuvio minimal + badges" formatter.
  Credentials are stripped from `services`, **but the TorBox API key sits inside the Comet and
  StremThru preset URLs** — keep this repo private, and redact those two URLs before ever sharing
  the file.
- `aiometadata-collections.json` — AIOMetadata 3.2.3, **main profile**: 351 catalogs, all enabled,
  no `addonName`, no streaming catalog set, one AIO manager account, mdblist watch tracking on,
  `hideUnreleased*` on, `sfw` off.
- `aiometadata-no-collections.json` — AIOMetadata 3.2.3, **Friends profile**: 46 catalogs
  (27 enabled), the six streaming catalogs, five AIO manager accounts, `sfw` on,
  `showDisabledCatalogs` on. Collections come from the Nuvio file instead of from catalogs.
  Same export format, different profile — these two are **not** two halves of one config.
- `nuvio-collections.json` — the Nuvio client's own export: 6 top folders / 114 sub-folders, the
  same folder ids `dist/` emits, plus per-folder **`sources`** (308 entries) and
  `focusGifEnabled`. `dist/nuvio-collections.json` carries neither; it carries `_coverMode`,
  `coverEmoji` and `focusGifUrl`, which the live export no longer has. The client's schema has
  moved past what the generator emits.

Open items:

1. `base/` and `dist/aiometadata-setup.json` still say `version: 1.35.2` (55 base catalogs) while
   the live instance and `addons/` are on 3.2.3 — the vendored base predates the current
   AIOMetadata.
2. `dist/nuvio-collections.json` has no folder `sources` at all while the live client export
   carries 308, so either the client resolves them another way or importing the generated file
   loses the wiring. Unverified.

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
