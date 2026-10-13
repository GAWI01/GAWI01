"""Render the profile README cards (Nord theme).

    python render.py static <dir>   # hand-written cards -> assets/
    python render.py stats  <dir>   # live GitHub stats  -> dist/ (needs GITHUB_TOKEN)

Every card is drawn on a 600px-wide canvas (1200px for full-width ones) with an
8px transparent margin, so two cards placed side by side at 50% line up exactly
with the full-width header above them.
"""
import datetime as dt
import json
import os
import sys
import urllib.request

USER = os.environ.get("GH_USER", "GAWI01")

FONT = "Inter,-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
M = 8  # outer margin
R = 14  # corner radius
BAND = 58  # header band height

C = dict(
    bg="#2e3440", band="#3b4252", border="#4c566a", line="#434c5e",
    text="#eceff4", muted="#a7b1c2", frost="#88c0d0", blue="#81a1c1",
    deep="#5e81ac", green="#a3be8c", purple="#b48ead", yellow="#ebcb8b",
    orange="#d08770", red="#bf616a",
)
LANG_COLORS = [C["frost"], C["green"], C["purple"], C["yellow"], C["orange"], C["blue"]]


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def card(w, h, title, body, status=None, aria=None):
    """A bordered card with a header band, drawn inside an M-px margin."""
    iw, ih = w - 2 * M, h - 2 * M
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{esc(aria or title)}">',
        f'<defs><clipPath id="c"><rect x="{M}" y="{M}" width="{iw}" height="{ih}" rx="{R}"/></clipPath></defs>',
        f'<g clip-path="url(#c)" font-family="{FONT}">',
        f'<rect x="{M}" y="{M}" width="{iw}" height="{ih}" fill="{C["bg"]}"/>',
        f'<rect x="{M}" y="{M}" width="{iw}" height="{BAND}" fill="{C["band"]}"/>',
        f'<line x1="{M}" y1="{M + BAND}" x2="{M + iw}" y2="{M + BAND}" stroke="{C["border"]}"/>',
        f'<text x="{M + 24}" y="{M + 37}" fill="{C["text"]}" font-size="21" font-weight="700">{esc(title)}</text>',
    ]
    if status:
        txt, col = status
        tw = len(txt) * 9.2
        out.append(
            f'<circle cx="{M + iw - 24 - tw - 12:.0f}" cy="{M + 30}" r="5" fill="{col}">'
            f'<animate attributeName="opacity" values="1;.3;1" dur="1.6s" repeatCount="indefinite"/></circle>'
            f'<text x="{M + iw - 24}" y="{M + 35}" text-anchor="end" fill="{col}" font-size="13" '
            f'font-weight="700" letter-spacing="1.2">{esc(txt)}</text>')
    out.append(f'<g transform="translate({M} {M + BAND})">{body}</g>')
    out.append("</g>")
    out.append(f'<rect x="{M + .5}" y="{M + .5}" width="{iw - 1}" height="{ih - 1}" rx="{R}" fill="none" stroke="{C["border"]}"/>')
    out.append("</svg>\n")
    return "\n".join(out)


def pills(items, x0, y0, maxx, fill, color, size=14):
    s, x, y = "", x0, y0
    for it in items:
        pw = len(it) * size * 0.6 + 26
        if x + pw > maxx:
            x, y = x0, y + 38
        s += (f'<rect x="{x:.0f}" y="{y}" width="{pw:.0f}" height="30" rx="15" fill="{fill}"/>'
              f'<text x="{x + pw / 2:.0f}" y="{y + 20}" text-anchor="middle" fill="{color}" '
              f'font-size="{size}" font-weight="700">{esc(it)}</text>')
        x += pw + 8
    return s, y + 30


