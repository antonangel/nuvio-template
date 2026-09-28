#!/usr/bin/env python3
"""Build the Nuvio artifacts from base/ + curation.json.

    python3 build.py            # write dist/
    python3 build.py --check    # validate + print audit, no writes
    python3 build.py --net      # additionally HEAD-check every art URL
    python3 build.py --manifest <manifest.json>   # also test source resolution

base/ is the upstream kit, vendored verbatim and never edited.
curation.json is the overlay: art swaps and structural edits.
dist/ is generated — never hand-edit it.
"""
import csv, json, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ART_FIELDS = {"cover": "coverImageUrl", "logo": "titleLogoUrl", "hero": "heroBackdropUrl"}
SHAPES = {"POSTER", "LANDSCAPE", "SQUARE"}


def load():
    base = json.loads((ROOT / "base/kit-collections.json").read_text())
    setup = json.loads((ROOT / "base/aiometadata-setup.json").read_text())
    curation = json.loads((ROOT / "curation.json").read_text())
    return base, setup, curation


def build(base, setup, curation):
    """Apply the overlay. Returns (collections, aio_config, notes)."""
    notes = []
    edits = curation.get("edits", {})
    art, art_base = curation.get("art", {}), curation.get("art_base", "")

    titles = {f["title"] for c in base for f in c["folders"]}
    unknown = sorted(set(art) - titles)
    if unknown:
        raise SystemExit(f"curation.json art keys are not folder titles: {unknown}")

    collections = []
    for c in base:
        if c["title"] in edits.get("remove_collections", []):
            notes.append(f"removed collection {c['title']!r}")
            continue
        c = json.loads(json.dumps(c))
        folders = []
        for f in c["folders"]:
            if f["title"] in edits.get("remove_folders", []):
                notes.append(f"removed folder {c['title']}/{f['title']}")
                continue
            f["title"] = edits.get("rename_folders", {}).get(f["title"], f["title"])
            for role, field in ART_FIELDS.items():
                spec = art.get(f["title"], {}).get(role)
                if spec:
                    f[field] = spec if spec.startswith(("http://", "https://")) else art_base + spec
            folders.append(f)
        c["folders"] = folders
        collections.append(c)

    order = edits.get("reorder_collections") or []
    if order:
        idx = {t: i for i, t in enumerate(order)}
        collections.sort(key=lambda c: idx.get(c["title"], len(idx)))

    config = setup["config"]
    extra = list(curation.get("extra_catalogs", []))
    for path in curation.get("extra_catalogs_files", []):
        extra += json.loads((ROOT / path).read_text())
    have = {(c.get("type"), c.get("id")) for c in config.get("catalogs", [])}
    added = []
    for c in extra:
        key = (c.get("type"), c.get("id"))
        if key in have:
            continue  # already in the base config — the curated entry wins
        have.add(key)
        added.append(c)
    config["catalogs"] = config.get("catalogs", []) + added

    for spec in curation.get("extra_collections", []):
        entry = {k: v for k, v in spec.items() if k not in ("folders_file", "append_to")}
        if spec.get("folders_file"):
            entry["folders"] = json.loads((ROOT / spec["folders_file"]).read_text())
        target = next((c for c in collections if c.get("title") == spec.get("append_to")), None) if spec.get("append_to") else None
        if target is not None:
            have = {f.get("title"): f for f in target.get("folders", [])}
            merged = 0
            for f in entry["folders"]:
                cur = have.get(f.get("title"))
                if cur is None:
                    target["folders"].append(f)
                    continue
                # Same folder, better art: swap the art fields and re-point the sources
                # (the kit ships a few folders wired to addons this stack doesn't run).
                for k in ("coverImageUrl", "titleLogoUrl", "heroBackdropUrl", "tileShape"):
                    if f.get(k):
                        cur[k] = f[k]
                if f.get("catalogSources"):
                    cur["catalogSources"] = f["catalogSources"]
                merged += 1
            notes.append(f"appended {len(entry['folders']) - merged} folders to {target['title']!r}, merged {merged} onto existing tiles")
            continue
        collections.append(entry)
        notes.append(f"added collection {entry.get('title')!r} ({len(entry.get('folders', []))} folders)")

    for title, url in (curation.get("collection_backdrops") or {}).items():
        for c in collections:
            if c.get("title") == title:
                c["backdropImageUrl"] = url

    if curation.get("source_overrides_file"):
        ov = json.loads((ROOT / curation["source_overrides_file"]).read_text())
        counts = {}
        for c in collections:
            for f in c.get("folders", []):
                counts[f.get("title")] = counts.get(f.get("title"), 0) + 1
        hit, ambiguous = 0, []
        for c in collections:
            for f in c.get("folders", []):
                key = f"{c.get('title')}/{f.get('title')}"
                if key in ov:
                    f["catalogSources"] = ov[key]
                    hit += 1
                elif f.get("title") in ov:
                    # Bare-title key: only safe when the title is unique across collections.
                    if counts[f.get("title")] == 1:
                        f["catalogSources"] = ov[f["title"]]
                        hit += 1
                    else:
                        ambiguous.append(key)
        notes.append(f"re-pointed {hit} folders from {curation['source_overrides_file']}")
        if ambiguous:
            notes.append(f"AMBIGUOUS override keys ignored: {', '.join(ambiguous)}")

    for title, shape in (curation.get("collection_shapes") or {}).items():
        for c in collections:
            if c.get("title") == title:
                for f in c.get("folders", []):
                    f["tileShape"] = shape
                notes.append(f"{title}: tileShape -> {shape} on {len(c.get('folders', []))} folders")

    # The client validates viewMode strictly: the kit's own export carries FOLLOW_HOME,
    # which this version rejects ("invalid viewMode") for every collection it appears on.
    valid_viewmodes = {"TABBED_GRID", "ROWS", "FOLLOW_LAYOUT"}
    for c in collections:
        if c.get("viewMode") not in valid_viewmodes:
            notes.append(f"viewMode {c.get('viewMode')!r} -> FOLLOW_LAYOUT on {c['title']!r}")
            c["viewMode"] = "FOLLOW_LAYOUT"

    setup["version"] = curation.get("aio_version", setup.get("version"))
    setup["exportedAt"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    setup["metadata"]["apiKeysExcluded"] = True
    setup["metadata"]["totalCatalogs"] = len(config["catalogs"])
    setup["metadata"]["enabledCatalogs"] = sum(1 for c in config["catalogs"] if c.get("enabled") is not False)
    return collections, setup, notes, added


def verify(collections, setup, manifest=None, net=False, pending=()):
    """Hard checks. Returns (rows, problems, pending_hits)."""
    problems, pending_hits, rows = [], [], []
    seen_sources = set()
    for c in collections:
        for key in ("id", "title", "folders"):
            if not c.get(key):
                problems.append(f"collection missing {key}: {c.get('title')!r}")
        for f in c["folders"]:
            where = f"{c['title']}/{f['title']}"
            if not f.get("id") or not f.get("title"):
                problems.append(f"{where}: folder missing id/title")
            if f.get("tileShape") not in SHAPES:
                problems.append(f"{where}: bad tileShape {f.get('tileShape')!r}")
            srcs = f.get("catalogSources") or []
            if not srcs:
                problems.append(f"{where}: no catalogSources (renders empty in the client)")
            for s in srcs:
                if not all(s.get(k) for k in ("addonId", "type", "catalogId")):
                    problems.append(f"{where}: incomplete source {s}")
                    continue
                seen_sources.add((s["addonId"], s["type"], s["catalogId"]))
                if manifest and (s["addonId"], s["type"], s["catalogId"]) not in manifest:
                    triple = (s["addonId"], s["type"], s["catalogId"])
                    if any(matches(p, triple) for p in pending):
                        pending_hits.append(f"{where} <- {'|'.join(triple)}")
                    else:
                        problems.append(f"{where}: does not resolve -> {'|'.join(triple)}")
            if net:
                for field in ART_FIELDS.values():
                    url = f.get(field)
                    if url and not head_ok(url):
                        problems.append(f"{where}: {field} not fetchable -> {url}")
            rows.append({
                "collection": c["title"], "folder": f["title"], "tileShape": f["tileShape"],
                "sources": " ".join(f"{s['addonId']}|{s['type']}|{s['catalogId']}" for s in f["catalogSources"]),
                "cover": f.get("coverImageUrl") or "", "logo": f.get("titleLogoUrl") or "",
                "hero": f.get("heroBackdropUrl") or "",
            })

    cats = setup["config"]["catalogs"]
    dupes = {k for k in seen_keys(cats) if seen_keys(cats).count(k) > 1}
    if dupes:
        problems.append(f"AIO catalogs have duplicate (type,id): {sorted(dupes)}")
    for c in cats:
        if not c.get("id") or not c.get("type") or not c.get("source"):
            problems.append(f"AIO catalog incomplete: {c}")
    if not setup["metadata"].get("apiKeysExcluded"):
        problems.append("apiKeysExcluded must stay true — the file must carry no keys")
    return rows, problems, pending_hits


def seen_keys(cats):
    return [(c.get("type"), c.get("id")) for c in cats]


def head_ok(url):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, method="HEAD",
                                  headers={"User-Agent": "curl/8"}), timeout=20)
        return r.status == 200
    except Exception:
        return False


