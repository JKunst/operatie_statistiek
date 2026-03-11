"""
Operatie Sterfgeval — Streamlit Website
Forensisch statistisch onderzoek voor HAVO/VWO wiskunde bovenbouw
"""

import streamlit as st
from dataset_generator import genereer_xlsx_bytes, ARTSEN, _hash
from download_logger import (
    log_download, haal_log_op, zoek_leerling, statistieken,
    controleer_wachtwoord, log_als_csv, verwijder_leerling,
    initialiseer_db, LESGROEPEN,
)

initialiseer_db()

st.set_page_config(
    page_title="Operatie Sterfgeval",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Special+Elite&family=Courier+Prime:wght@400;700&family=Oswald:wght@300;400;600&display=swap');

.stApp { background: #0d0b08; }
.block-container { max-width: 860px; padding-top: 2rem; padding-bottom: 3rem; }
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Dossier ── */
.dossier-wrapper {
    background: #f0e8d8; padding: 2.5rem 3rem; position: relative;
    box-shadow: 0 20px 60px rgba(0,0,0,0.75);
    border-top: 6px solid transparent;
    border-image: repeating-linear-gradient(90deg,#8b1a1a 0,#8b1a1a 8px,transparent 8px,transparent 16px) 6;
}
.dossier-wrapper::after { content:''; position:absolute; inset:10px; border:1px solid rgba(139,90,43,0.25); pointer-events:none; }
.dossier-eyebrow { font-family:'Oswald',sans-serif; font-size:0.65rem; letter-spacing:0.4em; color:#6b5d4e; text-transform:uppercase; margin-bottom:0.3rem; }
.dossier-title { font-family:'Special Elite',cursive; font-size:2.6rem; color:#1a1410; line-height:1.05; margin:0 0 0.5rem 0; }
.dossier-stamp { display:inline-block; border:3px solid #8b1a1a; color:#8b1a1a; font-family:'Oswald',sans-serif; font-size:1rem; font-weight:600; letter-spacing:0.3em; padding:0.15rem 0.8rem; transform:rotate(-8deg); margin:0.4rem 0 1.2rem 0; text-transform:uppercase; }
.case-meta { font-family:'Courier Prime',monospace; font-size:0.75rem; color:#6b5d4e; border-top:1px solid #d4c4a0; border-bottom:1px solid #d4c4a0; padding:0.6rem 0; margin-bottom:1.2rem; display:flex; gap:1.5rem; }
.intro-text { font-family:'Courier Prime',monospace; font-size:0.9rem; line-height:1.8; color:#3a2e22; margin-bottom:1rem; }
.intro-text strong { color:#8b1a1a; }
.redacted { background:#1a1410; color:transparent; border-radius:2px; padding:0 4px; user-select:none; font-size:0.85em; }
.form-label { font-family:'Oswald',sans-serif; font-size:0.7rem; letter-spacing:0.25em; text-transform:uppercase; color:#6b5d4e; margin-bottom:0.3rem; }

/* ── Lesgroep radio ── */
.stRadio > div { flex-direction: row !important; gap: 0.5rem !important; flex-wrap: wrap; }
.stRadio > div > label {
    background: white !important; border: 2px solid #d4c4a0 !important;
    padding: 0.4rem 1rem !important; cursor: pointer;
    font-family: 'Oswald', sans-serif !important; font-size: 0.85rem !important;
    letter-spacing: 0.1em !important; text-transform: uppercase !important;
    color: #1a1410 !important; border-radius: 0 !important;
}
.stRadio > div > label:has(input:checked) { background: #8b1a1a !important; color: white !important; border-color: #8b1a1a !important; }

/* ── Input ── */
.stTextInput > div > div > input { font-family:'Courier Prime',monospace !important; font-size:1.1rem !important; letter-spacing:0.2em !important; background:white !important; border:2px solid #d4c4a0 !important; color:#1a1410 !important; border-radius:0 !important; }
.stTextInput > div > div > input:focus { border-color:#8b1a1a !important; box-shadow:none !important; }

/* ── Selectbox ── */
.stSelectbox > div > div { border-radius:0 !important; border:2px solid #d4c4a0 !important; font-family:'Courier Prime',monospace !important; }

/* ── Knoppen ── */
.stButton > button { background:#8b1a1a !important; color:#f0e8d8 !important; border:none !important; border-radius:0 !important; font-family:'Oswald',sans-serif !important; font-size:0.85rem !important; letter-spacing:0.15em !important; text-transform:uppercase !important; padding:0.6rem 1.5rem !important; width:100% !important; }
.stButton > button:hover { background:#c0392b !important; }
.stDownloadButton > button { background:#2d5016 !important; color:white !important; border:none !important; border-radius:0 !important; font-family:'Oswald',sans-serif !important; font-size:0.8rem !important; letter-spacing:0.1em !important; text-transform:uppercase !important; width:100% !important; }
.stDownloadButton > button:hover { background:#3d6b1e !important; }

/* ── Meldingen ── */
.bevestiging-box { background:#1a2a0a; border-left:4px solid #4a8a1a; padding:1rem 1.2rem; margin:1rem 0; font-family:'Courier Prime',monospace; font-size:0.85rem; color:#a8d878; }
.bevestiging-box strong { color:#c8f098; }
.clue-box { background:#fff8ee; border-left:4px solid #8b1a1a; padding:0.8rem 1rem; margin:0.75rem 0; font-family:'Courier Prime',monospace; font-size:0.85rem; font-style:italic; color:#4a3a28; }
.clue-label { font-style:normal; font-family:'Oswald',sans-serif; font-size:0.65rem; letter-spacing:0.2em; text-transform:uppercase; color:#8b1a1a; display:block; margin-bottom:0.3rem; }

/* ── Kaarten ── */
.card { background:#f0e8d8; padding:1.5rem 1.8rem; margin-bottom:1.2rem; position:relative; box-shadow:0 4px 20px rgba(0,0,0,0.4); }
.card-label { position:absolute; top:-0.55rem; left:1.2rem; background:#8b1a1a; color:white; font-family:'Oswald',sans-serif; font-size:0.6rem; letter-spacing:0.2em; text-transform:uppercase; padding:0.1rem 0.5rem; }
.card h3 { font-family:'Special Elite',cursive; font-size:1.15rem; color:#1a1410; margin:0 0 0.8rem 0; padding-bottom:0.5rem; border-bottom:1px solid #d4c4a0; }
.card p, .card li { font-family:'Courier Prime',monospace; font-size:0.87rem; line-height:1.8; color:#3a2e22; }
.task-item { display:flex; gap:0.75rem; align-items:flex-start; padding:0.5rem 0; border-bottom:1px dashed #d4c4a0; font-family:'Courier Prime',monospace; font-size:0.87rem; color:#3a2e22; line-height:1.6; }
.task-item:last-child { border-bottom:none; }
.task-num { background:#1a1410; color:#f0e8d8; font-family:'Oswald',sans-serif; font-size:0.7rem; font-weight:600; width:1.4rem; height:1.4rem; display:inline-flex; align-items:center; justify-content:center; flex-shrink:0; margin-top:0.15rem; }
.formula-box { background:white; border:1px solid #d4c4a0; padding:0.5rem 0.8rem; font-family:'Courier Prime',monospace; font-size:0.88rem; color:#2d5016; margin:0.4rem 0; }
.data-table { width:100%; border-collapse:collapse; font-family:'Courier Prime',monospace; font-size:0.78rem; margin-top:0.6rem; }
.data-table th { background:#1a1410; color:#d4c4a0; text-align:left; padding:0.35rem 0.5rem; font-family:'Oswald',sans-serif; font-size:0.62rem; letter-spacing:0.1em; text-transform:uppercase; }
.data-table td { padding:0.3rem 0.5rem; border-bottom:1px solid #d4c4a0; color:#3a2e22; }
.data-table tr:nth-child(even) td { background:rgba(0,0,0,0.04); }
.highlight-row td { background:#fdecea !important; font-weight:bold; color:#8b1a1a !important; }
.progress-bar { display:flex; gap:0.4rem; margin-bottom:1.5rem; }
.progress-dot { flex:1; height:4px; background:#333; }
.progress-dot.active { background:#c0392b; }
.week-header { background:#1a1410; padding:1.5rem 2rem; margin-bottom:1.5rem; border-left:6px solid #8b1a1a; }
.week-header .wh-eyebrow { font-family:'Oswald',sans-serif; font-size:0.65rem; letter-spacing:0.4em; color:#666; text-transform:uppercase; }
.week-header h2 { font-family:'Special Elite',cursive; font-size:2rem; color:#f0e8d8; margin:0.3rem 0; }
.week-header .wh-sub { font-family:'Courier Prime',monospace; font-size:0.85rem; color:#c0392b; font-style:italic; }
.gesloten-stamp { text-align:center; padding:1.5rem 0; }
.gesloten-stamp span { display:inline-block; border:3px solid #8b1a1a; color:#8b1a1a; font-family:'Oswald',sans-serif; font-size:1.4rem; font-weight:600; letter-spacing:0.3em; padding:0.4rem 2rem; transform:rotate(5deg); text-transform:uppercase; }

/* ── Docent ── */
.docent-header { background:#0a1628; padding:2rem 2.5rem; margin-bottom:1.5rem; border-left:6px solid #1a5c8b; box-shadow:0 4px 20px rgba(0,0,0,0.5); }
.docent-header .dh-eyebrow { font-family:'Oswald',sans-serif; font-size:0.65rem; letter-spacing:0.4em; color:#4a7a9b; text-transform:uppercase; }
.docent-header h2 { font-family:'Special Elite',cursive; font-size:2rem; color:#d0e8f8; margin:0.3rem 0; }
.docent-header .dh-sub { font-family:'Courier Prime',monospace; font-size:0.85rem; color:#5a9abf; font-style:italic; }
.docent-card { background:#0f1e2e; border:1px solid #1e3a55; padding:1.5rem 1.8rem; margin-bottom:1.2rem; box-shadow:0 4px 20px rgba(0,0,0,0.4); }
.docent-card h3 { font-family:'Oswald',sans-serif; font-size:1rem; letter-spacing:0.1em; text-transform:uppercase; color:#7ab8d8; margin:0 0 1rem 0; padding-bottom:0.5rem; border-bottom:1px solid #1e3a55; }
.stat-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:0.75rem; margin-bottom:1.5rem; }
.stat-blok { background:#0a1628; border:1px solid #1e3a55; padding:0.9rem 0.8rem; text-align:center; }
.stat-blok .stat-num { font-family:'Oswald',sans-serif; font-size:1.8rem; font-weight:600; color:#7ab8d8; line-height:1; }
.stat-blok .stat-label { font-family:'Courier Prime',monospace; font-size:0.68rem; color:#4a7a9b; text-transform:uppercase; letter-spacing:0.1em; margin-top:0.3rem; }
.groep-tab { display:inline-block; padding:0.35rem 1rem; font-family:'Oswald',sans-serif; font-size:0.75rem; letter-spacing:0.15em; text-transform:uppercase; cursor:pointer; border:1px solid #1e3a55; color:#4a7a9b; margin-right:0.4rem; margin-bottom:0.5rem; }
.groep-tab.actief { background:#1a5c8b; color:white; border-color:#1a5c8b; }
.log-table { width:100%; border-collapse:collapse; font-family:'Courier Prime',monospace; font-size:0.82rem; }
.log-table th { background:#0a1628; color:#5a9abf; text-align:left; padding:0.45rem 0.6rem; font-family:'Oswald',sans-serif; font-size:0.63rem; letter-spacing:0.15em; text-transform:uppercase; border-bottom:2px solid #1e3a55; }
.log-table td { padding:0.45rem 0.6rem; border-bottom:1px solid #1a2e42; color:#b0c8d8; vertical-align:middle; }
.log-table tr:hover td { background:rgba(26,92,139,0.15); }
.ln-cell { font-size:0.95rem; font-weight:bold; letter-spacing:0.1em; color:#e0f0ff !important; }
.groep-badge { background:#1e3a55; color:#7ab8d8; padding:0.1rem 0.5rem; font-size:0.72rem; font-family:'Oswald',sans-serif; letter-spacing:0.1em; }
.ww-box { background:#0a1628; border:1px solid #1e3a55; padding:2rem 2.5rem; max-width:440px; margin:3rem auto; box-shadow:0 10px 40px rgba(0,0,0,0.6); }
.ww-box h2 { font-family:'Special Elite',cursive; font-size:1.5rem; color:#d0e8f8; margin-bottom:1rem; }
.ww-box p { font-family:'Courier Prime',monospace; font-size:0.85rem; color:#5a9abf; margin-bottom:1.5rem; }
.zoek-result { background:#0a1628; border:1px solid #1e3a55; padding:0.8rem 1rem; font-family:'Courier Prime',monospace; font-size:0.88rem; color:#b0c8d8; margin-top:0.5rem; }
</style>
""", unsafe_allow_html=True)


# ── Constanten ────────────────────────────────────────────────────────────────
ARTS_KLEUREN = {
    "Dr. E. Bakker":   "#ff9944",
    "Dr. R. Jansen":   "#44bbff",
    "Dr. S. Vermeer":  "#ff5555",
    "Dr. M. de Vries": "#44ee99",
}

def verdachte_voor(ln: str) -> str:
    return ARTSEN[_hash(str(ln)) % len(ARTSEN)]["naam"]


# ── Session state ─────────────────────────────────────────────────────────────
for k, v in [("pagina","intro"),("leerlingnummer",""),("lesgroep",""),
              ("dataset_gegenereerd",False),("docent_ingelogd",False),("actieve_groep","alle")]:
    if k not in st.session_state:
        st.session_state[k] = v

def ga_naar(p):
    st.session_state.pagina = p
    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# INTRO
# ══════════════════════════════════════════════════════════════════════════════
def render_intro():
    st.markdown("""
    <div class="dossier-wrapper">
        <div class="dossier-eyebrow">Ministerie van Justitie — Forensische Statistiek</div>
        <div class="dossier-title">Operatie<br>Sterfgeval</div>
        <div class="dossier-stamp">Vertrouwelijk</div>
        <div class="case-meta">
            <span>Zaak nr: OPS-2024-047</span>
            <span>Ziekenhuis De Beemsterhof</span>
            <span>Status: Actief onderzoek</span>
        </div>
        <div class="intro-text">
            <p>Beste rechercheur,</p><br>
            <p>In Ziekenhuis De Beemsterhof is iets grondig mis. Het sterftecijfer op afdeling
            <strong>C-3 (Interne Geneeskunde)</strong> ligt de afgelopen drie maanden
            <strong>beduidend hoger</strong> dan verwacht — maar alleen in bepaalde diensten.</p><br>
            <p>Het gaat om <span class="redacted">███ ███████</span>, een arts die al eerder
            onder een vergrootglas lag. Of is er iets anders aan de hand? De statistieken
            liegen niet — maar ze vertellen ook niet het hele verhaal.</p><br>
            <p><strong>Jouw taak:</strong> Analyseer de data van drie weken. Bereken, visualiseer,
            en trek je conclusie. Is er sprake van een patroon? En zo ja — wat betekent dat?</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Stap 1: Lesgroep ──
    st.markdown('<div class="form-label">Stap 1 — Kies je lesgroep</div>', unsafe_allow_html=True)
    lesgroep_keuze = st.radio(
        "lesgroep", options=LESGROEPEN, horizontal=True,
        label_visibility="collapsed", key="lesgroep_radio",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Stap 2: Leerlingnummer ──
    st.markdown('<div class="form-label">Stap 2 — Voer je leerlingnummer in (6 cijfers)</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        ln_input = st.text_input("ln", label_visibility="collapsed",
                                 placeholder="bijv. 144555", max_chars=6, key="ln_input_field")
    with col2:
        toegang = st.button("▶ Toegang", key="btn_toegang")

    if toegang or (ln_input and len(ln_input) == 6 and ln_input.isdigit()):
        if ln_input and len(ln_input) == 6 and ln_input.isdigit():
            st.session_state.leerlingnummer    = ln_input
            st.session_state.lesgroep          = lesgroep_keuze
            st.session_state.dataset_gegenereerd = True
        else:
            st.error("Voer een geldig leerlingnummer in van precies 6 cijfers.")

    if st.session_state.dataset_gegenereerd and st.session_state.leerlingnummer:
        ln    = st.session_state.leerlingnummer
        groep = st.session_state.lesgroep
        arts  = verdachte_voor(ln)

        st.markdown(f"""
        <div class="bevestiging-box">
            <strong>✓ Toegang verleend — Leerling {ln} &nbsp;|&nbsp; {groep.upper()}</strong><br>
            Jouw persoonlijke dataset is klaar. Download het Excel-bestand en open het in Microsoft Excel.
        </div>
        """, unsafe_allow_html=True)

        with st.spinner("Dataset genereren..."):
            xlsx_bytes = genereer_xlsx_bytes(ln, groep)

        st.download_button(
            label=f"⬇ Download Dataset_BeemsterhofC3_{ln}.xlsx",
            data=xlsx_bytes,
            file_name=f"Dataset_BeemsterhofC3_{ln}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_xlsx",
            on_click=log_download,
            kwargs={"leerlingnummer": ln, "lesgroep": groep, "arts_naam": arts},
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div style="font-family:\'Oswald\',sans-serif;font-size:0.7rem;letter-spacing:0.3em;text-transform:uppercase;color:#6b5d4e;margin-bottom:0.8rem;">Kies je onderzoeksweek</div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("WEEK 1\nBasisanalyse", key="btn_w1"): ga_naar("week1")
        with c2:
            if st.button("WEEK 2\nVerbanden",    key="btn_w2"): ga_naar("week2")
        with c3:
            if st.button("WEEK 3\nVisualisatie", key="btn_w3"): ga_naar("week3")

    st.markdown("<br>" * 4, unsafe_allow_html=True)
    _, col_r = st.columns([5, 1])
    with col_r:
        if st.button("· · ·", key="docent_link", help="Docentenportaal"):
            ga_naar("docent_login")


# ══════════════════════════════════════════════════════════════════════════════
# DOCENT LOGIN
# ══════════════════════════════════════════════════════════════════════════════
def render_docent_login():
    st.markdown("""
    <div class="ww-box">
        <h2>🔐 Docentenportaal</h2>
        <p>Dit gedeelte is alleen toegankelijk voor de docent.<br>
        Voer het wachtwoord in om het overzicht te bekijken.</p>
    </div>
    """, unsafe_allow_html=True)
    _, col, _ = st.columns([1, 2, 1])
    with col:
        ww = st.text_input("Wachtwoord", type="password", key="docent_ww_input",
                           label_visibility="collapsed", placeholder="Wachtwoord")
        ca, cb = st.columns(2)
        with ca:
            if st.button("→ Inloggen", key="btn_docent_login"):
                if controleer_wachtwoord(ww):
                    st.session_state.docent_ingelogd = True
                    ga_naar("docent_dashboard")
                else:
                    st.error("Onjuist wachtwoord.")
        with cb:
            if st.button("← Terug", key="btn_login_terug"):
                ga_naar("intro")


# ══════════════════════════════════════════════════════════════════════════════
# DOCENT DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def render_docent_dashboard():
    if not st.session_state.docent_ingelogd:
        ga_naar("docent_login")
        return

    stats        = statistieken()
    n_totaal     = stats["n_leerlingen"]
    per_arts     = {r["arts_verdachte"]: r["cnt"] for r in stats["per_arts"]}
    per_groep    = {r["lesgroep"]: r["cnt"] for r in stats["per_groep"]}

    st.markdown("""
    <div class="docent-header">
        <div class="dh-eyebrow">Docentenportaal — Operatie Sterfgeval</div>
        <h2>Download Overzicht</h2>
        <div class="dh-sub">» Overzicht per lesgroep van wie al een dataset heeft gedownload «</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Stat blokjes per groep ──
    groep_html = ""
    for groep in LESGROEPEN:
        cnt = per_groep.get(groep, 0)
        groep_html += f"""
        <div class="stat-blok">
            <div class="stat-num">{cnt}</div>
            <div class="stat-label">{groep.upper()}</div>
        </div>"""
    groep_html += f"""
        <div class="stat-blok" style="border-color:#2a4a6a;">
            <div class="stat-num" style="color:#aaccee;">{n_totaal}</div>
            <div class="stat-label" style="color:#3a6a8a;">Totaal</div>
        </div>"""
    st.markdown(f'<div class="stat-grid">{groep_html}</div>', unsafe_allow_html=True)

    # ── Verdeling verdachte artsen ──
    arts_bars = ""
    for arts in ARTSEN:
        cnt    = per_arts.get(arts["naam"], 0)
        kleur  = ARTS_KLEUREN.get(arts["naam"], "#aaa")
        breedte = max(3, int(cnt / max(n_totaal, 1) * 100))
        arts_bars += f"""
        <div style="margin-bottom:0.7rem;">
            <div style="display:flex;justify-content:space-between;font-family:'Courier Prime',monospace;
                        font-size:0.82rem;color:#b0c8d8;margin-bottom:0.2rem;">
                <span style="color:{kleur};font-weight:bold;">{arts['naam']}</span>
                <span style="color:#4a7a9b;font-size:0.75rem;">{cnt} leerling{'en' if cnt!=1 else ''}</span>
            </div>
            <div style="background:#1e3a55;height:7px;border-radius:3px;overflow:hidden;">
                <div style="background:{kleur};height:7px;width:{breedte}%;"></div>
            </div>
        </div>"""
    st.markdown(f"""
    <div class="docent-card">
        <h3>Verdeling verdachte artsen (alle groepen)</h3>
        {arts_bars or '<p style="color:#4a7a9b;font-family:Courier Prime,monospace;font-size:0.85rem;">Nog geen downloads.</p>'}
    </div>
    """, unsafe_allow_html=True)

    # ── Tabbladen per lesgroep ──
    st.markdown("""
    <div class="docent-card">
        <h3>Downloads per lesgroep</h3>
    """, unsafe_allow_html=True)

    tab_labels = ["Alle groepen"] + [g.upper() for g in LESGROEPEN]
    tabs = st.tabs(tab_labels)

    def _render_groep_tabel(groep_filter):
        log = haal_log_op(groep_filter)
        if not log:
            st.markdown(f'<p style="color:#4a7a9b;font-family:\'Courier Prime\',monospace;font-size:0.85rem;padding:0.5rem 0;">Nog geen downloads{"" if not groep_filter else f" voor {groep_filter.upper()}"}.</p>', unsafe_allow_html=True)
            return

        rijen = ""
        for r in log:
            kleur  = ARTS_KLEUREN.get(r["arts_verdachte"], "#aaa")
            groep  = r.get("lesgroep", "?")
            rijen += f"""<tr>
                <td class="ln-cell">{r['leerlingnummer']}</td>
                <td><span class="groep-badge">{groep.upper()}</span></td>
                <td style="color:{kleur};font-style:italic;">{r['arts_verdachte']}</td>
                <td>{r['eerste_download']}</td>
                <td>{r['laatste_download']}</td>
            </tr>"""

        st.markdown(f"""
        <table class="log-table">
            <thead><tr>
                <th>Leerlingnummer</th><th>Groep</th><th>Verdachte arts</th>
                <th>Eerste download</th><th>Laatste download</th>
            </tr></thead>
            <tbody>{rijen}</tbody>
        </table>
        """, unsafe_allow_html=True)

        # CSV export per groep
        st.download_button(
            f"⬇ Export {groep_filter.upper() if groep_filter else 'alle'} als CSV",
            data=log_als_csv(groep_filter),
            file_name=f"downloads_{'alle' if not groep_filter else groep_filter}.csv",
            mime="text/csv",
            key=f"csv_{groep_filter or 'alle'}",
        )

    with tabs[0]:
        _render_groep_tabel(None)
    for i, groep in enumerate(LESGROEPEN):
        with tabs[i + 1]:
            _render_groep_tabel(groep)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Opzoeken + verwijderen ──
    st.markdown('<div class="docent-card"><h3>Leerlingnummer opzoeken</h3>', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        zoek = st.text_input("Zoek", label_visibility="collapsed",
                             placeholder="6-cijferig leerlingnummer", max_chars=6, key="zoek_ln")
    with col2:
        st.button("🔎 Zoeken", key="btn_zoek")

    if zoek and len(zoek) == 6 and zoek.isdigit():
        arts     = verdachte_voor(zoek)
        kleur    = ARTS_KLEUREN.get(arts, "#aaa")
        gevonden = zoek_leerling(zoek)
        if gevonden:
            groep_str = gevonden.get("lesgroep", "?").upper()
            status    = f"✓ Gedownload op {gevonden['eerste_download']} (laatste: {gevonden['laatste_download']})"
            skl       = "#4a8a1a"
        else:
            groep_str = "—"
            status    = "✗ Nog niet gedownload"
            skl       = "#8b4a1a"

        st.markdown(f"""
        <div class="zoek-result">
            <strong style="color:#e0f0ff;">Leerling {zoek}</strong>
            &nbsp;&nbsp;<span class="groep-badge">{groep_str}</span><br>
            Verdachte arts: <span style="color:{kleur};font-weight:bold;">{arts}</span><br>
            Status: <span style="color:{skl};">{status}</span>
        </div>
        """, unsafe_allow_html=True)

        if gevonden:
            if st.button(f"🗑 Verwijder {zoek} uit de log", key="btn_verwijder"):
                verwijder_leerling(zoek)
                st.success(f"Leerling {zoek} verwijderd.")
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("← Uitloggen", key="btn_uitloggen"):
        st.session_state.docent_ingelogd = False
        ga_naar("intro")


# ══════════════════════════════════════════════════════════════════════════════
# WEEK 1
# ══════════════════════════════════════════════════════════════════════════════
def render_week1():
    st.markdown("""
    <div class="progress-bar"><div class="progress-dot active"></div><div class="progress-dot"></div><div class="progress-dot"></div></div>
    <div class="week-header">
        <div class="wh-eyebrow">Week 1 van 3</div>
        <h2>De Eerste Cijfers</h2>
        <div class="wh-sub">» Iets klopt niet in de sterftecijfers van dienst C-3 «</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card"><div class="card-label">Context</div>
        <h3>Wat zegt het dossier?</h3>
        <p>Jij bent aangesteld als forensisch statisticus. Je hebt de ziekenhuisdata van afdeling C-3
        ontvangen over 12 weken. Elke rij beschrijft één dienst: tijdstip, arts, verpleegkundige en patiëntuitkomsten.</p>
        <div class="clue-box"><span class="clue-label">🔍 Aanwijzing</span>
        Kijk naar het gemiddeld aantal patiënten <em>per dienst</em>. En wat is het maximum sterfgevallen op één dag?</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="card"><div class="card-label">Dataset</div><h3>Structuur</h3>
        <table class="data-table"><thead><tr><th>Kol.</th><th>Inhoud</th></tr></thead><tbody>
        <tr><td>A</td><td>Datum</td></tr><tr><td>B</td><td>Dag</td></tr>
        <tr><td>C</td><td>Weeknummer</td></tr><tr><td>D</td><td>Dienst</td></tr>
        <tr><td>E</td><td>Aanvangstijd</td></tr><tr><td>F</td><td>Arts</td></tr>
        <tr><td>G</td><td>Arts_code</td></tr><tr><td>H</td><td>Verpleegkundige</td></tr>
        <tr><td>I</td><td>Aantal_patienten</td></tr><tr><td>J</td><td>Ontslagen</td></tr>
        <tr><td>K</td><td>Stabiel</td></tr>
        <tr class="highlight-row"><td>L</td><td>Overlijden</td></tr>
        <tr><td>M</td><td>Overlijdenskans_%</td></tr>
        </tbody></table></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="card"><div class="card-label">Opdrachten</div><h3>Week 1 — taken</h3>
        <div class="task-item"><span class="task-num">1</span><span>Maak een <strong>Excel-tabel</strong> (Ctrl+T). Naam: <em>Beemsterhof</em>.</span></div>
        <div class="task-item"><span class="task-num">2</span><span><strong>Gemiddeld aantal patiënten</strong> per dienst met <code>=GEMIDDELDE(...)</code>.</span></div>
        <div class="task-item"><span class="task-num">3</span><span><strong>MAX en MIN</strong> overlijdens per dag.</span></div>
        <div class="task-item"><span class="task-num">4</span><span><strong>AutoFilter</strong> op Arts. Welke arts heeft de hoogste overlijdenskans?</span></div>
        <div class="task-item"><span class="task-num">5</span><span>Vul het <strong>antwoordformulier</strong> in (tabblad 'Week 1 - Analyse').</span></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="card"><div class="card-label">Formules</div><h3>Naslagwerk week 1</h3>
    <div class="formula-box">=GEMIDDELDE(Beemsterhof[Aantal_patienten])</div>
    <div class="formula-box">=GEMIDDELDE.ALS(Beemsterhof[Arts];"Dr. Vermeer";Beemsterhof[Overlijden])</div>
    <div class="formula-box">=MAX(Beemsterhof[Overlijden])</div>
    <div class="formula-box">=MIN(Beemsterhof[Overlijden])</div>
    <div class="formula-box">=AANTAL.ALS(Beemsterhof[Dienst];"Nachtdienst")</div>
    <div class="clue-box"><span class="clue-label">💡 Tip</span>Als het maximum veel hoger is dan het gemiddelde, is dat statistisch opvallend!</div>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("← Terug", key="w1_terug"): ga_naar("intro")
    with c2:
        if st.button("→ Week 2", key="w1_door"): ga_naar("week2")


# ══════════════════════════════════════════════════════════════════════════════
# WEEK 2
# ══════════════════════════════════════════════════════════════════════════════
def render_week2():
    st.markdown("""
    <div class="progress-bar"><div class="progress-dot active"></div><div class="progress-dot active"></div><div class="progress-dot"></div></div>
    <div class="week-header">
        <div class="wh-eyebrow">Week 2 van 3</div>
        <h2>Verbanden Leggen</h2>
        <div class="wh-sub">» Het patroon begint zichtbaar te worden «</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card"><div class="card-label">Verhaal</div>
        <h3>Nieuwe informatie</h3>
        <p>Hoofdarts De Wit: <em>"Meer patiënten = meer risico."</em> Klopt dat statistisch?</p>
        <div class="clue-box"><span class="clue-label">🔍 Aanwijzing</span>
        Bereken overlijdens ÷ patiënten. Als die verhouding bij één arts altijd hoger is, klopt het argument van De Wit niet.</div>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="card"><div class="card-label">Opdrachten</div><h3>Week 2 — taken</h3>
        <div class="task-item"><span class="task-num">1</span><span>Kolom N: <strong>Sterftequotiënt</strong> = <code>=ALS(I2=0;"n.v.t.";L2/I2)</code></span></div>
        <div class="task-item"><span class="task-num">2</span><span><strong>Gem. quotiënt per arts</strong> met <code>=GEMIDDELDE.ALS()</code>.</span></div>
        <div class="task-item"><span class="task-num">3</span><span><strong>Draaitabel</strong>: rijen=Arts, kolommen=Dienst, waarden=gem. quotiënt.</span></div>
        <div class="task-item"><span class="task-num">4</span><span><strong>Tijdlijnfilter</strong> toevoegen op de datumkolom.</span></div>
        <div class="task-item"><span class="task-num">5</span><span>Klopt het argument van De Wit? Onderbouw met getallen.</span></div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="card"><div class="card-label">Formules</div><h3>Naslagwerk week 2</h3>
        <div class="formula-box">=ALS(I2=0;"n.v.t.";L2/I2)</div>
        <div class="formula-box">=GEMIDDELDE.ALS(F:F;"Dr. Vermeer";N:N)</div>
        <div class="formula-box">=AANTAL.ALS(F:F;F2)</div>
        <div class="clue-box"><span class="clue-label">💡 Draaitabel tip</span>Zet quotiënt op "Gemiddelde" → Waardeveldinstellingen.</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="card"><div class="card-label">Voorbeeld</div>
        <h3>Zo zou jouw draaitabel eruit kunnen zien</h3>
        <table class="data-table"><thead><tr><th>Arts</th><th>Ochtend</th><th>Middag</th><th>Nacht</th><th>Gem.</th></tr></thead>
        <tbody>
        <tr><td>Dr. E. Bakker</td><td>0.021</td><td>0.019</td><td>0.023</td><td>0.021</td></tr>
        <tr><td>Dr. R. Jansen</td><td>0.018</td><td>0.022</td><td>0.020</td><td>0.020</td></tr>
        <tr class="highlight-row"><td>Dr. S. Vermeer</td><td>0.071</td><td>0.069</td><td>0.074</td><td>0.071</td></tr>
        <tr><td>Dr. M. de Vries</td><td>0.020</td><td>0.018</td><td>0.022</td><td>0.020</td></tr>
        </tbody></table>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("← Terug", key="w2_terug"): ga_naar("intro")
    with c2:
        if st.button("→ Week 3", key="w2_door"): ga_naar("week3")


# ══════════════════════════════════════════════════════════════════════════════
# WEEK 3
# ══════════════════════════════════════════════════════════════════════════════
def render_week3():
    st.markdown("""
    <div class="progress-bar"><div class="progress-dot active"></div><div class="progress-dot active"></div><div class="progress-dot active"></div></div>
    <div class="week-header">
        <div class="wh-eyebrow">Week 3 van 3</div>
        <h2>Het Oordeel</h2>
        <div class="wh-sub">» Jij sluit het dossier — wat is jouw conclusie? «</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card"><div class="card-label">Verhaal</div>
        <h3>De officier van justitie wacht op jouw rapport</h3>
        <p>Twee weken data-analyse. Nu visualiseren en een <strong>onderbouwde conclusie</strong> trekken.</p>
        <div class="clue-box"><span class="clue-label">🔍 Centrale vraag</span>
        Is er statistisch bewijs dat één arts verantwoordelijk is? Of zijn er alternatieve verklaringen?</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="card"><div class="card-label">Opdrachten</div><h3>Week 3 — taken</h3>
    <div class="task-item"><span class="task-num">1</span><span><strong>Boxplot</strong> van Sterftequotiënt per arts (Invoegen → Doos en Snorhaar). Welke arts heeft de hoogste mediaan?</span></div>
    <div class="task-item"><span class="task-num">2</span><span><strong>Staafdiagram</strong>: X=Arts, Y=gem. quotiënt per dienst. Titel en asbenamingen toevoegen.</span></div>
    <div class="task-item"><span class="task-num">3</span><span><strong>Lijndiagram</strong>: datum op X-as, overlijdens op Y-as. Kleur datapunten per arts.</span></div>
    <div class="task-item"><span class="task-num">4</span><span><strong>Conclusie</strong> 150–250 woorden in tabblad 'Conclusie'. Gebruik §1–§4 structuur.</span></div>
    <div class="task-item"><span class="task-num">5</span><span>Inleveren als <em>Rapport_Sterfgeval_[leerlingnummer].xlsx</em>.</span></div>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="card"><div class="card-label">Boxplot uitleg</div><h3>Wat zie je?</h3>
        <div class="task-item"><span class="task-num" style="background:#555">Q1</span><span>25% van waarden ligt hieronder</span></div>
        <div class="task-item"><span class="task-num" style="background:#555">M</span><span>Mediaan — middelste waarde</span></div>
        <div class="task-item"><span class="task-num" style="background:#555">Q3</span><span>75% van waarden ligt hieronder</span></div>
        <div class="task-item"><span class="task-num" style="background:#8b1a1a">!</span><span>Uitschieters buiten de snorharen zijn statistisch opvallend</span></div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="card"><div class="card-label">Conclusiestructuur</div><h3>Schrijf je conclusie zo</h3>
        <div class="task-item"><span class="task-num">§1</span><span><strong>Bevinding:</strong> Wat zie je? (1–2 zinnen)</span></div>
        <div class="task-item"><span class="task-num">§2</span><span><strong>Bewijs:</strong> ≥2 getallen of grafieken.</span></div>
        <div class="task-item"><span class="task-num">§3</span><span><strong>Alternatief:</strong> Eén andere mogelijke oorzaak.</span></div>
        <div class="task-item"><span class="task-num">§4</span><span><strong>Oordeel:</strong> Is dit voldoende bewijs? Waarom?</span></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="card"><div class="card-label">Achtergrond</div>
        <h3>De werkelijkheid achter de whodunit</h3>
        <p>Gebaseerd op de zaak van <strong>Lucia de Berk</strong> (2003–2010): veroordeeld op basis van statistisch bewijs dat later verkeerd bleek geïnterpreteerd. In 2010 volledig vrijgesproken.</p>
        <div class="clue-box"><span class="clue-label">🔍 Discussievraag</span>
        Wanneer is statistisch bewijs sterk genoeg om iemand te veroordelen? En wie is verantwoordelijk als de statistiek klopt maar de conclusie fout is?</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="gesloten-stamp"><span>Dossier gesloten</span></div></div>', unsafe_allow_html=True)
    if st.button("← Terug naar het dossier", key="w3_terug"): ga_naar("intro")


# ══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════════
p = st.session_state.pagina
if   p == "intro":            render_intro()
elif p == "week1":            render_week1()
elif p == "week2":            render_week2()
elif p == "week3":            render_week3()
elif p == "docent_login":     render_docent_login()
elif p == "docent_dashboard": render_docent_dashboard()
