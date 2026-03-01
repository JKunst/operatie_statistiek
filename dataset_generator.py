"""
Dataset generator voor Operatie Sterfgeval.
Genereert een unieke .xlsx dataset per leerlingnummer (6 cijfers).
"""

import math
import io
from datetime import date, timedelta
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

# ── Configuratie ─────────────────────────────────────────────────────────────

ARTSEN = [
    {"naam": "Dr. E. Bakker",   "specialisme": "Interne geneeskunde", "code": "BAK"},
    {"naam": "Dr. R. Jansen",   "specialisme": "Interne geneeskunde", "code": "JAN"},
    {"naam": "Dr. S. Vermeer",  "specialisme": "Interne geneeskunde", "code": "VER"},
    {"naam": "Dr. M. de Vries", "specialisme": "Interne geneeskunde", "code": "DVR"},
]

VERPLEEGKUNDIGEN = [
    "A. Smits", "B. Peters", "C. Hendriks",
    "D. Wolters", "E. Claassen", "F. Mulder",
]

DIENSTEN = [
    {"naam": "Ochtenddienst", "start": "07:00", "eind": "15:00"},
    {"naam": "Middagdienst",  "start": "15:00", "eind": "23:00"},
    {"naam": "Nachtdienst",   "start": "23:00", "eind": "07:00"},
]

WEKEN = 12
START_DATUM = date(2024, 1, 8)
DAGNAMES = ["Maandag","Dinsdag","Woensdag","Donderdag","Vrijdag","Zaterdag","Zondag"]

# Sterftekansen
NORM_MIN, NORM_MAX = 0.014, 0.026
VERD_MIN, VERD_MAX = 0.058, 0.082

# Kleuren
K_DONKER  = "1A1410"
K_ROOD    = "8B1A1A"
K_KOPTEKST = "2C3E50"
K_GEEL    = "FFF3CD"
K_ROOD_RIJ = "FDECEA"
K_GROEN_RIJ = "EBF5EB"
K_GRIJS   = "F5F5F5"
K_LIJN    = "DDDDDD"
K_WIT     = "FFFFFF"
K_PAPER   = "FAF6EE"
K_GROEN   = "2D5016"


# ── Seeded random ─────────────────────────────────────────────────────────────

def _sr(seed, idx):
    x = math.sin(seed * 9301 + idx * 49297 + 233) * 10000
    return x - math.floor(x)

def _hash(ln_str):
    h = 0
    for ch in str(ln_str):
        h = ((h << 5) - h) + ord(ch)
        h &= 0xFFFFFFFF
    return h


# ── Stijlhelpers ──────────────────────────────────────────────────────────────

def _fill(hex_c):
    return PatternFill("solid", start_color=hex_c, fgColor=hex_c)

def _font(bold=False, size=10, color="000000", italic=False):
    return Font(name="Arial", bold=bold, size=size, color=color, italic=italic)

def _border():
    s = Side(style="thin", color=K_LIJN)
    return Border(left=s, right=s, top=s, bottom=s)

def _center():
    return Alignment(horizontal="center", vertical="center", wrap_text=True)

def _left():
    return Alignment(horizontal="left", vertical="center")

def _style_hdr(cell, bg=K_KOPTEKST, fg=K_WIT, size=10):
    cell.font = _font(True, size, fg)
    cell.fill = _fill(bg)
    cell.alignment = _center()
    cell.border = _border()

def _style_data(cell, bg=K_WIT, bold=False, align="left", fmt=None, size=9):
    cell.font = _font(bold, size)
    cell.fill = _fill(bg)
    cell.alignment = _center() if align == "center" else _left()
    cell.border = _border()
    if fmt:
        cell.number_format = fmt


# ── Data genereren ────────────────────────────────────────────────────────────

