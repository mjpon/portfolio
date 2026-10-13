"""Builds the portfolio site: home page, project pages and the 404 page.

Run from anywhere:  python3 tools/build_site.py
It writes into ../site (next to this folder). Set SITE_DIR to write somewhere else.
"""
import html
import os
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
PROD = pathlib.Path(os.environ.get("SITE_DIR", HERE.parent / "site"))
PREV = pathlib.Path(os.environ["PREVIEW_DIR"]) if os.environ.get("PREVIEW_DIR") else None
CSS_FILE = PROD / "styles.css"

NAME = "Mitchell"
GITHUB = "https://github.com/mjpon"
EMAIL = "mitchellpon76@gmail.com"
LINKEDIN = "https://www.linkedin.com/in/ponm/"
REPO = "https://github.com/mjpon/car-maker-identifier"
FONT_URL = "https://fonts.googleapis.com/css2?family=Public+Sans:wght@300;400;600&display=swap"
LOGO = (
    '<svg class="logo" viewBox="0 0 36 36" aria-hidden="true" focusable="false">'
    '<rect class="tile" width="36" height="36" rx="3"/>'
    '<path class="glyph" d="M9 18h18M14 13.5v9M18 12v12M22 13.5v9"/></svg>'
)
ASSETS = ("favicon.svg", "favicon-32.png", "apple-touch-icon.png", "logo.svg", "motion.js",
          "vendor/anime.js", "vendor/anime-LICENSE.md")

DESIGN_RAIL = "SBB and ÖBB"

LINES = [
    dict(key="maps", name="Maps", shape="circle", note="Interactive maps built on public data."),
    dict(key="apps", name="Data apps", shape="square", note="Apps and pages that explore published numbers."),
    dict(key="tools", name="Tools", shape="diamond", note="Small web tools for Auxiliary members."),
]
LINE_BY_KEY = {l["key"]: l for l in LINES}

ORDER = [
    "derelict-vessel-map", "abandoned-vehicle-map", "card-theft-map",
    "car-maker-identifier",
    "ppe-inspection-report",
]
LINE_OF = {
    "derelict-vessel-map": "maps", "abandoned-vehicle-map": "maps", "card-theft-map": "maps",
    "car-maker-identifier": "apps",
    "ppe-inspection-report": "tools",
}

# Live versions of the projects. A project in this list gets an "Open the live version" button on its
# page. To unlink one, put a "#" in front of its line and run this script again.
LIVE = {
    "abandoned-vehicle-map": "https://vehicles.mitchell-pon.com",
    "ppe-inspection-report": "https://ppe.mitchell-pon.com",
    "car-maker-identifier": "https://cars.mitchell-pon.com",
    "derelict-vessel-map": "https://boats.mitchell-pon.com",
    "card-theft-map": "https://cards.mitchell-pon.com",
}

STATUS = "Alpha (preview)"

SPRITE = (
    '<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>'
    '<symbol id="shape-circle" viewBox="0 0 16 16"><circle cx="8" cy="8" r="5.5"/></symbol>'
    '<symbol id="shape-square" viewBox="0 0 16 16"><rect x="2.75" y="2.75" width="10.5" height="10.5" rx="1"/></symbol>'
    '<symbol id="shape-triangle" viewBox="0 0 16 16"><path d="M8 2.5 14 13H2z"/></symbol>'
    '<symbol id="shape-diamond" viewBox="0 0 16 16"><path d="M8 1.75 14.25 8 8 14.25 1.75 8z"/></symbol>'
    # Plain stand-in icons for the profile buttons: a branch for code, a person for LinkedIn.
    '<symbol id="icon-code" viewBox="0 0 24 24"><circle cx="6" cy="5.5" r="2.5"/><circle cx="6" cy="18.5" r="2.5"/>'
    '<circle cx="18" cy="8.5" r="2.5"/><path d="M6 8v8M18 11c0 3.5-3 5-8 5.5"/></symbol>'
    '<symbol id="icon-person" viewBox="0 0 24 24"><circle cx="12" cy="8" r="3.5"/>'
    '<path d="M5 20c0-3.9 3.1-6.5 7-6.5s7 2.6 7 6.5"/></symbol>'
    "</defs></svg>\n"
)


