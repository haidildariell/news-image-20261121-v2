#!/usr/bin/env python3
"""Render the make.fun news-image-20261121 v2 entry: one newspaper front page
summing up Saturday 21 November 2026. Pillow only, no network, deterministic.
Run: python3 build_image.py  -> writes entry.png next to this file.

v2 vs v1: 33 stories (was 14), 7 regions (was 5). Five v1 stories were
re-checked and DROPPED as Friday-20-Nov news (NSE 5th-largest, Indonesia
fire losses $30bn, Rohingya resettlement, Kuno cheetah cubs, Nepal PM visit)
-- they now live only in the DATE CHECK box. See SOURCES.md.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- palette ---
PAPER = (247, 242, 231)
INK = (26, 26, 26)
NAVY = (22, 40, 63)
NAVY2 = (30, 52, 80)
GOLD = (201, 162, 39)
RED = (176, 42, 33)
MUTED = (90, 83, 72)
RULE = (120, 110, 95)
WHITE = (255, 255, 255)
SKY = (18, 32, 58)

# ------------------------------------------------------------------ fonts ---
F = "/usr/share/fonts/truetype/liberation/"


def font(path, size):
    return ImageFont.truetype(path, size)


SERIF_B = lambda s: font(F + "LiberationSerif-Bold.ttf", s)
SERIF = lambda s: font(F + "LiberationSerif-Regular.ttf", s)
SERIF_I = lambda s: font(F + "LiberationSerif-Italic.ttf", s)
SANS_B = lambda s: font(F + "LiberationSans-Bold.ttf", s)
SANS = lambda s: font(F + "LiberationSans-Regular.ttf", s)

W, H = 1024, 1024
M = 20                      # page margin
CW = W - 2 * M              # content width = 984

# ---------------------------------------------------------------- helpers ---
def wrap(d, text, fnt, max_w):
    """Greedy word wrap; returns list of lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text(d, xy, s, fnt, fill=INK, anchor="la"):
    d.text(xy, s, font=fnt, fill=fill, anchor=anchor)


def centre(d, cx, y, s, fnt, fill=INK):
    d.text((cx, y), s, font=fnt, fill=fill, anchor="ma")


def rrect(d, box, rad, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=rad, fill=fill, outline=outline, width=width)


def pill(d, box, fill, outline=None):
    rrect(d, box, 9, fill=fill, outline=outline, width=1)


def tag(d, x, y, s, fnt, fg, bg, pad=5):
    w = d.textlength(s, font=fnt) + 2 * pad
    h = fnt.size + 2 * pad - 2
    pill(d, [x, y, x + w, y + h], bg)
    d.text((x + pad, y + pad - 1), s, font=fnt, fill=fg)
    return w


def star(d, cx, cy, r, fill):
    """8-point burst star."""
    pts = []
    for i in range(16):
        ang = i * math.pi / 8
        rr = r if i % 2 == 0 else r * 0.38
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=fill)


def parabola(d, x0, y0, x1, y1, apex_y, fill, width=3, steps=24):
    """Arc from (x0,y0) up to apex then down to (x1,y1)."""
    pts = []
    for i in range(steps + 1):
        t = i / steps
        x = x0 + (x1 - x0) * t
        y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * apex_y + t ** 2 * y1
        pts.append((x, y))
    d.line(pts, fill=fill, width=width, joint="curve")


# ------------------------------------------------------------------ data ----
LEADS = [
    dict(n=1, place="RIYADH, SAUDI ARABIA", topic="CONFLICT",
         head="Three Houthi missiles intercepted over Riyadh",
         body=("Coalition forces destroyed three ballistic missiles fired "
               "towards Riyadh early Saturday."),
         src="Reuters, AFP", tag="SATURDAY 02:40 \u00b7 3 INTERCEPTED"),
    dict(n=2, place="MERCURY", topic="SPACE",
         head="BepiColombo slips into orbit at Mercury",
         body=("The ESA/JAXA probe fires its thrusters at 19:24 CET, ending "
               "an 8-year, 6-billion-mile trip."),
         src="ESA, NPR", tag="19:24 CET \u00b7 6BN MILES"),
    dict(n=3, place="ANTALYA, T\u00dcRKIYE", topic="CLIMATE",
         head="COP31 talks spill into Saturday with no deal",
         body=("A third draft is due Saturday morning after the text dropped "
               "fossil fuels and the $120bn target."),
         src="AP, Reuters", tag="COP31 \u00b7 NO DEAL YET"),
]