def _genereer_rijen(leerlingnummer):
    seed = _hash(str(leerlingnummer))
    verdachte_idx = seed % len(ARTSEN)
    rijen = []
    ri = 0  # row index voor seeded random

    for dag in range(WEKEN * 7):
        datum = START_DATUM + timedelta(days=dag)
        is_weekend = datum.weekday() >= 5
        min_pat = 7 if is_weekend else 10
        max_pat = 14 if is_weekend else 20

        for d_idx, dienst in enumerate(DIENSTEN):
            arts_idx = int(_sr(seed, ri) * len(ARTSEN)) % len(ARTSEN)
            ri += 1
            # Rotatiesysteem: arts wisselt per dag/dienst
            arts_idx = (dag * 3 + d_idx + arts_idx) % len(ARTSEN)
            arts = ARTSEN[arts_idx]
            is_verdacht = (arts_idx == verdachte_idx)

            vplk_idx = int(_sr(seed, ri) * len(VERPLEEGKUNDIGEN))
            ri += 1
            vplk = VERPLEEGKUNDIGEN[vplk_idx]

            n_pat = min_pat + int(_sr(seed, ri) * (max_pat - min_pat + 1))
            ri += 1

            if is_verdacht:
                kans = VERD_MIN + _sr(seed, ri) * (VERD_MAX - VERD_MIN)
            else:
                kans = NORM_MIN + _sr(seed, ri) * (NORM_MAX - NORM_MIN)
            ri += 1

            overlijden = sum(1 for p in range(n_pat) if _sr(seed, ri + p) < kans)
            ri += n_pat

            ontslag_kans = 0.15 if is_weekend else 0.22
            max_ont = max(0, n_pat - overlijden)
            ontslagen = max(0, min(max_ont,
                round(n_pat * ontslag_kans + _sr(seed, ri) * 2 - 1)))
            ri += 1
            stabiel = n_pat - overlijden - ontslagen

            rijen.append({
                "datum": datum,
                "dag": DAGNAMES[datum.weekday()],
                "weeknr": datum.isocalendar()[1],
                "dienst": dienst["naam"],
                "start": dienst["start"],
                "arts_naam": arts["naam"],
                "arts_code": arts["code"],
                "vplk": vplk,
                "n_pat": n_pat,
                "ontslagen": ontslagen,
                "stabiel": stabiel,
                "overlijden": overlijden,
                "kans_pct": round(kans * 100, 2),
            })

    return rijen, verdachte_idx


# ── Tabblad 1: Opdracht ───────────────────────────────────────────────────────

