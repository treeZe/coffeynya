"""Генерирует HTML-страницы (мудборд, брендбук, носители, мокапы)
и manifest.json для render.js. Запуск: python3 logo.py && python3 build.py && node render.js"""
import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "src" / "html"
L = "../../logo/"  # путь к логотипам из src/html

C = {
    "espresso": "#3B2418", "terracotta": "#C4613A", "latte": "#EADCC8",
    "kraft": "#C9A27E", "milk": "#F7F2EA", "graphite": "#2B2B2B",
    "gray": "#8C857D", "white": "#FFFFFF",
}

BASE_CSS = f"""
@font-face{{font-family:Unbounded;src:url(../fonts/Unbounded-Regular.ttf);font-weight:400}}
@font-face{{font-family:Unbounded;src:url(../fonts/Unbounded-SemiBold.ttf);font-weight:600}}
@font-face{{font-family:Unbounded;src:url(../fonts/Unbounded-Bold.ttf);font-weight:700}}
@font-face{{font-family:Manrope;src:url(../fonts/Manrope-Regular.ttf);font-weight:400}}
@font-face{{font-family:Manrope;src:url(../fonts/Manrope-Medium.ttf);font-weight:500}}
@font-face{{font-family:Manrope;src:url(../fonts/Manrope-Bold.ttf);font-weight:700}}
@font-face{{font-family:Caveat;src:url(../fonts/Caveat-Bold.ttf);font-weight:700}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:Manrope;color:{C['graphite']};background:{C['milk']}}}
.slide{{width:1920px;height:1080px;position:relative;overflow:hidden;background:{C['milk']};
  padding:90px 110px;page-break-after:always}}
.h1{{font-family:Unbounded;font-weight:700;font-size:64px;color:{C['espresso']};letter-spacing:-1px}}
.h2{{font-family:Unbounded;font-weight:600;font-size:30px;color:{C['espresso']}}}
.kicker{{font-family:Unbounded;font-weight:600;font-size:16px;letter-spacing:4px;
  text-transform:uppercase;color:{C['terracotta']};margin-bottom:22px}}
.body{{font-size:22px;line-height:1.55}}
.hand{{font-family:Caveat;font-weight:700;color:{C['terracotta']}}}
.pnum{{position:absolute;right:110px;bottom:50px;font-family:Unbounded;font-size:14px;
  color:{C['gray']};letter-spacing:2px}}
.plogo{{position:absolute;left:110px;bottom:46px;height:26px;opacity:.85}}
.grid{{display:grid;gap:32px}}
.card{{background:#fff;border-radius:28px;padding:40px}}
.cap{{font-size:16px;color:{C['gray']};margin-top:12px}}
"""

random.seed(13)


# ---------- процедурная графика ----------

def bean_svg(x, y, h, rot, fill, slit):
    rx, ry = h * 0.39, h * 0.5
    return (f'<g transform="translate({x:.1f},{y:.1f}) rotate({rot:.0f})">'
            f'<ellipse rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}"/>'
            f'<path d="M{h*.02:.1f},{-ry*.86:.1f} C{-h*.2:.1f},{-ry*.3:.1f} {h*.2:.1f},{ry*.3:.1f} {-h*.02:.1f},{ry*.86:.1f}" '
            f'fill="none" stroke="{slit}" stroke-width="{h*.085:.1f}" stroke-linecap="round"/></g>')


def bean_pile(w, h, n=260, size=(34, 52), bg="#2a170e"):
    """Россыпь обжаренных зёрен — заменитель фото «coffee beans»."""
    tones = ["#3B2418", "#4A2C1C", "#5A3522", "#2E1B11", "#6B4028"]
    items = [f'<rect width="{w}" height="{h}" fill="{bg}"/>']
    for _ in range(n):
        s = random.uniform(*size)
        items.append(bean_svg(random.uniform(-20, w + 20), random.uniform(-20, h + 20), s,
                              random.uniform(0, 360), random.choice(tones), "#1a0e08"))
    return (f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid slice" '
            f'xmlns="http://www.w3.org/2000/svg">{"".join(items)}</svg>')


def noise_texture(base, w, h, freq=0.8, op=0.35, fibers=False, uid="n"):
    """Текстура бумаги/бетона через feTurbulence."""
    turb = (f'<feTurbulence type="fractalNoise" baseFrequency="{freq} {freq*0.12 if fibers else freq}" '
            f'numOctaves="4" seed="{random.randint(1,99)}"/>')
    return (f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">'
            f'<filter id="{uid}">{turb}<feColorMatrix type="saturate" values="0"/>'
            f'<feComponentTransfer><feFuncA type="linear" slope="{op}"/></feComponentTransfer></filter>'
            f'<rect width="100%" height="100%" fill="{base}"/>'
            f'<rect width="100%" height="100%" filter="url(#{uid})"/></svg>')


def wood_texture(w, h, uid="wood"):
    lines = []
    y = 0
    while y < h:
        amp = random.uniform(2, 8)
        d = f"M0,{y:.0f} " + " ".join(
            f"Q{x+30:.0f},{y+amp*math.sin(x/90+y):.1f} {x+60:.0f},{y:.0f}" for x in range(0, w + 60, 60))
        lines.append(f'<path d="{d}" stroke="#5a3a24" stroke-opacity="{random.uniform(.15,.4):.2f}" '
                     f'stroke-width="{random.uniform(1,4):.1f}" fill="none"/>')
        y += random.uniform(6, 18)
    return (f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">'
            f'<rect width="{w}" height="{h}" fill="#9a6b45"/>{"".join(lines)}</svg>')


def latte_art(size=400):
    c = size / 2
    return (f'<svg viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">'
            f'<rect width="{size}" height="{size}" fill="#d9c9b4"/>'
            f'<circle cx="{c}" cy="{c}" r="{size*.44}" fill="#f4efe8"/>'
            f'<circle cx="{c}" cy="{c}" r="{size*.40}" fill="#fbf8f3"/>'
            f'<circle cx="{c}" cy="{c}" r="{size*.34}" fill="#8a5232"/>'
            f'<radialGradient id="cr"><stop offset="0" stop-color="#b9774a"/><stop offset="1" stop-color="#6e3d22"/></radialGradient>'
            f'<circle cx="{c}" cy="{c}" r="{size*.33}" fill="url(#cr)"/>'
            f'<path d="M{c},{c+size*.2} C{c-size*.28},{c} {c-size*.14},{c-size*.2} {c},{c-size*.08} '
            f'C{c+size*.14},{c-size*.2} {c+size*.28},{c} {c},{c+size*.2}Z" fill="#f6eee3"/>'
            f'<path d="M{c},{c-size*.08} L{c},{c+size*.24}" stroke="#a8683f" stroke-width="3"/></svg>')


