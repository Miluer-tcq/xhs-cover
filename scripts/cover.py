#!/usr/bin/env python3
"""
XHS Cover Generator — pure Pillow, no browser needed.
Generates 1242x1660 PNG covers for Xiaohongshu.
"""
import os
import math
import argparse
import time
import random
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Canvas
# ---------------------------------------------------------------------------
W, H = 1242, 1660
MX = 80
CW = W - MX * 2
BICUBIC = getattr(getattr(Image, "Resampling", Image), "BICUBIC", Image.BICUBIC)

# Colors
BG     = "#FFF8F0"
DARK   = "#2D3436"
GRAY   = "#636E72"
LIGHT  = "#DFE6E9"
WHITE  = "#FFFFFF"
RED    = "#FF6B6B"
TEAL   = "#4ECDC4"
YELLOW = "#FFE66D"
BLUE   = "#45B7D1"
GREEN  = "#96CEB4"
ORG    = "#FFB347"
PINK   = "#FFCAD4"
PURPLE = "#CDB4DB"

STEP_COLS = [RED, TEAL, BLUE, GREEN, ORG, PURPLE]

# ---------------------------------------------------------------------------
# Font helpers
# ---------------------------------------------------------------------------
_cache = {}


def _best_font(bold: bool) -> str:
    candidates = (
        ["C:/Windows/Fonts/msyhbd.ttc", "C:/Windows/Fonts/simhei.ttf"]
        if bold else
        [
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simhei.ttf",
            "/System/Library/Fonts/PingFang.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        ]
    )
    for p in candidates:
        if os.path.exists(p):
            return p
    return ""


_FONT_REG = _best_font(False)
_FONT_BOLD = _best_font(True)


def fnt(size: int, bold: bool = False):
    path = _FONT_BOLD if bold else _FONT_REG
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size) if path else ImageFont.load_default()
    return _cache[key]


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------
def tw(text: str, font) -> int:
    if not text:
        return 0
    bb = font.getbbox(str(text))
    return bb[2] - bb[0]


def th(text: str, font) -> int:
    bb = font.getbbox(str(text) or "国")
    return bb[3] - bb[1]


def line_h(font) -> int:
    return th("国Ag", font)


def wrap(text: str, font, max_w: int) -> list:
    text = str(text or "")
    if not text:
        return []
    lines = []
    for para in text.replace("\r\n", "\n").split("\n"):
        if not para:
            lines.append("")
            continue
        line = ""
        for ch in para:
            trial = line + ch
            if line and tw(trial, font) > max_w:
                lines.append(line)
                line = ch
            else:
                line = trial
        if line:
            lines.append(line)
    return lines


def truncate_lines(lines: list, font, max_w: int, max_lines: int) -> list:
    if len(lines) <= max_lines:
        return lines
    out = lines[:max_lines]
    last = out[-1]
    while last and tw(last + "…", font) > max_w:
        last = last[:-1]
    out[-1] = (last or "") + "…"
    return out


def fit_wrapped(text: str, max_size: int, min_size: int, max_w: int, max_lines: int, bold: bool = False):
    for size in range(max_size, min_size - 1, -2):
        font = fnt(size, bold)
        lines = wrap(text, font, max_w)
        if len(lines) <= max_lines:
            return font, lines
    font = fnt(min_size, bold)
    return font, truncate_lines(wrap(text, font, max_w), font, max_w, max_lines)


def fit_single(text: str, max_size: int, min_size: int, max_w: int, bold: bool = False):
    text = str(text or "")
    for size in range(max_size, min_size - 1, -2):
        font = fnt(size, bold)
        if tw(text, font) <= max_w:
            return font
    return fnt(min_size, bold)


def block_h(lines: list, font, gap: int) -> int:
    if not lines:
        return 0
    return len(lines) * line_h(font) + (len(lines) - 1) * gap