def e(s):
    return html.escape(s, quote=False)


def a(s):
    return html.escape(s, quote=True)


def ico(name):
    return (f'<svg class="ico" viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
            f'<use href="#icon-{name}"/></svg>')


def st(shape):
    return (f'<svg class="st" viewBox="0 0 16 16" aria-hidden="true" focusable="false">'
            f'<use href="#shape-{shape}"/></svg>')


P = [
    dict(
        slug="derelict-vessel-map", name="Derelict vessel map",
        blurb="A public map of abandoned boats in California, designed to read well on a phone.",
        lede="A public map of derelict and abandoned boats in California. It opens on the Bay Area and is designed to be read on a phone.",
        made="Python, Leaflet, GeoJSON", status=STATUS,
        extra=[("Data", "BoatUS MyCoast reports"), ("Audience", "The public"),
               ("Design reference", "U.S. National Design Studio, SBB and ÖBB")],
        sections=[
            ("What it does", [
                "The map plots reported derelict vessels and opens on the Bay Area, with a data view that lists the same reports. The first import covered ten California reports across the Bay Area and the Delta.",
                "The goal is all of California. The current data stops at the Bay Area and the Delta, with nothing yet for Southern California.",
            ]),
            ("How it’s built", [
                "A Python script turns a CSV export into GeoJSON and keeps only an allow-list of fields: report ID, date, place and a link back to the source. Reporter names, vessel names, registration numbers, photos and street addresses are dropped, because some of these boats are people’s homes.",
                "A list of report IDs can be excluded by hand, each with a comment explaining why. That is how test submissions and duplicates stay out. Tests check that private text never reaches the output. The site itself is static and built on Leaflet.",
            ]),
            ("Preview only", [
                "The source data does not have confirmed reuse terms yet, so this map is a preview. It may change or be taken down once those are settled with the data owner.",
            ]),
        ],
    ),
    dict(
        slug="abandoned-vehicle-map", name="Abandoned vehicle map",
        blurb="About 833,000 abandoned-vehicle reports from San Francisco, Oakland and San José, shown on a plain map.",
        lede="A map of 311 abandoned-vehicle reports in San Francisco, Oakland and San José, from 2008 to 2026. It shows reports, not cars.",
        made="Python, Leaflet, city open data", status=STATUS,
        extra=[("Data", "City 311 service requests"), ("Coverage", "San Francisco, Oakland, San José")],
        sections=[
            ("What it does", [
                "Zoomed out, the map shades squares of about a block by how many reports they have, outlines the neighborhoods and ranks them in a list beside it. Zoomed in, each dot is one spot of about 35 feet, and a larger dot means more reports there. A data page charts the same reports over time.",
                "It maps reports, not cars. No license plate, photo, address or free text is kept, and the About page explains what a square or a dot does and does not mean.",
            ]),
            ("How it’s built", [
                "Python scripts turn each city’s 311 export into one shared format and write the squares, neighborhood totals and dots as static files. The site is plain HTML, JavaScript and Leaflet, with no framework and no server.",
                "Each city records things differently, so the page does not compare cities by their totals. San José’s newer “Vehicle Concerns” category most likely continues the same work after March 2024, but the city does not say so, so it is a separate switch.",
            ]),
        ],
    ),
    dict(
        slug="card-theft-map", name="Collectible theft map",
        blurb="Trading-card and collectible thefts reported in California news, on a map with a dashboard and a police-record check.",
        lede="A map and dashboard of trading-card and collectible thefts reported in California news, from April 2025 to October 2026. It starts from news stories because no public police dataset records what was stolen.",
        made="Python, JavaScript, d3", status=STATUS,
        extra=[("Data", "News reports, cross-checked against Burbank PD and LAPD open data"),
               ("Coverage", "California, April 2025 to October 2026"),
               ("Design reference", DESIGN_RAIL)],
        sections=[
            ("What it does", [
                "Each reported theft is pinned at city or neighborhood level, never at an address. A board beside the map lists every incident with its sources. Charts show when and at what time of day it happened, how thieves got in, what they took and the losses reported. Filters cover the type of crime, whether Pokémon was named, and whether a police record matched.",
                "It began with Pokémon cards and widened to sports cards, other trading card games and collectible toys.",
            ]),
            ("How it’s built", [
                "The incidents are compiled by hand from news stories, one row each, with source links, dates marked as reported or inferred, and a note wherever sources disagree. A Python script turns that spreadsheet into one static page. The basemap is a simplified outline of California’s counties, so the page needs no map-tile service.",
                "Where a police release or LAPD open data matched an incident’s date and place, it is marked. Those records cannot say what was taken or what it was worth, so they confirm that the crime was reported, not the details.",
            ]),
            ("A floor, not a total", [
                "News favors large, filmed thefts, so this shows how thefts happen better than how many there are. Dollar figures are owner, police or media estimates, and private victims are not named. Counts over time reflect how much was reported as well as how much happened.",
            ]),
        ],
    ),
    dict(
        slug="car-maker-identifier", name="Car maker identifier",
        blurb="Where the engine, transmission and assembly of new US vehicles come from, charted by manufacturer and model year.",
        lede="A web page that shows where new US vehicles get their engine, transmission and final assembly. It reads the parts-content labels the government requires and lets you compare manufacturers, countries and model years.",
        made="Python, HTML, CSS, JavaScript", status=STATUS,
        extra=[("Data", "NHTSA parts-content reports, model years 2020 to 2026"),
               ("Source", ("github.com/mjpon/car-maker-identifier", REPO)),
               ("Design reference", DESIGN_RAIL)],
        sections=[
            ("What it does", [
                "Pick a model year, a manufacturer or a car line, and the page updates its headline numbers and charts: models by manufacturer, assembly country, where engines and transmissions come from, and how much of each vehicle’s parts content is from the US and Canada. A table lists every vehicle, can be sorted, and downloads as a CSV.",
            ]),
            ("How it’s built", [
                "The reports are published as PDFs, so a Python script reads them, cleans up manufacturer names and turns country codes into country names. Another script writes the result as one JSON file. The page is plain HTML, CSS and JavaScript that draws every chart in the browser, with no server and no framework.",
                "The first version was a Streamlit app, and it is still in the repo.",
            ]),
            ("Design", [
                "The interface uses a grid, hairline rules and timetable-style rows, with red as the signal color, and it works down to phone width.",
            ]),
        ],
    ),
    dict(
        slug="ppe-inspection-report", name="PPE inspection report",
        blurb="A digital version of a Coast Guard Auxiliary PPE inspection form, made to be filled out on a phone.",
        lede="A digital version of the personal protective equipment (PPE) inspection form used in the Coast Guard Auxiliary. It covers every field on the paper form and produces a report that can be saved.",
        made="HTML, CSS, JavaScript", status=STATUS,
        extra=[("Based on", "The paper PPE inspection report"), ("Audience", "Auxiliary members")],
        notice="Independent work by an Auxiliary member. This is not an official Coast Guard or Auxiliary product.",
        sections=[
            ("What it does", [
                "An inspector fills in the form on a phone or a computer. The form covers nine kinds of equipment, including life jackets, personal locator beacons, float coats and helmets. When it is complete, the app shows a full-screen preview of the report and lets the inspector save it.",
            ]),
            ("Why I built it", [
                "A quick first pass to show how a paper process can become a working form. The aim is to make inspection records easy to fill out and easy to find.",
            ]),
            ("How it’s built", [
                "A single static web page with no server or database behind it. Entries save in the browser, and nothing leaves the device.",
            ]),
            ("Where it stands", [
                "A rough first pass, not a finished product. It shows the idea.",
            ]),
        ],
    ),
]

