"""Draws the Forall Labs mark: ∀ followed by an L whose stem runs parallel to
the ∀'s right leg, then turns flat along the baseline. Geometry lives here so every copy
(favicon, logo file, the inline symbol in base.html) comes from one place.

    python3 tools/logo.py           # rewrites site/static/favicon.svg and logo.svg
    python3 tools/logo.py --symbol  # prints the <symbol> to paste into base.html
"""

import sys
from pathlib import Path

STROKE = 10.0
TOP, BASE = 14.0, 86.0
LEFT, RIGHT, APEX = 8.0, 52.0, 30.0   # ∀: top-left x, top-right x, apex x
BAR_Y = 47.0
GAP = 21.0      # horizontal offset of the L's stem from the ∀'s right leg

VIEWBOX = "2.77 14 75.46 72"   # tight around the ink, so it sits flush with type
INK, WHITE = "#141413", "#ffffff"
STATIC = Path(__file__).resolve().parent.parent / "site" / "static"


# Horizontal half-width of a slanted stroke, so edges (not centrelines) line up.
HALF_W = STROKE / 2 * ((RIGHT - APEX) ** 2 + (BASE - TOP) ** 2) ** 0.5 / (BASE - TOP)


def right_leg_x(y):
    return RIGHT - (RIGHT - APEX) * (y - TOP) / (BASE - TOP)


def path_data():
    # The ∀'s legs meet at the apex on the baseline; every stroke starts a
    # little above the top so the clip, not the stroke end, makes flat tops.
    t = TOP - 2
    bar_left = 2 * APEX - right_leg_x(BAR_Y)
    forall = (f"M{2 * APEX - right_leg_x(t):.2f} {t:g}L{APEX:g} {BASE:g}L{right_leg_x(t):.2f} {t:g}"
              f"M{bar_left:.2f} {BAR_Y:g}L{right_leg_x(BAR_Y):.2f} {BAR_Y:g}")
    # The L: a straight stem parallel to the right leg, down until its outer
    # edge meets the baseline, then a straight foot that stops directly under
    # the stem's top-right corner.
    foot_y = BASE - STROKE / 2
    ell = (f"M{right_leg_x(t) + GAP:.2f} {t:g}L{right_leg_x(foot_y) + GAP:.2f} {foot_y:g}"
           f"L{right_leg_x(TOP) + GAP + HALF_W:.2f} {foot_y:g}")
    return forall, ell


def strokes(color, clip_id):
    forall, ell = path_data()
    return (f'<clipPath id="{clip_id}"><rect x="0" y="{TOP:g}" width="100" height="{BASE - TOP:g}"/></clipPath>'
            f'<g clip-path="url(#{clip_id})" fill="none" stroke="{color}" stroke-width="{STROKE:g}" stroke-miterlimit="10" stroke-linejoin="miter">'
            f'<path d="{forall}"/><path d="{ell}"/></g>')


def svg(color, tile=None):
    if tile:  # rounded square with breathing room around the mark
        box = "-15.5 -6 112 112"
        back = f'<rect x="-15.5" y="-6" width="112" height="112" rx="24" fill="{tile}"/>'
    else:
        box, back = VIEWBOX, ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{box}">'
            f'{back}{strokes(color, "fl-clip")}</svg>\n')


def symbol():
    return f'<symbol id="fl-mark" viewBox="{VIEWBOX}">{strokes("currentColor", "fl-mark-clip")}</symbol>'


if __name__ == "__main__":
    if "--symbol" in sys.argv:
        print(symbol())
    else:
        (STATIC / "favicon.svg").write_text(svg(WHITE, tile=INK))
        (STATIC / "logo.svg").write_text(svg(INK))
        print("wrote favicon.svg, logo.svg")