def draw_lines(d, x: int, y: int, lines: list, font, color, gap: int = 8, align: str = "left", width: int = 0):
    yy = y
    for line in lines:
        if align == "center":
            xx = x + (width - tw(line, font)) // 2
        elif align == "right":
            xx = x + width - tw(line, font)
        else:
            xx = x
        d.text((xx, yy), line, fill=color, font=font)
        yy += line_h(font) + gap
    return yy - gap if lines else y


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------
def hex_rgb(val: str):
    val = val.lstrip("#")
    return tuple(int(val[i:i + 2], 16) for i in (0, 2, 4))


def rgba(val: str, alpha: int):
    return (*hex_rgb(val), alpha)


def rrect(d, xy, r, fill=None, outline=None, lw=1):
    x0, y0, x1, y1 = xy
    r = min(r, (x1 - x0) // 2, (y1 - y0) // 2)
    d.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=lw)


def shadow(d, xy, r, off=6, col=(0, 0, 0, 24)):
    x0, y0, x1, y1 = xy
    rrect(d, (x0 + off, y0 + off, x1 + off, y1 + off), r, fill=col)


def draw_star(d, cx, cy, r, color, outline=None):
    pts = []
    for i in range(10):
        ang = -1.5708 + i * 0.6283
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=color, outline=outline)


def draw_spark(d, cx, cy, r, color, lw=4):
    d.line((cx - r, cy, cx + r, cy), fill=color, width=lw)
    d.line((cx, cy - r, cx, cy + r), fill=color, width=lw)
    d.line((cx - r * 0.7, cy - r * 0.7, cx + r * 0.7, cy + r * 0.7), fill=color, width=max(2, lw - 1))
    d.line((cx - r * 0.7, cy + r * 0.7, cx + r * 0.7, cy - r * 0.7), fill=color, width=max(2, lw - 1))


def paste_rotated_tape(img, x, y, w, h, color, angle):
    tape = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0))
    td = ImageDraw.Draw(tape)
    rrect(td, (10, 10, 10 + w, 10 + h), 5, fill=rgba(color, 122))
    for yy in range(14, 10 + h, 10):
        td.line((14, yy, 10 + w - 14, yy), fill=(255, 255, 255, 46), width=2)
    rot = tape.rotate(angle, expand=True, resample=BICUBIC)
    img.alpha_composite(rot, (int(x), int(y)))


# ---------------------------------------------------------------------------
# Components
# ---------------------------------------------------------------------------
def draw_grid_bg(d):
    step = 36
    for x in range(0, W, step):
        d.line((x, 0, x, H), fill=(94, 153, 236, 24), width=1)
    for y in range(0, H, step):
        d.line((0, y, W, y), fill=(94, 153, 236, 24), width=1)


def draw_corner_shapes(img, d, rng):
    paste_rotated_tape(img, W - 230, 22, 120, 34, YELLOW, -8)
    paste_rotated_tape(img, 105, H - 122, 128, 34, BLUE, 6)

    d.ellipse((W - 160, 92, W - 86, 166), fill=rgba(YELLOW, 220), outline=rgba(ORG, 230), width=3)
    draw_star(d, W - 123, 129, 22, rgba(WHITE, 255), outline=rgba(DARK, 210))

    d.ellipse((48, 54, 114, 120), fill=rgba(RED, 60))
    d.ellipse((74, 82, 132, 140), fill=rgba(TEAL, 56))
    draw_spark(d, W - 58, 254, 18, rgba(ORG, 220), 4)
    draw_spark(d, 120, 248, 16, rgba(BLUE, 150), 4)

    for _ in range(6):
        x = rng.randint(120, W - 120)
        y = rng.randint(170, H - 110)
        r = rng.randint(4, 7)
        d.ellipse((x - r, y - r, x + r, y + r), fill=rgba(rng.choice([YELLOW, TEAL, BLUE, RED, GREEN]), 80))


def draw_notebook(d):
    line_x = 92
    d.line((line_x, 0, line_x, H), fill=rgba(RED, 88), width=3)
    for cy in (190, 820, 1445):
        shadow(d, (54, cy - 18, 92, cy + 20), 19, off=2, col=(0, 0, 0, 18))
        d.ellipse((54, cy - 18, 92, cy + 20), fill=rgba(WHITE, 252), outline=rgba("#B2BEC3", 160), width=3)
        d.ellipse((67, cy - 6, 79, cy + 6), fill=rgba(LIGHT, 230))