P.sort(key=lambda p: ORDER.index(p["slug"]))
for p in P:
    p["line"] = LINE_OF[p["slug"]]


def link(path, preview):
    return path + "index.html" if preview else path


# ---------------------------------------------------------------------------
# Network map for the home page.
# Every line leaves one interchange (home) and runs to its projects, like a transit
# diagram. Lines only run at 0, 45 and 90 degrees. There are two drawings of the
# same network: a wide one, and a tall one for phones. site/motion.js animates them,
# and without it they are plain links.
# Each layout gives, per line, the corners of its path. The projects on that line are
# spaced evenly along the last straight stretch, with the last one at the very end.
# ---------------------------------------------------------------------------
NET_LAYOUTS = {
    "wide": dict(
        view=(1000, 280), hub=(52, 150), hub_size=(30, 66), font=16,
        lines={
            "apps": [(52, 132), (214, 132), (284, 62), (600, 62)],
            "maps": [(52, 150), (930, 150)],
            "tools": [(52, 168), (214, 168), (284, 238), (600, 238)],
        },
        first={"apps": 600, "maps": 380, "tools": 600},
        label={"apps": "above", "maps": "below", "tools": "below"},
    ),
    "tall": dict(
        view=(340, 420), hub=(52, 28), hub_size=(66, 30), font=16,
        lines={
            "tools": [(70, 28), (70, 56), (110, 96), (110, 112)],
            "apps": [(52, 28), (52, 140), (110, 198), (110, 214)],
            "maps": [(34, 28), (34, 394)],
        },
        first={"tools": 112, "apps": 214, "maps": 266},
        label={"apps": "right", "maps": "right", "tools": "right"},
    ),
}
NET_STOP = 26     # size of a station shape, in drawing units
NET_RADIUS = 14   # how round the corners of a line are


