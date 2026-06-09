import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np

# ── Global color settings ──────────────────────────────
# These are used by every chart to stay consistent
BG        = "#0A0E1A"    # dark background — matches dashboard
CARD      = "#111827"    # slightly lighter — chart area
ACCENT    = "#00B4D8"    # main blue — used for primary data
ACCENT2   = "#F4A261"    # orange — used for highlights
TEXT      = "#E2E8F0"    # light text
GRID      = "#1E2A3A"    # subtle grid lines
PALETTE   = ["#00B4D8","#F4A261","#48CAE4",
             "#E76F51","#90E0EF","#0077B6","#ADE8F4"]


def _style(fig, axes=None):
    """Apply dark theme to any figure — called at end of every chart"""
    fig.patch.set_facecolor(BG)
    if axes is None:
        axes = fig.get_axes()
    for ax in axes:
        ax.set_facecolor(CARD)
        ax.tick_params(colors=TEXT, labelsize=9)
        ax.xaxis.label.set_color(TEXT)
        ax.yaxis.label.set_color(TEXT)
        ax.title.set_color(TEXT)
        for spine in ax.spines.values():
            spine.set_edgecolor(GRID)
        ax.grid(color=GRID, linestyle="--", linewidth=0.5, alpha=0.6)
    return fig


# ── Chart 1: Histogram ────────────────────────────────
def chart_histogram(df):
    fig, ax = plt.subplots(figsize=(7, 4))

    ax.hist(df["Global_active_power"].dropna(),
            bins=50, color=ACCENT, edgecolor=BG, linewidth=0.4)

    # Mean line
    mean_val = df["Global_active_power"].mean()
    ax.axvline(mean_val, color=ACCENT2, linewidth=1.5,
               linestyle="--", label=f"Mean: {mean_val:.2f} kW")

    ax.set_title("Distribution of Global Active Power")
    ax.set_xlabel("Global Active Power (kW)")
    ax.set_ylabel("Frequency")
    ax.legend(facecolor=CARD, labelcolor=TEXT, fontsize=9)

    return _style(fig)


# ── Chart 2: Line Chart ───────────────────────────────
def chart_line_monthly(df):
    monthly = df.groupby(
        df["Datetime"].dt.to_period("M")
    )["Global_active_power"].mean()
    monthly.index = monthly.index.to_timestamp()

    fig, ax = plt.subplots(figsize=(9, 4))

    ax.plot(monthly.index, monthly.values,
            color=ACCENT, linewidth=1.8, marker="o", markersize=2.5)
    ax.fill_between(monthly.index, monthly.values,
                    alpha=0.15, color=ACCENT)

    ax.set_title("Monthly Average Active Power")
    ax.set_xlabel("Date")
    ax.set_ylabel("Avg Power (kW)")
    fig.autofmt_xdate()

    return _style(fig)


# ── Chart 3: Bar Chart ────────────────────────────────
def chart_bar_hourly(df):
    hourly = df.groupby("Hour")["Global_active_power"].mean()

    # Peak hours get different color
    colors = [ACCENT2 if h in [7,8,19,20,21]
              else ACCENT for h in hourly.index]

    fig, ax = plt.subplots(figsize=(9, 4))

    ax.bar(hourly.index, hourly.values,
           color=colors, edgecolor=BG, linewidth=0.4)

    ax.set_title("Average Power by Hour of Day")
    ax.set_xlabel("Hour (0 = midnight, 12 = noon)")
    ax.set_ylabel("Avg Power (kW)")
    ax.set_xticks(range(0, 24))

    # Legend
    from matplotlib.patches import Patch
    legend = [Patch(facecolor=ACCENT,  label="Normal"),
              Patch(facecolor=ACCENT2, label="Peak hours")]
    ax.legend(handles=legend, facecolor=CARD,
              labelcolor=TEXT, fontsize=9)

    return _style(fig)


# ── Chart 4: Pie Chart ────────────────────────────────
def chart_pie_season(df):
    season_data = df.groupby("Season")["Global_active_power"].sum()
    order = [s for s in ["Spring","Summer","Autumn","Winter"]
             if s in season_data.index]
    season_data = season_data[order]

    colors = ["#48CAE4","#F4A261","#E76F51","#ADE8F4"]

    fig, ax = plt.subplots(figsize=(6, 5))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    wedges, texts, autotexts = ax.pie(
        season_data.values,
        labels=season_data.index,
        autopct="%1.1f%%",
        colors=colors,
        startangle=140,
        wedgeprops=dict(edgecolor=BG, linewidth=2),
        textprops={"color": TEXT, "fontsize": 10},
    )
    for at in autotexts:
        at.set_color(BG)
        at.set_fontweight("bold")

    ax.set_title("Energy Consumption by Season", color=TEXT)

    return fig


