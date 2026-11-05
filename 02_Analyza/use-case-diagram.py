"""Use case diagram systému Bleskovka.

Zdroj údajov: use-case.docx (UC-001 až UC-030) a ../01_Poziadavky/role-systemu.xlsx.
Skript vygeneruje use-case-diagram.svg a (ak je dostupný rsvg-convert)
use-case-diagram.png.

Diagram je kvôli prehľadnosti rozdelený na dve časti toho istého systému:
  a) správa kvízov, účtov a administrácia,
  b) priebeh hry.
Aktér Hostiteľ je ten istý aktér zobrazený v oboch častiach.

Spustenie:  python3 use-case-diagram.py
Úprava:     zmeň zoznamy PANELY / VZTAHY nižšie a spusti skript znova.
"""
import math
import pathlib
import shutil
import subprocess

ADRESAR = pathlib.Path(__file__).resolve().parent

NAZVY = {
    "UC-001": "Vytvor kvíz",
    "UC-002": "Uprav otázku v kvíze",
    "UC-003": "Ulož kvíz",
    "UC-004": "Spravuj uložené kvízy",
    "UC-005": "Skopíruj kvíz",
    "UC-006": "Pridaj obrázok k otázke",
    "UC-007": "Importuj otázky zo súboru",
    "UC-008": "Zaregistruj hostiteľa",
    "UC-009": "Prihlás hostiteľa",
    "UC-010": "Odstráň nevhodný kvíz",
    "UC-011": "Zablokuj účet hostiteľa",
    "UC-012": "Vytvor hru",
    "UC-013": "Zobraz čakáreň",
    "UC-014": "Pripoj sa do hry",
    "UC-015": "Odstráň hráča z čakárne",
    "UC-016": "Spusti hru",
    "UC-017": "Odpovedz na otázku",
    "UC-018": "Sleduj priebeh otázky",
    "UC-019": "Ukonči otázku",
    "UC-020": "Vyhodnoť otázku",
    "UC-021": "Zobraz výsledok otázky hráčovi",
    "UC-022": "Pokračuj na ďalšiu otázku",
    "UC-023": "Pozastav hru",
    "UC-024": "Nastav automatické pokračovanie",
    "UC-025": "Zobraz záverečné poradie",
    "UC-026": "Exportuj výsledky hry",
    "UC-027": "Zobraz históriu hier",
    "UC-028": "Ukonči hru",
    "UC-029": "Vráť sa do hry po výpadku",
    "UC-030": "Obnov rozohranú hru",
}

# Aktéri a ich use cases (primárni aj sekundárni, podľa sekcie „Aktéri“ v use-case.docx)
HOSTITEL = ["UC-001", "UC-002", "UC-003", "UC-004", "UC-005", "UC-006", "UC-007",
            "UC-008", "UC-009", "UC-012", "UC-013", "UC-014", "UC-015", "UC-016",
            "UC-018", "UC-019", "UC-020", "UC-022", "UC-023", "UC-024", "UC-025",
            "UC-026", "UC-027", "UC-028", "UC-030"]
HRAC = ["UC-013", "UC-014", "UC-015", "UC-016", "UC-017", "UC-019", "UC-020",
        "UC-021", "UC-022", "UC-023", "UC-025", "UC-028", "UC-029", "UC-030"]
SPRAVCA = ["UC-010", "UC-011"]

# (odkiaľ, kam, stereotyp) – «include»: základný -> zahrnutý,
#                           «extend»: rozširujúci -> základný
VZTAHY = [
    ("UC-012", "UC-013", "include"),   # UC-012 krok 5
    ("UC-019", "UC-020", "include"),   # UC-019 krok 4
    ("UC-020", "UC-021", "include"),   # UC-020 krok 6
    ("UC-005", "UC-004", "extend"),    # UC-004 alt. 4c
    ("UC-006", "UC-001", "extend"),
    ("UC-007", "UC-001", "extend"),
    ("UC-015", "UC-013", "extend"),
    ("UC-024", "UC-013", "extend"),
    ("UC-025", "UC-022", "extend"),    # UC-022 alt. 2a (posledná otázka)
    ("UC-026", "UC-025", "extend"),
]

