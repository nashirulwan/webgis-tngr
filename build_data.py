#!/usr/bin/env python3
"""
Generator data untuk WebGIS Taman Nasional Gunung Rinjani.

Menghasilkan:
  1. rinjani.kml  -> batas resmi TNGR (data WDPA) dalam format KML  [LAYER WAJIB]
  2. data.js      -> salinan semua layer sebagai variabel JS, fallback agar peta
                     tetap tampil walau index.html dibuka langsung (file://).

Jalankan ulang bila data sumber berubah:  python3 build_data.py

Asal data layer (di-generate sekali via Overpass API OpenStreetMap):
  - sembalun_trail / senaru_trail : relation route=hiking id 17259217 & 17259241
  - pos_pendakian                 : node bernama "Pos *" + rim/plawangan
  - poi_wisata                    : air terjun & hot_spring (natural/waterway/tourism)
  - segara_anak                   : danau (way OSM)
  - rinjani_boundary              : WDPA / Protected Planet (batas resmi)
"""
import json

# ── 1. rinjani.kml dari batas resmi WDPA ───────────────────────────────────
def ring_to_coords(ring):
    return "\n".join(f"            {lon:.6f},{lat:.6f},0" for lon, lat in ring)

boundary = json.load(open("rinjani_boundary.geojson"))
feat = boundary["features"][0]
props = feat["properties"]
geom = feat["geometry"]
polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]

placemarks = []
for poly in polys:
    outer, inners = poly[0], poly[1:]
    inner_xml = ""
    for inner in inners:
        inner_xml += f"""
        <innerBoundaryIs><LinearRing><coordinates>
{ring_to_coords(inner)}
        </coordinates></LinearRing></innerBoundaryIs>"""
    placemarks.append(f"""    <Placemark>
      <name>Batas Taman Nasional Gunung Rinjani</name>
      <description>Kawasan TNGR (IUCN kategori {props.get('IUCN_CAT','II')}), luas resmi ±{props.get('REP_AREA',413.3)} km2 / 41.330 ha. Pengelola: {props.get('MANG_AUTH','Balai Taman Nasional Gunung Rinjani')}. Sumber: WDPA / Protected Planet (Jun 2026).</description>
      <styleUrl>#kawasanStyle</styleUrl>
      <Polygon>
        <tessellate>1</tessellate>
        <outerBoundaryIs><LinearRing><coordinates>
{ring_to_coords(outer)}
        </coordinates></LinearRing></outerBoundaryIs>{inner_xml}
      </Polygon>
    </Placemark>""")

kml = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Taman Nasional Gunung Rinjani</name>
    <description>Batas resmi kawasan TNGR, Lombok, Nusa Tenggara Barat. Data: WDPA / Protected Planet.</description>
    <Style id="kawasanStyle">
      <LineStyle><color>ffff8822</color><width>3</width></LineStyle>
      <PolyStyle><color>3322aaff</color><fill>1</fill><outline>1</outline></PolyStyle>
    </Style>
{chr(10).join(placemarks)}
  </Document>
</kml>
"""
open("rinjani.kml", "w").write(kml)
print(f"rinjani.kml  -> {len(placemarks)} placemark, {sum(len(p[0]) for p in polys)} titik")

# ── 2. data.js (fallback offline) — bundel semua layer ─────────────────────
def load(p):
    return json.load(open(p, encoding="utf-8"))

bundle = {
    "boundary": boundary,
    "lake":     load("segara_anak.geojson"),
    "sembalun": load("sembalun_trail.geojson"),
    "senaru":   load("senaru_trail.geojson"),
    "pos":      load("pos_pendakian.geojson"),
    "wisata":   load("poi_wisata.geojson"),
}
js = "// Dibuat otomatis oleh build_data.py — fallback offline (file://).\n"
js += "// Layer KML resmi tetap dimuat dari rinjani.kml saat dibuka via server.\n"
js += "window.RINJANI_DATA = " + json.dumps(bundle, ensure_ascii=False) + ";\n"
open("data.js", "w", encoding="utf-8").write(js)
print(f"data.js      -> {len(js)//1024} KB ({len(bundle)} layer)")
