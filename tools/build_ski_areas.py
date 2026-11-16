"""Build powder-monitor/ski_areas.json from OpenSkiMap (OpenStreetMap data, ODbL).

Keeps operating downhill ski areas in Europe with a compact set of fields.
Run by .github/workflows/ski-areas.yml; never fails the job: problems go to tools/ski_areas_status.txt.
"""
import datetime, json, sys, urllib.request

OUT = sys.argv[1] if len(sys.argv) > 1 else "powder-monitor/ski_areas.json"
STATUS = "tools/ski_areas_status.txt"
URLS = ["https://tiles.openskimap.org/geojson/ski_areas.geojson",
        "https://tiles.skimap.org/geojson/ski_areas.geojson"]


def coords(g):
    if not g:
        return
    t = g.get("type")
    if t == "GeometryCollection":
        for x in g.get("geometries", []):
            yield from coords(x)
        return
    def walk(c):
        if isinstance(c, (list, tuple)) and c and isinstance(c[0], (int, float)):
            yield c
        elif isinstance(c, (list, tuple)):
            for x in c:
                yield from walk(x)
    yield from walk(g.get("coordinates"))


def center(g):
    pts = list(coords(g))
    if not pts:
        return None
    lons = [p[0] for p in pts]; lats = [p[1] for p in pts]
    return (min(lats) + max(lats)) / 2, (min(lons) + max(lons)) / 2


def find_key(o, key):
    """Depth-first search for the first value stored under `key`."""
    if isinstance(o, dict):
        if isinstance(o.get(key), str) and o.get(key):
            return o[key]
        for v in o.values():
            r = find_key(v, key)
            if r:
                return r
    elif isinstance(o, list):
        for v in o:
            r = find_key(v, key)
            if r:
                return r
    return None


def num(*vals):
    for v in vals:
        if isinstance(v, (int, float)):
            return v
    return None


def main():
    data, used, errs = None, None, []
    for u in URLS:
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "PowderMonitor/1.0 (personal project; github.com/CrazySn0wman/powdermonitor)"})
            with urllib.request.urlopen(req, timeout=300) as r:
                data = json.loads(r.read())
            used = u
            break
        except Exception as e:  # noqa: BLE001
            errs.append(f"{u}: {e}")
    if data is None:
        open(STATUS, "w").write("FAILED " + datetime.datetime.utcnow().isoformat() + "\n" + "\n".join(errs) + "\n")
        return
    feats = data.get("features", [])
    out, sample, skipped = [], {}, {}
    def skip(k):
        skipped[k] = skipped.get(k, 0) + 1
    for f in feats:
        p = f.get("properties") or {}
        name = p.get("name")
        if name and ("Val Thorens" in name or "Kitzsteinhorn" in name) and len(sample) < 2:
            sample[name] = {"keys": sorted(p.keys()), "location": p.get("location"), "places": p.get("places")}
        if p.get("type") not in (None, "skiArea"):
            skip("type"); continue
        if "downhill" not in (p.get("activities") or []):
            skip("not downhill"); continue
        if p.get("status") not in (None, "operating"):
            skip("status"); continue
        if not name:
            skip("no name"); continue
        c = center(f.get("geometry"))
        if not c:
            skip("no geometry"); continue
        lat, lon = c
        if not (34 <= lat <= 72 and -11 <= lon <= 45):
            skip("outside Europe"); continue
        st = p.get("statistics") or {}
        runs = st.get("runs") or {}
        lifts = st.get("lifts") or {}
        top = num(st.get("maxElevation"), runs.get("maxElevation"), lifts.get("maxElevation"))
        bottom = num(st.get("minElevation"), runs.get("minElevation"), lifts.get("minElevation"))
        bd = ((runs.get("byActivity") or {}).get("downhill") or {}).get("byDifficulty") or {}
        km = {k: (v or {}).get("lengthInKm") or 0 for k, v in bd.items()}
        easy = km.get("novice", 0) + km.get("easy", 0)
        inter = km.get("intermediate", 0)
        adv = km.get("advanced", 0) + km.get("expert", 0) + km.get("freeride", 0) + km.get("extreme", 0)
        total = sum(km.values())
        if total < 3 or not top:
            skip("too small / no elevation"); continue
        cc = find_key(p.get("location"), "iso3166_1Alpha2") or find_key(p.get("places"), "iso3166_1Alpha2") or find_key(p, "iso3166_1Alpha2") or ""
        out.append([p.get("id") or "", name, round(lat, 4), round(lon, 4), round(top), round(bottom) if bottom else None,
                    round(total, 1), round(easy, 1), round(inter, 1), round(adv, 1), cc])
    # merge near-duplicates (e.g. "Val Thorens" and "Val Thorens - Orelle"): keep the bigger area
    out.sort(key=lambda a: -a[6])
    kept = []
    for a in out:
        if any(abs(a[2] - b[2]) < 0.02 and abs(a[3] - b[3]) < 0.03 for b in kept):
            skip("duplicate"); continue
        kept.append(a)
    out = kept
    out.sort(key=lambda a: (a[10], a[1]))
    doc = {
        "_about": "European downhill ski areas from OpenSkiMap.org (© OpenStreetMap contributors, ODbL). Built weekly by .github/workflows/ski-areas.yml. Lengths in km of downhill pistes by difficulty; elevations in metres.",
        "generated": datetime.datetime.utcnow().strftime("%Y-%m-%d"),
        "source": used,
        "fields": ["id", "name", "lat", "lon", "top", "bottom", "km", "easy", "inter", "adv", "cc"],
        "areas": out,
    }
    with open(OUT, "w") as fh:
        json.dump(doc, fh, ensure_ascii=False, separators=(",", ":"))
    open(STATUS, "w").write(
        f"OK {doc['generated']} from {used}\nfeatures: {len(feats)}, kept: {len(out)}\nskipped: {json.dumps(skipped)}\n"
        f"sample properties: {json.dumps(sample, ensure_ascii=False)[:4000]}\n")


if __name__ == "__main__":
    main()