def rounded_path(pts, r=NET_RADIUS):
    """SVG path through the points, with each corner rounded off."""
    def toward(p, q, d):
        dx, dy = q[0] - p[0], q[1] - p[1]
        length = (dx * dx + dy * dy) ** 0.5
        d = min(d, length / 2)
        return (p[0] + dx / length * d, p[1] + dy / length * d)

    def f(n):
        return f"{n:.1f}".rstrip("0").rstrip(".")

    out = [f"M{f(pts[0][0])} {f(pts[0][1])}"]
    for i in range(1, len(pts) - 1):
        a_, b_ = toward(pts[i], pts[i - 1], r), toward(pts[i], pts[i + 1], r)
        out.append(f"L{f(a_[0])} {f(a_[1])}Q{f(pts[i][0])} {f(pts[i][1])} {f(b_[0])} {f(b_[1])}")
    out.append(f"L{f(pts[-1][0])} {f(pts[-1][1])}")
    return "".join(out)


def net_stops(pts, first, n):
    """Where n stations sit on the last stretch of a line, and the path up to each one."""
    (x0, y0), (x1, y1) = pts[-2], pts[-1]
    horizontal = y0 == y1
    end = x1 if horizontal else y1
    spots = []
    for i in range(n):
        v = first + (end - first) * i / (n - 1) if n > 1 else end
        spot = (v, y1) if horizontal else (x1, v)
        spots.append((spot, pts[:-1] + [spot]))
    return spots