MIDS = [
    dict(n=4, place="KYIV, UKRAINE", topic="WAR",
         head="Kyiv bridges hit in war's biggest air attack",
         body=("110+ missiles, 400+ drones in one night; 9 killed, 28 injured."),
         src="BBC, Kyiv Independent", tag="9 KILLED \u00b7 28 INJURED"),
    dict(n=5, place="KRYVYI RIH, UKRAINE", topic="WAR",
         head="Kryvyi Rih strike kills 2, injures 42",
         body=("Ballistic strike kills a boy, 7, and a paramedic, 20."),
         src="Kyiv Post, Reuters", tag="2 DEAD \u00b7 42 INJURED"),
    dict(n=6, place="PERTH, AUSTRALIA", topic="CRICKET",
         head="19 wickets fall on Ashes Day 1 in Perth",
         body=("Starc 7-58 bowls England out for 172; Australia 123/9 at stumps."),
         src="Cricbuzz, ANI", tag="19 WICKETS \u00b7 DAY 1"),
    dict(n=7, place="GAZA", topic="CONFLICT",
         head="Four killed in Gaza as attacks go on",
         body=("At least four killed as attacks continue despite the ceasefire."),
         src="Al Jazeera", tag="4 KILLED SATURDAY"),
    dict(n=8, place="WELLINGTON, NEW ZEALAND", topic="CRICKET",
         head="Rahul century puts India on top in Wellington",
         body=("Rahul's century on Day 3 \u2014 a first for an Indian opener in SENA."),
         src="Particle, BCCI", tag="DAY 3 \u00b7 CENTURY"),
    dict(n=9, place="TURIN, ITALY", topic="TENNIS",
         head="Top four seeds reach Turin semi-finals",
         body=("Alcaraz v Shelton in the afternoon, Zverev v Medvedev at night."),
         src="ATP, Tennis Majors", tag="SEMI-FINALS TODAY"),
    dict(n=10, place="LAS VEGAS, USA", topic="MOTOR RACING",
         head="Las Vegas Grand Prix under the lights tonight",
         body=("Norris on pole for tonight's race on the Strip."),
         src="AP", tag="RACE 20:00 PST"),
    dict(n=11, place="WARSAW, POLAND", topic="DEFENCE",
         head="Rutte in Warsaw after Poland missile scare",
         body=("Rutte in Warsaw as Poland seeks more NATO forces."),
         src="Reuters, AP", tag="RUTTE IN WARSAW"),
    dict(n=12, place="CENTRAL PERU", topic="QUAKE",
         head="M6.7 quake off Peru; no tsunami threat",
         body=("M6.7 undersea quake off central Peru; no tsunami threat."),
         src="Australian BOM", tag="M6.7 \u00b7 NO TSUNAMI"),
    dict(n=13, place="VANDENBERG, USA", topic="SPACE",
         head="SpaceX launches classified USSF-317",
         body=("Falcon 9 lifts classified USSF-317 satellites into orbit."),
         src="Spaceflight Now", tag="04:20 UTC LAUNCH"),
]

# one-liners 14-33 (two columns in the ALSO block)
ONELINERS = [
    dict(n=14, place="ODISHA",
         head="Akvan's remnants bring heavy rain to south Bengal through Saturday morning.",
         src="IMD"),
    dict(n=15, place="LONDON",
         head="Seven Premier League games today: Man City v Fulham opens the day.",
         src="BBC"),
    dict(n=16, place="EUROPE",
         head="Saturday football: Real Madrid v Celta, PSG at Nice, five Bundesliga ties.",
         src="beIN SPORTS"),
    dict(n=17, place="RUGBY",
         head="Nations Championship R6: England v All Blacks tops six Saturday tests.",
         src="Planet Rugby"),
    dict(n=18, place="CLEVELAND",
         head="NBA Cup: Harden drops 56 as the Cavaliers beat Indiana 128-119.",
         src="ESPN"),
    dict(n=19, place="ATLANTA",
         head="NBA Cup: Hawks beat Hornets 111-97; Daniels two boards short of a triple-double.",
         src="AP"),
    dict(n=20, place="TURIN",
         head="ATP doubles semis: Arevalo/Pavic, Krawietz/Puetz in action.",
         src="ATP"),
    dict(n=21, place="PAS-DE-CALAIS",
         head="Floods force 450+ evacuations as rivers stay high after heavy rain.",
         src="Pollar"),
    dict(n=22, place="THE HAGUE",
         head="Dutch police foil planned attacks on Revolut customers after a data leak.",
         src="Pollar"),
    dict(n=23, place="SYDNEY",
         head="Auction clearance rates fall below 60% in Sydney and Melbourne.",
         src="AFR / CoreLogic"),
    dict(n=24, place="SYDNEY",
         head="Jay Chou brings his Carnival II tour to ENGIE Stadium tonight.",
         src="Noise11"),
    dict(n=25, place="MELBOURNE",
         head="AFLW preliminary finals: North Melbourne v Sydney, Melbourne v Carlton.",
         src="AFL"),
    dict(n=26, place="PERTH",
         head="AFP seizes 660kg of cocaine in a global ring bust spanning two continents.",
         src="The West"),
    dict(n=27, place="KYIV",
         head="Three Dnipro bridges hit: Podilsko-Voskresenskyi, Darnytskyi and Pivdennyi.",
         src="Klitschko"),
    dict(n=28, place="RIYADH",
         head="Third straight night of alerts in the capital as defences stay on watch.",
         src="WireMinute"),
    dict(n=29, place="MERCURY",
         head="Sixteen more burns to come; the two orbiters split on 9-10 December.",
         src="NPR / ESA"),
    dict(n=30, place="ANTALYA",
         head="Panama vows to block any final text that ignores its eight demands.",
         src="AP"),
    dict(n=31, place="PERTH",
         head="Record Ashes crowd of 51,531 packs Perth Stadium for Day 1.",
         src="Sport Nation"),
    dict(n=32, place="LAS VEGAS",
         head="Hamilton starts last after a qualifying nightmare in his Ferrari.",
         src="AP"),
    dict(n=33, place="ABUJA",
         head="Obi vows to end kidnappings and corruption as Nigeria's insecurity deepens.",
         src="Punch"),
]

STATS = [
    ("3", "Houthi missiles over Riyadh"),
    ("9 killed", "in Kyiv bridge strikes"),
    ("6bn miles", "BepiColombo's Mercury trip"),
    ("19", "wickets on Ashes Day 1"),
    ("51,531", "record Perth Ashes crowd"),
    ("M6.7", "Peru quake, no tsunami"),
]

# region counts from the final story list (33 stories, all 7 regions)
# strip label for Asia-Pacific is shortened so it fits its narrow cell
REGIONS = [("EUROPE", 13, (42, 78, 128)), ("AMERICAS", 6, (176, 42, 33)),
           ("ASIA-PAC", 1, (46, 130, 96)), ("MIDEAST", 3, (176, 120, 40)),
           ("AFRICA", 1, (140, 110, 60)), ("OCEANIA", 7, (30, 120, 130)),
           ("WORLD-SPACE", 2, (90, 90, 110))]

HOWWE = ("HOW WE DATE \u2014 A story counts as Saturday's if it happened, or was "
         "first reported, on 21 November 2026 in at least one time zone. "
         "Friday-evening strikes (Kyiv, Kryvyi Rih) appear only with their "
         "Saturday casualty updates; Friday's big stories sit in DATE CHECK below.")