def roaster_flame(w, h):
    """Абстракция «процесс обжарки»: жар и зерно в барабане."""
    beans = "".join(bean_svg(random.uniform(0, w), random.uniform(h * .45, h), random.uniform(26, 40),
                             random.uniform(0, 360), random.choice(["#7a4a2b", "#94603a", "#5d3620"]), "#2b170c")
                    for _ in range(70))
    return (f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">'
            f'<radialGradient id="fl" cx=".5" cy=".9" r=".9"><stop offset="0" stop-color="#ffb35c"/>'
            f'<stop offset=".35" stop-color="#c4613a"/><stop offset="1" stop-color="#1c0f08"/></radialGradient>'
            f'<rect width="{w}" height="{h}" fill="url(#fl)"/>'
            f'<circle cx="{w/2}" cy="{h*.35}" r="{h*.28}" fill="none" stroke="#2a1a10" stroke-width="18" opacity=".6"/>'
            f'{beans}</svg>')


def pattern_svg(w, h, bg, fg, dot, tile=160):
    """Фирменный паттерн: зёрна под разными углами + точки «аромата»."""
    items = []
    pts = [(40, 40, 30, 30), (120, 60, 26, -40), (80, 125, 30, 80), (20, 140, 6, 0), (140, 20, 6, 0), (150, 140, 8, 0)]
    for x, y, s, r in pts:
        if s < 10:
            items.append(f'<circle cx="{x}" cy="{y}" r="{s/2}" fill="{dot}"/>')
        else:
            items.append(bean_svg(x, y, s * 1.3, r, fg, bg))
    return (f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice">'
            f'<defs><pattern id="p{bg[1:]}{fg[1:]}" width="{tile}" height="{tile}" patternUnits="userSpaceOnUse">'
            f'{"".join(items)}</pattern></defs><rect width="{w}" height="{h}" fill="{bg}"/>'
            f'<rect width="{w}" height="{h}" fill="url(#p{bg[1:]}{fg[1:]})"/></svg>')


def uri(svg):
    import urllib.parse
    return "data:image/svg+xml;utf8," + urllib.parse.quote(svg)


ICONS = {
    "Эспрессо": '<path d="M10 20h30v10a12 12 0 0 1-12 12h-6A12 12 0 0 1 10 30z"/><path d="M40 23h4a5 5 0 0 1 0 10h-5"/><path d="M6 48h40"/><path d="M20 8c-2 3 2 5 0 8M28 8c-2 3 2 5 0 8"/>',
    "Фильтр / V60": '<path d="M8 12h36L32 34H20z"/><path d="M20 34v6h12v-6"/><path d="M12 44h28v4H12z"/><path d="M26 4v4"/>',
    "Зерно": '<ellipse cx="26" cy="26" rx="14" ry="19" transform="rotate(30 26 26)"/><path d="M33 11c-12 6 0 24-14 30"/>',
    "Обжарка": '<path d="M26 46c-10 0-16-7-16-15 0-9 9-12 8-22 7 4 9 10 8 14 3-2 4-5 4-8 6 5 12 10 12 16 0 9-7 15-16 15z"/><path d="M26 46c-4 0-7-3-7-7 0-5 5-6 6-11 4 3 8 6 8 11 0 4-3 7-7 7z"/>',
    "Фермер": '<path d="M26 46V22"/><path d="M26 30c-8 0-12-6-12-12 8 0 12 5 12 12zM26 24c0-8 5-13 13-13 0 8-5 13-13 13z"/><path d="M12 46h28"/>',
    "Рабочее место": '<rect x="8" y="12" width="36" height="22" rx="2"/><path d="M4 40h44l-3 4H7z"/>',
    "Дегустация": '<path d="M14 6h24l-3 22a9 9 0 0 1-18 0z"/><path d="M26 37v9M18 46h16"/><path d="M15 16h22"/>',
    "Адрес": '<path d="M26 47s-14-13-14-24a14 14 0 0 1 28 0c0 11-14 24-14 24z"/><circle cx="26" cy="23" r="5"/>',
}


def icon(name, color, size=64, sw=2.6):
    return (f'<svg viewBox="0 0 52 52" width="{size}" height="{size}" fill="none" stroke="{color}" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" '
            f'xmlns="http://www.w3.org/2000/svg">{ICONS[name]}</svg>')


# ---------- страницы ----------

def page(title, body, css="", w=1920, h=1080):
    return (f'<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>{title}</title>'
            f'<style>{BASE_CSS}{css} html,body{{width:{w}px}}</style></head><body>{body}</body></html>')


def slide(n, kicker, title, inner, bg=None, dark=False):
    style = f' style="background:{bg}"' if bg else ""
    logo = "r00ast-logo-on-dark.svg" if dark else "r00ast-logo-color.svg"
    tcol = f' style="color:{C["latte"]}"' if dark else ""
    return (f'<section class="slide"{style}><div class="kicker">{kicker}</div>'
            f'<div class="h1"{tcol}>{title}</div>{inner}'
            f'<img class="plogo" src="{L}{logo}"><div class="pnum">R00AST · BRAND BOOK · {n:02d}</div></section>')


def photo_slot(art, label, query, style):
    """Слот под фото: процедурная иллюстрация + подпись с запросом для стока."""
    return (f'<div class="ph" style="{style}"><div class="art" style="background-image:url(\'{uri(art)}\')"></div>'
            f'<div class="tag"><b>{label}</b><span>Unsplash/Pexels: «{query}»</span></div></div>')