def network_svg(kind, preview):
    L = NET_LAYOUTS[kind]
    w, h = L["view"]
    font = L["font"]
    lines, routes, stops = [], [], []
    for line in LINES:
        key = line["key"]
        pts = L["lines"][key]
        items = [p for p in P if p["line"] == key]
        lines.append(f'<path class="ln" data-line="{key}" d="{rounded_path(pts)}"/>')
        for i, (p, (spot, route)) in enumerate(zip(items, net_stops(pts, L["first"][key], len(items)))):
            x, y = spot
            routes.append(f'<path class="route" data-route="{p["slug"]}" d="{rounded_path(route)}"/>')
            side = L["label"][key]
            last = i == len(items) - 1 and len(items) > 1
            if side == "above":
                tx, ty, anchor = x, y - 26, "middle"
            elif side == "below":
                tx, ty, anchor = x, y + 26 + font * 0.75, "middle"
                if last:
                    tx, anchor = x + NET_STOP / 2, "end"
            else:
                tx, ty, anchor = x + NET_STOP, y + font * 0.36, "start"
            s = NET_STOP
            stops.append(
                f'<a class="stop" href="{link("work/" + p["slug"] + "/", preview)}" data-line="{key}" '
                f'data-slug="{p["slug"]}" aria-label="{a(p["name"])}, {a(line["name"])} line">'
                f'<circle class="hit" cx="{x:g}" cy="{y:g}" r="{s:g}"/>'
                f'<circle class="ring" cx="{x:g}" cy="{y:g}" r="{s * 0.82:g}"/>'
                f'<g class="mark" style="transform-origin:{x:g}px {y:g}px">'
                f'<use class="stn" href="#shape-{line["shape"]}" x="{x - s / 2:g}" y="{y - s / 2:g}" width="{s}" height="{s}"/></g>'
                f'<text class="lbl" x="{tx:g}" y="{ty:g}" text-anchor="{anchor}" aria-hidden="true">{e(p["name"])}</text>'
                "</a>"
            )
    hx, hy = L["hub"]
    hw, hh = L["hub_size"]
    hub = (f'<rect class="hub" x="{hx - hw / 2:g}" y="{hy - hh / 2:g}" width="{hw}" height="{hh}" '
           f'rx="{min(hw, hh) / 2:g}" style="transform-origin:{hx}px {hy}px"/>')
    return (
        f'<svg class="net-{kind}" viewBox="0 0 {w} {h}" role="group" aria-label="Projects by line">'
        f'<g class="routes" aria-hidden="true">{"".join(routes)}</g>'
        f'<g class="lns" aria-hidden="true">{"".join(lines)}</g>'
        f'<g aria-hidden="true">{hub}<rect class="train" x="-13" y="-6" width="26" height="12" rx="3"/></g>'
        f'<g class="stops">{"".join(stops)}</g>'
        "</svg>"
    )


def network_html(preview):
    return (
        '<figure class="net">\n'
        + network_svg("wide", preview) + "\n"
        + network_svg("tall", preview) + "\n"
        + "<figcaption>" + chips_html() + "</figcaption>\n"
        + "</figure>\n"
    )


# Marks the page as having scripts before it paints, so the network map can wait for
# site/motion.js to draw it instead of flashing in finished. Its hash is in site/_headers.
HEAD_JS = "<script>document.documentElement.classList.add('js')</script>\n"


def head(title, desc, css_href, assets="", extra=""):
    return (
        '<!doctype html>\n<html lang="en">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<meta name="color-scheme" content="light dark">\n'
        f"<title>{e(title)}</title>\n"
        f'<meta name="description" content="{a(desc)}">\n'
        f'<link rel="icon" href="{assets}favicon.svg" type="image/svg+xml">\n'
        f'<link rel="icon" href="{assets}favicon-32.png" sizes="32x32" type="image/png">\n'
        f'<link rel="apple-touch-icon" href="{assets}apple-touch-icon.png">\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        f'<link rel="stylesheet" href="{FONT_URL}">\n'
        f'<link rel="stylesheet" href="{css_href}">\n'
        + extra
        + "</head>\n<body>\n"
    )


