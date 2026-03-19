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
.formula-box { background:white; border:1px solid #d4c4a0; padding:0.5rem 0.8rem; font-family:'Courier Prime',monospace; font-size:0.88rem; color:#2d5016; margin:0.4rem 0; user-select:none; -webkit-user-select:none; cursor:default; }
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
              ("dataset_gegenereerd",False),("docent_ingelogd",False),
              ("actieve_groep","alle"),("sla_download_over",False),
              ("toon_download_form",False)]:
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

    # ── Direct naar opdrachten (geen leerlingnummer nodig) ──
    col_direct, col_nieuw = st.columns([1, 1])
    with col_direct:
        if st.button("→ Ik heb al een dataset", key="btn_al_dataset"):
            st.session_state.sla_download_over = True
            ga_naar("week1")
    with col_nieuw:
        if st.button("⬇ Nieuwe dataset downloaden", key="btn_nieuw"):
            st.session_state.toon_download_form = True

    # ── Downloadformulier (alleen zichtbaar na klik op "Nieuwe dataset") ──
    if st.session_state.get("toon_download_form", False):
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="form-label">Stap 1 — Kies je lesgroep</div>', unsafe_allow_html=True)
        lesgroep_keuze = st.radio(
            "lesgroep", options=LESGROEPEN, horizontal=True,
            label_visibility="collapsed", key="lesgroep_radio",
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="form-label">Stap 2 — Voer je leerlingnummer in (6 cijfers)</div>', unsafe_allow_html=True)

        col1, col2 = st.columns([3, 1])
        with col1:
            ln_input = st.text_input("ln", label_visibility="collapsed",
                                     placeholder="bijv. 144555", max_chars=6, key="ln_input_field")
        with col2:
            toegang = st.button("▶ Toegang", key="btn_toegang")

        if toegang or (ln_input and len(ln_input) == 6 and ln_input.isdigit()):
            if ln_input and len(ln_input) == 6 and ln_input.isdigit():
                st.session_state.leerlingnummer      = ln_input
                st.session_state.lesgroep            = lesgroep_keuze
                st.session_state.dataset_gegenereerd = True
                st.session_state.sla_download_over   = False
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
        <div class="wh-eyebrow">Week 1 van 3 &nbsp;·&nbsp; ~90 minuten</div>
        <h2>De Eerste Cijfers</h2>
        <div class="wh-sub">» Iets klopt niet in de sterftecijfers van afdeling C-3 «</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card"><div class="card-label">Context</div>
        <h3>Wat zegt het dossier?</h3>
        <p>Jij bent aangesteld als forensisch statisticus. De afdeling C-3 van Ziekenhuis De Beemsterhof
        registreert elke dienst nauwkeurig: welke arts er aanwezig was, hoeveel patiënten er lagen,
        en hoeveel er die dienst zijn overleden. Jij hebt toegang tot de data van de afgelopen 12 weken.</p>
        <div class="clue-box"><span class="clue-label">🔍 Aanwijzing</span>
        Begin rustig: verken de dataset, maak er een nette tabel van, en bereken de basiscijfers.
        Schrijf bij elke stap in je Word-document wat je hebt gedaan en wat je ziet.</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="card"><div class="card-label">Dataset — structuur</div><h3>Kolommen in jouw bestand</h3>
        <table class="data-table"><thead><tr><th>Kol.</th><th>Inhoud</th></tr></thead><tbody>
        <tr><td>A</td><td>Datum</td></tr>
        <tr><td>B</td><td>Dag</td></tr>
        <tr><td>C</td><td>Weeknummer</td></tr>
        <tr><td>D</td><td>Dienst</td></tr>
        <tr><td>E</td><td>Aanvangstijd</td></tr>
        <tr><td>F</td><td>Arts</td></tr>
        <tr><td>G</td><td>Arts_code</td></tr>
        <tr><td>H</td><td>Verpleegkundige</td></tr>
        <tr><td>I</td><td>Aantal_patienten</td></tr>
        <tr><td>J</td><td>Ontslagen</td></tr>
        <tr><td>K</td><td>Stabiel</td></tr>
        <tr class="highlight-row"><td>L</td><td>Overlijden</td></tr>
        <tr><td>M</td><td>Overlijdenskans_%</td></tr>
        </tbody></table></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="card"><div class="card-label">Opdrachten A — Dataset klaarmaken (§8.1A, §8.2A)</div>
        <h3>Stap 1: nette dataset en verkenning</h3>
        <p style="font-family:'Courier Prime',monospace;font-size:0.85rem;color:#3a2e22;margin-bottom:0.6rem;">
        Een <strong>nette dataset</strong> heeft kolomkoppen, geen lege rijen, en alle gegevens van één
        meting staan in één rij — dat heet een <em>record</em>. Jouw bestand is al netjes opgezet.</p>
        <div class="task-item"><span class="task-num">A1</span>
        <span>Selecteer alle data en maak er een <strong>Excel-tabel</strong> van (Ctrl+T).
        Geef de tabel de naam <em>Beemsterhof</em> via Tabelontwerp → Tabelnaam.
        <br><em>Screenshot + toelichting in Word: wat verandert er zichtbaar?</em></span></div>
        <div class="task-item"><span class="task-num">A2</span>
        <span>Activeer de <strong>totaalrij</strong> (Tabelontwerp → Totaalrij aanvinken).
        Stel per kolom in: gemiddelde voor I (patiënten), maximum voor L (overlijden), aantal voor F (arts).
        <br><em>Screenshot + noteer de drie waarden in Word.</em></span></div>
        <div class="task-item"><span class="task-num">A3</span>
        <span>Gebruik <strong>AutoFilter op Dienst</strong> → filter op "Nachtdienst".
        Hoeveel rijen blijven over? Stel de totaalrij in op gemiddelde voor kolom I.
        Noteer het getal. Verwijder het filter daarna.
        <br><em>Screenshot gefilterde tabel + getal in Word.</em></span></div>
        <div class="task-item"><span class="task-num">A4</span>
        <span>Onderzoek welke dienst(en) opvallen qua hoog sterftecijfer. Gebruik <strong>sorteren</strong>
        om dit te ontdekken. Beschrijf in je Word-document wat je hebt gedaan en wat je ziet —
        welke combinatie van datum en arts komt bovenaan?
        <br><em>Screenshot + bevinding in Word.</em></span></div>
        <div class="task-item"><span class="task-num">A5</span>
        <span>Kolom M toont overlijdenskansen, maar de weergave is nog niet handig leesbaar.
        Pas de <strong>opmaak</strong> aan zodat de waarden duidelijker zijn. Kies zelf een geschikte notatie.
        Gebruik daarna een filter om te bepalen hoeveel diensten je als "verhoogd risico" zou aanmerken —
        kies zelf een grenswaarde en onderbouw die keuze kort in je Word-document.
        <br><em>Screenshot + motivatie grenswaarde in Word.</em></span></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="card"><div class="card-label">Opdrachten B — Formules en verwijzingen (§8.1B)</div>
        <h3>Stap 2: berekeningen op tabblad Analyse</h3>
        <p style="font-family:'Courier Prime',monospace;font-size:0.85rem;color:#3a2e22;margin-bottom:0.6rem;">
        Maak een nieuw tabblad <em>Analyse</em>. Zet alle berekeningen hier neer met duidelijke labels ernaast.
        Een spreadsheet is <strong>dynamisch</strong>: pas je de brondata aan, herberekent Excel direct.</p>
        <div class="task-item"><span class="task-num">B1</span>
        <span>Bereken het <strong>gemiddelde, maximum en minimum</strong> van kolom I (patiënten)
        met <code>=GEMIDDELDE()</code>, <code>=MAX()</code> en <code>=MIN()</code>.
        Gebruik de <strong>vulgreep</strong> (het zwarte vierkantje rechtsonder de cel) om de drie formules
        naast elkaar te plaatsen zonder opnieuw te typen.
        <br><em>Screenshot formules zichtbaar in formulebalk + resultaten in Word.</em></span></div>
        <div class="task-item"><span class="task-num">B2</span>
        <span>Bereken het <strong>gemiddeld aantal overlijdens per dienst</strong> (ochtend, middag, nacht)
        met <code>=GEMIDDELDE.ALS()</code>. Typ de drie dienstnamen in drie cellen en gebruik een
        <strong>absolute verwijzing ($B$2)</strong> voor het criterium — dan kun je de formule doorkopiëren
        zonder dat het criterium meeschuift. Druk F4 om snel te wisselen.
        <br><em>Screenshot met formule + absolute verwijzing zichtbaar in Word.</em></span></div>
        <div class="task-item"><span class="task-num">B3</span>
        <span>Bereken het <strong>totaal overlijdens per arts</strong> met <code>=SOM.ALS()</code>.
        Gebruik ook <code>=AFRONDEN(SOM.ALS(...);0)</code> zodat het resultaat altijd een geheel getal
        toont. Welke arts heeft het hoogste totaal?
        <br><em>Screenshot + conclusie in Word.</em></span></div>
        <div class="task-item"><span class="task-num">B4</span>
        <span>Bereken het <strong>gemiddelde, de mediaan en de standaardafwijking</strong> van het aantal
        overlijdens (gebruik <code>=GEMIDDELDE()</code>, <code>=MEDIAAN()</code>,
        <code>=STDEV.P()</code> over de volledige kolom L). Als mediaan en gemiddelde sterk van elkaar
        afwijken, wat zegt dat over de verdeling?
        <br><em>Screenshot + toelichting in Word.</em></span></div>
        <div class="task-item"><span class="task-num">B5</span>
        <span>Bereken voor het aantal overlijdens: <strong>Q1</strong>, <strong>Q3</strong> en de
        <strong>interkwartielafstand</strong> (IKA = Q3 − Q1) met <code>=KWARTIEL.INC()</code>.
        Bereken ook de uitbijtergrens (Q3 + 1,5 × IKA). Ligt de hoogste waarde in de dataset
        boven deze grens?
        <br><em>Berekeningen + conclusie in Word.</em></span></div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="card"><div class="card-label">Naslagwerk week 1</div><h3>Handige Excel-functies</h3>
    <div class="formula-box">=GEMIDDELDE(Beemsterhof[Aantal_patienten])</div>
    <div class="formula-box">=GEMIDDELDE.ALS(Beemsterhof[Dienst];$B$2;Beemsterhof[Overlijden])</div>
    <div class="formula-box">=SOM.ALS(Beemsterhof[Arts];"Dr. Vermeer";Beemsterhof[Overlijden])</div>
    <div class="formula-box">=AFRONDEN(SOM.ALS(Beemsterhof[Arts];"Dr. Vermeer";Beemsterhof[Overlijden]);0)</div>
    <div class="formula-box">=MEDIAAN(Beemsterhof[Overlijden])</div>
    <div class="formula-box">=STDEV.P(Beemsterhof[Overlijden])</div>
    <div class="formula-box">=KWARTIEL.INC(Beemsterhof[Overlijden];1)   ← Q1</div>
    <div class="formula-box">=KWARTIEL.INC(Beemsterhof[Overlijden];3)   ← Q3</div>
    <div class="clue-box"><span class="clue-label">💡 Absolute vs. relatieve verwijzing</span>
    <code>$B$2</code> verandert niet bij kopiëren. <code>B2</code> wel.
    Klik op het celadres in de formulebalk en druk F4 om te wisselen.</div>
    <div class="clue-box"><span class="clue-label">💡 Vulgreep</span>
    Selecteer een cel met formule. Sleep het zwarte vierkantje rechtsonder naar
    naastliggende cellen om de formule snel door te kopiëren.</div>
    </div>
    <div class="card"><div class="card-label">Inleveren week 1</div><h3>Wat lever je in?</h3>
    <p>Lever aan het einde van week 1 <strong>twee bestanden</strong> in:</p>
    <div class="task-item"><span class="task-num">📄</span><span><strong>Word-document</strong>
    met per opdracht een screenshot en een korte toelichting in eigen woorden.</span></div>
    <div class="task-item"><span class="task-num">📊</span><span><strong>Excel-bestand</strong>
    met tabel Beemsterhof en tabblad Analyse. Naam: <em>Week1_[leerlingnummer].xlsx</em>.</span></div>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("\u2190 Terug", key="w1_terug"): ga_naar("intro")
    with c2:
        if st.button("\u2192 Week 2", key="w1_door"): ga_naar("week2")


# ══════════════════════════════════════════════════════════════════════════════
# WEEK 2
# ══════════════════════════════════════════════════════════════════════════════
def render_week2():
    st.markdown("""
    <div class="progress-bar"><div class="progress-dot active"></div><div class="progress-dot active"></div><div class="progress-dot"></div></div>
    <div class="week-header">
        <div class="wh-eyebrow">Week 2 van 3 &nbsp;·&nbsp; ~90 minuten</div>
        <h2>Verbanden Leggen</h2>
        <div class="wh-sub">» Het patroon begint zichtbaar te worden «</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card"><div class="card-label">Verhaal</div>
        <h3>Nieuwe informatie in het dossier</h3>
        <p>Hoofdarts De Wit wijst erop dat de bezetting sterk wisselt per dienst.
        <em>"Meer patiënten betekent logischerwijs meer risico"</em>, zegt hij.
        Bereken een sterftequotiënt en gebruik een draaitabel om dit per arts én per dienst te vergelijken.</p>
        <div class="clue-box"><span class="clue-label">🔍 Aanwijzing</span>
        Als het quotiënt bij één arts consequent hoger is — ook bij vergelijkbare bezetting —
        dan klopt het argument van De Wit niet.</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="card"><div class="card-label">Opdrachten C — Hercoderen en nieuwe variabelen (§8.2B)</div>
        <h3>Stap 3: data verrijken</h3>
        <p style="font-family:'Courier Prime',monospace;font-size:0.85rem;color:#3a2e22;margin-bottom:0.6rem;">
        Een nieuwe variabele maken op basis van een bestaande heet <strong>hercoderen</strong>.
        Geef bij elke nieuwe kolom aan in je Word-document wat de variabele meet.</p>
        <div class="task-item"><span class="task-num">C1</span>
        <span>Je wilt weten hoe gevaarlijk een dienst was — onafhankelijk van hoe druk het was.
        Bedenk zelf een berekening die dat uitdrukt op basis van kolommen I en L.
        <br>Voeg kolom N toe met de naam <strong>Sterftequotient</strong> en typ je formule in.
        Denk daarna na: wat moet er gebeuren als er nul patiënten waren? Pas je formule aan
        zodat dat geval netjes wordt afgevangen. Stel daarna een geschikte celopmaak in.
        <br><em>Screenshot + toelichting in Word: wat meet dit getal, en hoe heb je het nul-geval opgelost?</em></span></div>
        <div class="task-item"><span class="task-num">C2</span>
        <span>Een getal is soms moeilijker te interpreteren dan een categorie. Dat noemen we
        <strong>hercoderen</strong>. Simpel voorbeeld: je zou leeftijd kunnen hercoderen naar
        "jong / middel / oud" met grenzen op 30 en 60.
        <br>Bedenk zelf welke categorieën zinvol zijn voor het Sterftequotient — denk na: wat is
        "normaal" voor een ziekenhuis, en wanneer wordt het echt verontrustend?
        Voeg kolom O toe met de naam <strong>Risicocategorie</strong> en gebruik een
        <strong>geneste ALS-formule</strong> met jouw grenzen. Vergeet de "geen data"-variant niet.
        Filter daarna op de hoogste categorie: welke arts domineert?
        <br><em>Screenshot gefilterd + toelichting in Word: waarom heb je deze grenzen gekozen?</em></span></div>
        <div class="task-item"><span class="task-num">C3</span>
        <span>Bereken op tabblad Analyse het <strong>gemiddeld sterftequotiënt per arts</strong>
        met <code>=GEMIDDELDE.ALS()</code>. Gebruik absolute verwijzingen voor de artsennamen
        zodat je de formule doorheen kan kopiëren.
        <br><em>Screenshot formules + vier getallen in Word.</em></span></div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="card"><div class="card-label">Opdrachten D — Draaitabellen (§8.3A)</div>
        <h3>Stap 4: patroon analyseren met draaitabellen</h3>
        <p style="font-family:'Courier Prime',monospace;font-size:0.85rem;color:#3a2e22;margin-bottom:0.6rem;">
        Een <strong>draaitabel</strong> vat grote datasets snel samen: je kiest zelf welke variabelen
        op de rijen, kolommen en als waarden staan. Je kunt hem op elk moment aanpassen.</p>
        <div class="task-item"><span class="task-num">D1</span>
        <span>Maak een <strong>draaitabel</strong> (Invoegen → Draaitabel → Nieuw werkblad):
        <em>Rijen = Arts, Kolommen = Dienst, Waarden = Gemiddelde van Sterftequotient</em>.
        Stel in als Percentage met 1 decimaal via Waardeveldinstellingen → Getalnotatie.
        <br><em>Screenshot + toelichting: welke cel valt op?</em></span></div>
        <div class="task-item"><span class="task-num">D2</span>
        <span>Maak een <strong>frequentietabel</strong> met een tweede draaitabel:
        <em>Rijen = Risicocategorie, Waarden = Aantal van Risicocategorie</em>.
        Hoeveel diensten vallen in de categorie "hoog"?
        <br><em>Screenshot + getal in Word.</em></span></div>
        <div class="task-item"><span class="task-num">D3</span>
        <span>Maak een <strong>kruistabel</strong> in een derde draaitabel:
        <em>Rijen = Arts, Kolommen = Risicocategorie, Waarden = Aantal diensten</em>.
        Dit is precies een kruistabel: twee categorische variabelen gekruist.
        <br><em>Screenshot + toelichting: welke arts heeft de meeste "hoog"-diensten?</em></span></div>
        <div class="task-item"><span class="task-num">D4</span>
        <span>Voeg een <strong>tijdlijnfilter</strong> toe aan de draaitabel van D1
        (Draaitabelanalyse → Tijdlijn invoegen → Datum). Filter op de eerste 6 weken.
        Is het patroon hetzelfde als over de volledige 12 weken?
        <br><em>Twee screenshots: gefilterd én volledig, met toelichting.</em></span></div>
        <div class="task-item"><span class="task-num">D5</span>
        <span>Maak een vierde draaitabel om het argument van De Wit te toetsen:
        <em>Rijen = Arts, Waarden = Gemiddelde van Aantal_patienten + Gemiddelde van Sterftequotient</em>.
        Hebben alle artsen een vergelijkbare bezetting? Klopt het argument?
        <br><em>Screenshot + schrijf een alinea in Word: klopt het argument van De Wit?</em></span></div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="card"><div class="card-label">Opdrachten E — Klassenindeling in draaitabel (§8.3B)</div>
        <h3>Stap 5: groeperen in klassen</h3>
        <p style="font-family:'Courier Prime',monospace;font-size:0.85rem;color:#3a2e22;margin-bottom:0.6rem;">
        Je kunt in een draaitabel getalswaarden automatisch <strong>groeperen in klassen</strong>
        (zonder apart te hercoderen). Dit heet <em>groeperen</em>.</p>
        <div class="task-item"><span class="task-num">E1</span>
        <span>Maak een draaitabel met <em>Rijen = Aantal_patienten, Waarden = Aantal</em>.
        Klik met rechtermuisknop op een rij-waarde → Groeperen → stel in: begin 10, einde 50, stapgrootte 10.
        Je krijgt nu een <strong>frequentietabel in klassen</strong> van bezetting.
        <br><em>Screenshot + toelichting in Word: in welke klasse vallen de meeste diensten?</em></span></div>
        <div class="task-item"><span class="task-num">E2</span>
        <span>Voeg aan de draaitabel van E1 als kolom <strong>Arts</strong> toe.
        Je kunt nu per bezettingsklasse zien welke arts er het vaakst aanwezig was.
        Klopt dat met het argument van De Wit?
        <br><em>Screenshot + vergelijking met D5 in Word.</em></span></div>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="card"><div class="card-label">Voorbeeld draaitabel D1</div>
        <h3>Zo kan jouw draaitabel eruit zien</h3>
        <table class="data-table"><thead><tr><th>Arts</th><th>Ochtend</th><th>Middag</th><th>Nacht</th></tr></thead>
        <tbody>
        <tr><td>Dr. E. Bakker</td><td>2,1%</td><td>1,9%</td><td>2,3%</td></tr>
        <tr><td>Dr. R. Jansen</td><td>1,8%</td><td>2,2%</td><td>2,0%</td></tr>
        <tr class="highlight-row"><td>Dr. S. Vermeer</td><td>7,1%</td><td>6,9%</td><td>7,4%</td></tr>
        <tr><td>Dr. M. de Vries</td><td>2,0%</td><td>1,8%</td><td>2,2%</td></tr>
        </tbody></table>
        <div class="clue-box" style="margin-top:0.6rem;"><span class="clue-label">💡 Let op</span>
        De naam van de verdachte in jouw dataset wijkt af van dit voorbeeld!</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="card"><div class="card-label">Naslagwerk week 2</div>
        <h3>Handige formules en tips</h3>
        <div class="formula-box">=ALS([@Aantal_patienten]=0;"n.v.t.";[@Overlijden]/[@Aantal_patienten])</div>
        <div class="formula-box">=GEMIDDELDE.ALS(Beemsterhof[Arts];$A2;Beemsterhof[Sterftequotient])</div>
        <div class="clue-box"><span class="clue-label">💡 Hercoderen</span>
        Een nieuwe kolom op basis van een bestaande heet hercoderen.
        Categorieën maken filteren veel overzichtelijker dan losse getallen.</div>
        <div class="clue-box"><span class="clue-label">💡 Draaitabel: waarden als %</span>
        Rechtsklik op een getal → Waardeveldinstellingen → Getalnotatie → Percentage, 1 decimaal.</div>
        <div class="clue-box"><span class="clue-label">💡 Kruistabel</span>
        Een kruistabel heeft twee categorische variabelen: één in de rijen, één in de kolommen.
        Met een draaitabel maak je die met twee muisklikken.</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="card"><div class="card-label">Inleveren week 2</div><h3>Wat lever je in?</h3>
    <div class="task-item"><span class="task-num">📄</span><span><strong>Word-document</strong>
    uitgebreid met screenshots + toelichtingen van week 2, inclusief de alinea over De Wit (D3).</span></div>
    <div class="task-item"><span class="task-num">📊</span><span><strong>Excel-bestand</strong>
    met kolommen N en O, tabblad Analyse en draaitabellen. Naam: <em>Week2_[leerlingnummer].xlsx</em>.</span></div>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("\u2190 Terug", key="w2_terug"): ga_naar("intro")
    with c2:
        if st.button("\u2192 Week 3", key="w2_door"): ga_naar("week3")


# ══════════════════════════════════════════════════════════════════════════════
# WEEK 3
# ══════════════════════════════════════════════════════════════════════════════
def render_week3():
    st.markdown("""
    <div class="progress-bar"><div class="progress-dot active"></div><div class="progress-dot active"></div><div class="progress-dot active"></div></div>
    <div class="week-header">
        <div class="wh-eyebrow">Week 3 van 3 &nbsp;·&nbsp; ~90 minuten</div>
        <h2>Het Oordeel</h2>
        <div class="wh-sub">» Grafieken, boxplots en eindconclusie «</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card"><div class="card-label">Verhaal</div>
        <h3>De officier van justitie wacht op jouw rapport</h3>
        <p>Je hebt twee weken aan dit dossier gewerkt. Nu is het tijd om de bevindingen te visualiseren
        en een <strong>onderbouwde conclusie</strong> te trekken.</p>
        <div class="clue-box"><span class="clue-label">🔍 Centrale vraag</span>
        Is er statistisch bewijs dat één specifieke arts verantwoordelijk is?
        Of zijn er alternatieve verklaringen?</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="card"><div class="card-label">Opdrachten F — Diagrammen (§8.1C)</div>
        <h3>Stap 6: bevindingen visualiseren</h3>
        <p style="font-family:'Courier Prime',monospace;font-size:0.85rem;color:#3a2e22;margin-bottom:0.6rem;">
        Elk diagram moet beschikken over: een <strong>passende titel</strong>, duidelijke
        <strong>aslabels</strong> en een <strong>legenda</strong> waar nodig.
        Details als kleur en lettertype mogen van het voorbeeld afwijken — zolang het diagram
        maar duidelijk leesbaar is.</p>
        <div class="task-item"><span class="task-num">F1</span>
        <span>Maak een <strong>gegroepeerd staafdiagram</strong> op basis van draaitabel D1:
        artsen op de X-as, sterftequotiënt op de Y-as, drie staven per arts (één per dienst).
        Voeg een titel toe en benoem beide assen.
        <br><em>Screenshot + toelichting: welk patroon zie je direct?</em></span></div>
        <div class="task-item"><span class="task-num">F2</span>
        <span>Maak een <strong>gecombineerd diagram met secundaire as</strong>:
        <em>Primaire as (staafdiagram) = Gemiddelde Aantal_patienten per weeknummer,
        Secundaire as (lijndiagram) = Gemiddelde Sterftequotient per weeknummer</em>.
        Rechtsklik op een serie → Reekstype wijzigen → selecteer Lijn en vink Secundaire as aan.
        Zie je een verband tussen bezetting en sterftequotiënt?
        <br><em>Screenshot + toelichting in Word.</em></span></div>
        <div class="task-item"><span class="task-num">F3</span>
        <span>Maak een <strong>cirkeldiagram</strong> van de Risicocategorie-verdeling
        (gebruik de frequentietabel van D2). Zorg dat de percentages zichtbaar zijn in het diagram.
        <br><em>Screenshot + toelichting: hoe groot is het aandeel "hoog"?</em></span></div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="card"><div class="card-label">Opdrachten G — Draaigrafieken en datum groeperen (§8.3B, §8.3C)</div>
        <h3>Stap 7: dynamische grafieken</h3>
        <p style="font-family:'Courier Prime',monospace;font-size:0.85rem;color:#3a2e22;margin-bottom:0.6rem;">
        Een <strong>draaigrafiek</strong> is gekoppeld aan een draaitabel: pas je het filter aan,
        past de grafiek direct mee. Je kunt ook datums <strong>groeperen</strong> (op week of maand)
        zodat je trends over de tijd kunt zien.</p>
        <div class="task-item"><span class="task-num">G1</span>
        <span>Maak een nieuwe draaitabel: <em>Rijen = Datum, Waarden = Som van Overlijden</em>.
        Maak hiervan een <strong>draaigrafiek</strong> (Draaitabelanalyse → Draaigrafiek → Lijndiagram).
        Koppel het tijdlijnfilter aan deze grafiek. Filter op de laatste 4 weken.
        <br><em>Screenshot volledig lijndiagram + screenshot gefilterd, met toelichting.</em></span></div>
        <div class="task-item"><span class="task-num">G2</span>
        <span><strong>Groepeer de datums op week</strong>: klik rechts op een datum in de draaitabel →
        Groeperen → selecteer Weken. Je krijgt nu een lijndiagram per week in plaats van per dag.
        Is de wekelijkse trend beter zichtbaar dan de dagelijkse?
        <br><em>Screenshot voor én na groeperen, met toelichting.</em></span></div>
        <div class="task-item"><span class="task-num">G3</span>
        <span>Voeg aan de draaigrafiek van G1 een <strong>filter op Arts</strong> toe
        (sleep Arts naar het veld "Legenda" in het draaitabelpaneel).
        De grafiek toont nu een aparte lijn per arts. Welke arts veroorzaakt de pieken?
        <br><em>Screenshot + toelichting in Word.</em></span></div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="card"><div class="card-label">Opdrachten H — Boxplots en uitbijters (§8.1D)</div>
        <h3>Stap 8: spreiding per arts vergelijken</h3>
        <div class="task-item"><span class="task-num">H1</span>
        <span>Maak op een nieuw tabblad <em>BoxplotData</em> vier kolommen — één per arts —
        met behulp van AutoFilter: filter per arts, kopieer de Sterftequotient-waarden naar de
        bijbehorende kolom, verwijder het filter, herhaal voor de volgende arts.
        Maak van de vier kolommen één <strong>boxplot</strong>
        (Invoegen → Statistisch diagram → Doos en Snorhaar).
        <br><em>Screenshot + toelichting: welke arts heeft de hoogste mediaan en de meeste uitbijters?</em></span></div>
        <div class="task-item"><span class="task-num">H2</span>
        <span>Bereken op tabblad Analyse voor de verdachte arts:
        Q1, Q3, IKA (= Q3 − Q1) en de <strong>uitbijtergrens</strong> (Q3 + 1,5 × IKA) met
        <code>=KWARTIEL.INC()</code>. Is de hoogste waarde in de dataset een uitbijter?
        Leg uit wat een uitbijter statistisch betekent.
        <br><em>Berekening + conclusie in Word.</em></span></div>
        <div class="task-item"><span class="task-num">H3</span>
        <span><strong>Vergelijk twee boxplots</strong>: de verdachte arts vs. de overige drie samen.
        Filter de overige drie artsen samen als één groep op het BoxplotData-tabblad.
        Gebruik de vuistregels:<br>
        — Boxen overlappen niet → <em>groot verschil</em><br>
        — Mediaan ene buiten box andere → <em>middelmatig verschil</em><br>
        — Anders → <em>gering verschil</em><br>
        Pas dit toe op jouw boxplots. Hoe groot is het verschil?
        <br><em>Screenshot + conclusie in Word.</em></span></div>
        <div class="task-item"><span class="task-num">H4</span>
        <span>Bereken ook de <strong>mediaan</strong> van het sterftequotiënt per arts
        (<code>=MEDIAAN()</code>). Vergelijk mediaan en gemiddelde per arts.
        Een groot verschil wijst op uitbijters of een scheve verdeling — is dat hier het geval?
        <br><em>Screenshot vergelijkingstabel + toelichting in Word.</em></span></div>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="card"><div class="card-label">Boxplot — begrippen</div><h3>Wat zie je?</h3>
        <div class="task-item"><span class="task-num" style="background:#555">Q0</span>
        <span>Minimum (excl. uitbijters)</span></div>
        <div class="task-item"><span class="task-num" style="background:#555">Q1</span>
        <span>Eerste kwartiel — 25% ligt hieronder</span></div>
        <div class="task-item"><span class="task-num" style="background:#555">M</span>
        <span>Mediaan — middelste waarde</span></div>
        <div class="task-item"><span class="task-num" style="background:#555">Q3</span>
        <span>Derde kwartiel — 75% ligt hieronder</span></div>
        <div class="task-item"><span class="task-num" style="background:#555">Q4</span>
        <span>Maximum (excl. uitbijters)</span></div>
        <div class="task-item"><span class="task-num" style="background:#8b1a1a">!</span>
        <span>Uitbijter: verder dan 1,5 × IKA van de box</span></div>
        <div class="clue-box" style="margin-top:0.5rem;"><span class="clue-label">Twee boxplots vergelijken</span>
        Boxen overlappen niet → groot verschil<br>
        Mediaan ene buiten box andere → middelmatig<br>
        Anders → gering verschil</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="card"><div class="card-label">Naslagwerk week 3</div><h3>Formules en tips</h3>
        <div class="formula-box">=KWARTIEL.INC(bereik;1)   ← Q1</div>
        <div class="formula-box">=KWARTIEL.INC(bereik;3)   ← Q3</div>
        <div class="formula-box">=MEDIAAN(bereik)</div>
        <div class="clue-box"><span class="clue-label">💡 Gecombineerd diagram</span>
        Rechtsklik op een dataserie → Reekstype wijzigen →
        kies Lijn voor secundaire as.</div>
        <div class="clue-box"><span class="clue-label">💡 Draaigrafiek</span>
        Selecteer de draaitabel → Draaitabelanalyse → Draaigrafiek.
        De grafiek filtert automatisch mee met het tijdlijnfilter.</div>
        <div class="clue-box"><span class="clue-label">💡 Datums groeperen</span>
        Rechtsklik op een datum in de draaitabel → Groeperen →
        kies Weken of Maanden. Zo ontstaat een overzichtelijker trendlijn.</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="card"><div class="card-label">Opdracht I — Eindconclusie</div>
        <h3>Stap 9: jij sluit het dossier</h3>
        <div class="task-item"><span class="task-num">I1</span>
        <span>Schrijf je <strong>eindconclusie</strong> (150–250 woorden) in je Word-document
        volgens §1–§4 hieronder. Verwijs expliciet naar ten minste twee grafieken of berekeningen
        als bewijs.</span></div>
        <div class="task-item"><span class="task-num">I2</span>
        <span><strong>Discussievraag</strong> (optioneel, 3–5 zinnen): dit scenario is gebaseerd op de
        zaak van <strong>Lucia de Berk</strong> (2003–2010). Zij werd mede veroordeeld op basis van
        statistisch bewijs dat later verkeerd bleek geïnterpreteerd. In 2010 volledig vrijgesproken.<br>
        Wanneer is een statistisch patroon sterk genoeg om iemand te veroordelen?</span></div>
    </div>
    <div class="card"><div class="card-label">Conclusiestructuur §1–§4</div>
    <div class="task-item"><span class="task-num">§1</span>
    <span><strong>Bevinding:</strong> Wat zie je in de data? (1–2 zinnen)</span></div>
    <div class="task-item"><span class="task-num">§2</span>
    <span><strong>Bewijs:</strong> Minimaal 2 specifieke getallen of grafieken.</span></div>
    <div class="task-item"><span class="task-num">§3</span>
    <span><strong>Alternatieve verklaring:</strong> Eén andere mogelijke oorzaak.</span></div>
    <div class="task-item"><span class="task-num">§4</span>
    <span><strong>Oordeel:</strong> Is dit voldoende statistisch bewijs? Waarom wel/niet?</span></div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="card"><div class="card-label">Inleveren week 3 — eindopdracht</div><h3>Wat lever je in?</h3>
    <p>Dit is je definitieve inlevering. Twee bestanden:</p>
    <div class="task-item"><span class="task-num">📄</span><span><strong>Word-document</strong>
    met alle screenshots week 1 t/m 3, toelichtingen en eindconclusie (§1–§4).
    Naam: <em>Rapport_Sterfgeval_[leerlingnummer].docx</em>.</span></div>
    <div class="task-item"><span class="task-num">📊</span><span><strong>Excel-bestand</strong>
    met alle analyses, kolommen N en O, draaitabellen en grafieken.
    Naam: <em>Rapport_Sterfgeval_[leerlingnummer].xlsx</em>.</span></div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="gesloten-stamp"><span>Dossier gesloten</span></div></div>', unsafe_allow_html=True)
    if st.button("\u2190 Terug naar het dossier", key="w3_terug"): ga_naar("intro")


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