# ── Chart 5: Scatter Plot ─────────────────────────────
def chart_scatter(df):
    sample = df.sample(3000, random_state=42)

    fig, ax = plt.subplots(figsize=(6, 4))

    sc = ax.scatter(
        sample["Global_intensity"],
        sample["Global_active_power"],
        c=sample["Voltage"],
        cmap="cool",
        alpha=0.4,
        s=6
    )

    cbar = fig.colorbar(sc, ax=ax)
    cbar.set_label("Voltage (V)", color=TEXT, fontsize=9)
    cbar.ax.yaxis.set_tick_params(color=TEXT)
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color=TEXT)
    cbar.outline.set_edgecolor(GRID)

    ax.set_title("Active Power vs Global Intensity")
    ax.set_xlabel("Global Intensity (A)")
    ax.set_ylabel("Global Active Power (kW)")

    return _style(fig)


# ── Chart 6: Box Plot ─────────────────────────────────
def chart_boxplot_weekday(df):
    order = ["Monday","Tuesday","Wednesday",
             "Thursday","Friday","Saturday","Sunday"]
    order = [d for d in order if d in df["Weekday"].unique()]

    fig, ax = plt.subplots(figsize=(9, 4))

    sns.boxplot(
        data=df, x="Weekday", y="Global_active_power",
        order=order, palette=PALETTE[:7], ax=ax,
        linewidth=0.8,
        flierprops=dict(marker=".", markersize=1, alpha=0.3)
    )

    ax.set_title("Active Power Distribution by Weekday")
    ax.set_xlabel("Day of Week")
    ax.set_ylabel("Global Active Power (kW)")
    ax.set_xticklabels([d[:3] for d in order])

    return _style(fig)


# ── Chart 7: Heatmap ──────────────────────────────────
def chart_heatmap(df):
    cols = ["Global_active_power","Global_reactive_power",
            "Voltage","Global_intensity",
            "Sub_metering_1","Sub_metering_2","Sub_metering_3"]

    corr = df[cols].corr()

    fig, ax = plt.subplots(figsize=(8, 6))

    sns.heatmap(
        corr, annot=True, fmt=".2f", cmap="coolwarm",
        ax=ax, linewidths=0.5, linecolor=BG,
        annot_kws={"size": 8}, square=True
    )

    ax.set_title("Feature Correlation Heatmap", color=TEXT, pad=10)
    ax.tick_params(axis="x", rotation=45, labelsize=8)
    ax.tick_params(axis="y", rotation=0,  labelsize=8)

    return _style(fig)


# ── Chart 8: Area Chart ───────────────────────────────
def chart_area_submetering(df):
    weekly = df.groupby(
        df["Datetime"].dt.to_period("W")
    )[["Sub_metering_1","Sub_metering_2","Sub_metering_3"]].mean()
    weekly.index = weekly.index.to_timestamp()

    fig, ax = plt.subplots(figsize=(9, 4))

    ax.fill_between(weekly.index, weekly["Sub_metering_1"],
                    alpha=0.8, color="#00B4D8", label="Kitchen")
    ax.fill_between(weekly.index, weekly["Sub_metering_2"],
                    alpha=0.7, color="#48CAE4", label="Laundry")
    ax.fill_between(weekly.index, weekly["Sub_metering_3"],
                    alpha=0.6, color="#0077B6", label="HVAC/Heater")

    ax.set_title("Weekly Sub-Metering Trends")
    ax.set_xlabel("Date")
    ax.set_ylabel("Avg Energy (Wh)")
    ax.legend(facecolor=CARD, labelcolor=TEXT, fontsize=9)
    fig.autofmt_xdate()

    return _style(fig)


# ── Chart 9: Count Plot ───────────────────────────────
def chart_countplot_year(df):
    year_counts = df["Year"].value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(6, 4))

    bars = ax.bar(
        year_counts.index.astype(str),
        year_counts.values,
        color=PALETTE[:len(year_counts)],
        edgecolor=BG, linewidth=0.5
    )

    # Value labels on top of each bar
    for bar, val in zip(bars, year_counts.values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1000,
            f"{val:,}",
            ha="center", va="bottom",
            color=TEXT, fontsize=8
        )

    ax.set_title("Number of Records per Year")
    ax.set_xlabel("Year")
    ax.set_ylabel("Record Count")
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{int(x):,}")
    )

    return _style(fig)


