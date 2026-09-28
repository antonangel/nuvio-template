#!/usr/bin/env python3
"""Match assets/collections/*.jpg to mdblist lists and emit the Franchises data.

    python3 tools/match-mdblist.py            # write data/franchises*.json + report
    python3 tools/match-mdblist.py --dry      # print the review table only

Key: $MDBLIST_KEY, else read from the live AIO profile (never printed).
Slug -> list is scored on name equality; anything under the confidence bar is
reported for review and is not silently trusted. tileShape comes from the real
image aspect (all upstream art is landscape), never from a guess.
"""
import csv, json, os, re, sqlite3, struct, sys, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ART = ROOT / "assets/collections"
ART_BASE = "https://raw.githubusercontent.com/adamswlon/nuvio-collections-art/main/images/collections/"
CONFIDENT = 95

# Hand-picked after review: slug -> (list id, why, query used to fetch its metadata)
OVERRIDES = {
    "james-bond": (7947, "already in AIO", "James Bond Movies"),
    "harry-potter": (102972, "already in AIO", "Harry Potter Collection"),
    "matrix": (125142, "already in AIO (The Matrix Collection)", "The Matrix Collection"),
    "mission-impossible": (42716, "already in AIO", "Mission Impossible Collection"),
    "jurassic-world": (120197, "already in AIO (Jurassic Park Collection)", "Jurassic Park Collection"),
    "terminator": (125458, "already in AIO", "Terminator Collection"),
    "pirates-of-the-carribbean": (82145, "already in AIO", "Pirates of the Caribbean Collection"),
    "lord-of-the-rings-hobbit": (94304, "already in AIO", "Lord of the Rings and Hobbit Collection"),
    "halloween": (153954, "auto-match hit a 1637-item list; this is the franchise", "Halloween Collection"),
    "avatar": (102983, "auto-match hit the 'Avatar' TV show; this is the films", "Avatar Collection"),
    "star-wars": (102975, "auto-match hit a 58-item series list", "Star Wars Collection"),
    "predator": (31302, "auto-match hit a 4-item list", "Predator Collection"),
    "oceans": (59854, "auto-match hit a 775-item style list", "Ocean's Collection"),
    "it": (153958, "auto-match hit a 100-item mixed list", "It Collection"),
    "fast-furious": (76743, "search needs 'fast and furious'", "Fast and Furious Collection"),
    "eberhofer-krimis": (139107, "only list for the franchise", "eberhofer"),
}
# Flagged for Angel: best guess shipped, wrong is cheap to fix.
REVIEW = ["marvel", "gremlins", "quarantine", "are-you-afraid-of-the-dark", "dexter"]


def api_key():
    if os.environ.get("MDBLIST_KEY"):
        return os.environ["MDBLIST_KEY"]
    db = "/home/angel/homelab/docker/data/stremio-addons/aiometadata/db.sqlite"
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    for (cfg,) in con.execute("select config_data from user_configs"):
        k = (json.loads(cfg).get("apiKeys") or {}).get("mdblist")
        if isinstance(k, str) and k:
            return k
    raise SystemExit("no mdblist key: set MDBLIST_KEY")


def search(q, key, _cache={}):
    """Cached + retried. A failed query aborts the run — silently matching nothing
    is how you ship a wrong catalog."""
    if q in _cache:
        return _cache[q]
    url = f"https://api.mdblist.com/lists/search?query={urllib.parse.quote(q)}&apikey={key}"
    last = None
    for attempt in range(3):
        try:
            data = json.load(urllib.request.urlopen(
                urllib.request.Request(url, headers={"User-Agent": "curl/8"}), timeout=30))
            _cache[q] = data
            time.sleep(0.2)
            return data
        except Exception as e:
            last = e
            time.sleep(1.5 * (attempt + 1))
    raise SystemExit(f"mdblist search failed for {q!r}: {last}")


def norm(s):
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def jpeg_size(path):
    """(w, h) straight from the SOF marker — no image library needed."""
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
    return None


def shape_for(path):
    size = jpeg_size(path)
    if not size:
        raise SystemExit(f"{path.name}: could not read JPEG dimensions")
    w, h = size
    ar = w / h
    return "LANDSCAPE" if ar >= 1.2 else "POSTER" if ar <= 0.85 else "SQUARE"


