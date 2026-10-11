"""Fig. 1 (overview, Introduction) and Fig. 2 (methodology, Section 4).
Icons: Font Awesome Free solid font (pip install fontawesomefree), licensed CC BY 4.0 / SIL OFL."""
import pathlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch
from matplotlib.font_manager import FontProperties, fontManager
import fontawesomefree

FA = FontProperties(fname=str(next(pathlib.Path(fontawesomefree.__file__).parent.rglob('fa-solid-900.ttf'))))
FAMILY = 'Inter' if any(f.name == 'Inter' for f in fontManager.ttflist) else 'DejaVu Sans'
plt.rcParams['font.family'] = FAMILY

# palette: IT-operations / global software engineering
NAVY, BLUE, TEAL, DTEAL = '#14213D', '#1D6FA3', '#12A39A', '#0B7A75'
AMBER, DAMBER, CORAL, INK, MUTED = '#F4A259', '#D9822B', '#E05A47', '#1E2A38', '#5B6B7C'
TINT = {NAVY: '#E9EDF5', BLUE: '#E7F1F9', TEAL: '#E4F6F4', DTEAL: '#E2F2F1', CORAL: '#FCEBE8', DAMBER: '#FDF1E4', AMBER: '#FEF4E8'}
I = dict(database=0xf1c0, users=0xf0c0, tags=0xf02c, stream=0xf550, globe=0xf0ac, ticket=0xf145, bell=0xf0f3,
         stopwatch=0xf2f2, chart=0xf201, wrench=0xf0ad, search=0xf002, gauge=0xf625, brain=0xf5dc, sitemap=0xf0e8,
         server=0xf233, clock=0xf017, check=0xf058, flag=0xf024, warn=0xf071, layers=0xf5fd)

def icon(ax, x, y, name, size, color, z=6):
    ax.text(x, y, chr(I[name]), fontproperties=FA, fontsize=size, color=color, ha='center', va='center', zorder=z)

def card(ax, x, y, w, h, color, title=None, icon_name=None, head=5.2, body=None, r=1.4):
    ax.add_patch(FancyBboxPatch((x + 0.45, y - 0.55), w, h, boxstyle=f'round,pad=0,rounding_size={r}',
                                fc='#000000', ec='none', alpha=0.08, zorder=1))
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f'round,pad=0,rounding_size={r}',
                                fc=body or 'white', ec=color, lw=1.6, zorder=2))
    if title:
        ax.add_patch(FancyBboxPatch((x, y + h - head), w, head, boxstyle=f'round,pad=0,rounding_size={r}',
                                    fc=color, ec=color, lw=1.6, zorder=3))
        ax.add_patch(plt.Rectangle((x, y + h - head), w, head / 2, fc=color, ec='none', zorder=3))
        tx = x + 2.2
        if icon_name:
            icon(ax, x + 3.2, y + h - head / 2, icon_name, 13, 'white'); tx = x + 6.2
        ax.text(tx, y + h - head / 2, title, color='white', fontsize=11.5, fontweight='bold', va='center', ha='left', zorder=6)

def badge(ax, x, y, text, color, r=1.7, fs=10):
    ax.add_patch(Circle((x, y), r, fc=color, ec='white', lw=1.5, zorder=7))
    ax.text(x, y, text, color='white', fontsize=fs, fontweight='bold', ha='center', va='center', zorder=8)

def arrow(ax, x1, y1, x2, y2, color=MUTED, lw=1.8, rad=0.0, ms=14, z=4, style='-|>'):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=ms, color=color, lw=lw,
                                 connectionstyle=f'arc3,rad={rad}', zorder=z, shrinkA=0, shrinkB=0))

def lines(ax, x, y, items, step=3.1, fs=9.2, color=INK):
    for k, t in enumerate(items):
        bold = t.startswith('**')
        ax.text(x, y - k * step, t.strip('*'), fontsize=fs, color=color, va='center', ha='left',
                fontweight='bold' if bold else 'normal', zorder=6)