def moodboard():
    css = f"""
    .mb{{width:1920px;height:1080px;position:relative;background:{C['milk']};overflow:hidden}}
    .ph{{position:absolute;border-radius:18px;overflow:hidden;box-shadow:0 18px 40px rgba(59,36,24,.18)}}
    .ph .art{{position:absolute;inset:0;background-size:cover;background-position:center}}
    .ph .tag{{position:absolute;left:12px;bottom:12px;right:12px;background:rgba(247,242,234,.92);
      border-radius:10px;padding:8px 12px;font-size:13px;line-height:1.35;color:{C['espresso']}}}
    .ph .tag b{{display:block;font-family:Unbounded;font-weight:600;font-size:12px;letter-spacing:.5px}}
    .ph .tag span{{color:{C['gray']}}}
    .note{{position:absolute;font-family:Caveat;font-weight:700;font-size:30px;color:{C['terracotta']};transform:rotate(-4deg)}}
    .sw{{width:74px}}
    .sw i{{display:block;width:74px;height:74px;border-radius:14px;box-shadow:inset 0 0 0 1px rgba(0,0,0,.06)}}
    .sw b{{display:block;font-size:12px;margin-top:8px;color:{C['espresso']}}}
    .sw span{{font-size:11px;color:{C['gray']}}}
    """
    sw = [("Эспрессо", "espresso", "основной"), ("Терракота", "terracotta", "акцент"),
          ("Латте", "latte", "фон / доп."), ("Крафт", "kraft", "упаковка"),
          ("Молоко", "milk", "фон сайта"), ("Графит", "graphite", "текст"), ("Белый", "white", "")]
    swatches = "".join(f'<div class="sw"><i style="background:{C[k]}"></i><b>{n}</b><span>{C[k]}<br>{r}</span></div>'
                       for n, k, r in sw)
    body = f"""<div class="mb">
    <div style="position:absolute;left:70px;top:60px;width:560px">
      <div class="kicker">Moodboard · бриф 13</div>
      <img src="{L}r00ast-logo-color-tagline.svg" style="height:120px;margin:-6px 0 18px -12px">
      <div class="body" style="font-size:19px">Мудборд для сайта и айдентики кофейни-обжарочной R00ast:
      тёплый минимализм, ремесло и честный продукт — от фермы до чашки.</div>
    </div>
    {photo_slot(roaster_flame(900, 700), "ЯКОРЬ 1 · Процесс обжарки", "coffee roaster, coffee roasting",
                "left:680px;top:50px;width:620px;height:470px")}
    {photo_slot(bean_pile(700, 700), "ЯКОРЬ 2 · Зерно крупным планом", "roasted coffee beans macro",
                "left:1330px;top:50px;width:530px;height:330px")}
    {photo_slot(latte_art(), "Латте-арт сверху", "latte art top view", "left:1330px;top:405px;width:250px;height:250px")}
    {photo_slot(noise_texture('#c9a27e', 400, 400, .9, .45, True, 'kr'), "Текстура · крафт", "kraft paper texture",
                "left:1610px;top:405px;width:250px;height:250px")}
    {photo_slot(wood_texture(500, 400), "Текстура · дерево стойки", "wood counter cafe",
                "left:680px;top:545px;width:300px;height:230px")}
    {photo_slot(noise_texture('#b9b4ae', 400, 400, 1.6, .5, False, 'cn'), "Текстура · бетон / лофт", "concrete wall cafe interior",
                "left:1005px;top:545px;width:295px;height:230px")}
    {photo_slot(noise_texture('#3B2418', 400, 400, .7, .25, False, 'ap'), "Бариста в фартуке, руки", "barista hands pour over",
                "left:1330px;top:680px;width:530px;height:340px")}
    <div style="position:absolute;left:70px;top:395px;width:560px">
      <div class="kicker" style="margin-bottom:14px">Палитра</div>
      <div style="display:flex;gap:10px;width:600px">{swatches}</div>
    </div>
    <div style="position:absolute;left:70px;top:660px;width:580px">
      <div class="kicker" style="margin-bottom:12px">Типографика</div>
      <div style="font-family:Unbounded;font-weight:700;font-size:44px;color:{C['espresso']};line-height:1">Unbounded</div>
      <div style="font-size:15px;color:{C['gray']};margin:6px 0 12px">Заголовки · Regular / SemiBold / Bold</div>
      <div style="font-family:Manrope;font-size:28px;color:{C['graphite']}">Manrope <b>Bold</b> <span style="font-weight:500">Medium</span></div>
      <div style="font-size:15px;color:{C['gray']};margin:4px 0 10px">Основной текст: «Эфиопия Иргачефф — ноты жасмина и бергамота»</div>
      <div style="font-family:Caveat;font-weight:700;font-size:40px;color:{C['terracotta']}">Caveat — рукописные акценты</div>
    </div>
    <div style="position:absolute;left:680px;top:800px;width:620px;height:220px;border-radius:18px;overflow:hidden">
      <img src="{uri(pattern_svg(620, 220, C['latte'], C['terracotta'], C['espresso']))}" style="width:100%;height:100%">
    </div>
    <div class="note" style="left:1110px;top:70px;font-size:30px;color:#EADCC8">жар и ремесло</div>
    </div>"""
    return page("R00ast — Moodboard", body, css)


def brief_slide():
    rows = [
        ("Суть бренда", "R00ast — кофейня-обжарочная: сами обжариваем зерно прямых поставок от фермеров и подаём его как продукт с историей. Тёплый минимализм + ремесло."),
        ("Аудитория", "Кофейные энтузиасты 25–40 лет, фрилансеры и удалёнщики, творческая интеллигенция, жители и гости города."),
        ("Цели", "1) образ экспертной кофейни; 2) привлечь энтузиастов и креативных людей; 3) показать ценность зерна, обжарки и мастерства бариста."),
        ("Референсы", "Square Mile, Onyx Coffee Lab, Tim Wendelboe, Cofix (наоборот — от чего уходим), Surf Coffee. Общее: минимализм, крафт, плотные гротески, тёплые тона."),
        ("Название / сокращения", "R00ast · «00» — два зерна · компактный знак «00» · слоган: «Обжариваем сами»"),
    ]
    tbl = "".join(f'<div style="display:grid;grid-template-columns:330px 1fr;gap:40px;padding:22px 0;border-top:1px solid #e2d6c6">'
                  f'<div class="h2" style="font-size:20px">{a}</div><div class="body" style="font-size:21px">{b}</div></div>' for a, b in rows)
    return slide(1, "01 · Бриф", "Кофе — продукт с характером", f'<div style="margin-top:50px;width:1500px">{tbl}</div>')


def concepts_slide():
    def sk(svg, t, d):
        return (f'<div class="card" style="height:520px;display:flex;flex-direction:column">'
                f'<div style="flex:1;display:flex;align-items:center;justify-content:center">{svg}</div>'
                f'<div class="h2" style="font-size:20px">{t}</div><div class="cap" style="font-size:17px">{d}</div></div>')
    e, t = C["espresso"], C["terracotta"]
    a = (f'<svg width="330" height="160" viewBox="0 0 330 160"><text x="10" y="100" font-family="Unbounded" font-weight="700" font-size="62" fill="{e}">R</text>'
         f'{bean_svg(95,78,62,0,t,"#fff")}{bean_svg(150,78,62,0,t,"#fff")}<text x="182" y="100" font-family="Unbounded" font-weight="700" font-size="62" fill="{e}">ast</text></svg>')
    b = (f'<svg width="220" height="220" viewBox="0 0 220 220"><circle cx="110" cy="110" r="100" fill="none" stroke="{e}" stroke-width="4"/>'
         f'<text x="110" y="128" text-anchor="middle" font-family="Unbounded" font-weight="700" font-size="54" fill="{e}">R00</text>'
         f'<text x="110" y="168" text-anchor="middle" font-family="Manrope" font-weight="700" font-size="18" letter-spacing="6" fill="{t}">ROASTERY</text></svg>')
    c = (f'<svg width="240" height="200" viewBox="0 0 240 200"><path d="M40 150 Q120 20 200 150" fill="none" stroke="{t}" stroke-width="6" stroke-dasharray="2 14" stroke-linecap="round"/>'
         f'<text x="120" y="150" text-anchor="middle" font-family="Caveat" font-weight="700" font-size="72" fill="{e}">R00ast</text></svg>')
    d = (f'<svg width="200" height="200" viewBox="0 0 200 200"><rect x="20" y="20" width="160" height="160" rx="12" fill="{e}"/>'
         f'<text x="40" y="150" font-family="Unbounded" font-weight="700" font-size="120" fill="{C["latte"]}">R</text>{bean_svg(150,60,40,30,t,e)}</svg>')
    cards = sk(a, "A · Зёрна вместо «00» ✓", "Выбрана: имя читается сразу, «00» = два зерна, работает и как знак.") + \
        sk(b, "B · Круглая печать", "Классика обжарочных, но слабее узнаваемость и мелкий текст.") + \
        sk(c, "C · Рукописный", "Тепло и ремесло, но плохо читается на вывеске и в 16 px.") + \
        sk(d, "D · Монограмма R", "Сильный знак, но теряется игра с «00» в названии.")
    return slide(2, "02 · Logo Concepts", "Четыре эскиза — одна идея",
                 f'<div class="grid" style="grid-template-columns:repeat(4,1fr);margin-top:60px">{cards}</div>')