ICONS = {
    "shield": lambda c: f'<path d="M0 -11 L10 -7 V1 C10 7 5 11 0 13 C-5 11 -10 7 -10 1 V-7 Z" fill="none" stroke="{c}" stroke-width="2.2"/><path d="M-4 1 L-1 4 L5 -3" fill="none" stroke="{c}" stroke-width="2.2" stroke-linecap="round"/>',
    "chip": lambda c: f'<rect x="-8" y="-8" width="16" height="16" rx="3" fill="none" stroke="{c}" stroke-width="2.2"/><rect x="-3" y="-3" width="6" height="6" fill="{c}"/><path d="M-4 -12v4M4 -12v4M-4 8v4M4 8v4M-12 -4h4M-12 4h4M8 -4h4M8 4h4" stroke="{c}" stroke-width="2"/>',
    "code": lambda c: f'<path d="M-5 -8 L-12 0 L-5 8 M5 -8 L12 0 L5 8" fill="none" stroke="{c}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>',
    "pin": lambda c: f'<path d="M0 12 C-7 4 -9 0 -9 -3 A9 9 0 0 1 9 -3 C9 0 7 4 0 12 Z" fill="none" stroke="{c}" stroke-width="2.2"/><circle cy="-3" r="3" fill="{c}"/>',
}


# --------------------------------------------------------------- static cards
W, H = 600, 330
IW = W - 2 * M  # inner width


def about():
    rows = [("shield", C["frost"], "Cybersecurity junior"),
            ("chip", C["green"], "AI systems"),
            ("code", C["purple"], "Software"),
            ("pin", C["yellow"], "Norway")]
    b = f'<text x="24" y="52" fill="{C["text"]}" font-size="27" font-weight="800" letter-spacing="1">GABRIEL WITZØE</text>'
    for i, (ic, c, txt) in enumerate(rows):
        y = 104 + i * 44
        b += (f'<g transform="translate(24 {y - 23})"><rect width="34" height="34" rx="9" fill="{c}" fill-opacity=".12" '
              f'stroke="{c}" stroke-opacity=".45"/><g transform="translate(17 17)">{ICONS[ic](c)}</g></g>'
              f'<text x="74" y="{y}" fill="{C["text"]}" font-size="18" font-weight="700">{txt}</text>')
        if i < 3:
            b += f'<line x1="74" y1="{y + 16}" x2="{IW - 24}" y2="{y + 16}" stroke="{C["line"]}"/>'
    return card(W, H, "About", b, ("ONLINE", C["green"]), "About — cybersecurity junior, AI systems, software, Norway")


def stack():
    b = f'<text x="24" y="38" fill="{C["frost"]}" font-size="13" font-weight="700" letter-spacing="2">CORE</text>'
    p, end = pills(["Python", "TypeScript", "Next.js", "FastAPI", "Supabase", "SQL", "Git", "Docker", "Linux"],
                   24, 50, IW - 24, C["line"], C["frost"])
    b += p
    y = end + 36
    b += f'<text x="24" y="{y}" fill="{C["purple"]}" font-size="13" font-weight="700" letter-spacing="2">SECURITY</text>'
    p, _ = pills(["Burp Suite", "Nmap", "Wireshark", "Kali Linux", "Splunk", "ELK"], 24, y + 12, IW - 24, C["line"], C["purple"])
    return card(W, H, "Stack", b + p, ("DAILY DRIVERS", C["green"]),
                "Stack — Python, TypeScript, Next.js, FastAPI, Supabase, SQL, Git, Docker, Linux, Burp Suite, Nmap, Wireshark, Kali Linux, Splunk, ELK")


PH = 270


def ffai():
    pts = [(410, 150), (432, 132), (454, 140), (476, 112), (498, 120), (520, 92), (542, 100), (560, 70)]
    poly = " ".join(f"{x},{y}" for x, y in pts)
    b = (f'<polyline points="{poly}" fill="none" stroke="{C["frost"]}" stroke-width="2.5" stroke-linejoin="round" opacity=".5" '
         f'stroke-dasharray="260" stroke-dashoffset="260"><animate attributeName="stroke-dashoffset" from="260" to="0" dur="2s" begin=".3s" fill="freeze"/></polyline>'
         f'<circle cx="560" cy="70" r="4" fill="{C["green"]}" opacity="0"><set attributeName="opacity" to="1" begin="2.3s"/></circle>'
         f'<text x="24" y="60" fill="{C["text"]}" font-size="32" font-weight="800">Fantasy Football AI</text>'
         f'<text x="24" y="96" fill="{C["muted"]}" font-size="17">Gameweek intelligence for</text>'
         f'<text x="24" y="120" fill="{C["muted"]}" font-size="17">Fantasy Premier League.</text>')
    p, _ = pills(["Python", "FastAPI", "Next.js", "AI"], 24, 146, IW - 24, C["line"], C["frost"], 13)
    return card(W, PH, "Public", b + p, ("ACTIVE", C["green"]), "Fantasy Football AI — gameweek intelligence for Fantasy Premier League")