DATECHECK = ("First reported Friday 20 Nov (or earlier), so NOT Saturday's news: "
             "Russian missiles land in Poland \u2014 Tusk: \u201cintentional "
             "provocation\u201d \u00b7 Bitcoin below $60,000, first time since July "
             "\u00b7 Trump-Xi: humans must control military AI (Bessent) \u00b7 US "
             "tightens H200 chip curbs on China \u00b7 Trump pardons Pete Rose "
             "posthumously \u00b7 EU adopts \u20ac1bn military aid for Ukraine \u00b7 "
             "NSE becomes world's 5th-largest listed exchange \u00b7 Indonesia fire "
             "losses \u2018could reach $30bn\u2019 \u00b7 Malaysia to resettle 10,000 "
             "Rohingya in T\u00fcrkiye \u00b7 Four cheetah cubs born at Kuno \u00b7 "
             "Nepal PM's India visit announced \u00b7 WFP cuts 2027 food-aid target "
             "to 91m people \u00b7 UK\u2013EU reset deal signed in Brussels \u00b7 "
             "Rwanda\u2013DRC peace deal signed in Washington \u00b7 US strikes drug "
             "boats in the Caribbean and Pacific (Mon/Thu).")

# ------------------------------------------------------------- banner art ---
def banner_riyadh(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    for sx, sy, r in [(x + 30, y + 18, 2), (x + 90, y + 10, 1), (x + 150, y + 22, 2),
                      (x + 210, y + 12, 1), (x + 260, y + 20, 2), (x + 300, y + 9, 1),
                      (x + 60, y + 34, 1), (x + 240, y + 36, 1)]:
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=WHITE)
    d.ellipse([x + w - 42, y + 8, x + w - 18, y + 32], fill=(240, 230, 190))
    base = y + h
    # buildings scaled to fit a 72px banner (was drawn for 84px in v1)
    for bx, bw, bh in [(0, 34, 39), (38, 26, 53), (68, 30, 34), (102, 22, 60),
                       (128, 34, 45), (166, 26, 67), (196, 30, 38), (230, 26, 51),
                       (260, 30, 41), (294, 26, 50)]:
        d.rectangle([x + bx, base - bh, x + bx + bw, base], fill=(16, 26, 48))
        for wy in range(base - bh + 8, base - 6, 12):
            for wx in range(x + bx + 5, x + bx + bw - 4, 9):
                d.rectangle([wx, wy, wx + 3, wy + 4], fill=(255, 214, 120))
    # tall tower, capped inside the banner
    d.polygon([(x + 150, y + 12), (x + 158, y + 12), (x + 162, base - 40),
               (x + 146, base - 40)], fill=(60, 80, 118))
    d.polygon([(x + 150, y + 12), (x + 158, y + 12), (x + 154, y + 4)],
              fill=(90, 110, 148))
    d.rectangle([x + 150, y + 18, x + 158, y + 24], fill=(255, 214, 120))
    # 3 missile trails arcing up to intercept bursts (parabolas, stay in-banner)
    for sx0, bx0, apex in [(x + 26, x + 92, y + 30), (x + 128, x + 196, y + 18),
                           (x + 232, x + 292, y + 26)]:
        parabola(d, sx0, base - 8, bx0, apex + 12, apex - 6, GOLD, 3)
        star(d, bx0, apex + 12, 10, (255, 196, 66))
        star(d, bx0, apex + 12, 5, (255, 240, 180))
        d.ellipse([sx0 - 2, base - 12, sx0 + 2, base - 8], fill=(255, 160, 60))
    d.rectangle([x, base - 3, x + w, base], fill=(10, 18, 34))


def banner_mercury(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(12, 14, 30))
    for sx, sy, r in [(x + 18, y + 14, 2), (x + 60, y + 30, 1), (x + 110, y + 10, 2),
                      (x + 250, y + 16, 1), (x + 290, y + 34, 2), (x + 200, y + 8, 1),
                      (x + 160, y + 40, 1), (x + 40, y + 55, 1), (x + 130, y + 60, 1)]:
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=WHITE)
    d.arc([x + 20, y + 44, x + w - 20, y + h + 24], 180, 360,
          fill=(120, 130, 160), width=2)
    cx, cy, r = x + 92, y + h // 2 + 4, 32
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(150, 148, 140))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(110, 108, 100), width=2)
    for crx, cry, cr in [(cx - 14, cy - 8, 6), (cx + 8, cy - 14, 4), (cx + 15, cy + 8, 8),
                         (cx - 4, cy + 12, 5), (cx + 1, cy - 1, 3), (cx - 19, cy + 10, 4)]:
        d.ellipse([crx - cr, cry - cr, crx + cr, cry + cr], fill=(120, 118, 110))
        d.ellipse([crx - cr, cry - cr, crx + cr, cry + cr], outline=(100, 98, 90), width=1)
    px, py = x + 210, y + 30
    d.rectangle([px, py, px + 74, py + 16], fill=(40, 90, 160))
    d.rectangle([px, py, px + 74, py + 16], outline=(200, 210, 230), width=1)
    for gx in range(px + 9, px + 74, 9):
        d.line([gx, py, gx, py + 16], fill=(200, 210, 230), width=1)
    d.line([px, py + 8, px + 74, py + 8], fill=(200, 210, 230), width=1)
    d.rectangle([px + 76, py + 3, px + 92, py + 13], fill=(220, 220, 220))
    d.rectangle([px + 92, py + 5, px + 100, py + 11], fill=GOLD)
    d.line([px + 37, py + 16, px + 37, py + 26], fill=(220, 220, 220), width=2)
    d.ellipse([px + 29, py + 24, px + 45, py + 40], fill=(200, 200, 200))
    d.ellipse([px + 29, py + 24, px + 45, py + 40], outline=(120, 120, 120), width=1)