def header(home, root=None):
    if root:
        mark, work, about, contact = root, root + "#work", root + "#about", root + "#contact"
    elif home:
        mark, work, about, contact = "#", "#work", "#about", "#contact"
    else:
        mark, work, about, contact = "../../", "../../#work", "../../#about", "../../#contact"
    current = "" if root else ' aria-current="true"'
    return (
        '<header class="top">\n'
        f'  <a class="mark" href="{mark}">{LOGO}{NAME}</a>\n'
        '  <nav class="nav" aria-label="Main">\n'
        f'    <a href="{work}"{current}>Work</a>\n'
        f'    <a href="{about}">About</a>\n'
        f'    <a href="{contact}">Contact</a>\n'
        "  </nav>\n</header>\n"
    )


def footer():
    return (
        '<footer class="foot">\n'
        f"  <p>© 2026 {NAME}. These are independent projects and concepts. None of them is a product of, or endorsed by, "
        "Roche, the U.S. Coast Guard, the Coast Guard Auxiliary, BoatUS, SBB, ÖBB or any agency named on these pages.</p>\n"
        "  <p>SBB, ÖBB, the U.S. National Design Studio and the Mini Metro UI case study are visual references only. "
        "No logos, marks or game artwork are used.</p>\n"
        "</footer>\n"
    )


SCROLLSPY = """<script>
(function () {
  var ids = ['work', 'about', 'contact'];
  var links = [].slice.call(document.querySelectorAll('.nav a[href^="#"]'));
  if (!links.length) return;
  function update() {
    var y = window.innerHeight * 0.35, cur = ids[0];
    ids.forEach(function (id) {
      var el = document.getElementById(id);
      if (el && el.getBoundingClientRect().top <= y) cur = id;
    });
    if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 2) cur = ids[ids.length - 1];
    links.forEach(function (l) {
      if (l.getAttribute('href') === '#' + cur) l.setAttribute('aria-current', 'true');
      else l.removeAttribute('aria-current');
    });
  }
  window.addEventListener('scroll', update, { passive: true });
  update();
})();
</script>
"""


def count_label(n):
    return f"{n} project" + ("" if n == 1 else "s")


def row_html(p, preview):
    href = link(f"work/{p['slug']}/", preview)
    shape = LINE_BY_KEY[p["line"]]["shape"]
    return (
        f'<li><a class="row" href="{href}">'
        f'<span class="stn">{st(shape)}</span>'
        f'<span class="name"><strong style="view-transition-name:p-{p["slug"]}">{e(p["name"])}</strong><span class="blurb">{e(p["blurb"])}</span></span>'
        f'<span class="made"><span class="sr-only">Made with: </span>{e(p["made"])}</span>'
        f'<span class="status"><span class="sr-only">Status: </span><span class="pill">{e(p["status"])}</span></span>'
        '<span class="chev" aria-hidden="true"></span></a></li>\n'
    )


def entities(text):
    # Writes every character as &#NN; so the address is not sitting in the page as plain text.
    # Browsers show and use it normally, and it needs no script, so the security policy is unaffected.
    return "".join(f"&#{ord(c)};" for c in text)


def facts_html(rows, plain=False):
    out = []
    for k, v in rows:
        if isinstance(v, tuple) and v[1].startswith("mailto:"):
            val = f'<a href="mailto:{entities(v[1][7:])}">{entities(v[0])}</a>'
        elif isinstance(v, tuple):
            val = f'<a href="{a(v[1])}" target="_blank" rel="noopener">{e(v[0])}</a>'
        else:
            val = e(v)
        out.append(f'<div class="frow"><dt>{e(k)}</dt><dd>{val}</dd></div>')
    cls = "facts plain" if plain else "facts"
    return f'<dl class="{cls}">\n' + "\n".join(out) + "\n</dl>\n"


def group_html(line, preview):
    items = [p for p in P if p["line"] == line["key"]]
    rows = "".join(row_html(p, preview) for p in items)
    return (
        f'<div class="group" id="line-{line["key"]}" data-line="{line["key"]}">\n'
        f'<h3 class="line-head"><span class="badge">{st(line["shape"])}{e(line["name"])}</span>'
        f'<span class="line-note">{e(line["note"])} {count_label(len(items))}.</span></h3>\n'
        f'<ul class="board">\n{rows}</ul>\n</div>\n'
    )