def score(title, r, known):
    n, nt = norm(r["name"]), norm(title)
    v = 0
    if n == nt:
        v += 100
    elif n == nt + "collection":
        v += 95
    elif n.startswith(nt) or nt.startswith(n):
        v += 75
    else:
        toks = {w for w in re.split(r"[^a-z0-9]+", title.lower()) if len(w) > 3}
        v += 55 * len(toks & set(re.split(r"[^a-z0-9]+", r["name"].lower()))) / max(1, len(toks))
    v += min(r["items"], 200) / 20
    if r["items"] < 3:
        v -= 50
    if norm(r["name"]) in known:
        v += 12
    return v


def queries(slug):
    """Query variants for a slug. Note the 'and' variant must come from the slug —
    once the dashes are spaces there is nothing left to split."""
    title = slug.replace("-", " ")
    return [title, title + " collection", slug.replace("-", " and ", 1)]


def main():
    dry = "--dry" in sys.argv
    key = api_key()
    known = {norm(c["name"]) for c in json.loads((ROOT / "base/aiometadata-setup.json").read_text())["config"]["catalogs"]}
    slugs = sorted(p.stem for p in ART.glob("*.jpg"))

    rows, collection, catalogs, review = [], [], [], []
    for slug in slugs:
        title = slug.replace("-", " ")
        want_id, why, oquery = OVERRIDES.get(slug, (None, None, None))
        pick, ranked = None, []
        if want_id:
            # Metadata by id, not by search: search is rate-limit-flaky and misses lists
            # whose name differs from the slug (e.g. slug jurassic-world -> list "Jurassic Park").
            try:
                rec = json.load(urllib.request.urlopen(urllib.request.Request(
                    f"https://api.mdblist.com/lists/{want_id}?apikey={key}",
                    headers={"User-Agent": "curl/8"}), timeout=30))
                pick = rec[0] if isinstance(rec, list) and rec else None
            except Exception as e:
                raise SystemExit(f"override {slug}: list {want_id} fetch failed: {e}")
            if not pick:
                raise SystemExit(f"override {slug}: list {want_id} not found")
        else:
            cands = {}
            for q in queries(slug):
                for r in search(q, key):
                    cands[r["id"]] = r
            ranked = sorted(cands.values(), key=lambda r: score(title, r, known), reverse=True)
            if ranked:
                pick = ranked[0]
                if score(title, pick, known) < CONFIDENT:
                    review.append((slug, pick, ranked[1:3]))
        if not pick:
            review.append((slug, None, []))
            continue

        cid, media = f"mdblist.{pick['id']}", pick.get("mediatype") or "movie"
        catalogs.append({
            "id": cid, "type": media, "name": pick["name"], "source": "mdblist", "enabled": True,
            "showInHome": False, "sort": "default", "order": "asc", "cacheTTL": 86400,
            "enableRatingPosters": True, "genreSelection": "standard",
            "metadata": {"url": f"https://mdblist.com/lists/{pick['user_name']}/{pick.get('slug') or ''}",
                         "author": pick["user_name"], "itemCount": pick["items"], "mediatype": media},
        })
        collection.append({
            "id": f"018f-{slug}",
            "title": pick["name"],
            "tileShape": shape_for(ART / (slug + ".jpg")),
            "hideTitle": True,
            "_coverMode": "image",
            "coverImageUrl": ART_BASE + slug + ".jpg",
            "catalogSources": [{"addonId": "aio-metadata", "type": media, "catalogId": cid}],
        })
        rows.append({"slug": slug, "image": slug + ".jpg", "catalogId": cid, "listName": pick["name"],
                     "author": pick["user_name"], "items": pick["items"], "type": media,
                     "tileShape": collection[-1]["tileShape"], "override": why or "",
                     "review": "yes" if slug in REVIEW else ""})

    print(f"matched {len(collection)}/{len(slugs)}")
    for slug, pick, alts in review:
        print(f"  review: {slug} -> {pick and (pick['id'], pick['name'], pick['items'])} alt={[(a['id'], a['name'], a['items']) for a in alts]}")
    if dry:
        return

    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data/franchises-catalogs.json").write_text(json.dumps(catalogs, indent=2, ensure_ascii=False) + "\n")
    (ROOT / "data/franchises-folders.json").write_text(json.dumps(collection, indent=2, ensure_ascii=False) + "\n")
    with (ROOT / "data/match-report.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print("wrote data/franchises-catalogs.json, data/franchises-folders.json, data/match-report.csv")


if __name__ == "__main__":
    main()
