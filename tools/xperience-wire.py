#!/usr/bin/env python3
"""Wire Xperience catalogs into our families, from the reference collections export.

    python3 tools/xperience-wire.py

Reads reference/xperience-manifest.json (the addon's 641 catalogs) and the reference
collections export, then writes:
    data/sources-xperience.json   {our folder title: [catalogSources]}  (streaming, genres, decades)
    data/studios-folders.json     the Studios collection (art-backed folders only)

Every catalog id is validated against the manifest — a typo would otherwise ship a
dead source. Titles are matched through ALIAS because the reference and the kit name
the same folder differently ("Apple TV+" vs "Apple TV").
"""
import json, re, shutil, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REF = Path("/home/angel/.hermes/profiles/atlas/cache/documents/doc_5525281abbd1_xperience-tets-collections.json")
MANIFEST = ROOT / "reference/xperience-manifest.json"
ART_BASE = "https://raw.githubusercontent.com/adamswlon/nuvio-collections-art/main/images/studios/"
STUDIOS_ART = {"Marvel": "marvel-studios.jpg", "DC": "dc.jpg", "A24": "a24.jpg", "Pixar": "pixar.jpg",
               "Studio Ghibli": "studio-ghibli.jpg", "Blumhouse": "blumhouse.jpg", "Dreamworks": "dreamworks.jpg"}
ALIAS = {"Apple TV": "Apple TV+", "Animation": "Animated", "Documentary": "Documentaries",
         "Thriller": "Thrillers", "Western": "Westerns", "Sci-Fi": "Sci-Fi", "Music": "Musicals",
         "Anime": "Anime", "K-Drama": "K-Drama", "Spy Thrillers": "Spy Thrillers",
         "20's Movies": "2020s", "10's Movies": "2010s", "00's Movies": "2000s", "90's Movies": "1990s",
         "80's Movies": "1980s", "70's Movies": "1970s", "60's Movies": "1960s", "50's Movies": "1950s & Before"}
# Folders the reference doesn't carry but the addon does.
EXTRA = {"Dreamworks": ["studio_dreamworks_movies"]}


def norm(s):
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def main():
    manifest = json.loads(MANIFEST.read_text())
    addon = manifest["id"]
    ids = {c["id"] for c in manifest["catalogs"]}
    ref = json.loads(REF.read_text())
    by_title = {c["title"]: c for c in ref}

    def sources_for(family, title):
        c = by_title.get(family)
        if not c:
            return None
        want = norm(ALIAS.get(title, title))
        for f in c["folders"]:
            if norm(f["title"]) == want or norm(f["title"]).startswith(want):
                return [s for s in f.get("catalogSources", []) if s.get("addonId") == addon and s.get("catalogId") in ids]
        return None

    ours = json.loads((ROOT / "base/kit-collections.json").read_text())
    out, missed = {}, []
    FAMILY_COLLECTION = {"Streaming": "Streaming Services", "Genres": "Genres", "Decades": "Decades"}
    for family in ("Streaming", "Genres", "Decades"):
        coll = next((c for c in ours if c["title"] == FAMILY_COLLECTION[family]), None)
        if not coll:
            continue
        for f in coll["folders"]:
            srcs = sources_for(family, f["title"])
            if srcs:
                # Collection-scoped key: folder titles repeat across collections ("History"
                # is both a genre and a network), and an override keyed on the bare title
                # would silently re-point the wrong tile.
                out[f"{FAMILY_COLLECTION[family]}/{f['title']}"] = srcs
            else:
                missed.append(f"{family}/{f['title']}")
    (ROOT / "data").mkdir(exist_ok=True)
    json.dump(out, open(ROOT / "data/sources-xperience.json", "w"), indent=2, ensure_ascii=False)

    # Studios: only folders we have art for, sources straight from the reference family.
    studios, art_dir = [], ROOT / "assets/studios"
    art_dir.mkdir(parents=True, exist_ok=True)
    for title, art in STUDIOS_ART.items():
        srcs = sources_for("Studios", title)
        if not srcs and title in EXTRA:
            srcs = [{"addonId": addon, "type": "movie" if i.endswith("movies") else "series", "catalogId": i}
                    for i in EXTRA[title] if i in ids]
        if not srcs:
            continue
        p = art_dir / art
        if not p.exists():
            p.write_bytes(urllib.request.urlopen(urllib.request.Request(ART_BASE + art, headers={"User-Agent": "curl/8"}), timeout=60).read())
        studios.append({"id": "018f-st-" + norm(title), "title": title, "tileShape": "LANDSCAPE", "hideTitle": True,
                        "_coverMode": "image", "coverImageUrl": ART_BASE + art, "catalogSources": srcs})
    json.dump(studios, open(ROOT / "data/studios-folders.json", "w"), indent=2, ensure_ascii=False)

    print(f"wired {len(out)} folders to {addon}")
    for t, s in out.items():
        print(f"  {t:<22} {len(s)} sources")
    print(f"studios: {len(studios)} folders -> {', '.join(f['title'] for f in studios)}")
    if missed:
        print("no reference match (kept as-is):", ", ".join(missed))


if __name__ == "__main__":
    main()