# Rozloženie: každý panel má stĺpce use cases a aktérov vľavo / vpravo
PANELY = [
    {
        "nadpis": "a) Správa kvízov, účtov a administrácia",
        "stlpce": [
            ["UC-008", "UC-009", "UC-006", "UC-001", "UC-007",
             "UC-002", "UC-003", "UC-004", "UC-005", "UC-027"],
            ["UC-010", "UC-011"],
        ],
        "vlavo": "Hostiteľ",
        "vpravo": "Správca",
    },
    {
        "nadpis": "b) Priebeh hry",
        "stlpce": [
            ["UC-012", "UC-013", "UC-015", "UC-024", "UC-014", "UC-016",
             "UC-017", "UC-018", "UC-019", "UC-020", "UC-021", "UC-022",
             "UC-025", "UC-026", "UC-023", "UC-028", "UC-029", "UC-030"],
        ],
        "vlavo": "Hostiteľ",
        "vpravo": "Hráč",
        "okraj": 150,      # miesto pre oblúk «extend» UC-024 -> UC-013
    },
]
AKTERI = {"Hostiteľ": HOSTITEL, "Hráč": HRAC, "Správca": SPRAVCA}

RX, RY = 152, 25          # polosi elipsy
KROK = 84                 # zvislá vzdialenosť use cases
ODSTUP_AKTERA = 380       # vodorovná vzdialenosť aktéra od stĺpca
FONT = "DejaVu Sans, Arial, sans-serif"
MODRA = "#1F5FA8"


def esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def bod_na_elipse(cx, cy, k_x, k_y):
    """Bočný vrchol elipsy na strane aktéra – čiara tak nikdy nepretne stĺpec."""
    return (cx - RX, cy) if k_x < cx else (cx + RX, cy)


def panacik(cx, cy, meno):
    """UML aktér; (cx, cy) = stred tela, kam vedú asociácie."""
    s = 'stroke="#222" stroke-width="2.2" fill="none" stroke-linecap="round"'
    return (f'<circle cx="{cx}" cy="{cy - 38}" r="11" stroke="#222" stroke-width="2.2" fill="#fff"/>'
            f'<line x1="{cx}" y1="{cy - 27}" x2="{cx}" y2="{cy + 12}" {s}/>'
            f'<line x1="{cx - 20}" y1="{cy - 14}" x2="{cx + 20}" y2="{cy - 14}" {s}/>'
            f'<line x1="{cx}" y1="{cy + 12}" x2="{cx - 15}" y2="{cy + 38}" {s}/>'
            f'<line x1="{cx}" y1="{cy + 12}" x2="{cx + 15}" y2="{cy + 38}" {s}/>'
            f'<text x="{cx}" y="{cy + 60}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="15" font-weight="bold" fill="#222">{esc(meno)}</text>')


def sipka(x1, y1, x2, y2):
    """Otvorená hrot šípky v bode (x2, y2)."""
    u = math.atan2(y2 - y1, x2 - x1)
    a = (x2 - 10 * math.cos(u - 0.45), y2 - 10 * math.sin(u - 0.45))
    b = (x2 - 10 * math.cos(u + 0.45), y2 - 10 * math.sin(u + 0.45))
    return (f'<polyline points="{a[0]:.1f},{a[1]:.1f} {x2:.1f},{y2:.1f} {b[0]:.1f},{b[1]:.1f}" '
            f'fill="none" stroke="{MODRA}" stroke-width="1.6"/>')


