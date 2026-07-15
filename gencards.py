"""Generate self-hosted GitHub stats SVG cards (tokyonight theme) from ghdata.json."""
import datetime, json, math, os

YEAR = datetime.date.today().year

HERE = os.path.dirname(os.path.abspath(__file__))
BG, TITLE, ICON, TEXT = "#1a1b27", "#70a5fd", "#bf91f3", "#38bdae"
FONT = "'Segoe UI', Ubuntu, Sans-Serif"

with open(os.path.join(HERE, "ghdata.json"), encoding="utf-8") as f:
    u = json.load(f)["data"]["user"]

stars = sum(r["stargazerCount"] for r in u["repositories"]["nodes"])
cc = u["contributionsCollection"]
commits = cc["totalCommitContributions"]
prs = u["pullRequests"]["totalCount"]
contribs = cc["contributionCalendar"]["totalContributions"]

# ---------- stats card ----------
def star_points(cx, cy, ro=7.5, ri=3.2):
    pts = []
    for i in range(10):
        r = ro if i % 2 == 0 else ri
        a = -math.pi / 2 + i * math.pi / 5
        pts.append(f"{cx + r * math.cos(a):.2f},{cy + r * math.sin(a):.2f}")
    return " ".join(pts)

def icon_star(cx, cy):
    return f'<polygon points="{star_points(cx, cy)}" fill="none" stroke="{ICON}" stroke-width="1.6" stroke-linejoin="round"/>'

def icon_commit(cx, cy):
    return (f'<circle cx="{cx}" cy="{cy}" r="4" fill="none" stroke="{ICON}" stroke-width="1.8"/>'
            f'<line x1="{cx-9}" y1="{cy}" x2="{cx-5}" y2="{cy}" stroke="{ICON}" stroke-width="1.8" stroke-linecap="round"/>'
            f'<line x1="{cx+5}" y1="{cy}" x2="{cx+9}" y2="{cy}" stroke="{ICON}" stroke-width="1.8" stroke-linecap="round"/>')

def icon_pr(cx, cy):
    return (f'<circle cx="{cx-5}" cy="{cy-5}" r="2.8" fill="none" stroke="{ICON}" stroke-width="1.7"/>'
            f'<circle cx="{cx-5}" cy="{cy+5}" r="2.8" fill="none" stroke="{ICON}" stroke-width="1.7"/>'
            f'<line x1="{cx-5}" y1="{cy-2}" x2="{cx-5}" y2="{cy+2}" stroke="{ICON}" stroke-width="1.7"/>'
            f'<circle cx="{cx+5}" cy="{cy+5}" r="2.8" fill="none" stroke="{ICON}" stroke-width="1.7"/>'
            f'<path d="M {cx-1} {cy-5} h 3 a 3 3 0 0 1 3 3 v 4" fill="none" stroke="{ICON}" stroke-width="1.7" stroke-linecap="round"/>')

def icon_grid(cx, cy):
    s, g, out = 6, 2, []
    for dx in (0, 1):
        for dy in (0, 1):
            op = [1, 0.7, 0.45, 1][dx * 2 + dy]
            x = cx - s - g / 2 + dx * (s + g)
            y = cy - s - g / 2 + dy * (s + g)
            out.append(f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="1.5" fill="{ICON}" opacity="{op}"/>')
    return "".join(out)

rows = [
    (icon_star, "Total Stars Earned", stars),
    (icon_commit, f"Commits ({YEAR})", commits),
    (icon_pr, "Pull Requests", prs),
    (icon_grid, f"Contributions ({YEAR})", contribs),
]

W, H, y0, dy = 467, 195, 72, 30
body = []
for i, (icon, label, val) in enumerate(rows):
    y = y0 + i * dy
    body.append(f'<g class="row" style="animation-delay:{300 + i * 150}ms">'
                f'{icon(33, y - 5)}'
                f'<text x="55" y="{y}" font-size="14" fill="{TEXT}" font-family={FONT!r}>{label}:</text>'
                f'<text x="435" y="{y}" text-anchor="end" font-size="14" font-weight="700" fill="{TEXT}" font-family={FONT!r}>{val}</text></g>')

stats_svg = f'''<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Danny's GitHub stats">
<style>
.row{{opacity:0;animation:fi .6s ease-out forwards}}
.title{{opacity:0;animation:fi .6s ease-out forwards;animation-delay:.1s}}
@keyframes fi{{to{{opacity:1}}}}
</style>
<rect width="{W}" height="{H}" rx="8" fill="{BG}"/>
<text class="title" x="25" y="40" font-size="18" font-weight="700" fill="{TITLE}" font-family={FONT!r}>Danny's GitHub Stats</text>
{"".join(body)}
</svg>'''

# ---------- top languages card ----------
langs = {}
colors = {}
for repo in u["repositories"]["nodes"]:
    for e in repo["languages"]["edges"]:
        n = e["node"]["name"]
        langs[n] = langs.get(n, 0) + e["size"]
        colors[n] = e["node"]["color"]
total = sum(langs.values())
ordered = sorted(langs.items(), key=lambda kv: -kv[1])

LW, LH = 320, 210
bar_x, bar_y, bar_w, bar_h = 25, 58, LW - 50, 10
segs, x = [], bar_x
for name, size in ordered:
    w = size / total * bar_w
    segs.append(f'<rect x="{x:.2f}" y="{bar_y}" width="{w:.2f}" height="{bar_h}" fill="{colors[name]}"/>')
    x += w

legend = []
for i, (name, size) in enumerate(ordered):
    col, row = divmod(i, 3)
    lx, ly = 25 + col * 148, 95 + row * 27
    pct = size / total * 100
    legend.append(f'<g class="row" style="animation-delay:{400 + i * 100}ms">'
                  f'<circle cx="{lx + 5}" cy="{ly - 4}" r="5" fill="{colors[name]}"/>'
                  f'<text x="{lx + 18}" y="{ly}" font-size="12.5" fill="{TEXT}" font-family={FONT!r}>{name} <tspan font-weight="700">{pct:.1f}%</tspan></text></g>')

langs_svg = f'''<svg width="{LW}" height="{LH}" viewBox="0 0 {LW} {LH}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Most used languages">
<style>
.row{{opacity:0;animation:fi .6s ease-out forwards}}
.title{{opacity:0;animation:fi .6s ease-out forwards;animation-delay:.1s}}
.bar{{opacity:0;animation:fi .8s ease-out forwards;animation-delay:.25s}}
@keyframes fi{{to{{opacity:1}}}}
</style>
<rect width="{LW}" height="{LH}" rx="8" fill="{BG}"/>
<text class="title" x="25" y="40" font-size="18" font-weight="700" fill="{TITLE}" font-family={FONT!r}>Most Used Languages</text>
<defs><clipPath id="bar"><rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" rx="5"/></clipPath></defs>
<g class="bar" clip-path="url(#bar)">{"".join(segs)}</g>
{"".join(legend)}
</svg>'''

with open(os.path.join(HERE, "stats.svg"), "w", encoding="utf-8") as f:
    f.write(stats_svg)
with open(os.path.join(HERE, "top-langs.svg"), "w", encoding="utf-8") as f:
    f.write(langs_svg)
print("stars", stars, "| commits", commits, "| prs", prs, "| contribs", contribs)
print(" ".join(f"{n}:{s/total*100:.1f}%" for n, s in ordered))
