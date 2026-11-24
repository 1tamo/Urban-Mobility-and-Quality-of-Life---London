"""Step 6: map the five study stations on a real map (OpenStreetMap), 2018-2025.

Reads data/processed/part2_station_trends.csv (from step 4) and
data/station_locations.csv, and writes:

    figures/part2_map.gif        animation, one frame per year, three panels
                                 (weekday, Saturday, Sunday)
    figures/part2_map_2025.png   the 2025 frame as a still image
    docs/part2_map.html          interactive map: choose the year and day type

On each map, circle colour = demand compared with the same station in 2019
(blue = lower, red = higher), circle size = number of entries + exits.

The background map comes from OpenStreetMap. The first run downloads about 15
map tiles (needs internet) and keeps them in data/processed/tiles/, so later
runs work offline. If the download fails, the maps are drawn without a
background. Map data © OpenStreetMap contributors (ODbL).

Run from the repository root:
    python src/6_make_map.py
"""

import io
import json
import math
import time
import urllib.request
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, Normalize
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
TILES = DATA / "tiles"
FIGURES = ROOT / "figures"
DOCS = ROOT / "docs"

# Map area (longitude and latitude) and OpenStreetMap zoom level.
WEST, EAST, SOUTH, NORTH = -0.034, 0.013, 51.529, 51.549
ZOOM = 15
TILE_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
USER_AGENT = ("Urban-Mobility-London coursework map "
              "(https://github.com/1tamo/Urban-Mobility-and-Quality-of-Life---London)")

YEARS = list(range(2018, 2026))
DAY_TYPES = [("weekday", "Weekday"), ("saturday", "Saturday"), ("sunday", "Sunday")]
# Where to put each label relative to its circle (points), so labels do not overlap.
LABEL_OFFSET = {
    "Hackney Wick": (0, 16, "center", "bottom"),
    "Stratford International": (0, 16, "center", "bottom"),
    "Stratford": (16, 0, "left", "center"),
    "Stratford High Street": (14, -10, "left", "top"),
    "Pudding Mill Lane": (0, -16, "center", "top"),
}

BLUE, NEUTRAL, RED = "#2a78d6", "#d9d7d0", "#e34948"
TEXT, MUTED = "#0b0b0b", "#52514e"
CMAP = LinearSegmentedColormap.from_list("div", [BLUE, NEUTRAL, RED])
# Colour scale on a log scale: 0.25x (bluest) ... 1x (neutral) ... 4x (reddest).
NORM = Normalize(vmin=-2, vmax=2)
ATTRIBUTION = "Map data © OpenStreetMap contributors (ODbL). Powered by TfL Open Data. Source: NUMBAT 2018–2025."


# ---------- background map ----------

def lonlat_to_tile(lon: float, lat: float, z: int) -> tuple[float, float]:
    n = 2 ** z
    x = (lon + 180) / 360 * n
    y = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n
    return x, y


def lonlat_to_xy(lon, lat):
    """Longitude/latitude to Web Mercator metres (the projection map tiles use)."""
    r = 6378137
    x = np.radians(lon) * r
    y = np.log(np.tan(np.pi / 4 + np.radians(lat) / 2)) * r
    return x, y


def tile_corner_xy(x: int, y: int, z: int) -> tuple[float, float]:
    """Web Mercator metres of the top-left corner of a tile."""
    n = 2 ** z
    lon = x / n * 360 - 180
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
    return lonlat_to_xy(lon, lat)


def get_tile(x: int, y: int, z: int) -> Image.Image:
    path = TILES / f"{z}_{x}_{y}.png"
    if not path.exists():
        request = urllib.request.Request(TILE_URL.format(z=z, x=x, y=y),
                                         headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=20) as response:
            path.write_bytes(response.read())
        time.sleep(0.2)  # be polite to the OpenStreetMap servers
    return Image.open(path).convert("RGB")


def background():
    """Stitch OpenStreetMap tiles into one image. Returns (image, extent) or (None, None)."""
    TILES.mkdir(parents=True, exist_ok=True)
    x0, y0 = (int(v) for v in lonlat_to_tile(WEST, NORTH, ZOOM))
    x1, y1 = (int(v) for v in lonlat_to_tile(EAST, SOUTH, ZOOM))
    try:
        mosaic = Image.new("RGB", ((x1 - x0 + 1) * 256, (y1 - y0 + 1) * 256))
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                mosaic.paste(get_tile(x, y, ZOOM), ((x - x0) * 256, (y - y0) * 256))
    except Exception as error:  # no internet, blocked, etc.
        print(f"Could not download the background map ({error}); drawing without it.")
        return None, None
    left, top = tile_corner_xy(x0, y0, ZOOM)
    right, bottom = tile_corner_xy(x1 + 1, y1 + 1, ZOOM)
    return mosaic, (left, right, bottom, top)


# ---------- data ----------