def private():
    b = (f'<text x="24" y="60" fill="{C["text"]}" font-size="38" font-weight="800">[REDACTED]</text>'
         f'<rect x="24" y="82" width="300" height="18" rx="3" fill="{C["line"]}"/>'
         f'<rect x="24" y="82" width="0" height="18" rx="3" fill="{C["frost"]}" opacity=".75">'
         f'<animate attributeName="width" values="0;300;300;0" keyTimes="0;.4;.8;1" dur="5s" repeatCount="indefinite"/></rect>'
         f'<rect x="24" y="108" width="220" height="18" rx="3" fill="{C["line"]}"/>'
         f'<text x="24" y="168" fill="{C["muted"]}" font-size="17">Experiments in active development.</text>'
         f'<g transform="translate({IW - 70} 100)" fill="none" stroke="{C["frost"]}" stroke-width="3">'
         f'<rect x="-24" y="-4" width="48" height="36" rx="7"/><path d="M-13 -4v-11a13 13 0 0 1 26 0v11"/>'
         f'<circle cx="0" cy="13" r="4" fill="{C["frost"]}"/></g>')
    return card(W, PH, "Private", b, ("CLASSIFIED", C["purple"]), "Private projects in active development")


def static(out):
    for name, svg in dict(profile=about(), stack=stack(), ffai=ffai(), private=private()).items():
        open(os.path.join(out, f"{name}.svg"), "w").write(svg)


# --------------------------------------------------------------- live stats
QUERY = """query($login:String!){user(login:$login){
  createdAt
  contributionsCollection{totalCommitContributions restrictedContributionsCount totalPullRequestContributions
    contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}
  pullRequests{totalCount}
  repositories(ownerAffiliations:OWNER,isFork:false,first:100){totalCount nodes{stargazerCount
    languages(first:10,orderBy:{field:SIZE,direction:DESC}){edges{size node{name}}}}}
}}"""


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "Content-Type": "application/json"})
    data = json.load(urllib.request.urlopen(req, timeout=30))
    if "errors" in data:
        raise SystemExit(data["errors"])
    return data["data"]["user"]


def streaks(days):
    days = sorted(days, key=lambda d: d["date"])
    longest = run = 0
    best = (None, None)
    start = None
    for d in days:
        if d["contributionCount"] > 0:
            run += 1
            start = start or d["date"]
            if run > longest:
                longest, best = run, (start, d["date"])
        else:
            run, start = 0, None
    # current streak may end today (if today has contributions) or yesterday
    cur = 0
    i = len(days) - 1
    if i >= 0 and days[i]["contributionCount"] == 0:
        i -= 1
    end = days[i]["date"] if i >= 0 else None
    while i >= 0 and days[i]["contributionCount"] > 0:
        cur += 1
        i -= 1
    cstart = days[i + 1]["date"] if cur else None
    return cur, (cstart, end if cur else None), longest, best


def fmt_date(s):
    return dt.date.fromisoformat(s).strftime("%b %-d") if s else "—"


