"""Generates static charts using matplotlib/seaborn for embedding in PDF reports."""

import io
import base64

from apps.dashboards.services import DashboardService


OPERATOR_COLORS = {
    'TELECEL': '#E30613',
    'ORANGE': '#FF6600',
    'STARLINK': '#000000',
}

ARN_PRIMARY = '#1B2A4A'


def _get_color(code):
    return OPERATOR_COLORS.get(code, '#6B7280')


def generate_market_share_chart(year, quarter=None, market='mobile'):
    """Pie chart of market shares. Returns base64-encoded PNG."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    shares = DashboardService.get_market_share(year, quarter, market)
    if not shares:
        return None

    labels = [s['operator_name'] for s in shares]
    sizes = [s['share_pct'] for s in shares]
    colors = [_get_color(s['operator_code']) for s in shares]

    fig, ax = plt.subplots(figsize=(6, 4))
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors, autopct='%1.1f%%',
        startangle=90, textprops={'fontsize': 10},
    )
    for t in autotexts:
        t.set_color('white')
        t.set_fontweight('bold')

    ax.set_title(f'Quota de Mercado — {year}', fontsize=12, fontweight='bold', color=ARN_PRIMARY)
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')


def generate_trends_chart(category_code, start_year=2018, end_year=2026):
    """Stacked bar chart with trend line. Returns base64-encoded PNG."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        return None

    data = DashboardService.get_trends(category_code, start_year=start_year, end_year=end_year)
    if not data:
        return None

    operators = DashboardService.get_applicable_operators(category_code)
    op_codes = [op.code for op in operators]
    op_names = {op.code: op.name for op in operators}
    op_colors = {op.code: _get_color(op.code) for op in operators}

    years = [d['period'] for d in data]
    x = np.arange(len(years))
    width = 0.6

    fig, ax = plt.subplots(figsize=(10, 5))

    bottom = np.zeros(len(years))
    for code in op_codes:
        values = np.array([d.get(code, 0) for d in data], dtype=float)
        ax.bar(x, values, width, bottom=bottom, label=op_names.get(code, code),
               color=op_colors.get(code), alpha=0.85)
        bottom += values

    totals = [d.get('total', 0) for d in data]
    ax.plot(x, totals, color=ARN_PRIMARY, linewidth=2, marker='o', markersize=4, label='Total')

    ax.set_xticks(x)
    ax.set_xticklabels(years, fontsize=9)
    ax.legend(loc='upper left', fontsize=8)
    ax.set_title(f'Evolução — {category_code}', fontsize=12, fontweight='bold', color=ARN_PRIMARY)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')


def generate_hhi_chart(year, market='mobile'):
    """Gauge-style HHI indicator. Returns base64-encoded PNG."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    hhi_data = DashboardService.get_hhi(year, market)
    if not hhi_data:
        return None

    hhi_val = hhi_data['hhi']
    classification = hhi_data['classification']

    fig, ax = plt.subplots(figsize=(6, 3))

    color = '#10B981' if hhi_val < 1500 else '#F59E0B' if hhi_val < 2500 else '#EF4444'

    ax.barh(['HHI'], [hhi_val], color=color, height=0.4, alpha=0.85)
    ax.axvline(x=1500, color='#F59E0B', linestyle='--', linewidth=1, alpha=0.7)
    ax.axvline(x=2500, color='#EF4444', linestyle='--', linewidth=1, alpha=0.7)
    ax.set_xlim(0, max(hhi_val * 1.2, 3000))
    ax.set_title(f'HHI = {int(hhi_val)} — {classification}', fontsize=12,
                 fontweight='bold', color=ARN_PRIMARY)
    ax.text(1500, -0.35, '1500', ha='center', fontsize=8, color='#F59E0B')
    ax.text(2500, -0.35, '2500', ha='center', fontsize=8, color='#EF4444')
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')


def generate_all_charts(year, quarter=None):
    """Returns dict of all chart images as base64 PNGs for embedding in reports."""
    charts = {}

    for market in ['mobile', 'fixed_internet', 'revenue']:
        chart = generate_market_share_chart(year, quarter, market)
        if chart:
            charts[f'market_share_{market}'] = chart

    for cat_code in ['estacoes_moveis', 'trafego_originado', 'receitas']:
        chart = generate_trends_chart(cat_code, end_year=year)
        if chart:
            charts[f'trends_{cat_code}'] = chart

    hhi_chart = generate_hhi_chart(year)
    if hhi_chart:
        charts['hhi_mobile'] = hhi_chart

    return charts