def banner_cop31(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 238, 226))
    cx, cy, r = x + 72, y + h // 2 + 4, h // 2 - 4
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(64, 130, 170))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=NAVY, width=2)
    k = r / 48.0
    def P(ox, oy):
        return (cx + ox * k, cy + oy * k)
    d.polygon([P(-32, -28), P(-8, -36), P(6, -20), P(-12, -8), P(-28, -10)],
              fill=(96, 168, 96))
    d.polygon([P(8, 6), P(32, -2), P(38, 20), P(14, 32), P(2, 18)],
              fill=(96, 168, 96))
    d.polygon([P(-24, 16), P(-6, 24), P(-16, 38)], fill=(120, 180, 110))
    d.arc([cx - r, cy - r, cx + r, cy + r], 300, 60, fill=(200, 225, 240), width=2)
    # thermometer
    tx = x + 138
    d.text((tx, y + 6), "+1.5\u00b0C", font=SANS_B(12), fill=RED)
    d.rounded_rectangle([tx, y + 22, tx + 24, y + h - 10], radius=12, fill=WHITE,
                        outline=NAVY, width=2)
    d.ellipse([tx - 5, y + h - 30, tx + 29, y + h - 6], fill=RED)
    d.ellipse([tx - 5, y + h - 30, tx + 29, y + h - 6], outline=NAVY, width=2)
    d.rectangle([tx + 7, y + 34, tx + 17, y + h - 18], fill=RED)
    for i in range(4):
        ty = y + 30 + i * 13
        d.line([tx + 24, ty, tx + 31, ty], fill=NAVY, width=2)
    # red badge, right side
    bx = x + 180
    d.rounded_rectangle([bx, y + 12, x + w - 8, y + 58], radius=6, fill=RED)
    d.text((bx + 10, y + 16), "COP31", font=SANS_B(24), fill=WHITE)
    d.text((bx + 10, y + 43), "FINAL DAY \u00b7 DEADLOCK", font=SANS_B(10),
           fill=(255, 220, 200))


def banner_kryvyi(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 22, 40))
    for sx, sy, r in [(x + 14, y + 10, 1), (x + 80, y + 8, 1), (x + 150, y + 12, 1)]:
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=WHITE)
    base = y + h
    for bx, bw, bh in [(0, 26, 20), (30, 20, 30), (54, 24, 17), (82, 20, 27),
                       (106, 26, 20), (136, 20, 32), (160, 24, 19)]:
        d.rectangle([x + bx, base - bh, x + bx + bw, base], fill=(10, 14, 28))
        for wy in range(base - bh + 7, base - 5, 11):
            d.rectangle([x + bx + 4, wy, x + bx + 7, wy + 3], fill=(255, 200, 100))
    for fx, fy, fr in [(x + 40, base - 22, 7), (x + 118, base - 22, 8), (x + 168, base - 22, 6)]:
        d.ellipse([fx - fr, fy - fr, fx + fr, fy + fr], fill=(255, 140, 40))
        d.ellipse([fx - fr // 2, fy - fr // 2, fx + fr // 2, fy + fr // 2], fill=(255, 210, 90))
    d.rectangle([x, base - 4, x + w, base], fill=(8, 10, 22))


def banner_cricket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(46, 130, 70))
    d.rectangle([x, y + h - 14, x + w, y + h], fill=(36, 105, 56))
    d.rectangle([x + 60, y + 8, x + 130, y + h - 8], fill=(214, 196, 150))
    d.line([x + 60, y + h // 2, x + 130, y + h // 2], fill=(160, 140, 100), width=1)
    d.line([x + 70, y + 14, x + 120, y + 14], fill=WHITE, width=2)
    d.line([x + 70, y + h - 16, x + 120, y + h - 16], fill=WHITE, width=2)
    for sx in (x + 84, x + 90, x + 96):
        d.line([sx, y + 16, sx, y + 26], fill=(255, 220, 120), width=2)
        d.line([sx, y + h - 28, sx, y + h - 18], fill=(255, 220, 120), width=2)
    d.line([x + 150, y + 18, x + 162, y + 32], fill=(200, 160, 110), width=5)
    d.ellipse([x + 162, y + 24, x + 170, y + 32], fill=RED)


def banner_nato(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 60, 110))
    cx, cy = x + 52, y + h // 2
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        d.polygon([(cx, cy),
                   (cx + 16 * math.cos(a - 0.18), cy + 16 * math.sin(a - 0.18)),
                   (cx + 16 * math.cos(a + 0.18), cy + 16 * math.sin(a + 0.18))],
                  fill=WHITE)
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=GOLD)
    base = y + h
    for bx, bw, bh in [(96, 22, 23), (122, 18, 30), (144, 22, 20), (170, 16, 26)]:
        d.rectangle([x + bx, base - bh, x + bx + bw, base], fill=(16, 32, 64))
        for wy in range(base - bh + 7, base - 5, 10):
            d.rectangle([x + bx + 4, wy, x + bx + 8, wy + 4], fill=(255, 214, 120))


# ---- new v2 banners (all drawn to fit a 34px mid banner) ----
def banner_kyiv(d, x, y, w, h):
    """Dnipro river with three bridge arches, night sky, smoke."""
    d.rectangle([x, y, x + w, y + h], fill=(14, 26, 52))
    for sx, sy, r in [(x + 16, y + 8, 1), (x + 70, y + 12, 1), (x + 140, y + 7, 1),
                      (x + 170, y + 14, 1)]:
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=WHITE)
    base = y + h
    for bx, bw, bh in [(0, 20, 22), (24, 16, 26), (44, 22, 18), (150, 18, 26),
                       (172, 14, 20)]:
        d.rectangle([x + bx, base - bh - 8, x + bx + bw, base - 8], fill=(10, 16, 34))
        for wy in range(base - bh - 2, base - 12, 9):
            d.rectangle([x + bx + 4, wy, x + bx + 7, wy + 3], fill=(255, 200, 100))
    d.rectangle([x, base - 10, x + w, base], fill=(40, 90, 140))
    for wx in range(x + 8, x + w - 8, 22):
        d.line([wx, base - 6, wx + 12, base - 6], fill=(120, 170, 210), width=1)
        d.line([wx + 4, base - 3, wx + 16, base - 3], fill=(120, 170, 210), width=1)
    for ax in (x + 70, x + 100, x + 130):
        d.arc([ax - 12, base - 24, ax + 12, base - 2], 180, 360, fill=GOLD, width=3)
        d.line([ax - 12, base - 13, ax + 12, base - 13], fill=GOLD, width=2)
    for cx0, cy0, cr in [(x + 100, y + 8, 6), (x + 108, y + 13, 7), (x + 94, y + 14, 5)]:
        d.ellipse([cx0 - cr, cy0 - cr, cx0 + cr, cy0 + cr], fill=(120, 120, 120))
    d.ellipse([x + 100 - 3, y + 6, x + 100 + 3, y + 12], fill=(255, 140, 40))