def stat_cards(u):
    cc = u["contributionsCollection"]
    repos = u["repositories"]["nodes"]
    stars = sum(r["stargazerCount"] for r in repos)
    commits = cc["totalCommitContributions"] + cc["restrictedContributionsCount"]
    total = cc["contributionCalendar"]["totalContributions"]

    # -- stats
    items = [("Contributions", total, C["frost"]), ("Commits", commits, C["green"]),
             ("Pull requests", u["pullRequests"]["totalCount"], C["purple"]),
             ("Repositories", u["repositories"]["totalCount"], C["yellow"]),
             ("Stars", stars, C["orange"]), ("Since", u["createdAt"][:4], C["blue"])]
    b = ""
    cw = IW / 3
    for i, (label, val, col) in enumerate(items):
        x, y = (i % 3) * cw + 24, 62 + (i // 3) * 92
        b += (f'<text x="{x:.0f}" y="{y}" fill="{col}" font-size="34" font-weight="800">{esc(val)}</text>'
              f'<text x="{x:.0f}" y="{y + 26}" fill="{C["muted"]}" font-size="14">{label}</text>')
    b += f'<line x1="24" y1="112" x2="{IW - 24}" y2="112" stroke="{C["line"]}"/>'
    stats_svg = card(W, PH, "GitHub stats", b, ("LAST 12 MONTHS", C["frost"]), "GitHub stats")

    # -- languages (by bytes across owned, non-fork repos)
    sizes = {}
    for r in repos:
        for e in r["languages"]["edges"]:
            sizes[e["node"]["name"]] = sizes.get(e["node"]["name"], 0) + e["size"]
    top = sorted(sizes.items(), key=lambda kv: -kv[1])[:6]
    tot = sum(v for _, v in top) or 1
    b, x = "", 24.0
    bar_w = IW - 48
    b += f'<clipPath id="bar"><rect x="24" y="30" width="{bar_w}" height="12" rx="6"/></clipPath><g clip-path="url(#bar)">'
    for i, (name, v) in enumerate(top):
        w = bar_w * v / tot
        b += f'<rect x="{x:.1f}" y="30" width="{w + .5:.1f}" height="12" fill="{LANG_COLORS[i]}"/>'
        x += w
    b += "</g>"
    for i, (name, v) in enumerate(top):
        x, y = 24 + (i % 2) * (IW / 2), 86 + (i // 2) * 44
        b += (f'<circle cx="{x + 6:.0f}" cy="{y - 6}" r="6" fill="{LANG_COLORS[i]}"/>'
              f'<text x="{x + 22:.0f}" y="{y}" fill="{C["text"]}" font-size="17" font-weight="600">{esc(name)}</text>'
              f'<text x="{x + IW / 2 - 48:.0f}" y="{y}" text-anchor="end" fill="{C["muted"]}" font-size="15">{100 * v / tot:.1f}%</text>')
    langs_svg = card(W, PH, "Languages", b, None, "Top languages")

    # -- streak (full width)
    days = [d for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    cur, (cs, ce), longest, (ls, le) = streaks(days)
    first = days[0]["date"] if days else None
    SW, SH = 1200, 240
    siw = SW - 2 * M
    cols = [(f"{total}", "Total contributions", f"{fmt_date(first)} – now", C["frost"]),
            (f"{cur}", "Current streak", f"{fmt_date(cs)} – {fmt_date(ce)}" if cur else "start one today", C["green"]),
            (f"{longest}", "Longest streak", f"{fmt_date(ls)} – {fmt_date(le)}" if longest else "—", C["purple"])]
    b = ""
    for i, (num, label, sub, col) in enumerate(cols):
        cx = siw / 6 * (2 * i + 1)
        b += (f'<text x="{cx:.0f}" y="76" text-anchor="middle" fill="{col}" font-size="48" font-weight="800">{num}</text>'
              f'<text x="{cx:.0f}" y="110" text-anchor="middle" fill="{C["text"]}" font-size="17" font-weight="600">{label}</text>'
              f'<text x="{cx:.0f}" y="136" text-anchor="middle" fill="{C["muted"]}" font-size="14">{sub}</text>')
        if i:
            b += f'<line x1="{siw / 3 * i:.0f}" y1="28" x2="{siw / 3 * i:.0f}" y2="146" stroke="{C["line"]}"/>'
    streak_svg = card(SW, SH, "Streak", b, None, "GitHub contribution streak")
    return dict(stats=stats_svg, langs=langs_svg, streak=streak_svg)


if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    if mode == "static":
        static(out)
    elif mode == "stats":
        data = json.load(open(os.environ["MOCK"])) if os.environ.get("MOCK") else fetch()
        for name, svg in stat_cards(data).items():
            open(os.path.join(out, f"{name}.svg"), "w").write(svg)
    else:
        raise SystemExit(__doc__)