# ---------------------------------------------------------------- Fig. 1 overview
def overview(path):
    fig, ax = plt.subplots(figsize=(12, 5.4)); ax.set_xlim(0, 120); ax.set_ylim(0, 54); ax.axis('off')
    P = [(1, CORAL, 'The problem'), (41.5, BLUE, 'The approach'), (82, TEAL, 'What it delivers')]
    for i, (x, c, t) in enumerate(P):
        card(ax, x, 1.5, 37, 51, c, body=TINT[c] if c != BLUE else '#F3F8FC', head=6.4)
        ax.add_patch(FancyBboxPatch((x, 46.6), 37, 6.4, boxstyle='round,pad=0,rounding_size=1.4', fc=c, ec=c, zorder=3))
        ax.add_patch(plt.Rectangle((x, 46.6), 37, 3.2, fc=c, ec='none', zorder=3))
        badge(ax, x + 3.6, 49.8, str(i + 1), NAVY, r=2.0, fs=11)
        ax.text(x + 7.0, 49.8, t, color='white', fontsize=13.5, fontweight='bold', va='center', zorder=6)
    for x in (38.4, 78.9):
        arrow(ax, x, 27, x + 2.8, 27, color=NAVY, lw=3.2, ms=24, z=9)

    # panel 1: two teams across a border, ticket bouncing back
    x0 = 1
    ax.text(x0 + 18.5, 43.2, 'Incidents bounce between support\nteams in different countries', ha='center', va='center',
            fontsize=9.6, color=MUTED, linespacing=1.4, zorder=6)
    ax.plot([x0 + 18.5, x0 + 18.5], [19.5, 37.5], ls=(0, (3, 2.5)), color=MUTED, lw=1.4, zorder=3)
    icon(ax, x0 + 18.5, 38.6, 'flag', 10, MUTED)
    ax.text(x0 + 20.3, 38.6, 'national border', ha='left', va='center', fontsize=8.2, color=MUTED, style='italic', zorder=6)
    for cx, team, cty in [(x0 + 8.5, 'Team A', 'Sweden'), (x0 + 28.5, 'Team B', 'Poland')]:
        ax.add_patch(Circle((cx, 28.5), 5.0, fc='white', ec=NAVY, lw=2.0, zorder=5))
        icon(ax, cx, 28.9, 'users', 17, NAVY)
        ax.text(cx, 21.8, team, ha='center', fontsize=10, fontweight='bold', color=INK, zorder=6)
        ax.text(cx, 19.4, cty, ha='center', fontsize=8.8, color=MUTED, zorder=6)
    arrow(ax, x0 + 12.6, 32.4, x0 + 24.4, 32.4, color=NAVY, lw=2.2, rad=-0.45, ms=15)
    arrow(ax, x0 + 24.4, 25.0, x0 + 12.6, 25.0, color=CORAL, lw=3.0, rad=-0.35, ms=18)
    icon(ax, x0 + 18.5, 34.8, 'ticket', 15, DAMBER, z=7)
    ax.text(x0 + 18.5, 28.6, 'bounce\nback', ha='center', va='center', fontsize=8.6, color=CORAL, fontweight='bold', zorder=7,
            linespacing=1.1, bbox=dict(boxstyle='round,pad=0.25', fc='white', ec=CORAL, lw=1.0))
    for k, (num, txt, c) in enumerate([('10.3%', 'of incidents bounce\nacross a border', CORAL), ('62%', 'of all ping-pong\ncrosses a border', NAVY)]):
        bx = x0 + 2.2 + k * 17.6
        ax.add_patch(FancyBboxPatch((bx, 3.6), 15.6, 11.8, boxstyle='round,pad=0,rounding_size=1.0', fc='white', ec=c, lw=1.3, zorder=4))
        ax.text(bx + 7.8, 11.6, num, ha='center', va='center', fontsize=19, fontweight='bold', color=c, zorder=6)
        ax.text(bx + 7.8, 6.6, txt, ha='center', va='center', fontsize=8.3, color=INK, linespacing=1.25, zorder=6)

    # panel 2: three steps and an event timeline
    x0 = 41.5
    steps = [('database', BLUE, 'Public incident log', 'BPI Challenge 2013, Volvo IT\n7,554 incidents, 65,533 events'),
             ('wrench', TEAL, 'Corrected country labels', 'sender-logged transfers fixed\nfour definitions agree'),
             ('brain', DAMBER, 'Early-warning model', 're-scores every open incident\nafter each new event')]
    for k, (ic, c, head, sub) in enumerate(steps):
        y = 40.4 - k * 9.6
        ax.add_patch(Circle((x0 + 5.6, y), 3.6, fc=c, ec='white', lw=2, zorder=5)); icon(ax, x0 + 5.6, y, ic, 14, 'white')
        ax.text(x0 + 11.0, y + 1.7, head, fontsize=10.6, fontweight='bold', color=INK, va='center', zorder=6)
        ax.text(x0 + 11.0, y - 1.9, sub, fontsize=8.4, color=MUTED, va='center', linespacing=1.3, zorder=6)
        if k < 2:
            arrow(ax, x0 + 5.6, y - 3.8, x0 + 5.6, y - 5.8, color=MUTED, lw=1.6, ms=11)
    ty = 6.6
    ax.plot([x0 + 4, x0 + 31], [ty, ty], color=NAVY, lw=2.2, zorder=4)
    for j in range(6):
        ex = x0 + 4 + j * 4.6
        ax.add_patch(Circle((ex, ty), 1.05, fc='white' if j < 5 else CORAL, ec=NAVY, lw=1.6, zorder=5))
        ax.text(ex, ty - 2.6, f'e{j + 1}' if j < 5 else '', ha='center', fontsize=7.6, color=MUTED, zorder=6)
    ax.text(x0 + 27.0, ty - 2.6, 'bounce', ha='center', fontsize=7.6, color=CORAL, fontweight='bold', zorder=6)
    for ex in (x0 + 4, x0 + 13.2, x0 + 22.4):
        icon(ax, ex, ty + 3.0, 'bell', 10, DAMBER)
    ax.text(x0 + 18.5, 13.4, 'alert raised before the bounce happens', ha='center', fontsize=8.6, color=INK, style='italic', zorder=6)

    # panel 3: three result tiles
    x0 = 82
    tiles = [('bell', CORAL, '55%', 'of future cross-border bounces\ncaught by flagging 10%\nof incidents at intake'),
             ('chart', TEAL, '0.82 to 0.89', 'AUC on the same incidents\nas events arrive (k = 1 to 5)'),
             ('stopwatch', BLUE, '1 to 13 ms', 'to score one ticket on a\nsingle CPU thread')]
    for k, (ic, c, big, sub) in enumerate(tiles):
        y = 33.2 - k * 14.6
        ax.add_patch(FancyBboxPatch((x0 + 2.2, y), 32.6, 12.2, boxstyle='round,pad=0,rounding_size=1.1', fc='white', ec=c, lw=1.4, zorder=4))
        ax.add_patch(Circle((x0 + 7.4, y + 6.1), 3.6, fc=c, ec='white', lw=2, zorder=5)); icon(ax, x0 + 7.4, y + 6.1, ic, 14, 'white')
        ax.text(x0 + 12.8, y + 9.0, big, fontsize=15.5, fontweight='bold', color=c, va='center', zorder=6)
        ax.text(x0 + 12.8, y + 3.9, sub, fontsize=8.0, color=INK, va='center', linespacing=1.25, zorder=6)
    fig.savefig(path, dpi=300, bbox_inches='tight', facecolor='white'); plt.close(fig)