def _maak_opdracht(wb, leerlingnummer, verdachte_idx):
    ws = wb.active
    ws.title = "Opdracht"
    ws.sheet_view.showGridLines = False

    ws.column_dimensions["A"].width = 2
    ws.column_dimensions["B"].width = 32
    ws.column_dimensions["C"].width = 52
    ws.column_dimensions["D"].width = 2

    # Titelbalk
    ws.row_dimensions[1].height = 8
    ws.merge_cells("B2:C4")
    c = ws["B2"]
    c.value = "OPERATIE STERFGEVAL"
    c.font = Font(name="Arial", bold=True, size=24, color=K_ROOD)
    c.alignment = _left()
    ws.row_dimensions[2].height = 40
    ws.row_dimensions[3].height = 10
    ws.row_dimensions[4].height = 10

    ws.merge_cells("B5:C5")
    c = ws["B5"]
    c.value = "Forensisch Statistisch Onderzoek — Ziekenhuis De Beemsterhof, Afdeling C-3"
    c.font = _font(False, 11, "555555", italic=True)
    c.alignment = _left()
    ws.row_dimensions[5].height = 20
    ws.row_dimensions[6].height = 10

    # Zaakinfo
    info = [
        ("Leerlingnummer", str(leerlingnummer)),
        ("Ziekenhuis", "De Beemsterhof"),
        ("Afdeling", "C-3 Interne Geneeskunde"),
        ("Onderzoeksperiode", "8 januari 2024 – 30 maart 2024 (12 weken)"),
        ("Aantal diensten", "252  (3 diensten × 84 dagen)"),
        ("Status", "⚠  Actief forensisch onderzoek"),
    ]
    for i, (label, val) in enumerate(info):
        r = 7 + i
        ws.row_dimensions[r].height = 20
        c_l = ws.cell(r, 2, label)
        c_l.font = _font(True, 10)
        c_l.fill = _fill(K_GRIJS)
        c_l.border = _border()
        c_l.alignment = _left()

        ws.merge_cells(f"C{r}:C{r}")
        c_v = ws.cell(r, 3, val)
        c_v.font = _font(False, 10)
        c_v.fill = _fill(K_WIT)
        c_v.border = _border()
        c_v.alignment = _left()

    ws.row_dimensions[13].height = 14

    # Weekopdrachten
    weken = [
        ("WEEK 1 — Basisanalyse", K_KOPTEKST, [
            "1.  Maak van tabblad 'Data' een Excel-tabel (Ctrl+T)  →  naam: Beemsterhof",
            "2.  Bereken het gemiddeld aantal patiënten per dienst:  =GEMIDDELDE(...)",
            "3.  Bepaal het maximum en minimum overlijdens per dag:  =MAX(...)  /  =MIN(...)",
            "4.  Filter (AutoFilter) op Arts — welke arts heeft de hoogste overlijdenskans?",
        ]),
        ("WEEK 2 — Verbanden & Draaitabel", K_ROOD, [
            "1.  Voeg kolom N toe: Sterftequotiënt = Overlijden / Aantal_patienten",
            "2.  Bereken het gemiddeld quotiënt per arts:  =GEMIDDELDE.ALS(...)",
            "3.  Maak een draaitabel: rijen = Arts, kolommen = Dienst, waarden = quotiënt (gem.)",
            "4.  Voeg een tijdlijnfilter toe op de datumkolom",
            "5.  Klopt het argument van hoofdarts De Wit? Onderbouw statistisch.",
        ]),
        ("WEEK 3 — Visualisatie & Conclusie", K_GROEN, [
            "1.  Boxplot van Sterftequotiënt per arts  (Invoegen → Doos en Snorhaar)",
            "2.  Gegroepeerd staafdiagram: arts × dienst  (X = Arts, Y = gem. quotiënt)",
            "3.  Lijndiagram: overlijdens per dag  (kleur datapunten per arts)",
            "4.  Schrijf conclusie 150–250 woorden in tabblad 'Conclusie'  (structuur §1–§4)",
        ]),
    ]

    cur = 14
    for titel, kleur, taken in weken:
        ws.row_dimensions[cur].height = 24
        ws.merge_cells(f"B{cur}:C{cur}")
        c = ws.cell(cur, 2, titel)
        c.font = _font(True, 11, K_WIT)
        c.fill = _fill(kleur)
        c.alignment = _left()
        c.border = _border()
        cur += 1

        for taak in taken:
            ws.row_dimensions[cur].height = 18
            ws.merge_cells(f"B{cur}:C{cur}")
            c = ws.cell(cur, 2, taak)
            c.font = _font(False, 10)
            c.fill = _fill(K_WIT)
            c.alignment = _left()
            c.border = _border()
            cur += 1

        cur += 1

    # Disclaimer
    ws.row_dimensions[cur].height = 14
    cur += 1
    ws.merge_cells(f"B{cur}:C{cur}")
    c = ws.cell(cur, 2,
        "⚠  Deze dataset is uniek voor dit leerlingnummer en fictief gegenereerd voor onderwijsdoeleinden.")
    c.font = _font(False, 9, "888888", italic=True)
    c.alignment = _left()


# ── Tabblad 2: Data ───────────────────────────────────────────────────────────

KOLOMMEN = [
    ("Datum",               14, "datum",      "DD-MM-YYYY", "center"),
    ("Dag",                 12, "dag",         None,         "left"),
    ("Weeknummer",          11, "weeknr",      "#,##0",      "center"),
    ("Dienst",              18, "dienst",      None,         "left"),
    ("Aanvangstijd",        12, "start",       None,         "center"),
    ("Arts",                24, "arts_naam",   None,         "left"),
    ("Arts_code",            9, "arts_code",   None,         "center"),
    ("Verpleegkundige",     18, "vplk",        None,         "left"),
    ("Aantal_patienten",    15, "n_pat",       "#,##0",      "center"),
    ("Ontslagen",           12, "ontslagen",   "#,##0",      "center"),
    ("Stabiel",             10, "stabiel",     "#,##0",      "center"),
    ("Overlijden",          12, "overlijden",  "#,##0",      "center"),
    ("Overlijdenskans_pct", 17, "kans_pct",    "0.00%",      "center"),
]