# ── Chart 10: Violin Plot ─────────────────────────────
def chart_violin_season(df):
    order = [s for s in ["Spring","Summer","Autumn","Winter"]
             if s in df["Season"].unique()]

    season_colors = {
        "Spring": "#48CAE4",
        "Summer": "#F4A261",
        "Autumn": "#E76F51",
        "Winter": "#ADE8F4"
    }
    palette = {s: season_colors[s] for s in order}

    fig, ax = plt.subplots(figsize=(7, 4))

    sns.violinplot(
        data=df, x="Season", y="Global_active_power",
        order=order, palette=palette, ax=ax,
        linewidth=0.8, inner="quartile"
    )

    ax.set_title("Active Power Distribution by Season")
    ax.set_xlabel("Season")
    ax.set_ylabel("Global Active Power (kW)")

    return _style(fig)
# ── BONUS 1: Bubble Chart ─────────────────────────────
def chart_bubble(df):
    agg = df.groupby("Hour").agg(
        avg_power     = ("Global_active_power", "mean"),
        avg_voltage   = ("Voltage", "mean"),
        avg_intensity = ("Global_intensity", "mean"),
    ).reset_index()

    fig, ax = plt.subplots(figsize=(9, 4))

    sc = ax.scatter(
        agg["Hour"],
        agg["avg_power"],
        s=agg["avg_intensity"] * 15,
        c=agg["avg_voltage"],
        cmap="cool",
        alpha=0.85,
        edgecolors=BG,
        linewidths=0.5
    )

    cbar = fig.colorbar(sc, ax=ax)
    cbar.set_label("Avg Voltage (V)", color=TEXT, fontsize=9)
    cbar.ax.yaxis.set_tick_params(color=TEXT)
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color=TEXT)
    cbar.outline.set_edgecolor(GRID)

    ax.set_title("Bubble Chart — Hourly Power × Voltage × Intensity")
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Avg Active Power (kW)")
    ax.set_xticks(range(0, 24))

    return _style(fig)


# ── BONUS 2: Funnel Chart ─────────────────────────────
def chart_funnel(df):
    stages = {
        "Night (0–5 AM)":       df[df["Hour"].between(0,  5)]["Global_active_power"].mean(),
        "Morning (6–11 AM)":    df[df["Hour"].between(6, 11)]["Global_active_power"].mean(),
        "Afternoon (12–17 PM)": df[df["Hour"].between(12,17)]["Global_active_power"].mean(),
        "Evening (18–23 PM)":   df[df["Hour"].between(18,23)]["Global_active_power"].mean(),
    }

    labels = list(stages.keys())
    values = list(stages.values())

    sorted_pairs = sorted(zip(values, labels), reverse=True)
    values, labels = zip(*sorted_pairs)

    colors = ["#00B4D8", "#48CAE4", "#90E0EF", "#ADE8F4"]

    fig, ax = plt.subplots(figsize=(7, 5))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    max_val = max(values)

    for i, (val, label, color) in enumerate(zip(values, labels, colors)):
        width = val / max_val
        left  = (1 - width) / 2

        ax.barh(
            i, width, left=left,
            height=0.5,
            color=color,
            edgecolor=BG
        )

        ax.text(0.5, i, f"{label}  —  {val:.2f} kW",
                ha="center", va="center",
                color=BG, fontsize=9, fontweight="bold")

    ax.set_xlim(0, 1)
    ax.set_title("Funnel Chart — Avg Power by Time of Day",
                 color=TEXT, fontsize=12)
    ax.axis("off")

    return fig


# ── BONUS 3: Pair Plot ────────────────────────────────
def chart_pairplot(df):
    cols = ["Global_active_power", "Voltage",
            "Global_intensity", "Sub_metering_1"]

    sample = df[cols + ["Season"]].dropna().sample(
        min(2000, len(df)), random_state=42
    )

    season_colors = {
        "Spring": "#48CAE4",
        "Summer": "#F4A261",
        "Autumn": "#E76F51",
        "Winter": "#ADE8F4"
    }

    grid = sns.pairplot(
        sample,
        vars=cols,
        hue="Season",
        palette=season_colors,
        plot_kws={"alpha": 0.3, "s": 8},
        diag_kws={"fill": True},
    )

    grid.figure.suptitle(
        "Pair Plot — Key Feature Relationships by Season",
        y=1.02, color=TEXT, fontsize=11
    )

    grid.figure.patch.set_facecolor(BG)
    for ax in grid.axes.flatten():
        ax.set_facecolor(CARD)
        ax.tick_params(colors=TEXT, labelsize=7)
        ax.xaxis.label.set_color(TEXT)
        ax.yaxis.label.set_color(TEXT)
        for spine in ax.spines.values():
            spine.set_edgecolor(GRID)

    return grid.figure