def banner_gaza(d, x, y, w, h):
    """Dusk skyline: dome, minaret, smoke."""
    d.rectangle([x, y, x + w, y + h], fill=(232, 190, 130))
    d.ellipse([x + w - 34, y + 8, x + w - 14, y + 28], fill=(255, 220, 140))
    base = y + h
    for bx, bw, bh in [(0, 26, 24), (30, 20, 32), (54, 24, 20), (120, 22, 28),
                       (146, 20, 22), (170, 16, 30)]:
        d.rectangle([x + bx, base - bh, x + bx + bw, base], fill=(90, 70, 60))
        for wy in range(base - bh + 6, base - 4, 10):
            d.rectangle([x + bx + 4, wy, x + bx + 7, wy + 3], fill=(255, 220, 140))
    d.pieslice([x + 82, base - 30, x + 118, base - 8], 180, 360, fill=(40, 90, 120))
    d.rectangle([x + 82, base - 12, x + 118, base], fill=(40, 90, 120))
    d.line([x + 100, base - 34, x + 100, base - 30], fill=GOLD, width=2)
    d.rectangle([x + 126, base - 28, x + 132, base], fill=(60, 50, 45))
    d.polygon([(x + 124, base - 28), (x + 134, base - 28), (x + 129, base - 34)],
              fill=(60, 50, 45))
    for cx0, cy0, cr in [(x + 40, y + 8, 7), (x + 52, y + 13, 8), (x + 34, y + 14, 5),
                         (x + 62, y + 18, 6)]:
        d.ellipse([cx0 - cr, cy0 - cr, cx0 + cr, cy0 + cr], fill=(150, 140, 130))
    d.ellipse([x + 44 - 3, y + 18, x + 44 + 3, y + 24], fill=(255, 120, 40))


def banner_wellington(d, x, y, w, h):
    """Green outfield, bat, red ball, white '100' badge."""
    d.rectangle([x, y, x + w, y + h], fill=(46, 130, 70))
    d.rectangle([x, y + h - 14, x + w, y + h], fill=(36, 105, 56))
    d.ellipse([x + 14, y + 8, x + w - 14, y + h - 8], fill=(214, 196, 150))
    for sx in (x + 30, x + 36, x + 42):
        d.line([sx, y + h - 26, sx, y + h - 14], fill=(255, 220, 120), width=2)
    d.line([x + 30, y + h - 27, x + 44, y + h - 27], fill=(255, 220, 120), width=2)
    d.line([x + 96, y + 10, x + 110, y + 28], fill=(200, 160, 110), width=6)
    d.line([x + 110, y + 28, x + 113, y + 32], fill=(160, 120, 80), width=4)
    d.ellipse([x + 132, y + 14, x + 146, y + 28], fill=RED)
    d.arc([x + 132, y + 14, x + 146, y + 28], 200, 340, fill=WHITE, width=1)
    d.ellipse([x + w - 52, y + h - 34, x + w - 12, y + h - 6], fill=NAVY)
    d.ellipse([x + w - 52, y + h - 34, x + w - 12, y + h - 6], outline=GOLD, width=2)
    d.text((x + w - 32, y + h - 28), "100", font=SANS_B(13), fill=WHITE, anchor="ma")