def _maak_data(wb, rijen):
    ws = wb.create_sheet("Data")
    ws.sheet_view.showGridLines = False
    ws.freeze_panes = "A2"

    for i, (hdr, breedte, _, fmt, _align) in enumerate(KOLOMMEN):
        col = i + 1
        ws.column_dimensions[get_column_letter(col)].width = breedte
        c = ws.cell(1, col, hdr)
        _style_hdr(c)

    ws.row_dimensions[1].height = 28

    for r_idx, rij in enumerate(rijen):
        er = r_idx + 2
        overlijden = rij["overlijden"]

        if overlijden >= 2:
            bg = K_ROOD_RIJ
        elif overlijden == 0:
            bg = K_GROEN_RIJ
        else:
            bg = K_WIT if r_idx % 2 == 0 else K_GRIJS

        waarden = [
            rij["datum"], rij["dag"], rij["weeknr"],
            rij["dienst"], rij["start"],
            rij["arts_naam"], rij["arts_code"], rij["vplk"],
            rij["n_pat"], rij["ontslagen"], rij["stabiel"],
            rij["overlijden"], rij["kans_pct"] / 100,
        ]

        ws.row_dimensions[er].height = 16

        for c_idx, (_, _, _, fmt, align) in enumerate(KOLOMMEN):
            col = c_idx + 1
            c = ws.cell(er, col, waarden[c_idx])
            c.fill = _fill(bg)
            c.border = _border()
            c.font = _font(False, 9)
            c.alignment = _center() if align == "center" else _left()
            if fmt:
                c.number_format = fmt

    # Excel tabel
    last_row = len(rijen) + 1
    last_col = get_column_letter(len(KOLOMMEN))
    tabel = Table(displayName="Beemsterhof", ref=f"A1:{last_col}{last_row}")
    tabel.tableStyleInfo = TableStyleInfo(
        name="TableStyleMedium2",
        showRowStripes=True, showColumnStripes=False,
        showFirstColumn=False, showLastColumn=False,
    )
    ws.add_table(tabel)
    return ws


# ── Tabblad 3: Week 1 Analyse ─────────────────────────────────────────────────