def logo_final_slide():
    def box(src, bg, t, h=110):
        return (f'<div><div style="background:{bg};border-radius:24px;height:250px;display:flex;align-items:center;'
                f'justify-content:center;box-shadow:inset 0 0 0 1px rgba(0,0,0,.06)"><img src="{L}{src}" style="height:{h}px"></div>'
                f'<div class="cap">{t}</div></div>')
    g = (box("r00ast-logo-color.svg", "#fff", "Полноцветный — на светлом фоне")
         + box("r00ast-logo-on-dark.svg", C["espresso"], "Цветной на тёмном (латте + терракота)")
         + box("r00ast-logo-black.svg", C["latte"], "Чёрный — штамп, ч/б печать, крафт")
         + box("r00ast-logo-white.svg", C["terracotta"], "Белый — на тёмных и цветных фонах")
         + box("r00ast-icon-color.svg", "#fff", "Компактный знак «00» — аватар, стаканы", 170)
         + box("r00ast-icon-app.svg", C["milk"], "Иконка приложения / фавикон", 170))
    return slide(3, "03 · Logo Final", "Логотип и его версии",
                 f'<div class="grid" style="grid-template-columns:repeat(3,1fr);margin-top:56px;row-gap:28px">{g}</div>')


def sizes_slide():
    item = lambda s, t: (f'<div style="display:flex;flex-direction:column;align-items:center;justify-content:flex-end">'
                         f'<div style="width:{s}px;height:{s}px;outline:1px dashed #cdbfae;outline-offset:6px">'
                         f'<img src="{L}r00ast-icon-color.svg" style="width:{s}px;height:{s}px;display:block"></div>'
                         f'<div class="cap" style="margin-top:22px">{t}</div></div>')
    row = item(512, "512 × 512") + item(48, "48 × 48") + item(16, "16 × 16 — читается как «две точки»")
    words = "".join(f'<div style="display:flex;align-items:center;gap:30px;margin-bottom:26px"><img src="{L}r00ast-logo-color.svg" style="height:{h}px"><span class="cap" style="margin:0">{t}</span></div>'
                    for h, t in [(80, "80 px"), (40, "40 px"), (24, "24 px — минимум для экрана")])
    return slide(4, "04 · Тест читаемости", "Проверка в миниатюре",
                 f'<div style="display:flex;gap:110px;align-items:flex-end;margin-top:60px">{row}'
                 f'<div style="margin-left:40px">{words}</div></div>')


def colors_slide():
    groups = [
        ("Основной", [("Color/Primary · Эспрессо", "espresso", "RGB 59 36 24 · CMYK 0 39 59 77")]),
        ("Дополнительные", [("Color/Secondary/Latte", "latte", "RGB 234 220 200"),
                            ("Color/Secondary/Kraft", "kraft", "RGB 201 162 126")]),
        ("Акцентный", [("Color/Accent · Терракота", "terracotta", "RGB 196 97 58 · CMYK 0 51 70 23")]),
        ("Нейтральные", [("Neutral/Milk", "milk", "фон"), ("Neutral/Graphite", "graphite", "текст"),
                         ("Neutral/Gray", "gray", "подписи"), ("Neutral/White", "white", "")]),
    ]
    cols = ""
    for g, items in groups:
        cards = "".join(f'<div style="margin-bottom:18px"><div style="height:{150 if len(items) < 3 else 64}px;background:{C[k]};border-radius:20px;'
                        f'box-shadow:inset 0 0 0 1px rgba(0,0,0,.08)"></div><div style="font-weight:700;margin-top:10px;font-size:17px">{n}</div>'
                        f'<div class="cap" style="margin-top:2px;font-size:15px">{C[k]} · {d}</div></div>' for n, k, d in items)
        cols += f'<div><div class="h2" style="font-size:19px;margin-bottom:18px">{g}</div>{cards}</div>'
    prop = "".join(f'<div style="flex:{f};background:{C[k]}"></div>' for k, f in
                   [("milk", 40), ("latte", 20), ("espresso", 25), ("kraft", 8), ("terracotta", 7)])
    return slide(5, "05 · Color & Typo", "Цвета: тепло обжарки",
                 f'<div class="grid" style="grid-template-columns:repeat(4,1fr);margin-top:36px">{cols}</div>'
                 f'<div style="display:flex;height:40px;border-radius:12px;overflow:hidden;margin-top:6px;border:1px solid #d9cbb8">{prop}</div>'
                 f'<div class="cap">Пропорции в макетах: 40% молоко · 20% латте · 25% эспрессо · 8% крафт · 7% терракота (только акценты и CTA)</div>')


