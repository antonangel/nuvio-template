#!/usr/bin/env python3
"""Wire the rich families onto AIO's own catalogs — no third-party addon involved.

    python3 tools/aio-wire.py

Writes, for streaming / genres / decades:
    data/aio-<family>-catalogs.json   AIO catalog entries (go into the setup export)
    data/sources-aio.json             {Collection/Folder: [catalogSources]} for the build

Streaming and genres are tmdb.discover catalogs, which AIO serves itself. Decades are
the nobnobz mdblist lists from the design (one per decade, movies).

Note on ids: AIO's manifest renames its fixed tmdb catalogs by type — a config entry
`tmdb.top` is served as `tmdb.top_movie` / `tmdb.top_series`. Collection sources must
use the served (suffixed) ids, which is what data/discover-folders.json does.
"""
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGION = "US"  # Hulu/Peacock don't exist in CA; the kit's providers are US catalogues

PROVIDERS = {"Netflix": 8, "Disney+": 337, "Apple TV": 350, "Prime Video": 9, "HBO Max": 1899,
             "Hulu": 15, "Paramount+": 2303, "Peacock": 386, "Starz": 43, "Shudder": 99, "Adult Swim": 318}
# "Originals" on the movie side: TMDB has no originals flag, so this is the provider's
# own production arm (verified per id — the ones with a thin or wrong set are omitted
# rather than shipped as a near-empty tile).
ORIGINALS_COMPANY = {"Netflix": "178464|185004", "Prime Video": "210099", "Apple TV": "194232",
                     "HBO Max": "7429", "Adult Swim": "6760"}
NETWORK_IDS = {"Netflix": 213, "Disney+": 2739, "Apple TV": 2552, "Prime Video": 1024, "HBO Max": 3186,
               "Hulu": 453, "Paramount+": 4330, "Peacock": 3353, "Starz": 318, "Shudder": 2949, "Adult Swim": 80}
GENRES = {  # our folder title -> (movie genre id, tv genre id)
    "Action": (28, 10759), "Animation": (16, 16), "Comedy": (35, 35),
    "Crime": (80, 80), "Documentary": (99, 99), "Drama": (18, 18), "Family": (10751, 10751),
    "History": (36, 36), "Horror": (27, 27), "Mystery": (9648, 9648),
    "Romance": (10749, 10749), "Sci-Fi": (878, 10765), "Thriller": (53, None),
    "Reality TV": (None, 10764), "Nature": (99, 99),
}
KEYWORDS = {"Anime": "210024"}  # TMDB keyword; no genre id covers anime
DECADES = {"20s Movies": 158796, "10s Movies": 158791, "00s Movies": 158792,
           "90s Movies": 158793, "80s Movies": 158794, "70s Movies": 158795}


def slug(s):
    return "".join(c if c.isalnum() else "-" for c in s.lower()).strip("-")


def hex8(s):
    return hashlib.md5(s.encode()).hexdigest()[:8]


def catalog(kind, cid_slug, label, params):
    return {"id": f"tmdb.discover.{kind}.{cid_slug}.{hex8(cid_slug + kind)}", "type": kind, "name": label,
            "source": "tmdb", "enabled": True, "showInHome": False, "cacheTTL": 21600,
            "metadata": {"description": f"TMDB Discover ({kind})",
                         "discover": {"version": 2, "source": "tmdb", "mediaType": "tv" if kind == "series" else "movie",
                                      "params": params}}}


def base_params():
    return {"include_adult": "false", "vote_count.gte": 50, "sort_by": "popularity.desc"}


def axes_for(title, kind, seed, extra=""):
    """New / Popular / Top-rated for one kind, in the order the pills should read."""
    kind_slug = slug(title) + extra
    out = []
    q = base_params()
    q["sort_by"] = "first_air_date.desc" if kind == "series" else "primary_release_date.desc"
    q["vote_count.gte"] = 10
    out.append(catalog(kind, kind_slug + "-new", f"{title} — New", q))
    out.append(catalog(kind, kind_slug, f"{title} — Popular", base_params()))
    r = base_params()
    r["sort_by"] = "vote_average.desc"
    r["vote_count.gte"] = 300
    out.append(catalog(kind, kind_slug + "-toprated", f"{title} — Top Rated", r))
    return out


