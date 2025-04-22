import sqlite3, json
from pathlib import Path

ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx'}
MAX_FILE_SIZE = 10 * 1024 * 1024

def insert_tender(datum_objave, naziv_predmeta, vrsta_dokumenta, vrsta_ugovora, vrsta_postupka, cpv, prilozi):
    conn = sqlite3.connect('database.db'); c = conn.cursor()
    c.execute('INSERT INTO tenders (datum_objave, naziv_predmeta, vrsta_dokumenta, vrsta_ugovora, vrsta_postupka, cpv, prilozi) VALUES (?, ?, ?, ?, ?, ?, ?)',
              (datum_objave, naziv_predmeta, vrsta_dokumenta, vrsta_ugovora, vrsta_postupka, cpv, json.dumps(prilozi)))
    conn.commit(); conn.close()

def get_all_tenders():
    conn = sqlite3.connect('database.db'); c = conn.cursor()
    c.execute('SELECT * FROM tenders ORDER BY datum_objave DESC')
    rows = c.fetchall(); conn.close(); return rows

def get_filtered_tenders(vrsta_dokumenta, vrsta_ugovora, vrsta_postupka, from_date, to_date, cpv):
    conn = sqlite3.connect('database.db'); c = conn.cursor()
    query = "SELECT * FROM tenders WHERE 1=1 "; params = []
    if vrsta_dokumenta and vrsta_dokumenta != 'Odaberi':
        query += "AND vrsta_dokumenta = ? "; params.append(vrsta_dokumenta)
    if vrsta_ugovora and vrsta_ugovora != 'Odaberi':
        query += "AND vrsta_ugovora = ? "; params.append(vrsta_ugovora)
    if vrsta_postupka and vrsta_postupka != 'Odaberi':
        query += "AND vrsta_postupka = ? "; params.append(vrsta_postupka)
    if from_date and to_date:
        query += "AND datum_objave BETWEEN ? AND ? "; params.extend([from_date, to_date])
    if cpv:
        query += "AND CAST(cpv AS TEXT) LIKE ? "; params.append(f'%{cpv}%')
    c.execute(query, params); rows = c.fetchall(); conn.close(); return rows

def get_tender_by_id(i):
    conn = sqlite3.connect('database.db'); c = conn.cursor()
    c.execute('SELECT * FROM tenders WHERE id = ?', (i,)); row = c.fetchone(); conn.close(); return row

def update_tender(i, datum, naziv, doc, ug, post, cpv, prilozi):
    conn = sqlite3.connect('database.db'); c = conn.cursor()
    c.execute('UPDATE tenders SET datum_objave = ?, naziv_predmeta = ?, vrsta_dokumenta = ?, vrsta_ugovora = ?, vrsta_postupka = ?, cpv = ?, prilozi = ? WHERE id = ?',
              (datum, naziv, doc, ug, post, cpv, json.dumps(prilozi), i))
    conn.commit(); conn.close()

def delete_tender(i):
    conn = sqlite3.connect('database.db'); c = conn.cursor()
    c.execute('DELETE FROM tenders WHERE id = ?', (i,)); conn.commit(); conn.close()

def upload_files(files):
    saved = []
    folder = Path('uploads'); folder.mkdir(exist_ok=True)
    for f in files:
        ext = Path(f.name).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS or f.size > MAX_FILE_SIZE:
            continue
        path = folder / f.name
        with open(path, 'wb') as out:
            out.write(f.getbuffer())
        saved.append(f.name)
    return saved