def typo_slide():
    st = [("Text/H1", "Unbounded Bold 64 / 110%", "font-family:Unbounded;font-weight:700;font-size:64px;line-height:1.1;color:" + C["espresso"], "Обжариваем сами"),
          ("Text/H2", "Unbounded SemiBold 32 / 120%", "font-family:Unbounded;font-weight:600;font-size:32px;color:" + C["espresso"], "Эфиопия Иргачефф"),
          ("Text/Body", "Manrope Regular 18 / 155%", "font-size:18px;line-height:1.55", "Мытая обработка, светлая обжарка. Во вкусе — жасмин, бергамот и персик. Лучше всего раскрывается в воронке V60."),
          ("Text/Caption", "Manrope Medium 13 / 140%, капс +8%", "font-size:13px;font-weight:500;letter-spacing:1px;text-transform:uppercase;color:" + C["gray"], "Обжарено 24.10 · 250 г · фильтр"),
          ("Text/Accent", "Caveat Bold 40", "font-family:Caveat;font-weight:700;font-size:40px;color:" + C["terracotta"], "с любовью, ваш обжарщик")]
    rows = "".join(f'<div style="display:grid;grid-template-columns:300px 1fr;gap:40px;padding:20px 0;border-top:1px solid #e2d6c6;align-items:center">'
                   f'<div><div style="font-weight:700">{n}</div><div class="cap" style="margin-top:4px">{d}</div></div><div style="{s}">{t}</div></div>'
                   for n, d, s, t in st)
    alph = (f'<div class="card" style="width:520px"><div style="font-family:Unbounded;font-weight:700;font-size:120px;color:{C["espresso"]};line-height:1">Аа</div>'
            f'<div style="font-family:Unbounded;font-size:20px;margin:14px 0 26px;color:{C["espresso"]}">АБВГДЕЁЖЗИЙКЛМН<br>ОПРСТУФХЦЧШЩЭЮЯ 0123456789</div>'
            f'<div style="font-size:120px;line-height:1;color:{C["graphite"]}">Аа</div>'
            f'<div style="font-size:20px;margin-top:14px">абвгдеёжзийклмнопрстуфхцчшщъыьэюя<br>Regular · <b>Bold</b> · <span style="font-weight:500">Medium</span></div>'
            f'<div class="cap">Все шрифты — Google Fonts (OFL), бесплатны для коммерции, есть кириллица.</div></div>')
    return slide(6, "06 · Color & Typo", "Типографика",
                 f'<div style="display:flex;gap:70px;margin-top:40px"><div style="flex:1">{rows}</div>{alph}</div>')


def elements_slide():
    ic = "".join(f'<div style="text-align:center">{icon(n, C["espresso"], 64)}<div class="cap" style="font-size:14px">{n}</div></div>' for n in ICONS)
    pats = "".join(f'<div style="height:300px;border-radius:24px;overflow:hidden"><img src="{uri(pattern_svg(560, 300, bg, fg, d))}" style="width:100%;height:100%"></div>'
                   for bg, fg, d in [(C["latte"], C["terracotta"], C["espresso"]), (C["espresso"], "#5a3a28", C["terracotta"]),
                                     (C["kraft"], C["espresso"], C["milk"])])
    line = (f'<svg width="760" height="60" viewBox="0 0 760 60"><path d="M0 30 C120 0 240 60 380 30 S640 0 760 30" fill="none" '
            f'stroke="{C["terracotta"]}" stroke-width="3" stroke-dasharray="1 12" stroke-linecap="round"/></svg>')
    return slide(7, "07 · Графические элементы", "Паттерн, иконки, линии",
                 f'<div class="grid" style="grid-template-columns:repeat(3,1fr);margin-top:50px">{pats}</div>'
                 f'<div style="display:flex;justify-content:space-between;align-items:flex-end;margin-top:50px">'
                 f'<div><div class="h2" style="font-size:20px;margin-bottom:24px">Иконки — линия 2.6 px, скруглённые концы</div>'
                 f'<div style="display:flex;gap:44px">{ic}</div></div>'
                 f'<div><div class="h2" style="font-size:20px;margin-bottom:14px">«Ароматная» линия</div>{line}'
                 f'<div class="cap">пунктир-«пар»: разделитель секций, подчёркивания</div></div></div>')


def voice_slide():
    kw = "".join(f'<div style="background:{C["espresso"]};color:{C["latte"]};font-family:Unbounded;font-weight:600;font-size:26px;padding:20px 34px;border-radius:60px">{k}</div>'
                 for k in ["экспертно", "тепло", "без снобизма"])
    ph = [("Слоган", "Обжариваем сами. Отвечаем за каждое зерно."),
          ("Описание", "Мы знаем фермера по имени, обжариваем по вторникам и расскажем, почему этот кофе пахнет черникой."),
          ("Призыв к действию", "Загляните на дегустацию в четверг — сравним три способа заварить одну Колумбию."),
          ("Сайт / кнопка", "Выбрать зерно →")]
    rows = "".join(f'<div style="padding:22px 0;border-top:1px solid #e2d6c6"><div class="kicker" style="margin-bottom:8px;font-size:13px">{a}</div>'
                   f'<div style="font-size:30px;font-weight:500;color:{C["espresso"]}">«{b}»</div></div>' for a, b in ph)
    dont = (f'<div class="card" style="width:520px"><div class="h2" style="font-size:20px;margin-bottom:16px">Так не говорим ✕</div>'
            f'<div class="body" style="font-size:19px;color:{C["gray"]}">«Самый вкусный кофе в городе!!!»<br>«Купи 2 — получи 3!»<br>«Ароматный бодрящий напиток»</div>'
            f'<div class="h2" style="font-size:20px;margin:26px 0 16px">Так говорим ✓</div>'
            f'<div class="body" style="font-size:19px">Конкретно: страна, обработка, ноты, способ заваривания. На «вы», но без канцелярита.</div></div>')
    return slide(8, "08 · Тон голоса", "Говорим как бариста-друг",
                 f'<div style="display:flex;gap:18px;margin:40px 0 20px">{kw}</div>'
                 f'<div style="display:flex;gap:70px"><div style="flex:1">{rows}</div>{dont}</div>')


# --- носители ---

def bcard(dark):
    bg, fg = (C["espresso"], C["latte"]) if dark else (C["milk"], C["espresso"])
    logo = "r00ast-logo-on-dark.svg" if dark else "r00ast-logo-color.svg"
    return (f'<div style="width:1050px;height:585px;background:{bg};position:relative;overflow:hidden;font-family:Manrope;color:{fg}">'
            f'<img src="{L}{logo}" style="position:absolute;left:80px;top:80px;height:110px">'
            f'<div style="position:absolute;left:80px;bottom:80px;line-height:1.5">'
            f'<div style="font-family:Unbounded;font-weight:700;font-size:40px">Анна Беляева</div>'
            f'<div style="font-size:26px;color:{C["terracotta"]};font-weight:700;margin-bottom:22px">Q-грейдер, обжарщик</div>'
            f'<div style="font-size:26px">+7 900 000-00-13<br>hello@r00ast.coffee<br>ул. Обжарочная, 13</div></div>'
            f'<div style="position:absolute;right:0;top:0;width:300px;height:100%">'
            f'<img src="{uri(pattern_svg(300, 585, C["terracotta"] if dark else C["latte"], "#a94f2c" if dark else C["terracotta"], fg))}" style="width:100%;height:100%"></div></div>')


