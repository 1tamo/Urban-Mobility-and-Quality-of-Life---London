"""Step 5: draw the figures.

Reads the part tables from step 4 and saves PNG figures to figures/
(figures are small and are committed to Git):

    part0_growth_2007_2017.png
    part0_trend_by_zone.png
    part1_stratford_growth.png
    part2_station_trends.png
    part3_train_crowding.png
    part4_busiest_days.png

Run from the repository root:
    python src/5_make_figures.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
FIGURES = ROOT / "figures"

# Categorical colours, fixed order (validated default palette).
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
TEXT, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
RED, NEUTRAL = "#e34948", "#f0efec"  # diverging pair: blue = lower, red = higher
STATIONS = ["Stratford", "Stratford International", "Stratford High Street",
            "Pudding Mill Lane", "Hackney Wick"]

SOURCE_TFL = "Powered by TfL Open Data."


def style_axes(ax) -> None:
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def part0_growth() -> None:
    """The ten Underground stations with the largest growth, 2007-2017."""
    df = pd.read_csv(DATA / "part0_growth_2007_2017.csv").head(10).iloc[::-1]
    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=150)
    style_axes(ax)
    ax.yaxis.grid(False)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    colours = [BLUE if s == "Stratford" else "#b8b6b0" for s in df["station"]]
    ax.barh(df["station"], df["increase"] / 1000, color=colours, height=0.65)
    for i, row in enumerate(df.itertuples()):
        ax.text(row.increase / 1000 + 1.5, i, f"+{row.increase / 1000:.0f}k  (×{row.ratio:.2f})",
                va="center", fontsize=8, color=TEXT)
    ax.set_xlim(0, df["increase"].max() / 1000 * 1.25)
    ax.tick_params(axis="y", labelsize=9, labelcolor=TEXT)
    ax.set_xlabel("Increase in typical-weekday entries + exits, 2007 to 2017 (thousands)",
                  color=MUTED, fontsize=9)
    ax.set_title("Stratford grew more than any other Underground station in London, 2007–2017",
                 loc="left", fontsize=12, color=TEXT, pad=12)
    fig.text(0.01, 0.01, "Top 10 of 238 Underground stations with at least 5,000 weekday entries + exits "
             "in 2007. ×: 2017 ÷ 2007. Source: TfL station entry/exit counts. " + SOURCE_TFL,
             fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(FIGURES / "part0_growth_2007_2017.png")
    plt.close(fig)


def part0_trend() -> None:
    """London-wide typical-weekday demand by fare zone, each year compared with 2019."""
    df = pd.read_csv(DATA / "part0_trend_by_zone.csv")
    fig, ax = plt.subplots(figsize=(9, 5), dpi=150)
    style_axes(ax)
    series = [("All London", TEXT, 2.6), ("Zone 1", BLUE, 2), ("Zone 2", ORANGE, 2),
              ("Zones 3-4", AQUA, 2), ("Zones 5-6", "#8a5cc2", 2)]
    ends = []
    for name, colour, width in series:
        d = df[df["zone_group"] == name].sort_values("year")
        ax.plot(d["year"], d["vs_2019"], color=colour, linewidth=width, marker="o", markersize=4)
        ends.append([d["vs_2019"].iloc[-1], name])
    # Spread the end labels so they do not overlap (at least 0.045 apart).
    ends.sort(reverse=True)
    label_y = [ends[0][0]]
    for value, _ in ends[1:]:
        label_y.append(min(value, label_y[-1] - 0.045))
    for (value, name), y in zip(ends, label_y):
        ax.text(2025.15, y, f"{name}  {value:.2f}", va="center", fontsize=8, color=TEXT)
    ax.axhline(1, color=MUTED, linewidth=0.8, linestyle=(0, (3, 3)), zorder=0)
    ax.set_xlim(2017.6, 2026.4)
    ax.set_ylim(0, 1.25)
    ax.set_xticks(range(2018, 2026))
    ax.set_ylabel("Typical-weekday entries + exits ÷ 2019 level", color=MUTED, fontsize=9)
    ax.set_title("By 2025, London-wide weekday demand was 91% of 2019: lowest in Zones 1–2, highest in outer zones",
                 loc="left", fontsize=12, color=TEXT, pad=12)
    fig.text(0.01, 0.01, "All Underground, Overground, DLR and Elizabeth line stations, grouped by fare zone "
             "(stations on a zone boundary counted in the lower zone;\nthe few stations outside Zone 6 are in the London total only). Weekday = Mon–Thu up to 2021, "
             "Tue–Thu from 2022. Source: NUMBAT 2018–2025. " + SOURCE_TFL, fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(FIGURES / "part0_trend_by_zone.png")
    plt.close(fig)


def part1() -> None:
    """Stratford Underground station, typical-day entries + exits, 2007-2017."""
    df = pd.read_csv(DATA / "part1_stratford_growth.csv")
    fig, ax = plt.subplots(figsize=(9, 5), dpi=150)
    style_axes(ax)

    # (key, label, colour, vertical offset of the end label in points)
    series = [("weekday", "Weekday", BLUE, -7), ("saturday", "Saturday", ORANGE, 7),
              ("sunday", "Sunday", AQUA, 0)]
    for key, label, colour, dy in series:
        d = df[df["day_type"] == key].sort_values("year")
        ax.plot(d["year"], d["total"] / 1000, color=colour, linewidth=2,
                marker="o", markersize=5)
        last = d.iloc[-1]
        ax.annotate(label, (last["year"], last["total"] / 1000),
                    xytext=(8, dy), textcoords="offset points",
                    va="center", fontsize=9, color=TEXT)

    events = {2009: "HS1 domestic\nservices", 2011: "Westfield\nopens",
              2012: "Olympic\nGames", 2016: "West Ham move\nto London Stadium"}
    top = df["total"].max() / 1000 * 1.08
    for year, text in events.items():
        ax.axvline(year, color=MUTED, linewidth=0.8, linestyle=(0, (3, 3)), zorder=0)
        ax.text(year, top, text, ha="center", va="bottom", fontsize=8, color=MUTED)

    ax.set_xlim(2006.5, 2018.2)
    ax.set_ylim(0, top * 1.12)
    ax.set_xticks(range(2007, 2018))
    ax.set_ylabel("Entries + exits on a typical day (thousands)", color=MUTED, fontsize=9)
    ax.set_title("Stratford Underground station: typical-day use more than doubled, 2007–2017",
                 loc="left", fontsize=12, color=TEXT, pad=12)
    fig.text(0.01, 0.01, "Source: TfL station entry/exit counts (London Underground gates only). "
             "Event lines show timing, not cause. " + SOURCE_TFL,
             fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(FIGURES / "part1_stratford_growth.png")
    plt.close(fig)


def part3() -> None:
    """How long a 10-minute ride leaving Stratford feels, peak vs off-peak."""
    df = pd.read_csv(DATA / "part3_train_crowding.csv")
    df = df[df["direction"] == "leaving Stratford"]
    hours = {"08:00-09:00": ("AM peak (08:00–09:00)", BLUE),
             "11:00-12:00": ("Off-peak (11:00–12:00)", ORANGE)}
    lines = ["Elizabeth line", "Central", "Jubilee"]

    fig, ax = plt.subplots(figsize=(9, 4.6), dpi=150)
    style_axes(ax)
    ax.yaxis.grid(False)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)

    height = 0.36
    for i, (hour, (label, colour)) in enumerate(hours.items()):
        d = df[df["hour"] == hour].set_index("line").loc[lines]
        y = [j + (i - 0.5) * (height + 0.04) for j in range(len(lines))]
        ax.barh(y, d["ten_minutes_feels_like"], height=height, color=colour, label=label)
        for yy, val in zip(y, d["ten_minutes_feels_like"]):
            ax.text(val + 0.3, yy, f"{val:.1f} min", va="center", fontsize=9, color=TEXT)

    ax.axvline(10, color=MUTED, linewidth=1, linestyle=(0, (3, 3)))
    ax.text(10.2, -0.62, "actual ride: 10 min", ha="left",
            fontsize=8, color=MUTED)
    ax.set_yticks(range(len(lines)))
    ax.set_yticklabels([l if l.endswith("line") else f"{l} line" for l in lines], fontsize=10, color=TEXT)
    ax.set_ylim(len(lines) - 0.4, -0.75)
    ax.set_xlim(0, 27)
    ax.set_xlabel("How long a 10-minute ride feels (minutes)", color=MUTED, fontsize=9)
    ax.legend(frameon=False, fontsize=9, loc="lower right")
    ax.set_title("Leaving Stratford in the morning peak, a 10-minute ride feels like 16–24 minutes",
                 loc="left", fontsize=12, color=TEXT, pad=12)
    fig.text(0.01, 0.01,
             "Typical 2025 weekday (Tue–Thu), average of all trains in the hour. Perceived time = "
             "10 × (1 + 0.42 × standing passengers per m²), Yap, Wong & Cats (2023).\n"
             "Elizabeth line standing area estimated. Source: NUMBAT 2025; TfL rolling stock data. "
             + SOURCE_TFL, fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(FIGURES / "part3_train_crowding.png")
    plt.close(fig)


def part2() -> None:
    """Whole-day demand at the five study stations, each year compared with 2019."""
    df = pd.read_csv(DATA / "part2_station_trends.csv")
    df = df[df["time_band"] == "Whole day"]
    panels = [("weekday", "Weekday"), ("saturday", "Saturday"), ("sunday", "Sunday")]
    cmap = LinearSegmentedColormap.from_list("div", [BLUE, NEUTRAL, RED])
    norm = TwoSlopeNorm(vmin=0, vcenter=1, vmax=2)

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.4), dpi=150, sharey=True)
    for ax, (key, title) in zip(axes, panels):
        grid = df[df["day_type"] == key].pivot(index="station", columns="year", values="vs_2019")
        grid = grid.loc[STATIONS]
        ax.imshow(grid.clip(upper=2).values, cmap=cmap, norm=norm, aspect="auto")
        for i in range(grid.shape[0]):
            for j in range(grid.shape[1]):
                v = grid.iat[i, j]
                ax.text(j, i, f"{v:.1f}", ha="center", va="center", fontsize=8,
                        color="white" if v < 0.45 or v > 1.75 else TEXT)
        ax.set_xticks(range(grid.shape[1]))
        ax.set_xticklabels(grid.columns, fontsize=8, color=MUTED)
        ax.set_yticks(range(grid.shape[0]))
        ax.set_yticklabels(grid.index, fontsize=9, color=TEXT)
        ax.set_title(title, loc="left", fontsize=10, color=TEXT)
        ax.tick_params(length=0)
        for side in ax.spines.values():
            side.set_visible(False)
    fig.suptitle("In 2022–2025, Stratford stayed below its 2019 level; Hackney Wick and Pudding Mill Lane were well above theirs",
                 x=0.01, ha="left", fontsize=12, color=TEXT)
    fig.text(0.01, 0.01,
             "Each cell: whole-day entries + exits on a typical day ÷ the same station in 2019 (1.0 = same as 2019; "
             "red = busier, blue = quieter; colours capped at 2.0).\n"
             "Weekday = Mon–Thu up to 2021, Tue–Thu from 2022. Stratford's 2025 Saturday total equals 2024's, "
             "suggesting TfL reused the count. Source: NUMBAT 2018–2025. " + SOURCE_TFL,
             fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.07, 1, 0.97))
    fig.savefig(FIGURES / "part2_station_trends.png")
    plt.close(fig)


def part4() -> None:
    """On the busiest days for nearby stations, how busy was Stratford?"""
    df = pd.read_csv(DATA / "part4_busiest_days.csv", parse_dates=["date"])
    df = df.sort_values("busiest_nearby_index", ascending=True).reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(10, 6.4), dpi=150)
    style_axes(ax)
    ax.yaxis.grid(False)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)

    y = range(len(df))
    for i, row in df.iterrows():
        ax.plot([row["stratford_index"], row["busiest_nearby_index"]], [i, i], color=GRID, linewidth=2, zorder=1)
    ax.scatter(df["stratford_index"], y, s=60, color=BLUE, zorder=3, label="Stratford",
               edgecolor="white", linewidth=1.5)
    ax.scatter(df["busiest_nearby_index"], y, s=60, color=ORANGE, zorder=3,
               label="Busiest nearby station that day", edgecolor="white", linewidth=1.5)
    for i, row in df.iterrows():
        ax.text(row["busiest_nearby_index"] + 0.08, i, row["busiest_nearby"], va="center",
                fontsize=8, color=MUTED)

    labels = [f"{d:%a %d %b}" for d in df["date"]]
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels, fontsize=9, color=TEXT)
    for x, text in [(1, "usual"), (1.5, "1.5×"), (2, "2×")]:
        ax.axvline(x, color=MUTED, linewidth=0.8, linestyle=(0, (3, 3)), zorder=0)
        ax.text(x, len(df) - 0.3, text, ha="center", fontsize=8, color=MUTED)
    ax.set_xlim(0.8, 6.6)
    ax.set_ylim(-0.7, len(df) + 0.2)
    ax.set_xlabel("Entries + exits that day ÷ the station's usual level for that day of the week",
                  color=MUTED, fontsize=9)
    ax.legend(frameon=False, fontsize=9, loc="lower right")
    ax.set_title("On the 15 busiest days for nearby stations in 2025, Stratford rose far less (1.0–1.5× its usual level)",
                 loc="left", fontsize=12, color=TEXT, pad=12)
    fig.text(0.01, 0.01,
             "Usual = median for the same station and day of the week in 2025. Days a station had no taps are left out. "
             "Small stations swing more in relative terms;\nin absolute numbers Stratford often gains more people "
             "(see part4_busiest_days.csv). Source: TfL station footfall. " + SOURCE_TFL,
             fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(FIGURES / "part4_busiest_days.png")
    plt.close(fig)


def main() -> None:
    FIGURES.mkdir(exist_ok=True)
    part0_growth()
    part0_trend()
    part1()
    part2()
    part3()
    part4()
    print(f"Figures saved to {FIGURES}")


if __name__ == "__main__":
    main()
