"""Draw the project map (Figure 2.1) from its description.

    python scripts/make_project_map.py                       # figures/project-map.yml -> assets/project-map.svg
    python scripts/make_project_map.py --png preview.png     # also a PNG preview (needs rsvg-convert)

The description (figures/project-map.yml) lists the parts, what each contains and how they
connect; this script only does the drawing. Needs PyYAML.
"""
from __future__ import annotations

import argparse
import html
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

STYLE = """
      .col { font-size: 15px; font-weight: 700; fill: #8a929c; letter-spacing: .08em; }
      .repo { fill: #ffffff; stroke: #3f8f29; stroke-width: 2.5; }
      .data { fill: #eef4fb; stroke: #4a78a8; stroke-width: 2; }
      .published { fill: #f5effa; stroke: #7a5aa6; stroke-width: 2; }
      .planned { fill: #ffffff; stroke: #9aa2ab; stroke-width: 2; stroke-dasharray: 7 5; }
      .old { fill: #f3f4f5; stroke: #c3c8cd; stroke-width: 1.5; }
      .t { font-size: 17px; font-weight: 700; fill: #1d2228; }
      .s { font-size: 13.5px; fill: #4a525c; }
      .b { font-size: 13.5px; fill: #4a525c; font-weight: 700; }
      .m { font-size: 13px; fill: #4a525c; font-family: ui-monospace, 'DejaVu Sans Mono', monospace; }
      .flow { stroke: #5b6470; stroke-width: 2; fill: none; marker-end: url(#arrow); }
      .uses { stroke: #5b6470; stroke-width: 2; fill: none; stroke-dasharray: 6 5; marker-end: url(#arrow); }
      .l { font-size: 12.5px; fill: #5b6470; font-style: italic; }
      .tag { font-size: 11.5px; font-weight: 700; fill: #7a5aa6; }
      .rule { stroke: #dfe3e7; }
      a rect { transition: stroke-width .15s; }
      a:hover rect, a:focus rect { stroke-width: 4; }
      a:hover .t, a:focus .t { text-decoration: underline; }"""

LEGEND = [("repo", "repository"), ("data", "data on disk"), ("published", "published (DOI)"),
          ("planned", "planned / not on GitHub")]


def esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def advance(prev: str | None, kind: str) -> float:
    """Distance from the previous baseline to this one."""
    if prev is None:
        return 28 if kind == "title" else 26
    if prev == "rule":
        return 25  # below the separator line
    if prev == "title":
        return 20 if kind == "title" else 22
    return 19


def draw_node(node: dict) -> list[str]:
    x, y, w, h = node["box"]
    kind = node["kind"]
    out = [f'  <rect class="{kind}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{12 if h > 70 else 10}"/>']
    tx, cursor, prev = x + 16, y, None
    if node.get("tag"):
        out.append(f'  <text class="tag" x="{tx}" y="{y + 22}">{esc(node["tag"])}</text>')
        cursor, prev = y + 22, "tag"
    for item in node["items"]:
        (key, value), = item.items()
        if key == "space":
            cursor += value
            continue
        if key == "rule":
            cursor += 14
            out.append(f'  <line class="rule" x1="{tx}" y1="{cursor:g}" x2="{x + w - 16}" y2="{cursor:g}"/>')
            prev = "rule"
            continue
        cursor += advance(prev, key)
        text = str(value)
        if key == "title":
            cls = "t"
        elif key == "code":
            cls = "m"
        elif text.startswith("**") and text.endswith("**"):
            cls, text = "b", text[2:-2]
        else:
            cls = "s"
        out.append(f'  <text class="{cls}" x="{tx}" y="{cursor:g}">{esc(text)}</text>')
        prev = key
    return out


NORMAL = {"left": (-1, 0), "right": (1, 0), "top": (0, -1), "bottom": (0, 1)}


def anchor(nodes: dict, spec: list) -> tuple[float, float, str]:
    nid, side, t = spec
    x, y, w, h = nodes[nid]["box"]
    if side in ("left", "right"):
        return (x if side == "left" else x + w), y + t * h, side
    return x + t * w, (y if side == "top" else y + h), side