def letterhead():
    return (f'<div style="width:794px;height:1123px;background:#fff;position:relative;font-family:Manrope;color:{C["graphite"]}">'
            f'<div style="height:10px;background:{C["terracotta"]}"></div>'
            f'<img src="{L}r00ast-logo-color.svg" style="position:absolute;left:64px;top:56px;height:62px">'
            f'<div style="position:absolute;right:64px;top:62px;text-align:right;font-size:11px;line-height:1.6;color:{C["gray"]}">'
            f'ООО «Р00аст» · ИНН 0000000013<br>ул. Обжарочная, 13 · +7 900 000-00-13<br>hello@r00ast.coffee · r00ast.coffee</div>'
            f'<svg style="position:absolute;left:64px;top:140px" width="666" height="20"><path d="M0 10 C110 0 220 20 333 10 S556 0 666 10" fill="none" stroke="{C["terracotta"]}" stroke-width="2" stroke-dasharray="1 9" stroke-linecap="round"/></svg>'
            f'<div style="position:absolute;left:64px;top:200px;width:666px;font-size:13px;line-height:1.7">'
            f'<div style="color:{C["gray"]};margin-bottom:28px">26 октября 2026 · Исх. № 13</div>'
            f'<div style="font-family:Unbounded;font-weight:700;font-size:22px;color:{C["espresso"]};margin-bottom:18px">Коммерческое предложение на поставку зерна</div>'
            f'<p style="margin-bottom:12px">Здравствуйте! Предлагаем свежую обжарку зерна прямых поставок для вашего заведения: эспрессо-смесь «Терракота» и сезонные моносорта под фильтр.</p>'
            f'<p style="margin-bottom:12px">Обжариваем каждый вторник и отгружаем не позднее 72 часов после обжарки. Для партнёров — бесплатное обучение бариста и калибровка оборудования.</p>'
            f'<p>Будем рады пригласить вас на дегустацию.</p>'
            f'<div style="font-family:Caveat;font-weight:700;font-size:32px;color:{C["terracotta"]};margin-top:40px">Анна Беляева</div>'
            f'<div style="font-size:12px;color:{C["gray"]}">Q-грейдер, обжарщик R00ast</div></div>'
            f'<div style="position:absolute;left:0;right:0;bottom:0;height:70px;overflow:hidden">'
            f'<img src="{uri(pattern_svg(794, 70, C["latte"], C["terracotta"], C["espresso"]))}" style="width:100%;height:100%"></div></div>')


def stationery_slide():
    return slide(9, "09 · Stationery", "Визитки и бланк",
                 f'<div style="display:flex;gap:60px;margin-top:46px;align-items:flex-start">'
                 f'<div><div style="zoom:.55;box-shadow:0 20px 50px rgba(59,36,24,.2)">{bcard(False)}</div>'
                 f'<div style="zoom:.55;margin-top:50px;box-shadow:0 20px 50px rgba(59,36,24,.2)">{bcard(True)}</div>'
                 f'<div class="cap">Визитка 90×50 мм (1050×585 px @300 dpi) — светлая и тёмная</div></div>'
                 f'<div style="zoom:.64;box-shadow:0 20px 50px rgba(59,36,24,.2)">{letterhead()}</div>'
                 f'<div class="cap" style="align-self:flex-end;width:160px">Бланк A4<br>210×297 мм</div></div>')


# --- мокапы (векторные) ---

def coffee_bag(origin, notes, tint):
    kr = uri(noise_texture(C["kraft"], 400, 560, .9, .4, True, "bag" + tint[1:]))
    return (f'<div style="width:380px;height:540px;position:relative">'
            f'<div style="position:absolute;inset:0;background:url(\'{kr}\') center/cover;clip-path:polygon(4% 0,96% 0,100% 100%,0 100%);'
            f'border-radius:6px;box-shadow:inset -40px 0 60px rgba(0,0,0,.15),inset 30px 0 40px rgba(255,255,255,.12)"></div>'
            f'<div style="position:absolute;left:15px;right:15px;top:18px;height:22px;border-top:3px dashed rgba(59,36,24,.25)"></div>'
            f'<div style="position:absolute;left:46px;right:46px;top:120px;bottom:60px;background:#fff;border-radius:10px;padding:26px 24px;box-shadow:0 2px 6px rgba(0,0,0,.12)">'
            f'<img src="{L}r00ast-logo-color.svg" style="height:46px;margin-left:-6px">'
            f'<div style="height:6px;background:{tint};margin:16px 0 18px;border-radius:3px"></div>'
            f'<div style="font-family:Unbounded;font-weight:700;font-size:24px;color:{C["espresso"]};line-height:1.15">{origin}</div>'
            f'<div style="font-size:14px;color:{C["gray"]};margin:10px 0 14px;letter-spacing:1px;text-transform:uppercase">мытая · 1950 м</div>'
            f'<div style="font-family:Caveat;font-weight:700;font-size:28px;color:{C["terracotta"]};line-height:1.05">{notes}</div>'
            f'<div style="position:absolute;left:24px;right:24px;bottom:22px;display:flex;justify-content:space-between;font-size:12px;font-weight:700;color:{C["espresso"]}">'
            f'<span>250 г · ФИЛЬТР</span><span>обжарено __.__</span></div></div></div>')


def cup():
    return (f'<div style="width:300px;height:460px;position:relative">'
            f'<div style="position:absolute;left:0;right:0;top:0;height:40px;background:{C["espresso"]};border-radius:14px 14px 6px 6px"></div>'
            f'<div style="position:absolute;left:12px;right:12px;top:36px;bottom:0;background:#fff;clip-path:polygon(0 0,100% 0,88% 100%,12% 100%);'
            f'box-shadow:inset -40px 0 40px rgba(0,0,0,.08)"></div>'
            f'<div style="position:absolute;left:30px;right:30px;top:170px;height:150px;clip-path:polygon(0 0,100% 0,95% 100%,5% 100%);overflow:hidden">'
            f'<img src="{uri(pattern_svg(240, 150, C["terracotta"], "#a94f2c", C["latte"]))}" style="width:100%;height:100%"></div>'
            f'<img src="{L}r00ast-icon-color.svg" style="position:absolute;left:105px;top:205px;width:90px">'
            f'<img src="{L}r00ast-logo-color.svg" style="position:absolute;left:78px;top:100px;width:144px"></div>')