def draw_tag(d, text: str, y: int):
    font = fit_single(text, 34, 24, 340, bold=True)
    pad_x = 24
    box_w = tw(text, font) + pad_x * 2 + 28
    box_h = 62
    x0 = MX
    shadow(d, (x0, y, x0 + box_w, y + box_h), 18, off=5, col=(0, 0, 0, 24))
    rrect(d, (x0, y, x0 + box_w, y + box_h), 18, fill=rgba(YELLOW, 255), outline=rgba(DARK, 210), lw=2)
    d.ellipse((x0 + 16, y + 18, x0 + 30, y + 32), fill=rgba(RED, 255))
    d.text((x0 + 40, y + (box_h - line_h(font)) // 2 - 2), text, fill=rgba(DARK, 255), font=font)
    return y + box_h


def draw_title(d, text: str, y: int):
    font, lines = fit_wrapped(text, 108, 74, CW - 18, 3, bold=True)
    gap = 8 if len(lines) >= 3 else 12
    draw_lines(d, MX, y, lines, font, rgba(DARK, 255), gap=gap)
    end_y = y + block_h(lines, font, gap)
    underline_y = end_y + 10
    d.line((MX, underline_y, MX + min(CW - 40, 360 + len(lines[0]) * 20), underline_y), fill=rgba(ORG, 180), width=6)
    return underline_y + 18


def draw_subtitle(d, text: str, y: int):
    if not text:
        return y
    font, lines = fit_wrapped(text, 40, 28, CW - 10, 2, bold=False)
    draw_lines(d, MX, y, lines, font, rgba(GRAY, 255), gap=8)
    return y + block_h(lines, font, 8)


def draw_divider(d, y: int):
    x0, x1 = MX, W - MX
    cur = x0
    while cur < x1:
        d.line((cur, y, min(cur + 16, x1), y), fill=rgba("#D7CCC8", 255), width=3)
        cur += 28
    d.ellipse((x0 - 6, y - 6, x0 + 6, y + 6), fill=rgba(RED, 180))
    d.ellipse((x1 - 6, y - 6, x1 + 6, y + 6), fill=rgba(BLUE, 180))
    return y + 24


def draw_metric_box(d, x: int, y: int, w: int, h: int, accent: str, bg: str, value: str, label: str, strike: bool = False):
    shadow(d, (x, y, x + w, y + h), 26, off=7, col=(0, 0, 0, 28))
    rrect(d, (x, y, x + w, y + h), 26, fill=rgba(bg, 255), outline=rgba(accent, 255), lw=4)
    rrect(d, (x + 18, y + 14, x + 126, y + 48), 14, fill=rgba(accent, 48))

    tag_font = fit_single("效率对比", 22, 18, 84, bold=True)
    d.text((x + 34, y + 20), "效率对比", fill=rgba(accent, 255), font=tag_font)

    value_font = fit_single(value, 70, 42, w - 50, bold=True)
    label_font, label_lines = fit_wrapped(label, 28, 18, w - 48, 2, bold=False)
    gap = 8
    total_h = line_h(value_font) + 12 + block_h(label_lines, label_font, gap)
    sy = y + (h - total_h) // 2 + 10

    vx = x + (w - tw(value, value_font)) // 2
    d.text((vx, sy), value, fill=rgba(accent, 255), font=value_font)
    if strike:
        yy = sy + line_h(value_font) // 2 + 3
        d.line((vx - 8, yy, vx + tw(value, value_font) + 8, yy), fill=rgba(RED, 220), width=6)
    draw_lines(d, x + 24, sy + line_h(value_font) + 12, label_lines, label_font, rgba(DARK, 210), gap=gap, align="center", width=w - 48)


def draw_arrow(d, cx: int, cy: int):
    d.line((cx - 44, cy, cx + 26, cy), fill=rgba(ORG, 255), width=12)
    d.polygon([(cx + 26, cy - 22), (cx + 68, cy), (cx + 26, cy + 22)], fill=rgba(ORG, 255))
    d.ellipse((cx - 16, cy - 16, cx + 16, cy + 16), fill=rgba(YELLOW, 255), outline=rgba(ORG, 255), width=4)


def draw_highlight_boxes(d, y: int, left_val: str, right_val: str, left_label: str, right_label: str):
    gap = 28
    arrow_w = 110
    box_w = (CW - arrow_w - gap * 2) // 2
    box_h = 190
    left_x = MX
    right_x = W - MX - box_w
    draw_metric_box(d, left_x, y, box_w, box_h, RED, "#FFF1F1", left_val, left_label, strike=True)
    draw_metric_box(d, right_x, y, box_w, box_h, BLUE, "#EEF7FF", right_val, right_label, strike=False)
    draw_arrow(d, left_x + box_w + gap + arrow_w // 2 - 12, y + box_h // 2 + 4)
    return y + box_h


def draw_face(d, cx: int, cy: int, mood: str):
    skin = rgba("#FFE0B2", 255)
    hair = rgba("#4E342E", 255)
    d.ellipse((cx - 56, cy - 58, cx + 56, cy + 60), fill=skin, outline=rgba(DARK, 255), width=4)
    d.pieslice((cx - 62, cy - 78, cx + 62, cy + 38), start=180, end=360, fill=hair, outline=rgba(DARK, 255))
    d.ellipse((cx - 86, cy + 28, cx - 48, cy + 122), fill=rgba(PINK, 180), outline=rgba(DARK, 120), width=3)
    d.ellipse((cx + 48, cy + 28, cx + 86, cy + 122), fill=rgba(PINK, 180), outline=rgba(DARK, 120), width=3)

    if mood == "sad":
        d.arc((cx - 34, cy - 10, cx - 8, cy + 8), 200, 340, fill=rgba(DARK, 255), width=4)
        d.arc((cx + 8, cy - 10, cx + 34, cy + 8), 200, 340, fill=rgba(DARK, 255), width=4)
        d.arc((cx - 24, cy + 28, cx + 24, cy + 54), 20, 160, fill=rgba(DARK, 255), width=4)
        draw_spark(d, cx + 88, cy - 50, 14, rgba(RED, 180), 4)
    else:
        d.ellipse((cx - 28, cy - 4, cx - 14, cy + 10), fill=rgba(DARK, 255))
        d.ellipse((cx + 14, cy - 4, cx + 28, cy + 10), fill=rgba(DARK, 255))
        d.ellipse((cx - 24, cy, cx - 18, cy + 6), fill=rgba(WHITE, 220))
        d.ellipse((cx + 18, cy, cx + 24, cy + 6), fill=rgba(WHITE, 220))
        d.arc((cx - 28, cy + 18, cx + 28, cy + 58), 15, 165, fill=rgba(DARK, 255), width=4)
        draw_spark(d, cx + 90, cy - 54, 14, rgba(YELLOW, 220), 4)


def draw_laptop(d, x: int, y: int):
    shadow(d, (x, y, x + 246, y + 170), 18, off=6, col=(0, 0, 0, 30))
    rrect(d, (x, y, x + 246, y + 170), 18, fill=rgba("#1E293B", 255), outline=rgba(DARK, 255), lw=3)
    rrect(d, (x + 14, y + 14, x + 232, y + 140), 10, fill=rgba("#0F172A", 255))

    code_font = fnt(24, False)
    lines = [
        ("$ claude", rgba(GREEN, 255)),
        ("> 写封面脚本", rgba(BLUE, 255)),
        ("> 自动排版", rgba(YELLOW, 255)),
        ("> 输出 PNG ✓", rgba(WHITE, 240)),
    ]
    yy = y + 28
    for txt, color in lines:
        d.text((x + 26, yy), txt, fill=color, font=code_font)
        yy += 28

    d.polygon([(x + 54, y + 170), (x + 192, y + 170), (x + 224, y + 196), (x + 22, y + 196)], fill=rgba("#94A3B8", 255), outline=rgba(DARK, 120))
    d.rounded_rectangle((x + 104, y + 178, x + 142, y + 188), 4, fill=rgba("#CBD5E1", 255))


def draw_speech(d, x: int, y: int, w: int, h: int, fill_col, border_col, text: str):
    shadow(d, (x, y, x + w, y + h), 20, off=4, col=(0, 0, 0, 18))
    rrect(d, (x, y, x + w, y + h), 18, fill=fill_col, outline=border_col, lw=3)
    d.polygon([(x + 26, y + h), (x + 56, y + h), (x + 42, y + h + 24)], fill=fill_col, outline=border_col)
    font, lines = fit_wrapped(text, 30, 20, w - 28, 2, bold=True)
    top = y + (h - block_h(lines, font, 6)) // 2 - 2
    draw_lines(d, x + 14, top, lines, font, rgba(DARK, 255), gap=6, align="center", width=w - 28)


def draw_lightning(d, cx: int, cy: int):
    pts = [(cx - 8, cy - 54), (cx + 22, cy - 54), (cx - 4, cy - 10), (cx + 30, cy - 10), (cx - 24, cy + 58), (cx - 2, cy + 10), (cx - 30, cy + 10)]
    d.polygon(pts, fill=rgba(YELLOW, 255), outline=rgba(ORG, 255))


def draw_illustration(d, y: int):
    panel_h = 290
    shadow(d, (MX, y, W - MX, y + panel_h), 34, off=7, col=(0, 0, 0, 22))
    rrect(d, (MX, y, W - MX, y + panel_h), 34, fill=rgba(WHITE, 236), outline=rgba(LIGHT, 255), lw=3)

    left_cx = MX + 120
    right_cx = W - MX - 120
    face_y = y + 108

    draw_face(d, left_cx, face_y, "sad")
    draw_face(d, right_cx, face_y, "happy")
    draw_speech(d, MX + 18, y + 176, 188, 76, rgba("#FFE4E1", 255), rgba(RED, 220), "手动做太慢")
    draw_speech(d, W - MX - 206, y + 176, 188, 76, rgba("#E0F2FE", 255), rgba(BLUE, 220), "现在直接出图")

    draw_lightning(d, W // 2 - 110, y + 118)
    d.text((W // 2 - 150, y + 194), "AI 介入", fill=rgba(ORG, 255), font=fnt(34, True))
    d.line((W // 2 - 28, y + 118, W // 2 + 20, y + 118), fill=rgba(ORG, 255), width=10)
    d.polygon([(W // 2 + 20, y + 96), (W // 2 + 66, y + 118), (W // 2 + 20, y + 140)], fill=rgba(ORG, 255))

    draw_laptop(d, W // 2 + 58, y + 48)
    draw_star(d, W // 2 + 318, y + 78, 18, rgba(YELLOW, 255), outline=rgba(ORG, 255))
    draw_spark(d, W // 2 + 300, y + 206, 16, rgba(BLUE, 200), 4)
    return y + panel_h


def draw_steps(d, y: int, steps: list, footer_y: int):
    steps = steps[:5]
    n = len(steps)
    if n == 0:
        return y

    gap = 18
    avail = footer_y - y - (n - 1) * gap
    card_h = max(84, min(110, avail // n))

    for idx, step in enumerate(steps):
        x0, x1 = MX, W - MX
        y0 = y + idx * (card_h + gap)
        y1 = y0 + card_h
        col = STEP_COLS[idx % len(STEP_COLS)]

        shadow(d, (x0, y0, x1, y1), 28, off=6, col=(0, 0, 0, 22))
        rrect(d, (x0, y0, x1, y1), 28, fill=rgba(WHITE, 252), outline=rgba(col, 235), lw=3)
        rrect(d, (x0 + 18, y0 + 18, x0 + 78, y0 + 78), 30, fill=rgba(col, 255))

        num_font = fnt(34, True)
        num = str(idx + 1)
        d.text((x0 + 48 - tw(num, num_font) // 2, y0 + 48 - line_h(num_font) // 2 - 4), num, fill=rgba(WHITE, 255), font=num_font)

        text_font, lines = fit_wrapped(step, 34, 22, CW - 146, 2, bold=True)
        total = block_h(lines, text_font, 8)
        ty = y0 + (card_h - total) // 2 - 2
        draw_lines(d, x0 + 106, ty, lines, text_font, rgba(DARK, 255), gap=8)

        d.line((x0 + 96, y0 + 22, x0 + 96, y1 - 22), fill=rgba(LIGHT, 255), width=2)
    return y + n * card_h + (n - 1) * gap


def draw_footer(d, y: int, text: str):
    d.line((MX, y, W - MX, y), fill=rgba("#D7CCC8", 255), width=2)
    d.ellipse((MX, y - 7, MX + 14, y + 7), fill=rgba(BLUE, 255))
    font = fit_single(text, 22, 16, CW - 40, bold=False)
    d.text((MX + 28, y + 18), text, fill=rgba("#8D99AE", 255), font=font)
    draw_spark(d, W - MX - 24, y + 26, 10, rgba(YELLOW, 220), 3)
    return y + 46


# ---------------------------------------------------------------------------
# Main generation
# ---------------------------------------------------------------------------
def generate_cover(
    title: str,
    subtitle: str = "",
    tag: str = "效率干货",
    steps=None,
    footer: str = "@xhs-cover · Pillow 本地生成",
    hl_left: str = "3天",
    hl_right: str = "20分钟",
    hl_left_label: str = "手动硬肝才做完",
    hl_right_label: str = "AI 协作直接出稿",
    output: str = "",
    seed: int = None,
):
    steps = [s.strip() for s in (steps or []) if s and s.strip()]
    if not steps:
        steps = ["整理标题重点", "生成结构和卖点", "自动排版封面", "导出图片直接发笔记"]

    rng = random.Random(seed if seed is not None else int(time.time()))

    img = Image.new("RGBA", (W, H), rgba(BG, 255))
    d = ImageDraw.Draw(img, "RGBA")

    draw_grid_bg(d)
    draw_notebook(d)
    draw_corner_shapes(img, d, rng)

    y = 72
    y = draw_tag(d, tag, y) + 26
    y = draw_title(d, title, y)
    y = draw_subtitle(d, subtitle, y)
    y = draw_divider(d, y + 22)
    y = draw_highlight_boxes(d, y + 8, hl_left, hl_right, hl_left_label, hl_right_label) + 32
    y = draw_illustration(d, y) + 30

    footer_y = H - 110
    draw_steps(d, y, steps, footer_y - 18)
    draw_footer(d, footer_y, footer)

    output = output or os.path.join(os.getcwd(), f"cover_{int(time.time())}.png")
    output = os.path.abspath(output)
    parent = os.path.dirname(output) or os.getcwd()
    os.makedirs(parent, exist_ok=True)
    img.convert("RGB").save(output, quality=95)
    return output


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Generate XHS cover image with pure Pillow")
    parser.add_argument("title", help="Main title")
    parser.add_argument("subtitle_pos", nargs="?", default="", help="Subtitle (optional positional)")
    parser.add_argument("--subtitle", default=None, help="Subtitle")
    parser.add_argument("--tag", default="效率干货", help="Top tag")
    parser.add_argument("--steps", nargs="*", default=None, help="Step texts (up to 5)")
    parser.add_argument("--footer", default="@xhs-cover · Pillow 本地生成", help="Footer text")
    parser.add_argument("--hl-left", default="3天", help="Left highlight value")
    parser.add_argument("--hl-right", default="20分钟", help="Right highlight value")
    parser.add_argument("--hl-left-label", default="手动硬肝才做完", help="Left highlight label")
    parser.add_argument("--hl-right-label", default="AI 协作直接出稿", help="Right highlight label")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for decoration placement")
    parser.add_argument("--output", "-o", default=None, help="Output path")
    args = parser.parse_args()

    subtitle = args.subtitle if args.subtitle is not None else args.subtitle_pos
    output = generate_cover(
        title=args.title,
        subtitle=subtitle,
        tag=args.tag,
        steps=args.steps,
        footer=args.footer,
        hl_left=args.hl_left,
        hl_right=args.hl_right,
        hl_left_label=args.hl_left_label,
        hl_right_label=args.hl_right_label,
        output=args.output,
        seed=args.seed,
    )
    print(f"Cover saved: {output} ({W}x{H})")


if __name__ == "__main__":
    main()
