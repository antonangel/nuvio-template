#!/usr/bin/env python3
"""Match the awards and actors art families to catalogs.

    python3 tools/match-extra.py            # write data/awards-*.json + data/actors-*.json
    python3 tools/match-extra.py --dry      # review table only

Awards are mdblist lists (auto-matched, scored, under-confidence printed).
Actors are TMDB people resolved to a person id and served as discover catalogs
(`with_cast`), which is deterministic — no list has to exist for an actor.
Keys: $MDBLIST_KEY / $TMDB_KEY, else read from the live AIO profile.
"""
import csv, hashlib, json, os, re, sqlite3, struct, sys, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ART_BASE = "https://raw.githubusercontent.com/adamswlon/nuvio-collections-art/main/images/"
CONFIDENT = 95
# Slug -> (list id, why). Value None = drop the folder (no list worth pinning).
AWARD_OVERRIDES = {
    "golden-globes": (146627, "923-item winners list; search only surfaced per-category lists (49-84 items)"),
    "fisa": None,
}
AWARDS_BASE = ART_BASE + "awards/"
ACTORS_BASE = ART_BASE + "actors/"


def keys():
    out = {"mdblist": os.environ.get("MDBLIST_KEY"), "tmdb": os.environ.get("TMDB_KEY")}
    if not all(out.values()):
        con = sqlite3.connect("file:/home/angel/homelab/docker/data/stremio-addons/aiometadata/db.sqlite?mode=ro", uri=True)
        for (cfg,) in con.execute("select config_data from user_configs"):
            ak = json.loads(cfg).get("apiKeys") or {}
            out["mdblist"] = out["mdblist"] or ak.get("mdblist")
            out["tmdb"] = out["tmdb"] or ak.get("tmdb")
    if not all(out.values()):
        raise SystemExit("need MDBLIST_KEY and TMDB_KEY")
    return out


def fetch(url, tries=3):
    last = None
    for i in range(tries):
        try:
            data = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "curl/8"}), timeout=30))
            time.sleep(0.15)
            return data
        except Exception as e:
            last = e
            time.sleep(1.5 * (i + 1))
    raise SystemExit(f"fetch failed: {url.split('?')[0]}: {last}")


def norm(s):
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def award_score(r, title):
    n, nt = norm(r["name"]), norm(title)
    v = 100 if n == nt else 95 if n == nt + "winners" else 75 if (n.startswith(nt) or nt.startswith(n)) else 40
    return v + min(r["items"], 200) / 20 - (50 if r["items"] < 3 else 0)


def jpeg_size(path):
    data = path.read_bytes()
    i = 2
    while i < len(data) - 9:
        if data[i] != 0xFF:
            i += 1
            continue
        m = data[i + 1]
        if m in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            h, w = struct.unpack(">HH", data[i + 5:i + 9])
            return w, h
        if m in (0xD8, 0xD9) or 0xD0 <= m <= 0xD7:
            i += 2
            continue
        i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
    raise SystemExit(f"{path.name}: no JPEG dimensions")


def shape_for(path):
    w, h = jpeg_size(path)
    ar = w / h
    return "LANDSCAPE" if ar >= 1.2 else "POSTER" if ar <= 0.85 else "SQUARE"


def hex8(s):
    return hashlib.md5(s.encode()).hexdigest()[:8]


def award_catalog(r):
    return {"id": f"mdblist.{r['id']}", "type": r.get("mediatype") or "movie", "name": r["name"], "source": "mdblist",
            "enabled": True, "showInHome": False, "sort": "default", "order": "asc", "cacheTTL": 86400,
            "enableRatingPosters": True, "genreSelection": "standard",
            "metadata": {"url": f"https://mdblist.com/lists/{r['user_name']}/{r.get('slug') or ''}",
                         "author": r["user_name"], "itemCount": r["items"], "mediatype": r.get("mediatype") or "movie"}}


def discover_catalog(kind, slug, label, params):
    return {"id": f"tmdb.discover.{kind}.{slug}.{hex8(slug + kind)}", "type": kind, "name": label, "source": "tmdb",
            "enabled": True, "showInHome": False, "cacheTTL": 21600,
            "metadata": {"description": f"TMDB Discover ({kind})",
                         "discover": {"version": 2, "source": "tmdb",
                                      "mediaType": "tv" if kind == "series" else "movie", "params": params}}}


def folder(slug, title, base, shape, sources, prefix=""):
    return {"id": f"018f-{prefix}{slug}", "title": title, "tileShape": shape, "hideTitle": True, "_coverMode": "image",
            "coverImageUrl": base + slug + ".jpg", "catalogSources": sources}