def chips_html():
    out = []
    for line in LINES:
        n = len([p for p in P if p["line"] == line["key"]])
        out.append(
            f'<a class="badge" data-line="{line["key"]}" href="#line-{line["key"]}">'
            f'{st(line["shape"])}{e(line["name"])}<span class="count">{n}</span></a>'
        )
    return '<nav class="lines" aria-label="Browse by type">' + "".join(out) + "</nav>\n"


def home_inner(preview):
    groups = "".join(group_html(l, preview) for l in LINES)
    board_head = (
        '<div class="board-head" aria-hidden="true"><span class="hr"></span><span class="name">Project</span>'
        '<span class="made">Made with</span><span class="status">Status</span><span class="hc"></span></div>\n'
    )
    about_facts = facts_html([
        ("Based in", "San Francisco Bay Area"),
        ("Education", "B.S. Computer Science, UC Santa Cruz (2017 to 2020)"),
        ("Outside work", "Long-distance running, dragon boat, hiking"),
    ])
    contact = facts_html([("Email", (EMAIL, "mailto:" + EMAIL)),
                          ("GitHub", ("github.com/mjpon", GITHUB)),
                          ("LinkedIn", ("linkedin.com/in/ponm", LINKEDIN))])
    return (
        '<a class="skip" href="#main">Skip to content</a>\n'
        + SPRITE
        + '<div class="wrap">\n'
        + header(True)
        + '<main id="main">\n'
        '<section class="hero" id="top">\n'
        '  <h1 class="display">Just a software engineer... who enjoys concepts and building things!</h1>\n'
        '  <p class="lede">I love Python and dashboards! On my own time I build maps, data apps and small tools for boating and public data.</p>\n'
        '  <div class="actions"><a class="btn" href="#work">See the work</a>'
        f'<a class="btn ghost" href="{GITHUB}" target="_blank" rel="noopener">{ico("code")}GitHub</a>'
        f'<a class="btn ghost" href="{LINKEDIN}" target="_blank" rel="noopener">{ico("person")}LinkedIn</a></div>\n'
        + network_html(preview)
        + "</section>\n"
        '<section class="sec" id="work">\n<h2>Work</h2>\n'
        + board_head
        + groups
        + "</section>\n"
        '<section class="sec" id="about">\n<h2>About</h2>\n'
        '<p class="wip"><span class="pill draft">Work in progress</span>'
        "<span>I’m still writing this section.</span></p>\n"
        + about_facts
        + "</section>\n"
        '<section class="sec" id="contact">\n<h2>Contact</h2>\n'
        + contact
        + "</section>\n</main>\n"
        + footer()
        + "</div>\n"
        + SCROLLSPY
        + '<script type="module" src="motion.js"></script>\n'
    )


def section_html(sec):
    heading, body = sec[0], sec[1]
    kind = sec[2] if len(sec) > 2 else "p"
    if kind == "rows":
        inner = facts_html(body, plain=True)
    else:
        inner = "".join(f"<p>{e(t)}</p>\n" for t in body)
    return f'<section class="prose">\n<h2>{e(heading)}</h2>\n{inner}</section>\n'


def pager_html(i, preview):
    prev_p = P[i - 1] if i > 0 else None
    next_p = P[i + 1] if i < len(P) - 1 else None
    cells = []
    if prev_p:
        cells.append(
            f'<a class="prev" href="{link("../" + prev_p["slug"] + "/", preview)}">'
            f'<span class="dir">Previous</span><span class="to">{e(prev_p["name"])}</span></a>'
        )
    else:
        cells.append("<span></span>")
    if next_p:
        cells.append(
            f'<a class="next" href="{link("../" + next_p["slug"] + "/", preview)}">'
            f'<span class="dir">Next</span><span class="to">{e(next_p["name"])}</span></a>'
        )
    return '<nav class="pager" aria-label="More work">\n' + "\n".join(cells) + "\n</nav>\n"


