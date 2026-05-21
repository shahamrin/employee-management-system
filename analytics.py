"""
analytics.py - Matplotlib chart generation for Employee Analytics Dashboard
Charts are rendered to in-memory buffers and returned as Base64 strings
for direct embedding in HTML templates, avoiding file I/O overhead.
"""

import io
import base64
import matplotlib
matplotlib.use('Agg')  # Thread-safe, non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


# ---------------------------------------------------------------------------
# Color palette (matches the UI's indigo / violet theme)
# ---------------------------------------------------------------------------
COLORS = [
    '#6366f1',  # Indigo-500
    '#8b5cf6',  # Violet-500
    '#a78bfa',  # Violet-400
    '#c084fc',  # Purple-400
    '#e879f9',  # Fuchsia-400
    '#f472b6',  # Pink-400
    '#fb7185',  # Rose-400
    '#38bdf8',  # Sky-400
    '#34d399',  # Emerald-400
    '#facc15',  # Yellow-400
]

BG_COLOR   = '#0f172a'   # Slate-900
TEXT_COLOR  = '#e2e8f0'   # Slate-200
GRID_COLOR  = '#1e293b'  # Slate-800


def _fig_to_base64(fig):
    """Convert a matplotlib figure to a Base64-encoded PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


# ---------------------------------------------------------------------------
# Chart 1 – Department-wise Average Salary (Horizontal Bar)
# ---------------------------------------------------------------------------

def generate_salary_bar_chart(dept_stats):
    """
    Generate a horizontal bar chart showing average salary per department.
    Returns a Base64-encoded PNG string.
    """
    if not dept_stats:
        return None

    departments = [d['department'] for d in dept_stats]
    avg_salaries = [round(d['avg_salary'], 2) for d in dept_stats]

    fig, ax = plt.subplots(figsize=(8, max(3, len(departments) * 0.7)))
    fig.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    bars = ax.barh(departments, avg_salaries,
                   color=COLORS[:len(departments)],
                   height=0.55, edgecolor='none', zorder=3)

    # Value labels on each bar
    for bar, val in zip(bars, avg_salaries):
        ax.text(bar.get_width() + max(avg_salaries) * 0.02,
                bar.get_y() + bar.get_height() / 2,
                f'₹{val:,.0f}', va='center', ha='left',
                color=TEXT_COLOR, fontsize=10, fontweight='600')

    ax.set_xlabel('Average Salary (₹)', color=TEXT_COLOR, fontsize=11, labelpad=10)
    ax.set_title('Department-wise Average Salary', color=TEXT_COLOR,
                 fontsize=14, fontweight='bold', pad=15)

    ax.tick_params(colors=TEXT_COLOR, labelsize=10)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'₹{x:,.0f}'))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(GRID_COLOR)
    ax.spines['left'].set_color(GRID_COLOR)
    ax.set_axisbelow(True)
    ax.xaxis.grid(True, color=GRID_COLOR, linewidth=0.5)

    fig.tight_layout()
    return _fig_to_base64(fig)


# ---------------------------------------------------------------------------
# Chart 2 – Department Employee Distribution (Donut Chart)
# ---------------------------------------------------------------------------

def generate_department_pie_chart(dept_stats):
    """
    Generate a donut chart showing the employee distribution by department.
    Returns a Base64-encoded PNG string.
    """
    if not dept_stats:
        return None

    departments = [d['department'] for d in dept_stats]
    counts = [d['emp_count'] for d in dept_stats]

    fig, ax = plt.subplots(figsize=(6, 6))
    fig.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    wedges, texts, autotexts = ax.pie(
        counts,
        labels=departments,
        autopct='%1.1f%%',
        colors=COLORS[:len(departments)],
        startangle=140,
        pctdistance=0.78,
        wedgeprops=dict(width=0.45, edgecolor=BG_COLOR, linewidth=2),
    )

    for t in texts:
        t.set_color(TEXT_COLOR)
        t.set_fontsize(10)
    for t in autotexts:
        t.set_color('#ffffff')
        t.set_fontsize(9)
        t.set_fontweight('bold')

    # Center label
    total = sum(counts)
    ax.text(0, 0, f'{total}\nEmployees', ha='center', va='center',
            fontsize=16, fontweight='bold', color=TEXT_COLOR)

    ax.set_title('Employee Distribution by Department', color=TEXT_COLOR,
                 fontsize=14, fontweight='bold', pad=20)

    fig.tight_layout()
    return _fig_to_base64(fig)


# ---------------------------------------------------------------------------
# Chart 3 – Salary Distribution Histogram
# ---------------------------------------------------------------------------

def generate_salary_histogram(employees):
    """
    Generate a histogram of employee salaries.
    Returns a Base64-encoded PNG string.
    """
    if not employees:
        return None

    salaries = [e['salary'] for e in employees if e['salary'] > 0]
    if not salaries:
        return None

    fig, ax = plt.subplots(figsize=(8, 4.5))
    fig.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    n_bins = min(15, max(5, len(salaries) // 3))
    n, bins, patches = ax.hist(salaries, bins=n_bins, edgecolor=BG_COLOR,
                                linewidth=1.2, zorder=3)

    # Gradient coloring for bins
    max_n = max(n) if max(n) > 0 else 1
    for count, patch in zip(n, patches):
        ratio = count / max_n
        r = int(99 + (139 - 99) * ratio)
        g = int(102 + (92 - 102) * ratio)
        b = int(241 + (246 - 241) * ratio)
        patch.set_facecolor(f'#{r:02x}{g:02x}{b:02x}')

    ax.set_xlabel('Salary (₹)', color=TEXT_COLOR, fontsize=11, labelpad=10)
    ax.set_ylabel('Number of Employees', color=TEXT_COLOR, fontsize=11, labelpad=10)
    ax.set_title('Salary Distribution', color=TEXT_COLOR,
                 fontsize=14, fontweight='bold', pad=15)

    ax.tick_params(colors=TEXT_COLOR, labelsize=10)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'₹{x:,.0f}'))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(GRID_COLOR)
    ax.spines['left'].set_color(GRID_COLOR)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=GRID_COLOR, linewidth=0.5)

    fig.tight_layout()
    return _fig_to_base64(fig)
