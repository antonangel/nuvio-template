# nuvio-template

A complete **Nuvio** setup you can import in about ten minutes: four addons cover catalogs, streams,
recommendations and subtitles. Import the files, install the addons, and everything is set.

**Everything runs on my instances.** You don't self-host anything and you don't need a debrid
account — but you will create four free API keys (TMDB, TVDB, MDBList and Gemini) in step 5.
Catalogs, streams and recommendations are handled for you.

> These instances are shared privately with friends. Please don't post the links publicly — anyone
> with the URL can use them.

## What you need first

1. **Nuvio** — [nuvio.tv](https://nuvio.tv), on the device you watch on.

## Set it up

### 1. Create your Nuvio account

Open [nuvio.tv](https://nuvio.tv) and create an account.

### 2. Clean up the default addons

Go to Nuvio → **Addons**. Delete the **Nuvio Catalog** addon. Keep **OpenSubtitles**.

### 3. Import the collections

Nuvio → **Collections** → **Import collections** → paste or upload `collections.json`.

This builds the Streaming Services, Genres, Decades and Collections folders. The rows fill in once
AIOMetadata is installed in step 7.

### 4. Import the badges

In **Nuvio web**, open **System**:

- **TV** → TV Settings → Layout → **Fusion badge URLs**
- **Mobile** → Mobile Settings → Streams → **Fusion badge URLs**

Paste this URL where it asks for a Fusion badge JSON URL:

```
https://raw.githubusercontent.com/antonangel/nuvio-template/main/badge.json
```

### 5. Get your API keys

Create four free accounts and keep the keys handy — you will paste them into Watchly and
AIOMetadata:

1. **TMDB** — [themoviedb.org/settings/api](https://www.themoviedb.org/settings/api) → request an
   API key, then copy the **API Key (v3 auth)**.
2. **TVDB** — [thetvdb.com/dashboard/account/apikey](https://thetvdb.com/dashboard/account/apikey)
   → create an API key.
3. **MDBList** — [mdblist.com/preferences](https://mdblist.com/preferences) → copy the API key.
4. **Google Gemini** — [aistudio.google.com/api-keys](https://aistudio.google.com/api-keys) →
   create an API key.

All four are free. Nothing else in this setup needs a key.

### 6. Install Watchly

Open [watchly.angel.is](https://watchly.angel.is) → **Get started** → **Sign in** with Nuvio.

Keep every preference at its default.

Scroll down to the **API keys** section and paste your **TMDB** key (step 5).

In the **Posters** section, change the rating provider to **custom provider** and paste this URL —
use the copy button in the corner of the box:

```
https://posters.angel.is/poster?shape={shape}&top_gradient=medium&top_vignette_sash_only=true&sash_mode=notch&landscape_vignette_poster_color_top=0&landscape_vignette_poster_color_bottom=0&landscape_hide_year=1&landscape_sash_mode=sash&badge_pos=top_left&landscape_score_out_of_10=true&landscape_rating_separator=star&landscape_badge_shape=chip&landscape_winner_star=true&landscape_badge_glass_opacity=0.80&fallback_to_imdb=true&imdb_rating_source=dataset&tmdb_rating_source=direct&rating_display_mode=2&numeric_score_font_size_ratio=0.070&numeric_score_y_offset=0.91&score_out_of_10=true&movie_weights=lb:.3,tk:.1,rt:.25,pc:.35&tv_weights=tk:.1,rt:.35,pc:.45,im:.1&fallback_bg_style=photoreal&logo_max_h_ratio=0.20&logo_bottom_ratio=0.21&logo_bottom_anchor=true&cinema_greyscale=false&hide_unreleased_rating=true&sash_winner_star=true&sash_badge_size_w=1.00&sash_badge_size_h=0.90&sash_badge_font_ratio=0.45&sash_badge_frost_opacity=0.35&sash_badge_pos=left&sash_priority=wins,gg_wins,festival,pic_noms,metacritic,gg_noms,trending,trending_broad,premiere,new_release,just_added,new_season,season_finale,studio,director,watchlist,cast,blockbuster,cult,foreign,true_story,short_film,mini_series,binge_ready,returning,airing,cancelled,ended,physical,streaming,cinema,production,renewed&landscape_sash_priority=wins,gg_wins,festival,pic_noms,metacritic,gg_noms,premiere,new_release,just_added,new_season,season_finale,studio,director,watchlist,cast,blockbuster,cult,foreign,true_story,short_film,mini_series,binge_ready,returning,airing,cancelled,ended,physical,streaming,cinema,production,renewed,-trending,-trending_broad&badge_display_mode=7&badge_group1=chip:4:res,video,audio:22:0.01&badge_group2=below_logo:4:network,studio:20&badge_group3=chip:4:cinema:45&landscape_badge_display_mode=7&landscape_badge_group2=above_logo:4:network,studio&quality_after_digital=true&badge_cinema_style=frosted&badge_quality_style=frosted&wait_for_quality=true&imdb_id={imdb_id}&type={type}&access_key=IMnf1Y6BFE5zFdtoyQ6N72rfDf9PutMtemVi1zLHAz8
```

Then add your **Google Gemini** key and, in the model field, type
`gemini-3.5-flash`.

On the next page, **Catalogues**, keep the defaults on: **For you**, **Because you watched**, and
the genre and keyword rows.

Press **Save & Install**, then the **Nuvio** button.

### 7. Import the AIOMetadata setup

Open [aiometadata.angel.is/configure](https://aiometadata.angel.is/configure). On the
first page, scroll to the bottom and choose **Import a setup**. Paste this link:

```
https://raw.githubusercontent.com/antonangel/nuvio-template/main/aiometadata-setup.json
```

Review the lineup, then apply it. That fills the collection folders with catalogs.

Then open the **API keys** section and paste your **TMDB**, **TVDB** and **MDBList**
keys from step 5, and save. That keeps each account on its own free limits.

Next, set the posters: **Art Providers → Art URL Overrides**, choose **Custom Art
URLs**, and paste the same `posters.angel.is` address you used in step 6.

Copy the **manifest URL** it gives you, then add it in Nuvio: **Add addon** → paste →
install.

### 8. Import AIOStreams

Open [aiostreams.angel.is](https://aiostreams.angel.is) → **Save & Install** → **Import Config** →
upload `aiostreams.json`.

Debrid is already wired to the shared account on the instance — **don't add a key of your own**.

Save, copy the **manifest URL**, and add it in Nuvio the same way.

### 9. Sort the addons

Nuvio → **Addons**. The finished order is:

1. **Watchly**
2. **AIOMetadata**
3. **AIOStreams**
4. **OpenSubtitles**

The order is content, not cosmetics: Watchly first is what puts *Top Picks for You* and *Because
you watched …* above the collections.

### 10. If badges don't show

Set the same badge URL inside the client itself:

- **Desktop**: Settings → General → Streams → Fusion badge URLs
- **iOS**: Settings → Layout → Streams → Fusion badge URLs
- **TV**: Settings → Layout → Streams → Fusion badge URLs

## The files

| file | goes into | what it is |
|---|---|---|
| `watchly.json` | Nuvio → **Add addon** | the recommendation addon — *Top Picks for You* and *Because you watched …*, built from your own watch history. There is no file to import: you install it from the link in step 6. |
| `collections.json` | Nuvio → **Import collections** | the folder layout — the Streaming Services, Genres, Decades and Collections folders you browse in Nuvio |
| `badge.json` | Nuvio web → **Fusion badge URLs** | the badge pack Nuvio prints on every stream |
| `aiometadata.json` | AIOMetadata → **Import & Export** | the catalogs that fill those folders with movies and series |
| `aiostreams.json` | AIOStreams → **Save & Install** | the streams — which sources to search and what quality to keep |

`aiostreams-a.json` is my personal variant of the streams config (it adds a private Prowlarr
source). **Don't import it** — use `aiostreams.json`.

Everything `collections.json` and `badge.json` point at — tiles, posters, badges — lives in
[`images/`](images/) in this repo, served from GitHub so a TV client can fetch it with no login.

## What's inside

- **`collections.json`** — 4 top folders, 112 sub-folders, 266 rows, every row wired to a catalog
  in `aiometadata.json` by id:
  - **Streaming Services** (8) — one folder per service, each with New · Popular · Top Rated ·
    Originals rows for movies and series.
  - **Genres** (22) — one folder per genre, each carrying its own mix of movie and series rows.
  - **Decades** (6) — the 20s to the 70s, a popular-movies list and a popular-series catalog each.
  - **Collections** (76) — [TVDB lists](https://www.thetvdb.com/lists/), with popular franchises
    grouped together.
- **`badge.json`** — 100 badges in 10 groups, all with art: resolution, source, quality, HDR,
  audio, channels, encoder and streaming service, so you can tell what a release is at a glance.
- **`aiometadata.json`** — 423 catalogs (tmdb 158, mdblist 154, tvdb 108, mal 2, anilist 1), with
  the names, tags and poster art the folders ask for.
- **`aiostreams.json`** — the stream list: seven sources (Library, Meteor, Comet, StremThru Torz,
  Torrentio, Knaben, Zilean), deduplicated, with quality filtering and a short result list.

Each person imports their own copy, so your settings and watch history stay yours. Streams use the
shared debrid account.

## If something looks wrong

- **Nothing plays, or every result is an uncached torrent that won't start** — tell me. The shared
  debrid is one account, so a stream that isn't cached yet can take a minute to start.
- **"Invalid configuration file"** — you're in the wrong importer. `collections.json` is a *Nuvio*
  file; AIOMetadata takes `aiometadata.json`.
- **Folders are empty or missing** — re-import `collections.json` in Nuvio, and check that the
  AIOMetadata addon is installed. Collections only work in Nuvio.
- **Recommendation rows are missing** — Watchly has to be installed and signed in, and first in
  the addon list.
- **Badges don't render** — the badge URL has to be set in *both* places: Nuvio web **and** the
  client (see step 10).
- **No streams in the list** — the AIOStreams addon is missing or sits after a disabled one; check
  the order in step 9.

## License

MIT for the configuration files and this README — see [`LICENSE`](LICENSE). The artwork and the
service names and marks referenced here belong to their owners and are not covered by it.