def load() -> pd.DataFrame:
    trends = pd.read_csv(DATA / "part2_station_trends.csv")
    trends = trends[trends["time_band"] == "Whole day"]
    places = pd.read_csv(ROOT / "data" / "station_locations.csv")
    df = trends.merge(places, on="station", validate="many_to_one")
    assert df["station"].nunique() == 5, "a station is missing its location"
    df["x"], df["y"] = lonlat_to_xy(df["lon"].to_numpy(), df["lat"].to_numpy())
    return df


def colour(ratio: float):
    return CMAP(NORM(np.clip(np.log2(ratio), -2, 2)))


def size(total: float) -> float:
    """Circle area in points²: proportional to entries + exits."""
    return 30 + total / 200_000 * 2200


# ---------- animation ----------

def draw_panel(ax, frame: pd.DataFrame, title: str, image, extent) -> None:
    xw, ys = lonlat_to_xy(np.array([WEST, EAST]), np.array([SOUTH, NORTH]))
    if image is not None:
        ax.imshow(image, extent=extent, interpolation="lanczos")
        ax.imshow(np.ones((2, 2, 3)), extent=extent, alpha=0.35)  # soften the background
    else:
        ax.set_facecolor("#f4f3ef")
    ax.set_xlim(*xw)
    ax.set_ylim(*ys)
    ax.set_aspect("equal")  # keep the map's true shape
    for row in frame.sort_values("total", ascending=False).itertuples():
        ax.scatter(row.x, row.y, s=size(row.total), color=colour(row.vs_2019),
                   edgecolor="white", linewidth=1.5, zorder=3)
        dx, dy, ha, va = LABEL_OFFSET[row.station]
        gap = math.sqrt(size(row.total) / math.pi)  # circle radius in points
        dx, dy = dx + math.copysign(gap, dx) * (dx != 0), dy + math.copysign(gap, dy) * (dy != 0)
        ax.annotate(f"{row.station}\n{row.vs_2019:.1f}×", (row.x, row.y), xytext=(dx, dy),
                    textcoords="offset points", ha=ha, va=va, fontsize=8, color=TEXT, zorder=4,
                    bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.85))
    ax.set_title(title, loc="left", fontsize=11, color=TEXT)
    ax.set_xticks([])
    ax.set_yticks([])


def legend(fig) -> None:
    ax = fig.add_axes([0.06, 0.075, 0.30, 0.03])
    gradient = np.linspace(-2, 2, 256)[None, :]
    ax.imshow(gradient, aspect="auto", cmap=CMAP, norm=NORM)
    ax.set_xticks([0, 64, 128, 192, 255])
    ax.set_xticklabels(["0.25×", "0.5×", "same as 2019", "2×", "4×"], fontsize=8, color=MUTED)
    ax.set_yticks([])
    ax.set_title("Colour: compared with the same station in 2019", fontsize=8, color=MUTED, loc="left")
    for side in ax.spines.values():
        side.set_visible(False)
    size_ax = fig.add_axes([0.42, 0.015, 0.22, 0.12])
    size_ax.set_title("Size: entries + exits on a typical day", fontsize=8, color=MUTED, loc="left")
    for x, value in zip([0.05, 0.3, 0.62], [5_000, 50_000, 150_000]):
        size_ax.scatter(x, 0.5, s=size(value), color=NEUTRAL, edgecolor=MUTED)
        radius = math.sqrt(size(value) / math.pi)
        size_ax.annotate(f"{value // 1000}k", (x, 0.5), xytext=(radius + 4, 0), textcoords="offset points",
                         va="center", fontsize=8, color=MUTED)
    size_ax.set_xlim(-0.05, 1)
    size_ax.set_ylim(0, 1)
    size_ax.axis("off")


def frame_image(df: pd.DataFrame, year: int, image, extent) -> Image.Image:
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.4), dpi=110)
    for ax, (key, label) in zip(axes, DAY_TYPES):
        frame = df[(df["year"] == year) & (df["day_type"] == key)]
        draw_panel(ax, frame, label, image, extent)
    fig.suptitle(f"Stratford area stations: typical-day demand compared with 2019  —  {year}",
                 x=0.01, ha="left", fontsize=14, color=TEXT)
    legend(fig)
    fig.text(0.99, 0.02, ATTRIBUTION + "\nWeekday = Mon–Thu up to 2021, Tue–Thu from 2022.",
             ha="right", fontsize=7, color=MUTED)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.9, bottom=0.17, wspace=0.03)
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png")
    plt.close(fig)
    buffer.seek(0)
    return Image.open(buffer).convert("RGB")


def make_animation(df: pd.DataFrame) -> None:
    image, extent = background()
    frames = [frame_image(df, year, image, extent) for year in YEARS]
    frames[-1].save(FIGURES / "part2_map_2025.png")
    durations = [1300] * (len(frames) - 1) + [3000]  # pause on the last year
    frames[0].save(FIGURES / "part2_map.gif", save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, optimize=True)


# ---------- interactive page ----------

HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Stratford area stations, 2018–2025</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  body { margin: 0; font: 15px system-ui, sans-serif; color: #0b0b0b; background: #fafaf8; }
  main { max-width: 1000px; margin: auto; padding: 16px; }
  h1 { font-size: 24px; margin: 4px 0; }
  p { margin: 4px 0 12px; color: #52514e; }
  #map { height: 560px; border-radius: 8px; }
  .controls { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; margin: 12px 0; }
  .controls input { flex: 1; }
  button, select { font: inherit; padding: 6px 12px; border-radius: 6px; border: 1px solid #c9c7c0; background: white; }
  .label { background: rgba(255,255,255,.9); border: none; box-shadow: none; font-size: 12px; }
  .legend { display: flex; gap: 24px; flex-wrap: wrap; font-size: 13px; color: #52514e; }
  .bar { width: 220px; height: 10px; border-radius: 3px; background: linear-gradient(90deg, #2a78d6, #d9d7d0, #e34948); }
  .ticks { display: flex; justify-content: space-between; width: 220px; font-size: 11px; }
  small { color: #52514e; }
</style>
</head>
<body>
<main>
  <h1>Stratford area stations, 2018–2025</h1>
  <p>Typical-day entries + exits at each station, compared with the same station in 2019.</p>
  <div class="controls">
    <button id="play">Play</button>
    <strong id="year"></strong>
    <input id="slider" type="range" min="0" max="__MAXINDEX__" value="0" aria-label="Year">
    <select id="day" aria-label="Day type">
      <option value="weekday">Weekday</option>
      <option value="saturday">Saturday</option>
      <option value="sunday">Sunday</option>
    </select>
  </div>
  <div id="map"></div>
  <div class="legend">
    <div>Colour: compared with 2019
      <div class="bar"></div>
      <div class="ticks"><span>0.25×</span><span>same</span><span>4×</span></div>
    </div>
    <div>Size: entries + exits on a typical day (hover a circle for the numbers)</div>
  </div>
  <small>Weekday = Mon–Thu up to 2021, Tue–Thu from 2022. Source: TfL NUMBAT 2018–2025, Powered by TfL Open Data.
  Map data © OpenStreetMap contributors.</small>
</main>
<script>
const DATA = __DATA__;
const YEARS = __YEARS__;
const map = L.map("map").fitBounds([[__SOUTH__, __WEST__], [__NORTH__, __EAST__]]);
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19, attribution: "&copy; OpenStreetMap contributors"
}).addTo(map);

function colour(ratio) {
  const t = Math.max(-2, Math.min(2, Math.log2(ratio))) / 2;   // -1 .. 1
  const mix = (a, b, f) => a.map((v, i) => Math.round(v + (b[i] - v) * f));
  const blue = [42, 120, 214], grey = [217, 215, 208], red = [227, 73, 72];
  const c = t < 0 ? mix(grey, blue, -t) : mix(grey, red, t);
  return `rgb(${c.join(",")})`;
}
const layer = L.layerGroup().addTo(map);
function draw() {
  const year = YEARS[+slider.value], day = document.getElementById("day").value;
  document.getElementById("year").textContent = year;
  layer.clearLayers();
  DATA.filter(d => d.year === year && d.day_type === day)
      .sort((a, b) => b.total - a.total)
      .forEach(d => {
        L.circleMarker([d.lat, d.lon], {
          radius: 5 + Math.sqrt(d.total) / 12, color: "white", weight: 2,
          fillColor: colour(d.vs_2019), fillOpacity: 0.9
        }).bindTooltip(`${d.station} ${d.vs_2019.toFixed(1)}×`, {permanent: true, direction: "right", className: "label"})
          .bindPopup(`<b>${d.station}</b><br>${year}, ${day}<br>${d.total.toLocaleString()} entries + exits<br>${d.vs_2019.toFixed(2)}× the 2019 level`)
          .addTo(layer);
      });
}
let timer = null;
const slider = document.getElementById("slider"), play = document.getElementById("play");
play.onclick = () => {
  if (timer) { clearInterval(timer); timer = null; play.textContent = "Play"; return; }
  timer = setInterval(() => { slider.value = (+slider.value + 1) % YEARS.length; draw(); }, 1300);
  play.textContent = "Pause";
};
slider.oninput = draw;
document.getElementById("day").onchange = draw;
draw();
</script>
</body>
</html>
"""


def make_page(df: pd.DataFrame) -> None:
    records = df[["year", "day_type", "station", "lat", "lon", "total", "vs_2019"]].to_dict("records")
    page = (HTML.replace("__DATA__", json.dumps(records))
                .replace("__YEARS__", json.dumps(YEARS))
                .replace("__MAXINDEX__", str(len(YEARS) - 1))
                .replace("__SOUTH__", str(SOUTH)).replace("__NORTH__", str(NORTH))
                .replace("__WEST__", str(WEST)).replace("__EAST__", str(EAST)))
    DOCS.mkdir(exist_ok=True)
    (DOCS / "part2_map.html").write_text(page, encoding="utf-8")


def main() -> None:
    FIGURES.mkdir(exist_ok=True)
    df = load()
    make_animation(df)
    make_page(df)
    print("Saved figures/part2_map.gif, figures/part2_map_2025.png and docs/part2_map.html")


if __name__ == "__main__":
    main()
