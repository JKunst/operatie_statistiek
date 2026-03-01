# Operatie Sterfgeval — Streamlit Website

Forensisch statistisch onderzoek voor HAVO/VWO wiskunde bovenbouw (3 weken).

## Installeren & starten

```bash
# 1. Zorg dat Python 3.9+ is geïnstalleerd
# 2. Installeer de benodigde packages:
pip install -r requirements.txt

# 3. Start de website:
streamlit run app.py
```

De website opent automatisch op http://localhost:8501

## Structuur

```
operatie_sterfgeval/
├── app.py                  ← Streamlit website (alle pagina's)
├── dataset_generator.py    ← Excel-generator (geïmporteerd door app.py)
├── download_logger.py      ← SQLite-backend voor downloadregistratie
├── requirements.txt        ← Python packages
├── sterfgeval.db           ← SQLite database (automatisch aangemaakt)
└── README.md
```

## Docentenpagina

Bereikbaar via de kleine `· · ·` knop rechtsonder op de introductie-pagina.

**Standaard wachtwoord:** `beemsterhof2024`
Pas dit aan in `download_logger.py` regel 14: `DOCENT_WACHTWOORD = "..."`.

Het dashboard toont:
- Hoeveel leerlingen een dataset hebben gedownload
- Welke verdachte arts bij elk leerlingnummer hoort
- Eerste en laatste downloadtijd, plus aantal downloads
- Opzoekfunctie per leerlingnummer
- Verwijder-knop per leerling (handig bij testdata)
- CSV-export van de volledige log

## SQLite database

De database `sterfgeval.db` wordt automatisch aangemaakt naast `app.py`.
Bij **Streamlit Community Cloud** reset het bestandssysteem bij elke herstart.
Oplossingen voor permanente opslag in de cloud:

1. **Externe database** — vervang `DB_PAD` in `download_logger.py` door een
   PostgreSQL/MySQL connection string via `st.secrets`.
2. **Eigen server** — draai de app op een VPS of schoolserver met een persistent
   bestandssysteem. Dan werkt SQLite gewoon.

## Dataset handmatig genereren (batch)

```bash
# Één leerling:
python dataset_generator.py 144555

# Hele klas:
python dataset_generator.py 144555 144556 144557 144558
```

## Online zetten (gratis)

De makkelijkste manier is **Streamlit Community Cloud**:
1. Zet de map in een GitHub repository
2. Ga naar https://share.streamlit.io
3. Koppel je GitHub repo en kies `app.py` als hoofdbestand
4. Klaar — je leerlingen krijgen een publieke URL

## Hoe werkt de dataset?

- Elk 6-cijferig leerlingnummer genereert **deterministisch** dezelfde unieke dataset
- De "verdachte arts" wisselt per leerlingnummer (4 rotaties)
- 252 rijen: 12 weken × 7 dagen × 3 diensten
- Sterftekans verdachte arts: ~6-8% vs. normaal ~1.5-2.5%
- Rijen zijn gekleurd: rood = ≥2 overlijdens, groen = 0 overlijdens

## Aanpassen

- **Artsennamen wijzigen**: pas `ARTSEN` aan in `dataset_generator.py`
- **Meer weken**: pas `WEKEN` aan in `dataset_generator.py`
- **Klassen beheren**: genereer batch-gewijs met `python dataset_generator.py [nrs...]`
# operatie_statistiek