def _maak_analyse(wb):
    ws = wb.create_sheet("Week 1 - Analyse")
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 2
    ws.column_dimensions["B"].width = 36
    ws.column_dimensions["C"].width = 22
    ws.column_dimensions["D"].width = 22
    ws.column_dimensions["E"].width = 22
    ws.column_dimensions["F"].width = 22

    def hdr(row, col, val, bg=K_KOPTEKST):
        c = ws.cell(row, col, val)
        _style_hdr(c, bg)
        ws.row_dimensions[row].height = 24

    def lbl(row, col, val):
        c = ws.cell(row, col, val)
        c.font = _font(True, 10)
        c.fill = _fill(K_GRIJS)
        c.border = _border()
        c.alignment = _left()

    def form(row, col, formula, fmt="#,##0.00"):
        c = ws.cell(row, col, formula)
        c.font = _font(False, 10)
        c.border = _border()
        c.alignment = _center()
        c.number_format = fmt

    def geel(row, col):
        c = ws.cell(row, col, "")
        c.fill = _fill(K_GEEL)
        c.border = _border()
        c.alignment = _left()

    ws.row_dimensions[1].height = 8
    ws.merge_cells("B2:F2")
    hdr(2, 2, "SECTIE 1 — Basisstatistieken (Week 1)")

    for i, h in enumerate(["Meting", "Ochtenddienst", "Middagdienst", "Nachtdienst", "Alle diensten"]):
        hdr(3, i+2, h, K_KOPTEKST if i == 0 else "3D566E")

    metingen = [
        ("Gem. aantal patiënten",
         "=AVERAGEIF(Data!D:D,\"Ochtenddienst\",Data!I:I)",
         "=AVERAGEIF(Data!D:D,\"Middagdienst\",Data!I:I)",
         "=AVERAGEIF(Data!D:D,\"Nachtdienst\",Data!I:I)",
         "=AVERAGE(Data!I2:I253)"),
        ("Totaal overlijdens",
         "=SUMIF(Data!D:D,\"Ochtenddienst\",Data!L:L)",
         "=SUMIF(Data!D:D,\"Middagdienst\",Data!L:L)",
         "=SUMIF(Data!D:D,\"Nachtdienst\",Data!L:L)",
         "=SUM(Data!L2:L253)"),
        ("Max overlijdens (1 dienst)",
         "=SUMPRODUCT(MAX((Data!D2:D253=\"Ochtenddienst\")*(Data!L2:L253)))",
         "=SUMPRODUCT(MAX((Data!D2:D253=\"Middagdienst\")*(Data!L2:L253)))",
         "=SUMPRODUCT(MAX((Data!D2:D253=\"Nachtdienst\")*(Data!L2:L253)))",
         "=MAX(Data!L2:L253)"),
        ("Min overlijdens (1 dienst)",
         "=SUMPRODUCT(MIN(IF(Data!D2:D253=\"Ochtenddienst\",Data!L2:L253,9999)))",
         "=SUMPRODUCT(MIN(IF(Data!D2:D253=\"Middagdienst\",Data!L2:L253,9999)))",
         "=SUMPRODUCT(MIN(IF(Data!D2:D253=\"Nachtdienst\",Data!L2:L253,9999)))",
         "=MIN(Data!L2:L253)"),
    ]

    for i, (meting, f1, f2, f3, f4) in enumerate(metingen):
        r = 4 + i
        ws.row_dimensions[r].height = 18
        lbl(r, 2, meting)
        for j, f in enumerate([f1, f2, f3, f4]):
            fmt = "#,##0.0" if i == 0 else "#,##0"
            form(r, j+3, f, fmt)

    ws.row_dimensions[8].height = 14

    ws.merge_cells("B9:F9")
    hdr(9, 2, "SECTIE 2 — Statistieken per arts")
    for i, h in enumerate(["Arts", "Gem. overlijdens/dienst", "Max overlijdens/dienst", "Totaal diensten", "Jouw observatie"]):
        hdr(10, i+2, h, "3D566E")

    for i, arts in enumerate(ARTSEN):
        r = 11 + i
        ws.row_dimensions[r].height = 18
        lbl(r, 2, arts["naam"])
        form(r, 3, f"=AVERAGEIF(Data!F:F,\"{arts['naam']}\",Data!L:L)", "#,##0.00")
        form(r, 4, f"=SUMPRODUCT(MAX((Data!F2:F253=\"{arts['naam']}\")*(Data!L2:L253)))", "#,##0")
        form(r, 5, f"=COUNTIF(Data!F:F,\"{arts['naam']}\")", "#,##0")
        geel(r, 6)

    ws.row_dimensions[15].height = 14
    ws.merge_cells("B16:F16")
    c = ws.cell(16, 2, "💡 Gele cellen zijn voor jouw notities en antwoorden.")
    c.font = _font(False, 9, "555555", italic=True)
    c.alignment = _left()

    ws.row_dimensions[17].height = 8
    ws.merge_cells("B18:F18")
    hdr(18, 2, "JOUW ANTWOORDEN — Week 1", K_ROOD)

    vragen = [
        "Welke arts heeft de hoogste gemiddelde overlijdenskans?",
        "Wat is het maximum aantal overlijdens in één dienst?",
        "Valt het patroon op in alle diensten of alleen één?",
        "Klopt het argument dat meer patiënten = meer overlijdens?",
    ]
    for i, v in enumerate(vragen):
        r = 19 + i
        ws.row_dimensions[r].height = 22
        c = ws.cell(r, 2, f"{i+1}.  {v}")
        c.font = _font(False, 10)
        c.border = _border()
        c.alignment = _left()
        ws.merge_cells(f"C{r}:F{r}")
        geel(r, 3)

    return ws


