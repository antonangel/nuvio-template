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
DECADES = {"2020s": 2020, "2010s": 2010, "2000s": 2000, "1990s": 1990,
           "1980s": 1980, "1970s": 1970, "1960s": 1960}
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


def network_catalogs():
    """Series only, deliberately: TMDB's *movie* discover ignores with_networks (every id
    returns the same 20k-result set), so a 'network movies' row would be a lie. The ids
    come from the earlier network pass, which resolved them from the profile export."""
    old = json.loads((ROOT / "data/networks-catalogs.json").read_text())
    nets = {}
    for c in old:
        nets.setdefault(c["name"].split(" — ")[0], c["metadata"]["discover"]["params"]["with_networks"])
    cats, srcs = [], {}
    for title, nid in nets.items():
        plist = []
        for c in axes_for(title, "series", nid):
            c["metadata"]["discover"]["params"]["with_networks"] = str(nid)
            cats.append(c)
            plist.append({"addonId": "aio-metadata", "type": "series", "catalogId": c["id"]})
        srcs[f"Networks/{title}"] = plist
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
    """Four pills per decade, as specified: Popular movies, Popular series, Top rated
    movies, Top rated series. Slugs split movies/shows so the catalog names read right."""
    cats, srcs = [], {}
    for title, start in DECADES.items():
        plist = []
        lo, hi = f"{start}-01-01", f"{start + 9}-12-31"
        per_kind = {}
        for kind in ("movie", "series"):
            d1 = "primary_release_date" if kind == "movie" else "first_air_date"
            media = "Movies" if kind == "movie" else "Shows"
            stem = f"{slug(title)}-{'movies' if kind == 'movie' else 'shows'}"
            pop = catalog(kind, stem, f"{title} — Popular {media}", base_params())
            top = catalog(kind, stem + "-toprated", f"{title} — Top Rated {media}",
                          dict(base_params(), sort_by="vote_average.desc", **{"vote_count.gte": 300}))
            for c in (pop, top):
                p = c["metadata"]["discover"]["params"]
                p[f"{d1}.gte"], p[f"{d1}.lte"] = lo, hi
            per_kind[kind] = [pop, top]
        for i in range(2):
            for kind in ("movie", "series"):
                c = per_kind[kind][i]
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
                       ("decades", decade_catalogs), ("studios", studio_catalogs),
                       ("networks", network_catalogs)):
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