def draw_edge(nodes: dict, edge: dict) -> list[str]:
    x0, y0, s0 = anchor(nodes, edge["from"])
    x1, y1, s1 = anchor(nodes, edge["to"])
    n0, n1 = NORMAL[s0], NORMAL[s1]
    gap = 2  # stop just short of the box border so the arrowhead stays visible
    x1e, y1e = x1 + n1[0] * gap, y1 + n1[1] * gap
    x0s, y0s = (x0 + n0[0] * gap, y0 + n0[1] * gap) if edge.get("both") else (x0, y0)
    straight = (n0[1] == 0 and n1[1] == 0 and abs(y0 - y1) < 1) or (n0[0] == 0 and n1[0] == 0 and abs(x0 - x1) < 1)
    if straight:
        d = f"M{x0s:g},{y0s:g} L{x1e:g},{y1e:g}"
    else:
        k = 28.0 if s0 == s1 else 24.0  # same side (e.g. right to right): a short loop outside the boxes
        c0 = (x0s + n0[0] * k, y0s + n0[1] * k)
        c1 = (x1e + n1[0] * k, y1e + n1[1] * k)
        d = f"M{x0s:g},{y0s:g} C{c0[0]:g},{c0[1]:g} {c1[0]:g},{c1[1]:g} {x1e:g},{y1e:g}"
    start = ' marker-start="url(#arrow)"' if edge.get("both") else ""
    out = [f'  <path class="{edge.get("style", "flow")}" d="{d}"{start}/>']
    label = edge.get("label")
    if label:
        lines = label if isinstance(label, list) else [label]
        if edge.get("label_at"):
            lx, ly = edge["label_at"]
            out.append(f'  <text class="l" x="{lx:g}" y="{ly:g}">{esc(" ".join(lines))}</text>')
        elif n0[1] == 0 and n1[1] == 0:  # horizontal-ish: above the line at its left end
            lx, ly = (x0, y0) if x0 <= x1 else (x1, y1)
            out.append(f'  <text class="l" x="{lx + 4:g}" y="{ly - 9:g}">{esc(lines[0])}</text>')
            if len(lines) > 1:
                out.append(f'  <text class="l" x="{lx + 4:g}" y="{ly + 22:g}">{esc(lines[1])}</text>')
        else:  # vertical: beside the middle
            out.append(f'  <text class="l" x="{x0 + 8:g}" y="{(y0 + y1) / 2 + 4:g}">{esc(" ".join(lines))}</text>')
    return out


def draw(spec: dict) -> str:
    W, H = spec["canvas"]["width"], spec["canvas"]["height"]
    nodes = spec["nodes"]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
           "font-family=\"system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif\">",
           "  <title>How the DWARPH project fits together</title>",
           "  <style>a { cursor: pointer; }</style>",
           "  <!-- generated by scripts/make_project_map.py from figures/project-map.yml: edit those, not this -->",
           "  <defs>",
           '    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">',
           '      <path d="M0,0 L10,5 L0,10 z" fill="#5b6470"/>',
           "    </marker>",
           f"    <style>{STYLE}\n    </style>",
           "  </defs>",
           f'  <rect width="{W}" height="{H}" fill="#ffffff"/>']
    for col in spec["columns"]:
        out.append(f'  <text class="col" x="{col["x"]}" y="40">{esc(col["label"])}</text>')
    for node in nodes.values():
        body = draw_node(node)
        if node.get("link"):
            title = next((str(i["title"]) for i in node["items"] if "title" in i), node["link"])
            body = ([f'  <a href="{esc(node["link"])}" target="_blank" rel="noopener">',
                     f"  <title>{esc(title)}: {esc(node['link'])}</title>"] + body + ["  </a>"])
        out += body
    for edge in spec["edges"]:
        out += draw_edge(nodes, edge)
    lx, ly = spec["legend"]["at"]
    out.append(f'  <g transform="translate({lx},{ly})">')
    x = 0
    for kind, text in LEGEND:
        out.append(f'    <rect class="{kind}" x="{x}" y="0" width="26" height="18" rx="4"/>'
                   f'<text class="s" x="{x + 34}" y="14">{text}</text>')
        x += 34 + 8 * len(text) + 34
    for style, text in (("flow", "data or files flow"), ("uses", "used by / informs")):
        out.append(f'    <path class="{style}" d="M{x},9 L{x + 50},9"/><text class="s" x="{x + 58}" y="14">{text}</text>')
        x += 58 + 8 * len(text) + 40
    out += ["  </g>", "</svg>", ""]
    return "\n".join(out)


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--spec", type=Path, default=ROOT / "figures" / "project-map.yml")
    p.add_argument("--out", type=Path, default=ROOT / "assets" / "project-map.svg")
    p.add_argument("--png", type=Path, help="also render a PNG preview here")
    a = p.parse_args(argv)
    svg = draw(yaml.safe_load(a.spec.read_text()))
    a.out.write_text(svg)
    print(f"wrote {a.out}")
    if a.png:
        subprocess.run(["rsvg-convert", "-w", "1400", str(a.out), "-o", str(a.png)], check=True)
        print(f"wrote {a.png}")


if __name__ == "__main__":
    main()
