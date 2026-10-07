# nuvio-template

A complete **Nuvio** setup you can import in about ten minutes: four addons would cover most of
your needs. Designed to be used with debrid service. High-quality streams, rich metadata and personal recommendations. Import the files, then
add your own API keys and install addons in Nuvio.

## What you need first

1. **Nuvio** — the client, on the device you watch on ([nuvio.tv](https://nuvio.tv)). Any
   Stremio-addon-compatible client should work in the same way. 
2. **A debrid service** — TorBox, Real-Debrid, AllDebrid, Premiumize… Streams play from *your*
   debrid account, so without one you only get the free and peer-to-peer results.
   *(Usenet is optional — the AIOStreams files already carry a cache-and-play setup for it.)*
3. **The four addons.** For each one you either **run it yourself (self-hosted)** or **use a
   public instance** someone else runs. Either way you end up with a link — the addon URL — to
   paste into Nuvio:
   - **Watchly** ([github.com/TimilsinaBimal/Watchly](https://github.com/TimilsinaBimal/Watchly)) —
     **Top Picks for You** and **Because you watched …** rows, built from your watch history.
   - **AIOMetadata** ([github.com/cedya77/aiometadata](https://github.com/cedya77/aiometadata)) —
     the catalogs and the metadata behind the folder layout.
   - **AIOStreams** ([github.com/Viren070/AIOStreams](https://github.com/Viren070/AIOStreams)) —
     the stream list Nuvio plays from.
   - **OpenSubtitles v3** — subtitles. An official addon hosted by Stremio, with no public repo;
     there is nothing to run yourself, you just install it.
4. **Your own API keys** — the catalogs here are built from **TMDB, TVDB and MDBList**; use a free
   **Gemini** API key (or other AI provider) for personal recommendations.

> **If you're using a public instance, read this.** Public instances work well and are the quick
> way in, but each one decides what it allows — some disable particular sources (a tracker addon,
> or peer-to-peer streams). **If a source that should be there doesn't show up, try another public
> instance or self-host that addon.** The file itself is fine.

## The files

| file | goes into | what it is |
|---|---|---|
| `watchly.json` | Nuvio → **Add addon** | the recommendation rows — *Top Picks for You* and *Because you watched …*, built from your own watch history |
| `collections.json` | Nuvio → **Import collections** | the folder layout — the Streaming Services, Genres, Decades and Collections folders you browse in Nuvio |
| `badge.json` | Nuvio web → **Fusion badge URLs** | the badge pack Nuvio prints on every stream |
| `aiometadata.json` | AIOMetadata → **Import & Export** | the catalogs that fill those folders with movies and series |
| `aiostreams.json` | AIOStreams → **Save & Install** | the streams — which sources to search and what quality to keep (or `aiostreams-a.json`, the personal variant; import **one**, not both) |

**You need all five**: `watchly.json`, `aiostreams.json`, `aiometadata.json`, `collections.json`
and `badge.json`.

What's in them:

- **`collections.json`** — 4 top folders, 112 sub-folders, 266 rows, every row wired to a catalog
  above by id:
  - **Streaming Services** (8) — one folder per service, each with **New · Popular · Top Rated ·
    Originals** rows for movies and series.
  - **Genres** (22) — one folder per genre, each carrying its own mix of movie and series rows.
  - **Decades** (6) — the 20s to the 70s, a popular-movies list + a popular-series catalog each.
  - **Collections** (76) — [TVDB lists](https://www.thetvdb.com/lists/), with popular franchises
    grouped together.
- **`badge.json`** — 100 badges in 10 groups, all with art — resolution, source, quality, HDR,
  audio, channels, encoder and streaming service, so you can tell what a release is at a glance.
  All 100 are mirrored in [`images/badges/`](images/badges).
- **`aiometadata.json`** — 423 catalogs (tmdb 158, mdblist 154, tvdb 108, mal 2, anilist 1), with
  the names, tags and poster art the folders ask for.
- **`aiostreams.json` / `aiostreams-a.json`** — the Tamtaro SEL filtering stack over 7 sources
  (Comet, StremThru Torz, Meteor, Torrentio, Knaben, Zilean and a library source): dedup, size
  floors, and a hard cap of **3× best 4K + 3× best 1080p + 1 small mobile row last**. The (A) file
  adds a Prowlarr source.

Everything `collections.json` and `badge.json` point at — tiles, posters, badges — lives in
[`images/`](images/) in this repo, served from GitHub so a TV client can fetch it with no login.
Fork it, host `images/` yourself, and swap the host in those URLs.

## Assemble it — step by step

### Start with Watchly

Open your Watchly instance — the one you self-host, or a public instance — and press **Get
started** → **Sign in** with **Nuvio**. Choose which recommendation rows you want — the recommended
set is a fine start — then press **Save & install** → **Nuvio** (or copy the addon `watchly.json`
link to Nuvio manually).

Install it as its **own addon**, separate from AIOMetadata and AIOStreams, and keep it **first**
in your Nuvio addon list — that is what puts its rows **above the collections**.

### AIOMetadata

Open your AIOMetadata instance (self-hosted or public) → **Import & Export → Import
Configuration** and upload `aiometadata.json`. This replaces your whole configuration. Then add
your own API keys (every key in the file is blank) and save. Copy the **manifest URL** — that is
the addon URL you paste into Nuvio further down.

### AIOStreams

Open your AIOStreams instance → **Save & Install** → import `aiostreams.json` (or
`aiostreams-a.json` if you want the personal (A) setup — pick one). Then add your debrid
credentials: **Services** → enable your service → paste your API key. Add your **TMDB** token too.
Save and copy the manifest URL. *(If you imported the (A) file and don't run Prowlarr, turn that
source off.)*

The Comet and StremThru Torz presets inside the file point at public instances. Add your own key,
or point them at your own instance, if you want cached results from them too.

### Nuvio

Open Nuvio web — [nuvio.tv/account?tab=addons](https://nuvio.tv/account?tab=addons) → **Add addon**
→ paste your addon URLs. The finished setup is **four addons, in this order**:

1. **Watchly** — first, so its rows sit above the collections
2. **AIOMetadata** — the manifest URL you copied above
3. **AIOStreams** — the manifest URL you copied above
4. **OpenSubtitles v3** — subtitles, official and hosted by Stremio:
   `https://opensubtitles-v3.strem.io/manifest.json`

Then import `collections.json` (Nuvio → **Import collections**) to get the folder layout.

### Badges

In **Nuvio web**, under **System**:

- **TV**: System → **TV Settings** → Layout → Fusion badge URLs
- **Mobile**: System → **Mobile Settings** → Streams → Fusion badge URLs

Paste this URL wherever a *Fusion badge URL* is asked for
("Import Fusion-style stream badge JSON from a URL"):

```
https://raw.githubusercontent.com/antonangel/nuvio-template/main/badge.json
```

If the badges don't show up, set the same URL inside the client itself:

- **Nuvio desktop**: Settings → General → Streams → Fusion badge URLs
- **Nuvio iOS**: Settings → Layout → Streams → Fusion badge URLs
- **Nuvio TV**: Settings → Layout → Streams → Fusion badge URLs

## If something looks wrong

- **Nothing plays, or every result is an uncached torrent that won't start** — you haven't added a
  debrid key in AIOStreams (**Services**), or your debrid plan has lapsed.
- **"Invalid configuration file"** — you're in the wrong importer. `collections.json` is a *Nuvio*
  file; AIOMetadata takes `aiometadata.json`.
- **Folders are empty, missing, or in the wrong order** — collections only work in Nuvio, so
  re-import `collections.json` there, and check that **Watchly is the first addon** in your list.
- **Badges don't render** — the badge URL has to be set in *both* places: Nuvio web **and** the
  client (see *Badges* above).
- **A source you expected is missing** — your public instance disables it; try another public
  instance or self-host that addon.

## License

MIT for the configuration files and this README — see [`LICENSE`](LICENSE). The artwork and the
service names and marks referenced here belong to their owners and are not covered by it.