# ---------------------------------------------------------------- Fig. 2 methodology
def methodology(path):
    fig, ax = plt.subplots(figsize=(12, 7.0)); ax.set_xlim(0, 120); ax.set_ylim(0, 70); ax.axis('off')
    ax.text(1.5, 67.6, 'DATA AND LABELS', fontsize=10.5, fontweight='bold', color=NAVY, va='center')
    ax.plot([19.5, 118.5], [67.6, 67.6], color='#C9D3DE', lw=1.2)
    W, H, Y = 26.6, 25.5, 39.2
    xs = [1.5, 31.6, 61.7, 91.8]
    stages = [(NAVY, 'database', 'Event log', ['BPI Challenge 2013', 'Volvo IT, VINST system', '**7,554 incidents', '**65,533 events', '649 teams, 704 products']),
              (BLUE, 'sitemap', 'Team segments', ['Runs of events by one team', 'Transfer event is logged', 'under the sender:', '**excluded from receiving', '**team\'s country (92%)']),
              (TEAL, 'tags', 'Labels', ['Team ping-pong: 16.7%', '**Cross-border (D1): 10.3%', 'Checks with D2, D3, D5', 'Jaccard 0.78 to 0.93', 'Matches prior count (1,258)']),
              (DTEAL, 'stream', 'Prefix encoding', ['k = 1 to 10 events', 'Outcome still in the future', '**44 features at event k', '**41,813 prefixes', 'from 7,553 incidents'])]
    for k, (c, ic, t, body) in enumerate(stages):
        x = xs[k]
        card(ax, x, Y, W, H, c, t, ic, head=5.6)
        badge(ax, x + W - 2.2, Y + H - 0.2, str(k + 1), DAMBER, r=1.8, fs=10)
        for j, txt in enumerate(body):
            b = txt.startswith('**')
            ax.text(x + 2.2, Y + H - 9.2 - j * 3.45, txt.strip('*'), fontsize=9.0, color=c if b else INK,
                    fontweight='bold' if b else 'normal', va='center', zorder=6)
        if k < 3:
            arrow(ax, x + W + 0.3, Y + H / 2, xs[k + 1] - 0.3, Y + H / 2, color=NAVY, lw=2.4, ms=18, z=8)

    ax.text(1.5, 33.6, 'ANALYSES', fontsize=10.5, fontweight='bold', color=NAVY, va='center')
    ax.plot([12.5, 118.5], [33.6, 33.6], color='#C9D3DE', lw=1.2)
    bus = 35.9
    ax.plot([xs[0] + W / 2, xs[3] + W / 2], [bus, bus], color=MUTED, lw=1.8, zorder=3)
    ax.plot([xs[2] + W / 2, xs[2] + W / 2], [Y - 0.6, bus], color=MUTED, lw=1.8, zorder=3)
    ax.plot([xs[3] + W / 2, xs[3] + W / 2], [Y - 0.6, bus], color=MUTED, lw=1.8, zorder=3)
    H2, Y2 = 22.8, 7.6
    rqs = [(CORAL, 'globe', 'RQ1  Prevalence', ['Country pairs, entry points', 'Opening hour and period', '**Time-varying Cox model', 'Proportionality by time band']),
           (DAMBER, 'brain', 'RQ2  Prediction', ['**11 models, nested tuning', 'Grouped 5 x 3 repeated CV', 'Common cohort, ablation', 'Label variants, time split']),
           (BLUE, 'search', 'RQ3  Drivers', ['**SHAP values', 'Tuned LightGBM', '5,000 sampled prefixes', 'Per-feature contributions']),
           (TEAL, 'gauge', 'RQ4  Deployment', ['**Single-thread latency', 'Batch throughput', 'Model size', 'Training time per fold'])]
    for k, (c, ic, t, body) in enumerate(rqs):
        x = xs[k]
        arrow(ax, x + W / 2, bus, x + W / 2, Y2 + H2 + 0.5, color=MUTED, lw=1.8, ms=13)
        card(ax, x, Y2, W, H2, c, t, ic, head=5.6, body=TINT[c])
        for j, txt in enumerate(body):
            b = txt.startswith('**')
            ax.text(x + 2.2, Y2 + H2 - 9.0 - j * 3.45, txt.strip('*'), fontsize=9.0, color=c if b else INK,
                    fontweight='bold' if b else 'normal', va='center', zorder=6)
    # environment strip
    ax.add_patch(FancyBboxPatch((1.5, 0.6), 117, 4.4, boxstyle='round,pad=0,rounding_size=1.0', fc='#F1F4F8', ec='#C9D3DE', lw=1, zorder=2))
    items = [('server', 'Google Colab, 2 vCPU'), ('clock', 'Full run 77 min'), ('layers', 'Every fold saved as it finishes'), ('check', 'Rerun within 0.007 AUC')]
    for k, (ic, t) in enumerate(items):
        x = 4.5 + k * 28.6
        icon(ax, x, 2.8, ic, 10.5, NAVY); ax.text(x + 2.4, 2.8, t, fontsize=9, color=INK, va='center', zorder=6)
    fig.savefig(path, dpi=300, bbox_inches='tight', facecolor='white'); plt.close(fig)

if __name__ == '__main__':
    overview('Fig1_overview.png'); methodology('Fig2_methodology.png'); print('ok', FAMILY)