def apron():
    e, k = C["espresso"], C["kraft"]
    return (f'<div style="width:330px;height:470px;position:relative">'
            f'<svg width="330" height="470" viewBox="-30 -60 390 530">'
            f'<path d="M70 20 Q165 -110 260 20" stroke="{k}" stroke-width="10" fill="none"/>'
            f'<path d="M-25 175 L10 165 M355 175 L320 165" stroke="{k}" stroke-width="10" stroke-linecap="round"/>'
            f'<path d="M60 20 L270 20 L270 60 Q280 120 330 150 L330 470 L0 470 L0 150 Q50 120 60 60Z" fill="{e}"/>'
            f'<rect x="80" y="320" width="170" height="100" rx="6" fill="none" stroke="{C["latte"]}" stroke-width="2" stroke-dasharray="6 6"/></svg>'
            f'<img src="{L}r00ast-logo-on-dark.svg" style="position:absolute;left:92px;top:175px;width:146px">'
            f'<div style="position:absolute;left:0;right:0;top:232px;text-align:center;font-family:Caveat;font-weight:700;font-size:26px;color:{k}">бариста</div></div>')


def loyalty():
    stamps = "".join(f'<div style="width:62px;height:62px;border-radius:50%;border:2px dashed {C["kraft"]};display:flex;align-items:center;justify-content:center">'
                     + (f'<img src="{L}r00ast-icon-light.svg" style="width:56px">' if i < 5 else "") + "</div>" for i in range(8))
    return (f'<div style="width:510px;height:320px;background:{C["espresso"]};border-radius:22px;padding:30px 34px;position:relative;color:{C["latte"]};box-shadow:0 20px 40px rgba(0,0,0,.25)">'
            f'<div style="display:flex;justify-content:space-between;align-items:center"><img src="{L}r00ast-logo-on-dark.svg" style="height:40px">'
            f'<span style="font-family:Unbounded;font-size:12px;letter-spacing:3px">КАРТА ГОСТЯ</span></div>'
            f'<div style="display:grid;grid-template-columns:repeat(4,62px);gap:16px 28px;margin-top:30px">{stamps}</div>'
            f'<div style="font-family:Caveat;font-weight:700;font-size:26px;color:{C["terracotta"]};position:absolute;right:34px;bottom:24px">8-й — за наш счёт</div></div>')


def menu():
    def sec(t, items):
        rows = "".join(f'<div style="display:flex;justify-content:space-between;font-weight:700;font-size:16px;margin-top:10px"><span>{a}</span><span>{p}</span></div>'
                       f'<div style="font-size:12px;color:{C["gray"]}">{d}</div>' for a, d, p in items)
        return f'<div style="margin-top:22px"><div class="kicker" style="margin-bottom:4px;font-size:12px">{t}</div>{rows}</div>'
    return (f'<div style="width:400px;height:600px;background:{C["milk"]};border-radius:10px;padding:34px;color:{C["espresso"]};box-shadow:0 20px 40px rgba(59,36,24,.2)">'
            f'<img src="{L}r00ast-logo-color.svg" style="height:40px">'
            + sec("Эспрессо-карта", [("Эспрессо", "смесь «Терракота»: какао, орех, карамель", "160"),
                                     ("Капучино", "молоко 3,2% или овсяное", "240"), ("Флэт уайт", "двойной эспрессо", "260")])
            + sec("Фильтр-кофе", [("V60 · Эфиопия", "жасмин · бергамот · персик", "320"),
                                  ("Аэропресс · Колумбия", "красное яблоко · тростниковый сахар", "300")])
            + sec("Десерты", [("Баскский чизкейк", "", "290"), ("Канеле", "", "180")])
            + f'<div class="hand" style="font-size:24px;margin-top:20px">спросите про лот дня</div></div>')


def sign():
    brick = uri(noise_texture("#8a5a44", 900, 520, 1.2, .35, False, "br"))
    return (f'<div style="width:880px;height:520px;position:relative;background:url(\'{brick}\') center/cover;border-radius:18px;overflow:hidden">'
            f'<div style="position:absolute;left:70px;right:250px;top:70px;height:150px;background:{C["espresso"]};border-radius:8px;display:flex;align-items:center;justify-content:center;box-shadow:0 14px 30px rgba(0,0,0,.4)">'
            f'<img src="{L}r00ast-logo-on-dark.svg" style="height:100px"></div>'
            f'<div style="position:absolute;right:60px;top:50px;width:150px;height:150px;border-radius:50%;box-shadow:0 0 40px rgba(255,190,120,.6),0 14px 30px rgba(0,0,0,.4)">'
            f'<img src="{L}r00ast-icon-color.svg" style="width:150px"></div>'
            f'<div style="position:absolute;left:70px;right:70px;bottom:0;height:230px;background:linear-gradient(#1b120c,#2e1d12);border-radius:8px 8px 0 0;'
            f'border:10px solid {C["espresso"]};border-bottom:0"><div style="color:{C["latte"]};font-family:Caveat;font-weight:700;font-size:44px;padding:40px 50px;opacity:.9">обжариваем сами · с 8:00</div></div></div>')


def mockup_slide1():
    bags = (coffee_bag("Эфиопия<br>Иргачефф", "жасмин,<br>бергамот, персик", C["terracotta"])
            + coffee_bag("Колумбия<br>Уила", "красное яблоко,<br>тростниковый сахар", C["espresso"]))
    return slide(10, "10 · Носители", "Упаковка зерна и стаканы",
                 f'<div style="display:flex;gap:60px;margin-top:50px;align-items:flex-end">{bags}'
                 f'<div style="display:flex;gap:40px;align-items:flex-end">{cup()}<div style="transform:scale(.72);transform-origin:bottom">{cup()}</div></div></div>'
                 f'<div class="cap" style="margin-top:20px">Крафт-пакет с белой этикеткой: цветная полоса кодирует обжарку (терракота — фильтр, эспрессо — эспрессо). Стакан — паттерн-рукав + знак «00».</div>',
                 bg=C["latte"])


def mockup_slide2():
    return slide(11, "11 · Носители", "Униформа, меню, карта, вывеска",
                 f'<div style="display:flex;gap:56px;margin-top:40px;align-items:flex-start">'
                 f'<div style="padding:30px 40px 0">{apron()}</div>{menu()}'
                 f'<div style="display:flex;flex-direction:column;gap:40px">{loyalty()}<div style="zoom:.6">{sign()}</div></div></div>',
                 bg=C["latte"])