def detail_page(i, preview):
    p = P[i]
    line = LINE_BY_KEY[p["line"]]
    facts = [("Status", p["status"]), ("Made with", p["made"])] + p.get("extra", [])
    notice = f'<p class="notice">{e(p["notice"])}</p>\n' if p.get("notice") else ""
    live_url = LIVE.get(p["slug"])
    live = (
        f'<div class="actions live"><a class="btn" href="{a(live_url)}" target="_blank" rel="noopener">'
        "Open the live version</a></div>\n"
        if live_url else ""
    )
    return (
        head(f"{p['name']} | {NAME}", p["lede"], "../../styles.css", "../../")
        + '<a class="skip" href="#main">Skip to content</a>\n'
        + SPRITE
        + '<div class="wrap">\n'
        + header(False)
        + f'<main id="main" class="page" data-line="{line["key"]}">\n'
        '<a class="textlink back" href="../../#work">All work</a>\n'
        f'<p class="where"><a class="badge" href="../../#line-{line["key"]}">{st(line["shape"])}{e(line["name"])}</a></p>\n'
        f'<h1 class="display sm" style="view-transition-name:p-{p["slug"]}">{e(p["name"])}</h1>\n'
        f'<p class="lede">{e(p["lede"])}</p>\n'
        + live
        + facts_html(facts)
        + notice
        + "".join(section_html(s) for s in p["sections"])
        + pager_html(i, preview)
        + "</main>\n"
        + footer()
        + "</div>\n</body>\n</html>\n"
    )


def not_found_page():
    # Served for any address that does not exist. Without it, a mistyped address would show the home page.
    return (
        head(f"Page not found | {NAME}", "That address does not match a page on this site.", "/styles.css", "/")
        + '<a class="skip" href="#main">Skip to content</a>\n'
        + SPRITE
        + '<div class="wrap">\n'
        + header(False, root="/")
        + '<main id="main" class="page">\n'
        '<h1 class="display sm">Page not found</h1>\n'
        '<p class="lede">That address does not match a page on this site. The link may have a typo, or the page may have moved.</p>\n'
        '<div class="actions"><a class="btn" href="/#work">Back to the work</a></div>\n'
        "</main>\n"
        + footer()
        + "</div>\n</body>\n</html>\n"
    )


def home_page_prod():
    return (
        head(f"{NAME} | Software engineer",
             "Software engineer who enjoys concepts and building things. Maps, data apps and small tools for boating and public data.",
             "styles.css", extra=HEAD_JS)
        + home_inner(False)
        + "</body>\n</html>\n"
    )


def home_fragment_preview(css):
    return (
        "<title>Mitchell Portfolio</title>\n"
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        f'<link rel="stylesheet" href="{FONT_URL}">\n'
        f"<style>\n{css}\n</style>\n"
        + HEAD_JS
        + home_inner(True)
    )


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main():
    css = CSS_FILE.read_text(encoding="utf-8")
    write(PROD / "index.html", home_page_prod())
    write(PROD / "404.html", not_found_page())
    for i, p in enumerate(P):
        write(PROD / "work" / p["slug"] / "index.html", detail_page(i, False))
    if PREV is not None:  # only used to publish a preview of the site
        if PREV.exists():
            shutil.rmtree(PREV)
        PREV.mkdir(parents=True)
        shutil.copy(CSS_FILE, PREV / "styles.css")
        for asset in ASSETS:
            (PREV / asset).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(PROD / asset, PREV / asset)
        write(PREV / "index.html", home_fragment_preview(css))
        for i, p in enumerate(P):
            write(PREV / "work" / p["slug"] / "index.html", detail_page(i, True))
    print("site files:")
    for f in sorted(PROD.rglob("*")):
        if f.is_file():
            print(" ", f.relative_to(PROD), f.stat().st_size)


if __name__ == "__main__":
    main()