def banner_turin(d, x, y, w, h):
    """Tennis court from above: blue court, white lines, yellow ball."""
    d.rectangle([x, y, x + w, y + h], fill=(30, 90, 140))
    d.rectangle([x + 14, y + 6, x + w - 14, y + h - 6], fill=(60, 130, 90))
    d.rectangle([x + 14, y + 6, x + w - 14, y + h - 6], outline=WHITE, width=2)
    d.line([x + 14, y + h // 2, x + w - 14, y + h // 2], fill=WHITE, width=2)
    d.line([x + w // 2, y + 6, x + w // 2, y + h - 6], fill=WHITE, width=1)
    d.rectangle([x + 52, y + 12, x + w - 52, y + h - 12], outline=WHITE, width=1)
    d.line([x + w // 2 - 14, y + h // 2 - 8, x + w // 2 + 14, y + h // 2 - 8],
           fill=WHITE, width=2)
    d.line([x + w // 2 - 14, y + h // 2 + 8, x + w // 2 + 14, y + h // 2 + 8],
           fill=WHITE, width=2)
    for i, (bx, by) in enumerate([(x + 150, y + 12), (x + 157, y + 19), (x + 164, y + 27)]):
        r = 7 - i * 2
        d.ellipse([bx - r, by - r, bx + r, by + r],
                  fill=(220, 230, 60) if i == 2 else (180, 190, 60))
    d.arc([x + 157, y + 21, x + 171, y + 33], 250, 60, fill=WHITE, width=1)


def banner_vegas(d, x, y, w, h):
    """Neon night skyline with a lit sign tower."""
    d.rectangle([x, y, x + w, y + h], fill=(20, 10, 40))
    for sx, sy, r in [(x + 16, y + 10, 1), (x + 60, y + 8, 1), (x + 120, y + 12, 1),
                      (x + 170, y + 8, 1)]:
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=WHITE)
    base = y + h
    cols = [(255, 60, 120), (60, 220, 255), (255, 200, 40), (120, 255, 120),
            (255, 120, 40)]
    for i, (bx, bw, bh) in enumerate([(0, 26, 21), (30, 20, 30), (54, 24, 17),
                                      (118, 22, 25), (144, 20, 21), (168, 18, 28)]):
        col = cols[i % len(cols)]
        d.rectangle([x + bx, base - bh, x + bx + bw, base], fill=(30, 20, 60))
        d.rectangle([x + bx, base - bh, x + bx + bw, base - bh + 3], fill=col)
        for wy in range(base - bh + 8, base - 4, 10):
            d.rectangle([x + bx + 4, wy, x + bx + 7, wy + 3], fill=col)
    d.rectangle([x + 82, y + 4, x + 112, y + 20], fill=(255, 200, 40))
    d.rectangle([x + 82, y + 4, x + 112, y + 20], outline=WHITE, width=2)
    d.text((x + 97, y + 6), "LV", font=SANS_B(13), fill=(20, 10, 40), anchor="ma")
    d.rectangle([x + 95, y + 20, x + 99, base - 8], fill=(200, 200, 200))
    d.rounded_rectangle([x + 150, base - 18, x + 164, base - 4], radius=3, fill=WHITE)
    d.ellipse([x + 153, base - 15, x + 156, base - 12], fill=RED)
    d.ellipse([x + 158, base - 10, x + 161, base - 7], fill=RED)


def banner_peru(d, x, y, w, h):
    """Mountains + seismograph zigzag on paper."""
    d.rectangle([x, y, x + w, y + h], fill=(210, 225, 235))
    d.polygon([(x, y + h), (x + 40, y + 14), (x + 80, y + h)], fill=(90, 110, 140))
    d.polygon([(x + 60, y + h), (x + 110, y + 8), (x + 160, y + h)], fill=(60, 80, 115))
    d.polygon([(x + 104, y + 16), (x + 110, y + 8), (x + 116, y + 16)], fill=WHITE)
    d.polygon([(x + 36, y + 20), (x + 40, y + 14), (x + 44, y + 20)], fill=WHITE)
    d.rectangle([x, y + h - 12, x + w, y + h], fill=(70, 110, 70))
    d.rectangle([x + 8, y + h - 34, x + w - 8, y + h - 16], fill=WHITE)
    d.rectangle([x + 8, y + h - 34, x + w - 8, y + h - 16], outline=NAVY, width=1)
    pts = [(x + 12, y + h - 25), (x + 30, y + h - 25), (x + 38, y + h - 31),
           (x + 46, y + h - 19), (x + 54, y + h - 25), (x + 66, y + h - 25),
           (x + 74, y + h - 32), (x + 82, y + h - 18), (x + 90, y + h - 25),
           (x + 110, y + h - 25), (x + 118, y + h - 30), (x + 126, y + h - 20),
           (x + 134, y + h - 25), (x + 160, y + h - 25), (x + 168, y + h - 31),
           (x + 176, y + h - 19), (x + 184, y + h - 25)]
    d.line(pts, fill=RED, width=2, joint="curve")
    d.text((x + w - 12, y + 6), "M6.7", font=SANS_B(13), fill=RED, anchor="ra")


def banner_vandenberg(d, x, y, w, h):
    """Falcon 9 on the pad, flame and smoke at liftoff."""
    d.rectangle([x, y, x + w, y + h], fill=(18, 32, 58))
    for sx, sy, r in [(x + 14, y + 10, 1), (x + 50, y + 8, 1), (x + 160, y + 12, 1),
                      (x + 180, y + 8, 1)]:
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=WHITE)
    d.ellipse([x + w - 30, y + 8, x + w - 14, y + 24], fill=(240, 230, 190))
    base = y + h
    d.rectangle([x, base - 10, x + w, base], fill=(30, 60, 30))
    d.rectangle([x + 118, y + 6, x + 124, base - 10], fill=(120, 120, 120))
    for ty in range(y + 10, base - 14, 8):
        d.line([x + 118, ty, x + 124, ty + 4], fill=(80, 80, 80), width=1)
    rx = x + 92
    d.rectangle([rx, y + 6, rx + 16, base - 14], fill=WHITE)
    d.rectangle([rx, y + 6, rx + 16, base - 14], outline=(150, 150, 150), width=1)
    d.polygon([(rx, y + 6), (rx + 16, y + 6), (rx + 8, y + 2)], fill=RED)
    d.rectangle([rx + 2, y + 10, rx + 6, y + 15], fill=NAVY)
    d.rectangle([rx + 10, y + 10, rx + 14, y + 15], fill=NAVY)
    d.text((rx + 8, y + 16), "F9", font=SANS_B(7), fill=NAVY, anchor="ma")
    d.polygon([(rx + 2, base - 14), (rx + 14, base - 14), (rx + 8, base - 6)],
              fill=(255, 160, 40))
    d.polygon([(rx + 5, base - 14), (rx + 11, base - 14), (rx + 8, base - 10)],
              fill=(255, 230, 120))
    for cx0, cy0, cr in [(rx - 6, base - 12, 7), (rx + 22, base - 12, 8),
                         (rx + 34, base - 10, 6), (rx - 16, base - 10, 5)]:
        d.ellipse([cx0 - cr, cy0 - cr, cx0 + cr, cy0 + cr], fill=(200, 200, 200))


BANNERS = {1: banner_riyadh, 2: banner_mercury, 3: banner_cop31,
           4: banner_kyiv, 5: banner_kryvyi, 6: banner_cricket,
           7: banner_gaza, 8: banner_wellington, 9: banner_turin,
           10: banner_vegas, 11: banner_nato, 12: banner_peru,
           13: banner_vandenberg}

# ------------------------------------------------------------- world map ----
CONTINENTS = [
    [(18, 52), (46, 38), (72, 28), (96, 30), (106, 46), (94, 60), (78, 76),
     (56, 86), (30, 76)],
    [(96, 116), (116, 110), (132, 130), (122, 160), (106, 176), (96, 150)],
    [(160, 46), (186, 34), (202, 44), (196, 60), (176, 66), (160, 60)],
    [(166, 86), (196, 80), (216, 96), (206, 130), (186, 146), (170, 120)],
    [(206, 40), (282, 28), (316, 50), (300, 82), (262, 96), (230, 90),
     (214, 64)],
    [(272, 150), (302, 144), (312, 164), (286, 176), (266, 164)],
]
# pin positions (map coords); 2 (Mercury) lives in the legend
PINS = {1: (214, 96), 3: (196, 66), 4: (194, 46), 5: (204, 60), 6: (296, 160),
        7: (202, 84), 8: (320, 182), 9: (170, 58), 10: (48, 64), 11: (184, 36),
        12: (104, 128), 13: (28, 66)}


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    d.text((x + 10, y + 8), "WHERE IT HAPPENED", font=SANS_B(13), fill=GOLD)
    scale_x = 0.75
    scale_y = 0.62
    mw = 330 * scale_x
    mx = x + (w - mw) / 2
    my = y + 28
    for poly in CONTINENTS:
        pts = [(mx + px * scale_x, my + py * scale_y) for px, py in poly]
        d.polygon(pts, fill=(214, 190, 140))
    for n, (px, py) in PINS.items():
        cx, cy = mx + px * scale_x, my + py * scale_y
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=RED, outline=WHITE, width=1)
        d.text((cx, cy - 4), str(n), font=SANS_B(8), fill=WHITE, anchor="mm")
    ly = y + h - 28
    d.ellipse([x + 12, ly, x + 26, ly + 14], fill=RED, outline=WHITE, width=1)
    d.text((x + 19, ly + 1), "2", font=SANS_B(9), fill=WHITE, anchor="ma")
    d.text((x + 30, ly + 2), "SPACE \u00b7 Mercury", font=SANS_B(10), fill=WHITE)
    d.ellipse([x + 158, ly, x + 172, ly + 14], fill=RED, outline=WHITE, width=1)
    d.text((x + 165, ly + 1), "13", font=SANS_B(9), fill=WHITE, anchor="ma")
    d.text((x + 176, ly + 2), "USA \u00b7 Vandenberg", font=SANS_B(10), fill=WHITE)
    d.text((x + 12, ly + 16), "1-3 Lead \u00b7 4-13 Feature stories \u00b7 Positions approximate.",
           font=SANS(9), fill=(170, 178, 190))


# ------------------------------------------------------------------ render --
def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # deterministic paper texture: sparse darker specks
    for gx in range(0, W, 5):
        for gy in range(0, H, 5):
            if ((gx * 2654435761) ^ (gy * 40503)) % 41 == 0:
                d.point((gx, gy), fill=(238, 232, 218))
    d.rectangle([4, 4, W - 5, H - 5], outline=NAVY, width=2)

    y = 12
    text(d, (M, y), "THE WORLD IN ONE DAY", SANS_B(12), NAVY)
    d.text((W - M, y), "SATURDAY'S NEWS \u00b7 ONE PAGE \u00b7 33 STORIES \u00b7 7 REGIONS",
           font=SANS_B(12), fill=NAVY, anchor="ra")
    y = 28
    centre(d, W // 2, y, "Saturday 21 November 2026", SERIF_B(40), NAVY)
    y = 72
    centre(d, W // 2, y, ("Riyadh intercepts three Houthi missiles \u00b7 BepiColombo "
                           "reaches Mercury \u00b7 COP31 talks spill into Saturday \u00b7 "
                           "Starc's seven stuns England"),
           SERIF_I(15), RED)
    y = 92
    d.line([M, y, W - M, y], fill=NAVY, width=2)
    y = 98

    # ---- stat strip ----
    cell = CW // 6
    for i, (num, lab) in enumerate(STATS):
        cx = M + i * cell + cell // 2
        fnum = SERIF_B(24)
        if d.textlength(num, font=fnum) > cell - 10 and ", " in num:
            a, b = num.split(", ", 1)
            centre(d, cx, y, a + ",", SERIF_B(19), RED)
            centre(d, cx, y + 19, b, SERIF_B(19), RED)
            ly = y + 38
        else:
            centre(d, cx, y, num, fnum, RED)
            ly = y + 27
        for ln in wrap(d, lab, SANS(10), cell - 12)[:1]:
            centre(d, cx, ly, ln, SANS(10), MUTED)
            ly += 11
        if i:
            d.line([M + i * cell, y + 2, M + i * cell, y + 46], fill=RULE, width=1)
    y = 146
    d.line([M, y, W - M, y], fill=RULE, width=1)
    y = 152

    # ---- region strip ----
    total = sum(c for _, c, _ in REGIONS)
    minw = 56
    free = CW - minw * len(REGIONS)
    widths = []
    for _, c, _ in REGIONS:
        widths.append(minw + (free * c // total if total else 0))
    widths[-1] += CW - sum(widths)
    rx = M
    for (name, cnt, col), wdt in zip(REGIONS, widths):
        if cnt:
            d.rectangle([rx, y, rx + wdt - 1, y + 22], fill=col)
            fnt = SANS_B(11)
            if d.textlength("%s %d" % (name, cnt), font=fnt) > wdt - 6:
                fnt = SANS_B(10)
            centre(d, rx + wdt // 2, y + 4, "%s %d" % (name, cnt), fnt, WHITE)
        else:
            d.rectangle([rx, y, rx + wdt - 1, y + 22], fill=(200, 192, 175))
            centre(d, rx + wdt // 2, y + 6, "%s 0" % name, SANS_B(8), (110, 100, 85))
        rx += wdt
    y = 180

    # ---- leads: 3 columns, dynamic height ----
    gap = 12
    lw = (CW - 2 * gap) // 3
    banner_h = 72
    lead_bottom = y
    for i, s in enumerate(LEADS):
        x0 = M + i * (lw + gap)
        BANNERS[s["n"]](d, x0, y, lw, banner_h)
        d.rectangle([x0, y, x0 + lw - 1, y + banner_h - 1], outline=NAVY, width=1)
        tag(d, x0 + 6, y + banner_h - 24, s["tag"], SANS_B(10), WHITE, RED)
        ty = y + banner_h + 6
        text(d, (x0, ty), "%02d \u00b7 %s \u00b7 %s" % (s["n"], s["place"], s["topic"]),
             SANS_B(11), RED)
        ty += 13
        for ln in wrap(d, s["head"], SERIF_B(22), lw)[:2]:
            text(d, (x0, ty), ln, SERIF_B(22))
            ty += 22
        ty += 1
        for ln in wrap(d, s["body"], SERIF(12), lw)[:3]:
            text(d, (x0, ty), ln, SERIF(12), (40, 40, 40))
            ty += 14
        text(d, (x0, ty + 1), "(%s)" % s["src"], SERIF_I(11), MUTED)
        lead_bottom = max(lead_bottom, ty + 1 + 11)
    y = lead_bottom + 4
    d.line([M, y, W - M, y], fill=RULE, width=1)
    y += 10

    # ---- mids: 2 rows x 5, dynamic row heights ----
    mgap = 10
    mw = (CW - 4 * mgap) // 5
    mid_banner = 34
    for row in range(2):
        row_bottom = y
        for col in range(5):
            s = MIDS[row * 5 + col]
            x0 = M + col * (mw + mgap)
            y0 = y
            BANNERS[s["n"]](d, x0, y0, mw, mid_banner)
            d.rectangle([x0, y0, x0 + mw - 1, y0 + mid_banner - 1], outline=NAVY, width=1)
            tag(d, x0 + 5, y0 + mid_banner - 19, s["tag"], SANS_B(9), WHITE, RED)
            ty = y0 + mid_banner + 5
            text(d, (x0, ty), "%02d \u00b7 %s" % (s["n"], s["place"]), SANS_B(10), RED)
            ty += 13
            for ln in wrap(d, s["head"], SERIF_B(16), mw)[:2]:
                text(d, (x0, ty), ln, SERIF_B(16))
                ty += 16
            ty += 1
            for ln in wrap(d, s["body"], SERIF(11), mw)[:2]:
                text(d, (x0, ty), ln, SERIF(11), (40, 40, 40))
                ty += 11
            text(d, (x0, ty + 1), "(%s)" % s["src"], SERIF_I(9), MUTED)
            row_bottom = max(row_bottom, ty + 1 + 9)
        y = row_bottom + 6
    d.line([M, y + 4, W - M, y + 4], fill=RULE, width=1)
    y += 14

    # ---- bottom block: map + HOW WE DATE left, ALSO ON right (2 cols) ----
    bot_top = y
    map_h = 176
    map_w = 330
    draw_map(d, M, y, map_w, map_h)
    ny = y + map_h + 8
    note_h = 84
    d.rectangle([M, ny, M + map_w, ny + note_h], fill=(240, 234, 218))
    d.rectangle([M, ny, M + map_w, ny + note_h], outline=RULE, width=1)
    ly = ny + 6
    for ln in wrap(d, HOWWE, SERIF(11), map_w - 16):
        text(d, (M + 8, ly), ln, SERIF(11), (40, 40, 40))
        ly += 13
    left_h = map_h + 8 + note_h

    ax = M + map_w + 14
    aw = W - M - ax
    text(d, (ax, y), "ALSO ON SATURDAY 21 NOVEMBER \u2014 20 MORE STORIES",
         SANS_B(13), NAVY)
    d.line([ax, y + 20, W - M, y + 20], fill=NAVY, width=2)
    col_gap = 12
    col_w = (aw - col_gap) // 2
    col_bottom = y
    for col in range(2):
        cy0 = y + 28
        for s in ONELINERS[col * 10:(col + 1) * 10]:
            cx0 = ax + col * (col_w + col_gap)
            text(d, (cx0, cy0), str(s["n"]), SERIF_B(14), RED)
            lines = wrap(d, "%s \u2014 %s (%s)" % (s["place"], s["head"], s["src"]),
                         SERIF(11), col_w - 26)
            ly = cy0
            for ln in lines:
                text(d, (cx0 + 26, ly), ln, SERIF(11))
                ly += 12
            cy0 = ly + 1
        col_bottom = max(col_bottom, cy0)
    y = bot_top + max(left_h, col_bottom - bot_top) + 6

    # ---- DATE CHECK box ----
    d.rectangle([M, y, W - M, y + 4], fill=RED)
    y += 8
    text(d, (M, y), "DATE CHECK \u2014 FIRST REPORTED FRIDAY 20 NOVEMBER (OR EARLIER), SO NOT SATURDAY'S NEWS",
         SANS_B(11), RED)
    y += 15
    ly = y
    for ln in wrap(d, DATECHECK, SERIF(10), CW - 4):
        text(d, (M + 2, ly), ln, SERIF(10), (60, 20, 16))
        ly += 11
    y = ly + 6

    # ---- footer ----
    centre(d, W // 2, y, ("Every story here happened, or was first reported, on Saturday "
                           "21 November 2026 in at least one time zone. Claims are "
                           "attributed, not stated as fact."),
           SERIF_I(10), MUTED)
    y += 10
    centre(d, W // 2, y, ("Sources: Reuters, AFP, AP, BBC, ESA, UN News, and others "
                           "\u2014 full list in SOURCES.md. Original vector drawings."),
           SERIF(10), MUTED)
    y += 10

    out = os.path.join(HERE, "entry.png")
    img.save(out, optimize=True)
    print("wrote", out, img.size, "final y =", y)


if __name__ == "__main__":
    render()
