#!/usr/bin/env python3
"""Wire the rich families onto AIO's own catalogs — no third-party addon involved.

    python3 tools/aio-wire.py

Writes, for streaming / genres / decades / studios:
    data/aio-<family>-catalogs.json   AIO catalog entries (go into the setup export)
    data/sources-aio.json             {Collection/Folder: [catalogSources]} for the build

Everything is a tmdb.discover catalog, which AIO serves itself: one mechanism, no
Xperience, no mdblist. The reference setup's richness comes from stacking axes on the
same provider/genre — base, latest, top-rated, kids — which is exactly what this does.
"""
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGION = "US"  # Hulu/Peacock don't exist in CA; the kit's providers are US catalogues

PROVIDERS = {"Netflix": 8, "Disney+": 337, "Apple TV": 350, "Prime Video": 9, "HBO Max": 1899,
             "Hulu": 15, "Paramount+": 2303, "Peacock": 386, "Starz": 43, "Shudder": 99, "Adult Swim": 318}
KIDS_PROVIDERS = {"Netflix", "Disney+", "Apple TV", "Prime Video", "HBO Max", "Hulu", "Paramount+", "Peacock"}
GENRES = {  # our folder title -> (movie genre id, tv genre id)
    "Action": (28, 10759), "Animation": (16, 16), "Comedy": (35, 35),
    "Crime": (80, 80), "Documentary": (99, 99), "Drama": (18, 18), "Family": (10751, 10751),
    "History": (36, 36), "Horror": (27, 27), "Mystery": (9648, 9648),
    "Romance": (10749, 10749), "Sci-Fi": (878, 10765), "Thriller": (53, None),
    "Reality TV": (None, 10764), "Nature": (99, 99),
}
KEYWORDS = {"Anime": "210024"}  # TMDB keyword; no genre id covers anime
DECADES = {"20's Movies": 2020, "10's Movies": 2010, "00's Movies": 2000, "90's Movies": 1990,
           "80's Movies": 1980, "70's Movies": 1970, "60's Movies": 1960}
STUDIOS = {  # title -> (movie company id, tv company id)
    "Marvel": (420, 420), "DC": (429, 429), "A24": (41077, None), "Pixar": (3, None),
    "Studio Ghibli": (10342, None), "Blumhouse": (3172, 68884), "Dreamworks": (7, 15258),
}
COLLECTION = {"Streaming Services": PROVIDERS, "Genres": GENRES, "Decades": DECADES, "Studios": STUDIOS}


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
    """The stacked axes: base, latest, top-rated (+ kids where it makes sense)."""
    kind_slug = slug(title) + extra
    out = []
    p = base_params()
    out.append(catalog(kind, kind_slug, f"{title} — {'Series' if kind == 'series' else 'Movies'}", dict(p)))
    q = base_params()
    q["sort_by"] = "first_air_date.desc" if kind == "series" else "primary_release_date.desc"
    q["vote_count.gte"] = 10
    out.append(catalog(kind, kind_slug + "-latest", f"{title} — Latest", q))
    r = base_params()
    r["sort_by"] = "vote_average.desc"
    r["vote_count.gte"] = 300
    out.append(catalog(kind, kind_slug + "-toprated", f"{title} — Top Rated", r))
    return out


def provider_catalogs():
    cats, srcs = [], {}
    for title, pid in PROVIDERS.items():
        plist = []
        for kind, media in (("movie", "movie"), ("series", "tv")):
            for c in axes_for(title, kind, pid):
                c["metadata"]["discover"]["params"].update(
                    {"watch_region": REGION, "with_watch_providers": str(pid), "with_watch_monetization_types": "flatrate"})
                cats.append(c)
                plist.append({"addonId": "aio-metadata", "type": kind, "catalogId": c["id"]})
            if title in KIDS_PROVIDERS:
                k = catalog(kind, slug(title) + "-kids", f"{title} — Kids",
                            dict(base_params(), watch_region=REGION, with_watch_providers=str(pid),
                                 with_watch_monetization_types="flatrate",
                                 with_genres=str(10762 if kind == "series" else 10751)))
                cats.append(k)
                plist.append({"addonId": "aio-metadata", "type": kind, "catalogId": k["id"]})
        srcs[f"Streaming Services/{title}"] = plist
    return cats, srcs


def genre_catalogs():
    cats, srcs = [], {}
    for title, (mid, tid) in GENRES.items():
        plist = []
        for kind, gid in (("movie", mid), ("series", tid)):
            if gid is None:
                continue
            for c in axes_for(title, kind, gid):
                c["metadata"]["discover"]["params"]["with_genres"] = str(gid)
                cats.append(c)
                plist.append({"addonId": "aio-metadata", "type": kind, "catalogId": c["id"]})
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
    cats, srcs = [], {}
    for title, start in DECADES.items():
        plist = []
        lo = "1950-01-01" if start is None else f"{start}-01-01"
        hi = "1959-12-31" if start is None else f"{start + 9}-12-31"
        for kind in ("movie", "series"):
            d1 = "primary_release_date" if kind == "movie" else "first_air_date"
            for c in axes_for(title, kind, start or 1950):
                p = c["metadata"]["discover"]["params"]
                p[f"{d1}.gte"], p[f"{d1}.lte"] = lo, hi
                cats.append(c)
                plist.append({"addonId": "aio-metadata", "type": kind, "catalogId": c["id"]})
        srcs[f"Decades/{title}"] = plist
    return cats, srcs


def studio_catalogs():
    cats, srcs = [], {}
    for title, (mid, tid) in STUDIOS.items():
        plist = []
        for kind, cid in (("movie", mid), ("series", tid)):
            if cid is None:
                continue
            for c in axes_for(title, kind, cid):
                c["metadata"]["discover"]["params"]["with_companies"] = str(cid)
                cats.append(c)
                plist.append({"addonId": "aio-metadata", "type": kind, "catalogId": c["id"]})
        srcs[f"Studios/{title}"] = plist
    return cats, srcs


def main():
    all_srcs = {}
    for family, fn in (("streaming", provider_catalogs), ("genres", genre_catalogs),
                       ("decades", decade_catalogs), ("studios", studio_catalogs)):
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