def matches(pattern, triple):
    return all(p == "*" or p == t for p, t in zip(pattern.split("|"), triple))


def load_manifest(path):
    """-> (addonId, {(addonId, type, catalogId)}). addonId is the manifest's own id,
    which is what the client keys sources off."""
    m = json.loads(Path(path).read_text())
    return m["id"], {(m["id"], c["type"], c["id"]) for c in m["catalogs"]}


def main():
    args = sys.argv[1:]
    check = "--check" in args
    net = "--net" in args
    addon_id, manifest = None, None
    if "--manifest" in args:
        addon_id, manifest = load_manifest(args[args.index("--manifest") + 1])
    xp = ROOT / "reference/xperience-manifest.json"
    if xp.exists():
        # Second addon, second manifest: a source is resolvable if either addon serves it.
        _, xtriples = load_manifest(xp)
        manifest = (manifest or set()) | xtriples

    base, setup_in, curation = load()
    collections, setup, notes, added = build(base, setup_in, curation)
    if manifest is not None and added and addon_id:
        # Catalogs this build is adding become resolvable on import, under the AIO addon id.
        manifest |= {(addon_id, c["type"], c["id"]) for c in added}
    rows, problems, pending_hits = verify(collections, setup, manifest, net, curation.get("pending", []))

    folders = sum(len(c["folders"]) for c in collections)
    sources = sum(len(f["catalogSources"]) for c in collections for f in c["folders"])
    print(f"collections={len(collections)} folders={folders} sources={sources} "
          f"aio_catalogs={len(setup['config']['catalogs'])}")
    for n in notes:
        print(f"  note: {n}")
    if pending_hits:
        print(f"  pending ({len(pending_hits)}, documented in curation.json):")
        for p in pending_hits:
            print(f"    - {p}")
    if problems:
        print(f"FAIL ({len(problems)}):")
        for p in problems:
            print(f"  - {p}")
        raise SystemExit(1)
    print(f"OK{'' if not manifest else f' ({len(pending_hits)} pending)'}{'' if not net else ' (all art reachable)'}")

    if check:
        return
    out = ROOT / "dist"
    out.mkdir(exist_ok=True)
    (out / "nuvio-collections.json").write_text(json.dumps(collections, indent=2, ensure_ascii=False) + "\n")
    (out / "aiometadata-setup.json").write_text(json.dumps(setup, indent=2, ensure_ascii=False) + "\n")
    with (out / "mapping.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {out}/nuvio-collections.json, aiometadata-setup.json, mapping.csv")


if __name__ == "__main__":
    main()
