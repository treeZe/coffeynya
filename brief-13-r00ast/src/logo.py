"""Логотип R00ast: буквы переведены в кривые (шрифт Unbounded Bold),
два «0» заменены кофейными зёрнами. Генерирует SVG в ../logo/."""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "src" / "fonts"
OUT = ROOT / "logo"

ESPRESSO = "#3B2418"
TERRACOTTA = "#C4613A"
BEIGE = "#EADCC8"
WHITE = "#FFFFFF"
BLACK = "#1E1E1E"


def text_path(font_file, text, x, baseline, size):
    """Возвращает (svg path d, ширина) для строки, переведённой в кривые."""
    font = TTFont(font_file)
    gs = font.getGlyphSet()
    cmap = font.getBestCmap()
    scale = size / font["head"].unitsPerEm
    d = []
    for ch in text:
        name = cmap[ord(ch)]
        pen = SVGPathPen(gs)
        gs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, x, baseline)))
        d.append(pen.getCommands())
        x += gs[name].width * scale
    return " ".join(d), x


def cap_height(font_file, size):
    font = TTFont(font_file)
    return font["OS/2"].sCapHeight / font["head"].unitsPerEm * size


def bean(cx, cy, h, fill, slit, uid):
    """Кофейное зерно: эллипс с S-образной бороздкой (вырезана маской)."""
    rx, ry = h * 0.39, h * 0.5
    sw = h * 0.085
    s = (f"M{cx + h*0.02:.1f},{cy - ry*0.86:.1f} "
         f"C{cx - h*0.2:.1f},{cy - ry*0.3:.1f} {cx + h*0.2:.1f},{cy + ry*0.3:.1f} "
         f"{cx - h*0.02:.1f},{cy + ry*0.86:.1f}")
    if slit == "mask":
        return (f'<mask id="m{uid}"><rect x="{cx-rx-2:.1f}" y="{cy-ry-2:.1f}" '
                f'width="{2*rx+4:.1f}" height="{2*ry+4:.1f}" fill="#fff"/>'
                f'<path d="{s}" fill="none" stroke="#000" stroke-width="{sw:.1f}" '
                f'stroke-linecap="round"/></mask>'
                f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
                f'fill="{fill}" mask="url(#m{uid})"/>')
    return (f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}"/>'
            f'<path d="{s}" fill="none" stroke="{slit}" stroke-width="{sw:.1f}" stroke-linecap="round"/>')


def wordmark(letters, beans, tagline=None, pad=40, id_prefix="w"):
    """Основной логотип «R00ast». tagline — цвет подписи или None."""
    bold = FONTS / "Unbounded-Bold.ttf"
    size = 200
    ch = cap_height(bold, size)
    base = pad + ch
    d1, x = text_path(bold, "R", pad, base, size)
    bh = ch * 1.02
    x += bh * 0.06
    parts = []
    for i in range(2):
        cx = x + bh * 0.39
        parts.append(bean(cx, base - ch / 2, bh, beans, "mask", f"{id_prefix}{i}"))
        x = cx + bh * 0.39 + bh * 0.09
    x += bh * 0.02
    d2, x = text_path(bold, "ast", x, base, size)
    w = x + pad
    h = base + pad
    tag = ""
    if tagline:
        cav = FONTS / "Caveat-Bold.ttf"
        td, tw = text_path(cav, "обжариваем сами", 0, 0, 74)
        tx = w - pad - tw
        tag = f'<path d="{text_path(cav, "обжариваем сами", tx, base + 78, 74)[0]}" fill="{tagline}"/>'
        h = base + 78 + pad
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" '
            f'width="{w:.0f}" height="{h:.0f}">'
            f'<path d="{d1} {d2}" fill="{letters}"/>{"".join(parts)}{tag}</svg>')


def icon(bg, beans, slit=None, size=512, shape="circle"):
    """Компактный знак: два зерна «00» в круге. Читается даже в 16 px."""
    c = size / 2
    h = size * 0.46
    slit = slit or bg
    bgel = (f'<circle cx="{c}" cy="{c}" r="{c}" fill="{bg}"/>' if shape == "circle"
            else f'<rect width="{size}" height="{size}" rx="{size*0.22}" fill="{bg}"/>')
    b = bean(c - h * 0.42, c, h, beans, slit, "") + bean(c + h * 0.42, c, h, beans, slit, "")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
            f'width="{size}" height="{size}">{bgel}{b}</svg>')


VARIANTS = {
    "r00ast-logo-color.svg": lambda: wordmark(ESPRESSO, TERRACOTTA),
    "r00ast-logo-color-tagline.svg": lambda: wordmark(ESPRESSO, TERRACOTTA, TERRACOTTA),
    "r00ast-logo-black.svg": lambda: wordmark(BLACK, BLACK),
    "r00ast-logo-white.svg": lambda: wordmark(WHITE, WHITE),
    "r00ast-logo-on-dark.svg": lambda: wordmark(BEIGE, TERRACOTTA),
    "r00ast-icon-color.svg": lambda: icon(ESPRESSO, TERRACOTTA),
    "r00ast-icon-light.svg": lambda: icon(BEIGE, ESPRESSO),
    "r00ast-icon-black.svg": lambda: icon(BLACK, WHITE),
    "r00ast-icon-app.svg": lambda: icon(TERRACOTTA, WHITE, shape="square"),
}

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for name, fn in VARIANTS.items():
        (OUT / name).write_text(fn(), encoding="utf-8")
        print("wrote", name)