def main():
    dry = "--dry" in sys.argv
    k = keys()
    rows, cat_out, fol_out = [], {}, {}

    # ---- awards: mdblist lists -------------------------------------------------
    # One winners list is not a hub. A curator's award *family* is: qjao's twenty
    # "Academy Award for Best X" lists are what the Oscars tile should carry. So: find
    # the curator with the most lists matching the award, pull their whole family, and
    # fall back to the single best list when no family exists.
    AWARD_FAMILIES = {
        "oscars": ("academy award", "Academy Award"),
        "bafta": ("bafta", "BAFTA"),
        "cannes": ("cannes", "Cannes"),
        "emmy": ("emmy", "Emmy"),
        "golden-globes": ("golden globe", "Golden Globe"),
        "venice-film-festival": ("venice", "Venice Film Festival"),
    }
    AWARD_TITLES = {"oscars": "Academy Awards", "emmy": "Emmy Awards", "golden-globes": "Golden Globes",
                    "bafta": "BAFTA", "cannes": "Cannes", "venice-film-festival": "Venice Film Festival"}
    aw_slugs = sorted(p.stem for p in (ROOT / "assets/awards").glob("*.jpg"))
    acats, afolders = [], []
    for slug in aw_slugs:
        title = AWARD_TITLES.get(slug, slug.replace("-", " ").title())
        fam_lists, pinned = [], []
        if slug in AWARD_FAMILIES:
            kw, seed = AWARD_FAMILIES[slug]
            nkw = norm(kw)
            cands = {}
            for q in (seed, kw + " winners", kw + " award"):
                for r in fetch(f"https://api.mdblist.com/lists/search?query={urllib.parse.quote(q)}&apikey={k['mdblist']}"):
                    cands[r["id"]] = r
            fam = [r for r in cands.values() if nkw in norm(r["name"])]
            counts = {}
            for r in fam:
                counts[r["user_name"]] = counts.get(r["user_name"], 0) + 1
            top = max(counts, key=lambda u: counts[u]) if counts else None
            if top and counts[top] >= 3:
                r = fetch(f"https://api.mdblist.com/lists/user/{urllib.parse.quote(top)}?apikey={k['mdblist']}")
                alluser = r if isinstance(r, list) else r.get("lists", [])
                fam_lists = sorted((x for x in alluser if nkw in norm(x["name"])), key=lambda x: x["name"])
            if len(fam_lists) < 2:
                fam_lists = []
                if fam:
                    fam_lists = [max(fam, key=lambda r: r["items"])]
        if slug in AWARD_OVERRIDES:
            ov = AWARD_OVERRIDES[slug]
            if ov is None and not fam_lists:
                print(f"  awards {slug:<22} -> skipped (no list worth pinning)")
                continue
            if ov is not None:
                r = fetch(f"https://api.mdblist.com/lists/{ov[0]}?apikey={k['mdblist']}")
                pinned = [r[0] if isinstance(r, list) else r]
        if not fam_lists and not pinned:
            print(f"  awards: NO MATCH for {slug}")
            continue
        lists = fam_lists + [p for p in pinned if p.get("id") not in {x["id"] for x in fam_lists}]
        for x in lists:
            acats.append(award_catalog(x))
        afolders.append(folder(slug, title, AWARDS_BASE, shape_for(ROOT / f"assets/awards/{slug}.jpg"),
                               [{"addonId": "aio-metadata", "type": "series" if x.get("mediatype") in ("show", "series") else "movie",
                                 "catalogId": f"mdblist.{x['id']}"} for x in lists], prefix="aw-"))
        for x in lists:
            rows.append({"family": "awards", "slug": slug, "catalogId": f"mdblist.{x['id']}", "name": x["name"],
                         "uid": x["user_name"], "items": x["items"], "score": 100,
                         "review": "yes" if x["items"] < 3 else ""})
        print(f"  awards {slug:<22} -> {len(lists)} lists, top curator "
              f"{lists[0]['user_name'] if lists else '-'}: {', '.join(x['name'][:26] for x in lists[:3])}...")
    cat_out["awards"], fol_out["awards"] = acats, afolders

    # ---- actors: TMDB people -> with_cast discover catalogs --------------------
    ac_slugs = sorted(p.stem for p in (ROOT / "assets/actors").glob("*.jpg"))
    ccats, cfolders = [], []
    for slug in ac_slugs:
        name = slug.replace("-", " ")
        res = fetch(f"https://api.themoviedb.org/3/search/person?query={urllib.parse.quote(name)}&api_key={k['tmdb']}")
        people = res.get("results") or []
        pick = next((p for p in people if norm(p["name"]) == norm(name)), people[0] if people else None)
        if not pick:
            print(f"  actors: NO PERSON for {slug}")
            continue
        base_params = {"with_cast": pick["id"], "sort_by": "popularity.desc", "vote_count.gte": 20, "include_adult": "false"}
        ccats.append(discover_catalog("movie", slug, f"{pick['name']} — Movies", dict(base_params)))
        ccats.append(discover_catalog("series", slug, f"{pick['name']} — Series", dict(base_params)))
        cfolders.append(folder(slug, pick["name"], ACTORS_BASE, shape_for(ROOT / f"assets/actors/{slug}.jpg"), [
            {"addonId": "aio-metadata", "type": "movie", "catalogId": ccats[-2]["id"]},
            {"addonId": "aio-metadata", "type": "series", "catalogId": ccats[-1]["id"]}], prefix="ac-"))
        rows.append({"family": "actors", "slug": slug, "catalogId": ccats[-2]["id"], "name": pick["name"], "uid": pick["id"],
                     "items": pick.get("popularity"), "score": 100 if norm(pick["name"]) == norm(name) else 60,
                     "review": "" if norm(pick["name"]) == norm(name) else "yes"})
        print(f"  actors {slug:<26} -> tmdb person {pick['id']} {pick['name']!r} pop={pick.get('popularity')}")
    cat_out["actors"], fol_out["actors"] = ccats, cfolders

    if dry:
        return
    (ROOT / "data").mkdir(exist_ok=True)
    for family in cat_out:
        json.dump(cat_out[family], open(ROOT / f"data/{family}-catalogs.json", "w"), indent=2, ensure_ascii=False)
        json.dump(fol_out[family], open(ROOT / f"data/{family}-folders.json", "w"), indent=2, ensure_ascii=False)
    with (ROOT / "data/match-extra-report.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote data/{{awards,actors}}-{{catalogs,folders}}.json + match-extra-report.csv "
          f"({len(fol_out['awards'])} awards, {len(fol_out['actors'])} actors)")


if __name__ == "__main__":
    main()
