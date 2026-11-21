"""Step 4: draw the figures.

Reads the part tables from step 3 and saves PNG figures to figures/
(figures are small and are committed to Git):

    part1_stratford_growth.png
    part3_train_crowding.png

Run from the repository root:
    python src/4_make_figures.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
FIGURES = ROOT / "figures"

# Categorical colours, fixed order (validated default palette).
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
TEXT, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"

SOURCE_TFL = "Powered by TfL Open Data."


def style_axes(ax) -> None:
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


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


def main() -> None:
    FIGURES.mkdir(exist_ok=True)
    part1()
    part3()
    print(f"Figures saved to {FIGURES}")


if __name__ == "__main__":
    main()