# ── Tabblad 4: Conclusie ──────────────────────────────────────────────────────

def _maak_conclusie(wb):
    ws = wb.create_sheet("Conclusie")
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 2
    ws.column_dimensions["B"].width = 28
    ws.column_dimensions["C"].width = 60
    ws.column_dimensions["D"].width = 2

    ws.row_dimensions[1].height = 8
    ws.merge_cells("B2:C2")
    c = ws["B2"]
    c.value = "EINDRAPPORT — Operatie Sterfgeval"
    c.font = Font(name="Arial", bold=True, size=16, color=K_ROOD)
    c.alignment = _left()
    ws.row_dimensions[2].height = 30

    ws.merge_cells("B3:C3")
    c = ws["B3"]
    c.value = "Schrijf je conclusie hieronder. Gebruik de structuur als leidraad (150–250 woorden)."
    c.font = _font(False, 10, "666666", italic=True)
    c.alignment = _left()
    ws.row_dimensions[3].height = 18
    ws.row_dimensions[4].height = 10

    secties = [
        ("§1  Bevinding",              "Wat zie je in de data? Welk patroon springt eruit? (1–2 zinnen)", 6),
        ("§2  Bewijs",                 "Noem 2 specifieke getallen of grafieken die dit ondersteunen.", 6),
        ("§3  Alternatieve verklaring","Bespreek één andere mogelijke verklaring (bijv. toeval).", 5),
        ("§4  Oordeel",                "Is de statistische analyse voldoende bewijs? Waarom wel/niet?", 5),
    ]

    cur = 5
    for titel, instructie, hoogte in secties:
        ws.row_dimensions[cur].height = 22
        c = ws.cell(cur, 2, titel)
        c.font = _font(True, 11, K_WIT)
        c.fill = _fill(K_KOPTEKST)
        c.border = _border()
        c.alignment = _left()

        c2 = ws.cell(cur, 3, instructie)
        c2.font = _font(False, 9, "BBBBBB", italic=True)
        c2.fill = _fill(K_KOPTEKST)
        c2.border = _border()
        c2.alignment = _left()
        cur += 1

        for _ in range(hoogte):
            ws.row_dimensions[cur].height = 18
            ws.merge_cells(f"B{cur}:C{cur}")
            c = ws.cell(cur, 2, "")
            c.fill = _fill(K_GEEL)
            c.border = _border()
            c.alignment = _left()
            cur += 1

        cur += 1


# ── Publieke functie ──────────────────────────────────────────────────────────

def genereer_xlsx_bytes(leerlingnummer: str) -> bytes:
    """Genereer een xlsx bestand als bytes-object (voor Streamlit download)."""
    rijen, verdachte_idx = _genereer_rijen(leerlingnummer)

    wb = Workbook()
    _maak_opdracht(wb, leerlingnummer, verdachte_idx)
    _maak_data(wb, rijen)
    _maak_analyse(wb)
    _maak_conclusie(wb)

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def genereer_xlsx_bestand(leerlingnummer: str, pad: str = None) -> str:
    """Sla een xlsx bestand op schijf op (voor batch-gebruik)."""
    if pad is None:
        pad = f"Dataset_BeemsterhofC3_{leerlingnummer}.xlsx"
    rijen, verdachte_idx = _genereer_rijen(leerlingnummer)
    wb = Workbook()
    _maak_opdracht(wb, leerlingnummer, verdachte_idx)
    _maak_data(wb, rijen)
    _maak_analyse(wb)
    _maak_conclusie(wb)
    wb.save(pad)
    print(f"✅  {pad}  ({len(rijen)} rijen, verdachte: {ARTSEN[verdachte_idx]['naam']})")
    return pad


if __name__ == "__main__":
    import sys
    args = sys.argv[1:] or ["144555"]
    for ln in args:
        genereer_xlsx_bestand(ln)
