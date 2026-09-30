# nuvio-template

A Nuvio + AIOMetadata setup as four importable files plus the art library they point at.
Everything here is a verbatim export of a working setup — nothing is generated, nothing is
scripted, nothing is built. Import a file, or take the art and host your own.

```
<addon>.json   the four exports, at the repo root. import these.
images/        the folder/collection art library, one dir per family
```

## The four files

| file | addon | what it is |
|---|---|---|
| `aiometadata-collections.json` | AIOMetadata 3.2.3 | **main profile** — 423 catalogs, all enabled, collections carried as catalogs |
| `aiometadata-no-collections.json` | AIOMetadata 3.2.3 | **Friends profile** — 46 catalogs (27 on), collections come from the Nuvio file instead |
| `nuvio-collections.json` | Nuvio client | the folder/collection layout: 4 top folders, 112 sub-folders, each wired to catalog sources |
| `aiostreams.json` | AIOStreams | Tamtaro partial SEL 3.0.4 + Vidhin ranked regexes, usenet `cacheAndPlay` |

The two AIOMetadata files are **two different profiles, not two halves of one config** — different
catalog sets, different manager accounts, different defaults. Import the one you want.

## What's inside

**`aiometadata-collections.json`** — main profile, 423 catalogs, all enabled, none pinned to home.

- Sources: tmdb 158, mdblist 154, tvdb 108, mal 2, anilist 1.
- Every catalog carries `displayType` — plural, `"movies" | "series"` (270 / 147, plus 3 `anime` and
  3 `all`), because that value *is* the published manifest type (`catalogType = displayType || type`).
- `config.collections` is **empty on purpose**: embedding collections makes AIO publish one
  `type: collection` catalog each, which breaks the Genres / Decades / Collections groups in Nuvio.
  The collections live in `nuvio-collections.json` and reach AIO through its **Collections** tab.
- House rules applied: catalog name = the collection folder title, catalogs tagged with the group
  they serve (`config.tags`, 4 entries), poster art from
  `customPosterUrlPattern = https://btttr.cc/poster/imdb/poster-default/{imdb_id}.jpg` with
  `posterRatingProvider: custom` and `usePosterProxy: true`.
- One manager account (`Angel`, `https://aiomanager.angel.is`), timezone `America/Los_Angeles`, `sfw: false`.

**`aiometadata-no-collections.json`** — Friends profile, 46 catalogs, 27 enabled, 19 on home.

- Sources: mal 18 (all off), streaming 12, tmdb 10, tvdb 5, tvmaze 1.
- Five manager accounts on `https://aiomanager.angel.is` (Test, Alexa, Jordan, Maddy, Simon).
- Same custom poster pattern; `sfw: true`. No `displayType` on the mal / streaming / tvmaze rows.

**`nuvio-collections.json`** — Nuvio client / AIO Collections tab.

- 4 top collections, 112 folders, 270 sources. Every source is `provider: addon` → `aio-metadata`,
  spelled `"type": "movies" | "series"` to match the catalogs above — a singular/plural mismatch
  silently drops that folder's rows.
- **Streaming Services** — 8: Netflix, Disney+, Apple TV, Prime Video, HBO Max, Hulu, Paramount+, Peacock
- **Genres** — 22: Action, Animation, Anime, Comedy, Crime, Documentary, Drama, Fantasy, Horror,
  Myths and Legends, Nature, Reality, Robots and AI, Romance, Sci-Fi, Short Films, Spies, Thriller,
  War Stories, Westerns, Whodunits, Zombie Orama
- **Decades** — 6: 20s, 10s, 00s, 90s, 80s, 70s (movies + a per-decade popular-series catalog)
- **Collections** — 76 folders, TVDB lists ([thetvdb.com/lists](https://www.thetvdb.com/lists)), one
  folder per list with a `Movies` and/or `Series` source (`tvdb.list.<id>.movies` / `.series`). Only
  lists that carry their own poster are in: the list poster is mirrored to `images/lists/<id>.webp`
  and the folder is a `POSTER` tile with `hideTitle` on. Lists whose TVDB page serves the
  `/images/missing/movie.jpg` placeholder are dropped — no movie-poster fallback, no blank tiles.
- Tiles: 36 `LANDSCAPE` (Streaming Services, Genres, Decades) and 76 `POSTER` (Collections), every
  folder `FOLLOW_LAYOUT` with `focusGlowEnabled` and a cover; no `pinToTop`.

## Importing

- `aiometadata-collections.json` / `aiometadata-no-collections.json` → AIOMetadata → **Import config**.
  This **replaces the whole config**, and carries no API keys — add your own TMDB/TVDB/etc. keys after.
- `nuvio-collections.json` → Nuvio client → **Import collections**, or AIO → Collections → Import collections.
- `aiostreams.json` → AIOStreams → **Import config**.

A collections file in the Catalogs dialog fails with *Invalid configuration file format*, and a
catalog export in the Collections dialog is rejected — one file per dialog.

Order matters: a catalog import replaces the whole config, so it wipes the collections on the AIO
side. Re-import the Nuvio file into the Collections tab after any catalog import.

## Credentials

Nothing here holds a working credential. Both AIOMetadata exports are `apiKeysExcluded` with every
`apiKeys` entry empty, the AIOStreams `services[].credentials` are empty on all 18 services, and the
Nuvio file's `addonBaseUrl` is `null`. The only URLs left across the three are the art host and the
manager instance (`aiomanager.angel.is`). Substitute your own keys before importing.

## Art

`images/` is mirrored publicly at [antonangel/nuvio-template](https://github.com/antonangel/nuvio-template)
and `nuvio-collections.json` points at it —
`raw.githubusercontent.com/antonangel/nuvio-template/main/images/<family>/<name>.webp` for all 112
folders, so a TV client can fetch the tiles with no login (`git.angel.is` sits behind OIDC and 302s
raw file reads to a login). Fork this, host `images/` yourself, and swap the host in the URLs.

Every file is **WebP at q90 and native resolution** — posters stay 852 wide, wide art keeps its
1920/2560 pixels: 104.5 MB of originals → 29.8 MB. `images/genres/` holds all 56 wide tiles of the
Genres collection; `images/networks/` (69 files, 30 networks × cover/hero/logo) is the exception and
keeps an earlier q78/500-wide encode. `images/awards/` (7 files) is unused since the Awards
collection was dropped — it stays as art you can reuse if you build that collection back.

## The older files

`aiometadata-setup-2026-09-29.json`, `aiometadata-setup-2026-09-29-v2…v20.json` and
`genres-wide-dannyrutledge.nuvio.json` are superseded drafts from the day the four current files
were built — the dated one is the main profile after 45 MDBList catalogs were added (396 catalogs),
`v20` is the previous main profile (437 catalogs), and the `genres-wide` file is the 52-tile Genres
collection on its own. Nothing in the current set depends on them; they stay for history.

## Provenance

This repo was `nuvio-settings`, which also carried the generator that produced an importable
catalog setup from a curated overlay (`build.py`, `curation.json`, `base/`, `data/`, `dist/`,
`tools/`, `reference/`). That pipeline was removed to leave a template; it is intact at `9fd89fb^`
(`git show 9fd89fb^:build.py`). Its last state built AIOMetadata **1.35.2** artifacts while the
live instance had moved to **3.2.3**.

History has been rewritten twice — to purge a debrid key that an export carried, then to repack the
art (114.9 MB → 21.0 MB) — so every pre-repack commit SHA is gone. Re-clone rather than pull if your
copy predates that.
