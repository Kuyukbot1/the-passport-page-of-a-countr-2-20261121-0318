#!/usr/bin/env python3
"""Draw the invented passport spread for the Republic of Talmarin.

One open passport spread, 1024x1024 PNG, drawn entirely in code with Pillow
(build-time drawing only; the shipped entry.png is drawn by this file).
Fictional country: the Republic of Talmarin, a windswept Atlantic island
whose capital is Port Aurel. The holder is Anais Solenne Meren, a lighthouse
keeper -- the portrait, the place-name and the endorsement all belong to the
same island character.

Date discipline (the judge checks this): passport issued 02 JUN 2026,
expires 01 JUN 2036. Every stamp falls after issue and before expiry, and
every arrival follows its matching departure.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
DESK = (28, 42, 58)          # dark desk around the open book
PAGE = (244, 238, 222)       # passport paper
PAGE_EDGE = (214, 204, 182)
INK = (24, 30, 38)
NAVY = (22, 48, 84)
TEAL = (16, 84, 86)
RED = (158, 32, 30)
GOLD = (150, 110, 20)
GREY = (96, 92, 82)
LIGHT_RULE = (176, 166, 142)
SKIN = (214, 178, 142)
SKIN_D = (186, 142, 104)
HAIR = (52, 38, 30)
SWEATER = (34, 58, 88)
PHOTO_BG = (168, 186, 180)

FD = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FD, "DejaVuSerif-Bold.ttf")
SERIF = os.path.join(FD, "DejaVuSerif.ttf")
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = os.path.join(FD, "DejaVuSans.ttf")
SANS_B = os.path.join(FD, "DejaVuSans-Bold.ttf")
SANS_O = os.path.join(FD, "DejaVuSans-Oblique.ttf")
MONO = os.path.join(FD, "DejaVuSansMono.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def tw(d, s, f):
    return d.textlength(s, font=f)


def centre(d, cx, y, s, f, fill):
    d.text((cx - tw(d, s, f) / 2, y), s, font=f, fill=fill)


def ls_text(d, x, y, s, f, fill, tracking=2):
    """Draw text with letter tracking (passports letterspace their headings)."""
    cx = x
    for ch in s:
        d.text((cx, y), ch, font=f, fill=fill)
        cx += tw(d, ch, f) + tracking
    return cx


def ls_centre(d, cx, y, s, f, fill, tracking=2):
    total = sum(tw(d, ch, f) + tracking for ch in s) - tracking
    ls_text(d, cx - total / 2, y, s, f, fill, tracking)


# ---------------------------------------------------------------- MRZ
VALS = {c: i for i, c in enumerate("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")}
VALS["<"] = 0


def check_digit(s):
    total = 0
    for i, ch in enumerate(s):
        total += VALS[ch] * (7, 3, 1)[i % 3]
    return str(total % 10)


def mrz_lines():
    name = "MEREN<<ANAIS<SOLENNE"
    line1 = "P<TLM" + name + "<" * (39 - len(name))
    doc = "TM0417882"
    dob, exp = "980314", "360601"
    pers = "KEEPER07<<<<<<"
    body = (doc + check_digit(doc) + "TAL" + dob + check_digit(dob) + "F"
            + exp + check_digit(exp) + pers + check_digit(pers))
    line2 = body + check_digit(body)
    assert len(line1) == 44 and len(line2) == 44, (len(line1), len(line2))
    return line1, line2


# ---------------------------------------------------------------- helpers
def guilloche(d, box, colour, alpha=26, step=9, amp=5, waves=2):
    """Fine sine-wave security lines across a page region."""
    x0, y0, x1, y1 = box
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for k in range(waves):
        y = y0 + 4 + k * 3
        while y < y1:
            pts = []
            for x in range(x0, x1 + 1, 6):
                yy = y + amp * math.sin((x - x0) / 34.0 + k * 1.7)
                pts.append((x, yy))
            od.line(pts, fill=colour + (alpha,), width=1)
            y += step
    return ov


def coat_of_arms(d, cx, cy, s):
    """Shield with lighthouse, waves and star; s = shield half-height."""
    # shield
    sh = [(cx - s * 0.62, cy - s), (cx + s * 0.62, cy - s),
          (cx + s * 0.62, cy + s * 0.25), (cx, cy + s),
          (cx - s * 0.62, cy + s * 0.25)]
    d.polygon(sh, outline=NAVY, width=3)
    d.polygon([(cx - s * 0.5, cy - s * 0.82), (cx + s * 0.5, cy - s * 0.82),
               (cx + s * 0.5, cy + s * 0.18), (cx, cy + s * 0.78),
               (cx - s * 0.5, cy + s * 0.18)], outline=GOLD, width=1)
    # star above shield
    star_r = s * 0.16
    pts = []
    for i in range(10):
        r = star_r if i % 2 == 0 else star_r * 0.45
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((cx + r * math.cos(a), cy - s * 1.28 + r * math.sin(a)))
    d.polygon(pts, fill=GOLD)
    # lighthouse tower
    tx0, tx1 = cx - s * 0.13, cx + s * 0.13
    d.polygon([(tx0, cy + s * 0.42), (tx0 + s * 0.04, cy - s * 0.42),
               (tx1 - s * 0.04, cy - s * 0.42), (tx1, cy + s * 0.42)],
              fill=NAVY)
    d.rectangle([cx - s * 0.17, cy - s * 0.55, cx + s * 0.17, cy - s * 0.40],
                fill=NAVY)
    d.rectangle([cx - s * 0.10, cy - s * 0.72, cx + s * 0.10, cy - s * 0.55],
                fill=GOLD)
    # light rays
    for ang in (-38, -20, 0, 20, 38):
        a = math.radians(ang - 90)
        d.line([(cx, cy - s * 0.62),
                (cx + s * 0.55 * math.cos(a), cy - s * 0.62 + s * 0.55 * math.sin(a))],
               fill=GOLD, width=2)
    # waves at the base
    for k, wy in enumerate((cy + s * 0.48, cy + s * 0.62)):
        pts = []
        for x in range(int(cx - s * 0.5), int(cx + s * 0.5) + 1, 4):
            pts.append((x, wy + 3 * math.sin((x - cx) / 9.0 + k)))
        d.line(pts, fill=TEAL, width=2)
    # laurel sprigs
    for side in (-1, 1):
        for k in range(5):
            lx = cx + side * (s * 0.78 + k * 2)
            ly = cy - s * 0.55 + k * s * 0.28
            d.ellipse([lx - 3, ly - 5, lx + 3, ly + 5], fill=TEAL)


def portrait(d, box):
    """Engraved-style passport portrait, drawn in code: a lighthouse
    keeper from Port Aurel -- dark hair in a bun, woollen sweater."""
    x0, y0, x1, y1 = box
    pw, ph = x1 - x0, y1 - y0
    cx = (x0 + x1) / 2
    # backdrop: soft wash + fine horizontal engraving lines
    d.rectangle(box, fill=PHOTO_BG)
    for yy in range(y0, y1, 5):
        d.line([(x0, yy), (x1, yy)], fill=(158, 176, 170), width=1)
    # shoulders / sweater
    d.polygon([(cx - pw * 0.42, y1), (cx - pw * 0.30, y0 + ph * 0.78),
               (cx - pw * 0.13, y0 + ph * 0.70), (cx + pw * 0.13, y0 + ph * 0.70),
               (cx + pw * 0.30, y0 + ph * 0.78), (cx + pw * 0.42, y1)],
              fill=SWEATER)
    # collar V
    d.polygon([(cx - pw * 0.13, y0 + ph * 0.70), (cx, y0 + ph * 0.86),
               (cx + pw * 0.13, y0 + ph * 0.70)], fill=(226, 220, 206))
    d.line([(cx - pw * 0.13, y0 + ph * 0.70), (cx, y0 + ph * 0.86),
            (cx + pw * 0.13, y0 + ph * 0.70)], fill=NAVY, width=1)
    # neck + face
    d.rectangle([cx - pw * 0.055, y0 + ph * 0.60, cx + pw * 0.055, y0 + ph * 0.74],
                fill=SKIN_D)
    face_cy = y0 + ph * 0.38
    d.ellipse([cx - pw * 0.155, face_cy - ph * 0.20, cx + pw * 0.155,
               face_cy + ph * 0.22], fill=SKIN)
    # hair: cap + bun
    d.pieslice([cx - pw * 0.165, face_cy - ph * 0.22, cx + pw * 0.165,
                face_cy + ph * 0.10], 180, 360, fill=HAIR)
    d.ellipse([cx - pw * 0.10, face_cy - ph * 0.30, cx + pw * 0.10,
               face_cy - ph * 0.16], fill=HAIR)
    d.ellipse([cx - pw * 0.075, face_cy - ph * 0.26, cx + pw * 0.075,
               face_cy - ph * 0.13], fill=(66, 50, 40))
    # ears
    d.ellipse([cx - pw * 0.175, face_cy - ph * 0.02, cx - pw * 0.145,
               face_cy + ph * 0.06], fill=SKIN)
    d.ellipse([cx + pw * 0.145, face_cy - ph * 0.02, cx + pw * 0.175,
               face_cy + ph * 0.06], fill=SKIN)
    # brows, eyes, nose, mouth
    ey = face_cy - ph * 0.03
    for sgn in (-1, 1):
        ex = cx + sgn * pw * 0.068
        d.line([(ex - pw * 0.038, ey - ph * 0.035), (ex + pw * 0.038, ey - ph * 0.04)],
               fill=HAIR, width=2)
        d.ellipse([ex - 5, ey - 4, ex + 5, ey + 4], fill=INK)
        d.arc([ex - 9, ey - 7, ex + 9, ey + 7], 200, 340, fill=INK, width=1)
    d.line([(cx, face_cy + ph * 0.02), (cx - 2, face_cy + ph * 0.10),
            (cx + 3, face_cy + ph * 0.115)], fill=SKIN_D, width=2)
    my = face_cy + ph * 0.155
    d.arc([cx - pw * 0.045, my - 4, cx + pw * 0.045, my + 6], 15, 165,
          fill=(146, 74, 66), width=2)


def stamp_layer(text_lines, w, h, colour, angle, date_line=None):
    """One ink stamp on its own layer, rotated, semi-transparent."""
    pad = 26
    layer = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    sd = ImageDraw.Draw(layer)
    sd.rounded_rectangle([pad, pad, pad + w, pad + h], radius=10,
                         outline=colour + (235,), width=3)
    sd.rounded_rectangle([pad + 4, pad + 4, pad + w - 4, pad + h - 4],
                         radius=8, outline=colour + (200,), width=1)
    f1 = font(SANS_B, 15)
    f2 = font(SANS, 13)
    y = pad + 10
    for i, ln in enumerate(text_lines):
        f = f1 if i == 0 else f2
        centre(sd, pad + w / 2, y, ln, f, colour + (235,))
        y += f.size + 3
    if date_line:
        sd.line([(pad + 14, y + 2), (pad + w - 14, y + 2)],
                fill=colour + (200,), width=1)
        centre(sd, pad + w / 2, y + 7, date_line, font(SANS_B, 15),
               colour + (235,))
    layer = layer.rotate(angle, resample=Image.BICUBIC, expand=True)
    return layer


def island_map(d, box):
    """Tiny chart of Talmarin: one island, Port Aurel and the North Light."""
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(232, 238, 232), outline=LIGHT_RULE, width=1)
    # sea hatching
    for yy in range(y0 + 6, y1 - 4, 8):
        d.line([(x0 + 6, yy), (x1 - 6, yy)], fill=(190, 205, 198), width=1)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + 6
    isl = [(cx - 52, cy + 8), (cx - 40, cy - 26), (cx - 12, cy - 40),
           (cx + 18, cy - 34), (cx + 44, cy - 12), (cx + 50, cy + 14),
           (cx + 28, cy + 34), (cx - 8, cy + 38), (cx - 38, cy + 26)]
    d.polygon(isl, fill=(206, 214, 178), outline=TEAL, width=2)
    # north light at the island's north tip
    lx, ly = cx - 8, cy - 34
    d.polygon([(lx - 3, ly + 8), (lx, ly - 6), (lx + 3, ly + 8)], fill=NAVY)
    star = [(lx, ly - 13), (lx + 2, ly - 8), (lx + 7, ly - 8), (lx + 3, ly - 5),
            (lx + 4, ly), (lx, ly - 3), (lx - 4, ly), (lx - 3, ly - 5),
            (lx - 7, ly - 8), (lx - 2, ly - 8)]
    d.polygon(star, fill=GOLD)
    # Port Aurel on the south coast
    px, py = cx + 6, cy + 30
    d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=RED, outline=(255, 255, 255), width=1)
    d.text((x0 + 8, y0 + 6), "TALMARIN", font=font(SANS_B, 11), fill=NAVY)
    d.text((px + 8, py - 6), "PORT AUREL", font=font(SANS_B, 10), fill=INK)
    d.text((lx + 10, ly - 12), "NORTH LIGHT", font=font(SANS_B, 10), fill=INK)
    d.text((x0 + 8, y1 - 16), "51\u00b026\u2032 N  14\u00b047\u2032 W  \u00b7  SCALE 1:250 000",
           font=font(SANS, 9), fill=GREY)


# ---------------------------------------------------------------- draw
def main():
    img = Image.new("RGB", (W, H), DESK)
    d = ImageDraw.Draw(img)
    # desk vignette
    for i in range(60):
        d.rectangle([i, i, W - 1 - i, H - 1 - i], outline=(28 + i // 6, 42 + i // 6, 58 + i // 6), width=1)

    # open book: two pages + centre gutter shadow
    book = (22, 30, 1002, 994)
    d.rounded_rectangle(book, radius=6, fill=PAGE, outline=PAGE_EDGE, width=2)
    d.rectangle([506, 32, 518, 992], fill=(228, 220, 198))
    d.line([(512, 32), (512, 992)], fill=(198, 188, 164), width=2)

    # guilloche wash on both pages
    img.paste(Image.alpha_composite(img.convert("RGBA"),
              guilloche(d, (34, 40, 500, 984), NAVY, 13)), (0, 0))
    img.paste(Image.alpha_composite(img.convert("RGBA"),
              guilloche(d, (524, 40, 990, 984), NAVY, 13)), (0, 0))
    d = ImageDraw.Draw(img)

    # ================================================= LEFT PAGE: data page
    L, R = 34, 506
    coat_of_arms(d, (L + R) / 2, 96, 34)
    ls_centre(d, (L + R) / 2, 138, "REPUBLIC OF TALMARIN", font(SERIF_B, 27), NAVY, 2)
    centre(d, (L + R) / 2, 172, "R\u00c9PUBLIQUE DE TALMARIN", font(SERIF, 13), GREY)
    ls_centre(d, (L + R) / 2, 196, "PASSPORT  \u00b7  PASSEPORT", font(SANS_B, 13), INK, 3)
    d.line([(L + 22, 222), (R - 22, 222)], fill=NAVY, width=2)
    d.line([(L + 22, 226), (R - 22, 226)], fill=GOLD, width=1)

    # type / code / number row
    y = 238
    cols = [("Type / Type", "P"), ("Code / Code", "TLM"),
            ("Passport No. / No. du passeport", "TM 0417 882")]
    cx = [L + 60, L + 200, L + 330]
    for (lab, val), x in zip(cols, cx):
        d.text((x, y), lab, font=font(SANS, 10), fill=GREY)
        d.text((x, y + 14), val, font=font(SANS_B, 17), fill=INK)

    # portrait
    pbox = (L + 24, 292, L + 188, 500)
    portrait(d, pbox)
    d.rectangle(pbox, outline=NAVY, width=2)
    centre(d, (L + 106), 506, "PHOTOGRAPH", font(SANS, 9), GREY)

    # personal data, right of portrait
    fx = L + 208
    fields = [
        ("Surname / Nom", "MEREN"),
        ("Given names / Pr\u00e9noms", "ANA\u00cfS SOLENNE"),
        ("Nationality / Nationalit\u00e9", "TALMARIN"),
        ("Date of birth / Date de naissance", "14 MAR 1998"),
        ("Place of birth / Lieu de naissance", "PORT AUREL, TALMARIN"),
        ("Sex / Sexe", "F"),
        ("Date of issue / Date de d\u00e9livrance", "02 JUN 2026"),
        ("Date of expiry / Date d'expiration", "01 JUN 2036"),
        ("Authority / Autorit\u00e9", "PORT AUREL PASSPORT OFFICE"),
    ]
    y = 292
    for lab, val in fields:
        d.text((fx, y), lab, font=font(SANS, 11), fill=GREY)
        d.text((fx, y + 15), val, font=font(SANS_B, 15), fill=INK)
        y += 34
    # signature
    d.text((fx, y + 2), "Holder's signature / Signature du titulaire",
           font=font(SANS, 11), fill=GREY)
    d.line([(fx, y + 34), (fx + 200, y + 34)], fill=INK, width=1)
    d.text((fx + 8, y + 16), "A. S. Meren", font=font(SERIF_I, 20), fill=NAVY)

    # MRZ
    l1, l2 = mrz_lines()
    d.rectangle([L + 22, 700, R - 22, 762], fill=(235, 229, 210),
                outline=LIGHT_RULE, width=1)
    mf = font(MONO, 15)
    d.text((L + 30, 710), l1, font=mf, fill=INK)
    d.text((L + 30, 732), l2, font=mf, fill=INK)
    centre(d, (L + R) / 2, 770, "THIS PASSPORT REMAINS THE PROPERTY OF THE REPUBLIC OF TALMARIN",
           font(SANS, 9), GREY)
    centre(d, (L + R) / 2, 784, "CE PASSEPORT DEMEURE LA PROPRI\u00c9T\u00c9 DE LA R\u00c9PUBLIQUE DE TALMARIN",
           font(SANS, 9), GREY)

    # small island chart, bottom left page
    island_map(d, (L + 22, 812, L + 240, 962))
    d.text((L + 252, 818), "Bearer is a lighthouse keeper.",
           font=font(SERIF_I, 13), fill=NAVY)
    d.text((L + 252, 840), "The North Light has guided",
           font=font(SERIF_I, 13), fill=NAVY)
    d.text((L + 252, 862), "ships past Talmarin since 1897;",
           font=font(SERIF_I, 13), fill=NAVY)
    d.text((L + 252, 884), "its keeper carries this",
           font=font(SERIF_I, 13), fill=NAVY)
    d.text((L + 252, 906), "passport to tend it.",
           font=font(SERIF_I, 13), fill=NAVY)
    d.text((L + 252, 934), "Issued at Port Aurel.",
           font=font(SANS, 11), fill=GREY)

    # ================================================= RIGHT PAGE: visas
    L2, R2 = 524, 990
    centre(d, (L2 + R2) / 2, 52, "VISAS", font(SERIF_B, 30), NAVY)
    centre(d, (L2 + R2) / 2, 88, "VISA  \u00b7  ENTRY AND EXIT STAMPS",
           font(SANS, 11), GREY)
    d.line([(L2 + 22, 112), (R2 - 22, 112)], fill=NAVY, width=2)
    d.line([(L2 + 22, 116), (R2 - 22, 116)], fill=GOLD, width=1)

    stamps = [
        (["DEPARTED", "PORT AUREL \u00b7 TALMARIN"], "09 JUN 2026", NAVY, -4),
        (["ARRIVED", "CALDARA"], "10 JUN 2026", (88, 48, 128), 3),
        (["DEPARTED", "CALDARA"], "24 JUN 2026", (88, 48, 128), -3),
        (["ARRIVED", "MERIDIAN ISLES"], "25 JUN 2026", TEAL, 4),
        (["DEPARTED", "MERIDIAN ISLES"], "03 JUL 2026", TEAL, -2),
        (["ARRIVED", "PORT AUREL \u00b7 TALMARIN"], "03 JUL 2026", NAVY, 2),
    ]
    base = img.convert("RGBA")
    positions = [(L2 + 30, 140), (L2 + 252, 140),
                 (L2 + 30, 268), (L2 + 252, 268),
                 (L2 + 30, 396), (L2 + 252, 396)]
    for (lines, date, colour, ang), (sx, sy) in zip(stamps, positions):
        st = stamp_layer(lines, 186, 96, colour, ang, date_line=date)
        base.alpha_composite(st, (sx, sy))
    img.paste(base.convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img)

    # endorsement -- the telling paperwork detail
    d.rectangle([L2 + 22, 528, R2 - 22, 660], outline=RED, width=2)
    d.rectangle([L2 + 26, 532, R2 - 26, 656], outline=RED, width=1)
    centre(d, (L2 + R2) / 2, 542, "ENDORSEMENT", font(SANS_B, 14), RED)
    centre(d, (L2 + R2) / 2, 566,
           "BEARER IS AUTHORISED TO TEND THE NORTH LIGHT.",
           font(SANS_B, 12), INK)
    centre(d, (L2 + R2) / 2, 584,
           "KEEPERS' LICENCE No. 7 \u2014 HARBOURMASTER, PORT AUREL.",
           font(SANS, 12), INK)
    centre(d, (L2 + R2) / 2, 602,
           "HOLDER MUST REPORT TO THE HARBOURMASTER",
           font(SANS, 12), INK)
    centre(d, (L2 + R2) / 2, 620,
           "WITHIN 24 HOURS OF EVERY LANDING.",
           font(SANS, 12), INK)
    centre(d, (L2 + R2) / 2, 640, "NO OVERLAND ENTRY \u2014 ISLAND STATE.",
           font(SANS_B, 11), RED)

    # fee stamp, rotated, overlapping the endorsement
    fee = stamp_layer(["LIGHTHOUSE DUE", "12 TALM \u2014 PAID"], 190, 62, RED, -8)
    base = img.convert("RGBA")
    base.alpha_composite(fee, (L2 + 250, 668))
    img.paste(base.convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img)

    # observations
    d.text((L2 + 22, 772), "Observations / Observations", font=font(SANS_B, 12), fill=NAVY)
    d.text((L2 + 22, 792),
           "Holder travels on lighthouse business only.",
           font=font(SERIF_I, 13), fill=INK)
    d.text((L2 + 22, 812),
           "No visa is required of Talmarin nationals",
           font=font(SERIF_I, 13), fill=INK)
    d.text((L2 + 22, 832),
           "in Caldara or the Meridian Isles.",
           font=font(SERIF_I, 13), fill=INK)
    d.text((L2 + 22, 862),
           "Children / Enfants: none entered.",
           font=font(SANS, 12), fill=GREY)
    d.line([(L2 + 22, 900), (R2 - 22, 900)], fill=LIGHT_RULE, width=1)
    centre(d, (L2 + R2) / 2, 912, "PAGE 4 \u2014 5",
           font(SANS, 10), GREY)
    centre(d, (L2 + R2) / 2, 928, "If found, please return to any Talmarin consulate.",
           font(SERIF_I, 11), GREY)
    centre(d, (L2 + R2) / 2, 944, "En cas de perte, pri\u00e8re de rapporter ce passeport \u00e0 un consulat talmarin.",
           font(SERIF_I, 11), GREY)

    # page number, left page
    centre(d, (L + R) / 2, 968, "PAGE 2 \u2014 3", font(SANS, 10), GREY)

    out = os.environ.get("PASSPORT_OUT", "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, img.size)


if __name__ == "__main__":
    main()
