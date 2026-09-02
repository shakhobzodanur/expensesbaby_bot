# -*- coding: utf-8 -*-
"""Generate weekly spending bar chart as PNG."""

import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta


WEEKDAY_LABELS = {
    "en": ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
    "ru": ["Пн","Вт","Ср","Чт","Пт","Сб","Вс"],
    "uz": ["Du","Se","Ch","Pa","Ju","Sh","Ya"],
}


def generate_week_chart(daily_totals: list, currency: str = "UZS", lang: str = "en") -> io.BytesIO:
    """
    daily_totals: list of (date_str 'YYYY-MM-DD', amount) for days that have data.
    Builds a full 7-day series (today back 6 days), filling zeros for missing days.
    """
    today = datetime.now().date()
    days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    totals_map = {d: v for d, v in daily_totals}

    values = []
    for d in days:
        key = d.strftime("%Y-%m-%d")
        values.append(totals_map.get(key, 0))

    labels_set = WEEKDAY_LABELS.get(lang, WEEKDAY_LABELS["en"])
    labels = [labels_set[d.weekday()] for d in days]

    BG = "#16213e"
    fig, ax = plt.subplots(figsize=(7, 4))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    max_val = max(values) if max(values) > 0 else 1
    colors = []
    for v in values:
        ratio = v / max_val
        if ratio == 0:
            colors.append("#2a3050")
        elif ratio < 0.4:
            colors.append("#2ecc71")
        elif ratio < 0.7:
            colors.append("#f39c12")
        else:
            colors.append("#e74c3c")

    bars = ax.bar(labels, values, color=colors, width=0.6, zorder=3)

    # value labels on top of bars
    for bar, v in zip(bars, values):
        if v > 0:
            label = f"{v/1000:.0f}k" if v >= 1000 else f"{v:.0f}"
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max_val*0.02,
                    label, ha='center', va='bottom', fontsize=9, color='white', zorder=4)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#445')
    ax.tick_params(colors='#cccccc', labelsize=10)
    ax.set_ylim(0, max_val * 1.25)
    ax.yaxis.set_visible(False)
    ax.grid(axis='y', color='#2a3050', linewidth=0.5, zorder=0)

    plt.tight_layout(pad=1.0)

    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=140, bbox_inches='tight',
                facecolor=BG, edgecolor='none')
    plt.close(fig)
    buf.seek(0)
    return buf