def provider_catalogs():
    cats, srcs = [], {}
    for title, pid in PROVIDERS.items():
        plist = []
        per_kind = {kind: axes_for(title, kind, pid) for kind in ("movie", "series")}
        for i in range(3):  # interleave: New movies, New series, Popular movies, … as asked
            for kind in ("movie", "series"):
                c = per_kind[kind][i]
                c["metadata"]["discover"]["params"].update(
                    {"watch_region": REGION, "with_watch_providers": str(pid), "with_watch_monetization_types": "flatrate"})
                cats.append(c)
                plist.append({"addonId": "aio-metadata", "type": kind, "catalogId": c["id"]})
        nid = NETWORK_IDS.get(title)
        ocid = ORIGINALS_COMPANY.get(title)
        if ocid:
            om = catalog("movie", slug(title) + "-originals", f"{title} — Originals",
                         dict(base_params(), with_companies=ocid))
            cats.append(om)
            plist.append({"addonId": "aio-metadata", "type": "movie", "catalogId": om["id"]})
        if nid:
            # Originals = the provider's own network, narrowed to what it streams itself.
            o = catalog("series", slug(title) + "-originals", f"{title} — Originals",
                        dict(base_params(), watch_region=REGION, with_watch_providers=str(pid),
                             with_watch_monetization_types="flatrate", with_networks=str(nid)))
            cats.append(o)
            plist.append({"addonId": "aio-metadata", "type": "series", "catalogId": o["id"]})
        srcs[f"Streaming Services/{title}"] = plist
    return cats, srcs


def genre_catalogs():
    cats, srcs = [], {}
    for title, (mid, tid) in GENRES.items():
        plist = []
        per_kind = {}
        for kind, gid in (("movie", mid), ("series", tid)):
            if gid is None:
                continue
            for c in axes_for(title, kind, gid):
                c["metadata"]["discover"]["params"]["with_genres"] = str(gid)
                per_kind.setdefault(kind, []).append(c)
        for i in range(3):
            for kind in ("movie", "series"):
                if kind in per_kind and i < len(per_kind[kind]):
                    cats.append(per_kind[kind][i])
                    plist.append({"addonId": "aio-metadata", "type": kind, "catalogId": per_kind[kind][i]["id"]})
        if plist:
            srcs[f"Genres/{title}"] = plist
    for title, kw in KEYWORDS.items():
        plist = []
        for kind in ("movie", "series"):
            for c in axes_for(title, kind, kw):
                c["metadata"]["discover"]["params"]["with_keywords"] = kw
                cats.append(c)
                plist.append({"addonId": "aio-metadata", "type": kind, "catalogId": c["id"]})
        srcs[f"Genres/{title}"] = plist
    return cats, srcs


def decade_catalogs():
    """One nobnobz mdblist list per decade (movies), per the design."""
    cats, srcs = [], {}
    for title, lid in DECADES.items():
        c = {"id": f"mdblist.{lid}", "type": "movie", "name": title, "source": "mdblist",
             "enabled": True, "showInHome": False, "sort": "default", "order": "asc", "cacheTTL": 86400,
             "metadata": {"url": f"https://mdblist.com/lists/nobnobz/decades-{slug(title)}",
                          "author": "nobnobz", "itemCount": 250, "mediatype": "movie"}}
        cats.append(c)
        srcs[f"Decades/{title}"] = [{"addonId": "aio-metadata", "type": "movie", "catalogId": c["id"]}]
    return cats, srcs


def main():
    all_srcs = {}
    for family, fn in (("streaming", provider_catalogs), ("genres", genre_catalogs),
                       ("decades", decade_catalogs)):
        cats, srcs = fn()
        ids = [c["id"] for c in cats]
        assert len(ids) == len(set(ids)), f"duplicate catalog ids in {family}"
        json.dump(cats, open(ROOT / f"data/aio-{family}-catalogs.json", "w"), indent=2, ensure_ascii=False)
        all_srcs.update(srcs)
        print(f"  {family:<10} {len(cats):>3} catalogs  {len(srcs):>2} folders  "
              f"{len(cats) / max(len(srcs), 1):.1f} per folder")
    json.dump(all_srcs, open(ROOT / "data/sources-aio.json", "w"), indent=2, ensure_ascii=False)
    print(f"wrote data/aio-*-catalogs.json + data/sources-aio.json ({len(all_srcs)} folders, "
          f"{sum(len(v) for v in all_srcs.values())} sources)")


if __name__ == "__main__":
    main()