def guide_logo_slide():
    clear = (f'<div style="position:relative;display:inline-block;padding:60px;background:#fff;outline:2px dashed {C["terracotta"]};outline-offset:-1px">'
             f'<img src="{L}r00ast-logo-color.svg" style="height:120px;display:block;outline:1px solid #e2d6c6">'
             f'<div style="position:absolute;left:8px;top:8px;font-family:Caveat;font-weight:700;font-size:26px;color:{C["terracotta"]}">X = высота «R»/2</div></div>')
    bad = [("filter:hue-rotate(140deg)", "Не меняйте цвета"), ("transform:scaleX(1.5)", "Не растягивайте"),
           ("transform:rotate(-12deg)", "Не поворачивайте"), ("filter:drop-shadow(6px 6px 2px #000)", "Без теней и эффектов")]
    bads = "".join(f'<div><div style="height:150px;background:#fff;border-radius:18px;display:flex;align-items:center;justify-content:center;overflow:hidden;position:relative">'
                   f'<img src="{L}r00ast-logo-color.svg" style="height:46px;{s}"><div style="position:absolute;right:12px;top:6px;color:#c0392b;font-size:30px;font-weight:700">✕</div></div>'
                   f'<div class="cap">{t}</div></div>' for s, t in bad)
    bads += (f'<div><div style="height:150px;background:url(\'{uri(bean_pile(400, 200, 80))}\') center/cover;border-radius:18px;display:flex;align-items:center;justify-content:center;position:relative">'
             f'<img src="{L}r00ast-logo-color.svg" style="height:46px"><div style="position:absolute;right:12px;top:6px;color:#c0392b;font-size:30px;font-weight:700">✕</div></div>'
             f'<div class="cap">Не ставьте на пёстрый фон без подложки</div></div>')
    good = (f'<div><div style="height:150px;background:{C["espresso"]};border-radius:18px;display:flex;align-items:center;justify-content:center;position:relative">'
            f'<img src="{L}r00ast-logo-on-dark.svg" style="height:46px"><div style="position:absolute;right:12px;top:6px;color:#3aa66b;font-size:30px;font-weight:700">✓</div></div>'
            f'<div class="cap">Правильно: фирменный фон, контраст</div></div>')
    return slide(12, "12 · Guidelines", "Правила логотипа",
                 f'<div style="display:flex;gap:80px;margin-top:46px">'
                 f'<div><div class="h2" style="font-size:20px;margin-bottom:20px">Охранное поле</div>{clear}'
                 f'<div class="body" style="font-size:18px;margin-top:26px;width:560px">Вокруг логотипа — свободное поле не меньше X (половина высоты «R»). '
                 f'<b>Мин. размер:</b> логотип — 24 px / 15 мм по ширине; знак «00» — 16 px / 6 мм.</div></div>'
                 f'<div style="flex:1"><div class="h2" style="font-size:20px;margin-bottom:20px">Правильно / неправильно</div>'
                 f'<div class="grid" style="grid-template-columns:repeat(3,1fr);gap:22px">{good}{bads}</div></div></div>')


def guide_summary_slide():
    blocks = [
        ("Логотип", "Основная версия — цветная на молочном/белом. На тёмном — латте + терракота или белая. Знак «00» — для аватаров, стаканов, фавикона. Охранное поле X, минимум 24 px."),
        ("Цвета", f"Эспрессо {C['espresso']} · Терракота {C['terracotta']} · Латте {C['latte']} · Крафт {C['kraft']} · Молоко {C['milk']} · Графит {C['graphite']}. Терракота — только акценты и кнопки."),
        ("Шрифты", "Unbounded — заголовки и логотип; Manrope — основной текст, меню, интерфейс; Caveat — короткие рукописные акценты (не более 1 на макет)."),
        ("Тон голоса", "Экспертно · тепло · без снобизма. Конкретика о зерне вместо превосходных степеней."),
    ]
    cards = "".join(f'<div class="card" style="height:330px"><div class="kicker">{a}</div><div class="body" style="font-size:21px">{b}</div></div>' for a, b in blocks)
    return slide(13, "13 · Guidelines", "Коротко о главном",
                 f'<div class="grid" style="grid-template-columns:repeat(2,1fr);margin-top:50px">{cards}</div>')


def cover_slide():
    pat = uri(pattern_svg(1920, 1080, C["espresso"], "#4a2e1f", C["terracotta"]))
    return (f'<section class="slide" style="background:url(\'{pat}\') center/cover;display:flex;flex-direction:column;align-items:center;justify-content:center">'
            f'<img src="{L}r00ast-logo-on-dark.svg" style="height:200px">'
            f'<div style="font-family:Caveat;font-weight:700;font-size:56px;color:{C["latte"]};margin-top:20px">обжариваем сами</div>'
            f'<div style="position:absolute;bottom:60px;font-family:Unbounded;font-size:16px;letter-spacing:6px;color:{C["kraft"]}">BRAND BOOK · 2026</div></section>')


SLIDES = [cover_slide, brief_slide, concepts_slide, logo_final_slide, sizes_slide, colors_slide, typo_slide,
          elements_slide, voice_slide, stationery_slide, mockup_slide1, mockup_slide2, guide_logo_slide, guide_summary_slide]

SLIDE_NAMES = ["00-cover", "01-brief", "02-logo-concepts", "03-logo-final", "04-logo-sizes", "05-colors", "06-typography",
               "07-elements", "08-tone-of-voice", "09-stationery", "10-mockups-packaging", "11-mockups-merch",
               "12-guidelines-logo", "13-guidelines-summary"]

if __name__ == "__main__":
    HTML.mkdir(exist_ok=True)
    jobs = []

    def emit(name, html, out, w, h, scale=1):
        (HTML / f"{name}.html").write_text(html, encoding="utf-8")
        jobs.append({"html": f"{name}.html", "out": out, "w": w, "h": h, "scale": scale})

    emit("moodboard", moodboard(), "moodboard/r00ast-moodboard.png", 1920, 1080)
    built = []
    for name, fn in zip(SLIDE_NAMES, SLIDES):
        s = fn()
        built.append(s)
        emit(name, page(name, s), f"brandbook/{name}.png", 1920, 1080)
    (HTML / "brandbook.html").write_text(
        page("R00ast Brand Book", "".join(built), "@page{size:1920px 1080px;margin:0}"), encoding="utf-8")
    emit("card-light", page("card", bcard(False), w=1050, h=585), "stationery/business-card-light.png", 1050, 585)
    emit("card-dark", page("card", bcard(True), w=1050, h=585), "stationery/business-card-dark.png", 1050, 585)
    emit("letterhead", page("A4", letterhead(), w=794, h=1123), "stationery/letterhead-a4.png", 794, 1123, 3.125)
    for n, html, w, h in [("bag", coffee_bag("Эфиопия<br>Иргачефф", "жасмин,<br>бергамот, персик", C["terracotta"]), 380, 540),
                          ("cup", cup(), 300, 460), ("apron", apron(), 330, 470), ("loyalty-card", loyalty(), 510, 320),
                          ("menu", menu(), 400, 600), ("signboard", sign(), 880, 520)]:
        wrap = f'<div style="padding:60px;background:{C["latte"]};display:inline-block">{html}</div>'
        emit(f"mock-{n}", page(n, wrap, "body{background:" + C["latte"] + "}", w=w + 120, h=h + 120),
             f"mockups/{n}.png", w + 120, h + 120, 2)
    (HTML / "manifest.json").write_text(json.dumps(jobs, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(jobs), "pages")
