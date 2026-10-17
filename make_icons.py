#!/usr/bin/env python3
"""Generate app icons (one-time; output committed in icons/). Green background, white cart with an 'R'."""
from PIL import Image, ImageDraw, ImageFont
import pathlib
OUT = pathlib.Path(__file__).parent / "icons"; OUT.mkdir(exist_ok=True)
GREEN = (31, 111, 67, 255); WHITE = (255, 255, 255, 255); S = 1024
FONT = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

def art(scale):
    """Cart + R, drawn on a transparent 1024 canvas, content scaled around the center."""
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    c = S / 2
    def p(x, y): return (c + (x - c) * scale, c + (y - c) * scale)
    w = int(56 * scale)
    # handle
    d.line([p(150, 270), p(260, 270), p(330, 640)], fill=WHITE, width=w, joint="curve")
    # basket (trapezoid)
    basket = [p(280, 340), p(880, 340), p(800, 640), p(330, 640)]
    d.line(basket + [basket[0]], fill=WHITE, width=w, joint="curve")
    # base bar
    d.line([p(330, 640), p(350, 720), p(810, 720)], fill=WHITE, width=w, joint="curve")
    # wheels
    for x in (400, 760):
        cx, cy = p(x, 820); r = 52 * scale
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=WHITE)
    # R monogram in basket
    f = ImageFont.truetype(FONT, int(300 * scale))
    tx, ty = p(560, 492)
    d.text((tx, ty), "R", font=f, fill=WHITE, anchor="mm")
    return im

def any_icon():
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, S - 1, S - 1], radius=220, fill=GREEN)
    im.alpha_composite(art(0.92)); return im

def maskable_icon():
    im = Image.new("RGBA", (S, S), GREEN)   # full bleed; art kept inside the 80% safe circle
    im.alpha_composite(art(0.68)); return im

a, m = any_icon(), maskable_icon()
for size in (192, 512):
    a.resize((size, size), Image.LANCZOS).save(OUT / f"icon-{size}.png")
    m.resize((size, size), Image.LANCZOS).save(OUT / f"icon-maskable-{size}.png")
# apple-touch-icon: opaque, iOS rounds it itself
m2 = Image.new("RGBA", (S, S), GREEN); m2.alpha_composite(art(0.8))
m2.convert("RGB").resize((180, 180), Image.LANCZOS).save(OUT / "apple-touch-icon.png")
a.resize((32, 32), Image.LANCZOS).save(OUT / "favicon-32.png")
print("icons written:", sorted(x.name for x in OUT.iterdir()))