def vykresli():
    casti = []
    pozicie = {}          # UC -> (cx, cy)
    x_panel = 40
    y_hore = 150
    vyska_max = max(len(s) for p in PANELY for s in p["stlpce"]) * KROK
    pozadie, popredie = [], []

    for p in PANELY:
        sirka_stlpcov = len(p["stlpce"]) * (2 * RX + 70) - 70
        x_hranica = x_panel + ODSTUP_AKTERA - RX - 60
        x_stlpec = x_hranica + 40 + RX
        vyska = max(len(s) for s in p["stlpce"]) * KROK
        hranica_w = sirka_stlpcov + 40 + p.get("okraj", 40)
        hranica_h = vyska + 70
        stred_y = y_hore + 50 + vyska / 2

        # hranica systému
        pozadie.append(
            f'<rect x="{x_hranica}" y="{y_hore}" width="{hranica_w}" height="{hranica_h}" '
            f'rx="14" fill="#FAFAFA" stroke="#333" stroke-width="1.6"/>'
            f'<text x="{x_hranica + 14}" y="{y_hore + 26}" font-family="{FONT}" font-size="16" '
            f'font-weight="bold" fill="#333">Systém Bleskovka</text>'
            f'<text x="{x_hranica + hranica_w / 2}" y="{y_hore - 18}" text-anchor="middle" '
            f'font-family="{FONT}" font-size="18" fill="#111">{esc(p["nadpis"])}</text>')

        # use cases
        for i, stlpec in enumerate(p["stlpce"]):
            cx = x_stlpec + i * (2 * RX + 70)
            y0 = stred_y - (len(stlpec) - 1) * KROK / 2
            for j, uc in enumerate(stlpec):
                cy = y0 + j * KROK
                pozicie[uc] = (cx, cy)
                popredie.append(
                    f'<ellipse cx="{cx}" cy="{cy}" rx="{RX}" ry="{RY}" fill="#FFF8DC" '
                    f'stroke="#8A6D00" stroke-width="1.4"/>'
                    f'<text x="{cx}" y="{cy - 4}" text-anchor="middle" font-family="{FONT}" '
                    f'font-size="11" fill="#7A5C00">{uc}</text>'
                    f'<text x="{cx}" y="{cy + 13}" text-anchor="middle" font-family="{FONT}" '
                    f'font-size="13" fill="#111">{esc(NAZVY[uc])}</text>')

        uc_panelu = [u for s in p["stlpce"] for u in s]
        x_vlavo = x_hranica - 150
        x_vpravo = x_hranica + hranica_w + 150
        for meno, ax in ((p["vlavo"], x_vlavo), (p["vpravo"], x_vpravo)):
            moje = [u for u in uc_panelu if u in AKTERI[meno]]
            ay = sum(pozicie[u][1] for u in moje) / len(moje)
            for u in moje:
                ex, ey = bod_na_elipse(*pozicie[u], ax, ay)
                pozadie.append(f'<line x1="{ax}" y1="{ay}" x2="{ex:.1f}" y2="{ey:.1f}" '
                               f'stroke="#555" stroke-width="1.2"/>')
            popredie.append(panacik(ax, ay, meno))

        x_panel = x_vpravo + 60

    # vzťahy «include» / «extend»
    for z, k, typ in VZTAHY:
        (zx, zy), (kx, ky) = pozicie[z], pozicie[k]
        smer = 1 if ky > zy else -1
        if abs(ky - zy) <= KROK + 1:       # susedné – krátka zvislá šípka
            y1, y2 = zy + smer * RY, ky - smer * RY
            popredie.append(f'<line x1="{zx}" y1="{y1}" x2="{kx}" y2="{y2}" stroke="{MODRA}" '
                            f'stroke-width="1.6" stroke-dasharray="6,4"/>' + sipka(zx, y1, kx, y2))
            ly = (y1 + y2) / 2 + 4
            popredie.append(f'<text x="{zx + 8}" y="{ly}" font-family="{FONT}" font-size="11" '
                            f'fill="{MODRA}">«{typ}»</text>')
        else:                               # vzdialené – oblúk po pravej strane stĺpca
            x1, x2 = zx + RX * 0.55, kx + RX * 0.55
            y1 = zy - smer * RY * 0.84
            y2 = ky + smer * RY * 0.84
            bx = zx + RX + 60
            popredie.append(f'<path d="M{x1},{y1} C{bx},{y1} {bx},{y2} {x2},{y2}" fill="none" '
                            f'stroke="{MODRA}" stroke-width="1.6" stroke-dasharray="6,4"/>'
                            + sipka(bx - 20, y2, x2, y2))
            popredie.append(f'<text x="{bx + 6}" y="{(y1 + y2) / 2 + 4}" font-family="{FONT}" '
                            f'font-size="11" fill="{MODRA}" '
                            f'style="paint-order:stroke" stroke="#FAFAFA" stroke-width="4">«{typ}»</text>')

    sirka = x_panel
    vyska = y_hore + vyska_max + 70 + 70
    casti.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{sirka}" height="{vyska}" '
                 f'viewBox="0 0 {sirka} {vyska}">')
    casti.append(f'<rect width="100%" height="100%" fill="#fff"/>')
    casti.append(f'<text x="{sirka / 2}" y="52" text-anchor="middle" font-family="{FONT}" '
                 f'font-size="26" font-weight="bold" fill="#111">Bleskovka – use case diagram</text>')
    casti.extend(pozadie)
    casti.extend(popredie)
    casti.append(f'<text x="40" y="{vyska - 28}" font-family="{FONT}" font-size="12" fill="#555">'
                 'Obe časti zobrazujú ten istý systém; Hostiteľ je ten istý aktér. '
                 'Plná čiara = asociácia aktéra (primárneho aj sekundárneho), '
                 'prerušovaná šípka = «include» / «extend». Zdroj: use-case.docx.</text>')
    casti.append('</svg>')
    return "\n".join(casti)


def main():
    svg_cesta = ADRESAR / "use-case-diagram.svg"
    svg_cesta.write_text(vykresli(), encoding="utf-8")
    print("Hotovo:", svg_cesta)
    if shutil.which("rsvg-convert"):
        png = ADRESAR / "use-case-diagram.png"
        subprocess.run(["rsvg-convert", "--zoom=2", "-o", str(png), str(svg_cesta)], check=True)
        print("Hotovo:", png)
    else:
        print("rsvg-convert nie je nainštalovaný – PNG vytvor zo SVG ručne.")


if __name__ == "__main__":
    main()
