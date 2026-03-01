"""
Download logger voor Operatie Sterfgeval — SQLite backend.
De database wordt automatisch aangemaakt als die nog niet bestaat.
Op Streamlit Community Cloud: gebruik een persistent pad via st.secrets of
sla de db op in een gemounte volume. Standaard staat de db naast app.py.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager

DB_PAD = Path(__file__).parent / "sterfgeval.db"
DOCENT_WACHTWOORD = "beemsterhof2024"   # ← pas dit aan!


# ── Database setup ────────────────────────────────────────────────────────────

@contextmanager
def _verbinding():
    """Context manager: opent verbinding, commit bij succes, sluit altijd."""
    con = sqlite3.connect(DB_PAD, check_same_thread=False)
    con.row_factory = sqlite3.Row          # rijen als dict-achtige objecten
    con.execute("PRAGMA journal_mode=WAL") # betere concurrency
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def initialiseer_db():
    """Maak de tabel aan als die nog niet bestaat. Veilig meerdere keren aan te roepen."""
    with _verbinding() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS downloads (
                id                INTEGER PRIMARY KEY AUTOINCREMENT,
                leerlingnummer    TEXT    NOT NULL UNIQUE,
                arts_verdachte    TEXT    NOT NULL,
                eerste_download   TEXT    NOT NULL,
                laatste_download  TEXT    NOT NULL,
                aantal_downloads  INTEGER NOT NULL DEFAULT 1
            )
        """)
        # Index voor snelle opzoekacties per leerlingnummer
        con.execute("""
            CREATE INDEX IF NOT EXISTS idx_leerlingnummer
            ON downloads (leerlingnummer)
        """)


# ── Publieke API ──────────────────────────────────────────────────────────────

def log_download(leerlingnummer: str, arts_naam: str):
    """
    Registreer een download.
    - Nieuw leerlingnummer  → nieuwe rij
    - Bestaand nummer       → teller +1, laatste_download bijwerken
    """
    initialiseer_db()
    nu = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    with _verbinding() as con:
        bestaand = con.execute(
            "SELECT id FROM downloads WHERE leerlingnummer = ?",
            (str(leerlingnummer),)
        ).fetchone()

        if bestaand:
            con.execute("""
                UPDATE downloads
                SET aantal_downloads  = aantal_downloads + 1,
                    laatste_download  = ?
                WHERE leerlingnummer  = ?
            """, (nu, str(leerlingnummer)))
        else:
            con.execute("""
                INSERT INTO downloads
                    (leerlingnummer, arts_verdachte, eerste_download, laatste_download, aantal_downloads)
                VALUES (?, ?, ?, ?, 1)
            """, (str(leerlingnummer), arts_naam, nu, nu))


def haal_log_op() -> list[dict]:
    """
    Geeft alle downloads terug als lijst van dicts,
    gesorteerd op eerste_download (nieuwste eerst).
    """
    initialiseer_db()
    with _verbinding() as con:
        rijen = con.execute("""
            SELECT
                leerlingnummer,
                arts_verdachte,
                eerste_download,
                laatste_download,
                aantal_downloads  AS downloads
            FROM downloads
            ORDER BY eerste_download DESC
        """).fetchall()
    return [dict(r) for r in rijen]


def zoek_leerling(leerlingnummer: str) -> dict | None:
    """Geef de logregel voor één specifiek leerlingnummer, of None."""
    initialiseer_db()
    with _verbinding() as con:
        rij = con.execute(
            "SELECT * FROM downloads WHERE leerlingnummer = ?",
            (str(leerlingnummer),)
        ).fetchone()
    return dict(rij) if rij else None


def verwijder_leerling(leerlingnummer: str) -> bool:
    """Verwijder een leerling uit de log (handig voor herstel/testdata). Geeft True bij succes."""
    initialiseer_db()
    with _verbinding() as con:
        cur = con.execute(
            "DELETE FROM downloads WHERE leerlingnummer = ?",
            (str(leerlingnummer),)
        )
    return cur.rowcount > 0


def statistieken() -> dict:
    """Geeft een samenvatting terug voor het docentendashboard."""
    initialiseer_db()
    with _verbinding() as con:
        n_leerlingen = con.execute(
            "SELECT COUNT(*) FROM downloads"
        ).fetchone()[0]

        n_downloads = con.execute(
            "SELECT COALESCE(SUM(aantal_downloads), 0) FROM downloads"
        ).fetchone()[0]

        per_arts = con.execute("""
            SELECT arts_verdachte, COUNT(*) AS cnt
            FROM downloads
            GROUP BY arts_verdachte
            ORDER BY cnt DESC
        """).fetchall()

        recent = con.execute("""
            SELECT leerlingnummer, arts_verdachte, laatste_download
            FROM downloads
            ORDER BY laatste_download DESC
            LIMIT 5
        """).fetchall()

    return {
        "n_leerlingen":  n_leerlingen,
        "n_downloads":   n_downloads,
        "per_arts":      [dict(r) for r in per_arts],
        "recent":        [dict(r) for r in recent],
    }


def controleer_wachtwoord(ww: str) -> bool:
    return ww.strip() == DOCENT_WACHTWOORD


def log_als_csv() -> str:
    """Exporteer de volledige log als CSV-string."""
    log = haal_log_op()
    regels = ["Leerlingnummer,Verdachte arts,Eerste download,Laatste download,Aantal downloads"]
    for r in log:
        regels.append(
            f"{r['leerlingnummer']},{r['arts_verdachte']},"
            f"{r['eerste_download']},{r['laatste_download']},{r['downloads']}"
        )
    return "\n".join(regels)
