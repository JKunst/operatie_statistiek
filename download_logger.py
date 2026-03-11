"""
Download logger voor Operatie Sterfgeval — SQLite backend.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager

DB_PAD = Path(__file__).parent / "sterfgeval.db"
DOCENT_WACHTWOORD = "beemsterhof2024"   # ← pas dit aan!
LESGROEPEN = ["h4wia1", "h4wia2", "h4wia3", "h4wia4"]


@contextmanager
def _verbinding():
    con = sqlite3.connect(DB_PAD, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def initialiseer_db():
    with _verbinding() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS downloads (
                id                INTEGER PRIMARY KEY AUTOINCREMENT,
                leerlingnummer    TEXT    NOT NULL UNIQUE,
                lesgroep          TEXT    NOT NULL,
                arts_verdachte    TEXT    NOT NULL,
                eerste_download   TEXT    NOT NULL,
                laatste_download  TEXT    NOT NULL
            )
        """)
        # Migratie: voeg lesgroep kolom toe als die nog niet bestaat (voor bestaande db's)
        try:
            con.execute("ALTER TABLE downloads ADD COLUMN lesgroep TEXT NOT NULL DEFAULT 'onbekend'")
        except Exception:
            pass  # kolom bestaat al
        con.execute("""
            CREATE INDEX IF NOT EXISTS idx_leerlingnummer ON downloads (leerlingnummer)
        """)
        con.execute("""
            CREATE INDEX IF NOT EXISTS idx_lesgroep ON downloads (lesgroep)
        """)


def log_download(leerlingnummer: str, lesgroep: str, arts_naam: str):
    initialiseer_db()
    nu = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    with _verbinding() as con:
        bestaand = con.execute(
            "SELECT id FROM downloads WHERE leerlingnummer = ?", (str(leerlingnummer),)
        ).fetchone()
        if bestaand:
            con.execute("""
                UPDATE downloads SET laatste_download = ?, lesgroep = ?
                WHERE leerlingnummer = ?
            """, (nu, lesgroep, str(leerlingnummer)))
        else:
            con.execute("""
                INSERT INTO downloads (leerlingnummer, lesgroep, arts_verdachte, eerste_download, laatste_download)
                VALUES (?, ?, ?, ?, ?)
            """, (str(leerlingnummer), lesgroep, arts_naam, nu, nu))


def haal_log_op(lesgroep: str = None) -> list[dict]:
    initialiseer_db()
    with _verbinding() as con:
        if lesgroep:
            rijen = con.execute("""
                SELECT leerlingnummer, lesgroep, arts_verdachte, eerste_download, laatste_download
                FROM downloads WHERE lesgroep = ?
                ORDER BY leerlingnummer ASC
            """, (lesgroep,)).fetchall()
        else:
            rijen = con.execute("""
                SELECT leerlingnummer, lesgroep, arts_verdachte, eerste_download, laatste_download
                FROM downloads ORDER BY lesgroep ASC, leerlingnummer ASC
            """).fetchall()
    return [dict(r) for r in rijen]


def zoek_leerling(leerlingnummer: str) -> dict | None:
    initialiseer_db()
    with _verbinding() as con:
        rij = con.execute(
            "SELECT * FROM downloads WHERE leerlingnummer = ?", (str(leerlingnummer),)
        ).fetchone()
    return dict(rij) if rij else None


def verwijder_leerling(leerlingnummer: str) -> bool:
    initialiseer_db()
    with _verbinding() as con:
        cur = con.execute("DELETE FROM downloads WHERE leerlingnummer = ?", (str(leerlingnummer),))
    return cur.rowcount > 0


def statistieken() -> dict:
    initialiseer_db()
    with _verbinding() as con:
        n_leerlingen = con.execute("SELECT COUNT(*) FROM downloads").fetchone()[0]
        per_arts = con.execute("""
            SELECT arts_verdachte, COUNT(*) AS cnt FROM downloads
            GROUP BY arts_verdachte ORDER BY cnt DESC
        """).fetchall()
        per_groep = con.execute("""
            SELECT lesgroep, COUNT(*) AS cnt FROM downloads
            GROUP BY lesgroep ORDER BY lesgroep ASC
        """).fetchall()
    return {
        "n_leerlingen": n_leerlingen,
        "per_arts":     [dict(r) for r in per_arts],
        "per_groep":    [dict(r) for r in per_groep],
    }


def controleer_wachtwoord(ww: str) -> bool:
    return ww.strip() == DOCENT_WACHTWOORD


def log_als_csv(lesgroep: str = None) -> str:
    log = haal_log_op(lesgroep)
    regels = ["Leerlingnummer,Lesgroep,Verdachte arts,Eerste download,Laatste download"]
    for r in log:
        regels.append(
            f"{r['leerlingnummer']},{r['lesgroep']},{r['arts_verdachte']},"
            f"{r['eerste_download']},{r['laatste_download']}"
        )
    return "\n".join(regels)
