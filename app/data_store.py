"""Almacen generico REAL (Postgres/Neon con fallback SQLite). Guarda cualquier
entidad como JSON -> persistencia server-side multi-dispositivo para todo CRUD."""
import os, json
DATABASE_URL = os.environ.get("DATABASE_URL"); _PG = bool(DATABASE_URL)
if _PG:
    import psycopg
    _PH = "%s"
else:
    import sqlite3
    _PH = "?"; _PATH = os.environ.get("SQLITE_PATH", "/tmp/app.db")
def _c():
    if _PG: return psycopg.connect(DATABASE_URL, autocommit=True)
    return sqlite3.connect(_PATH)
def init_db():
    pk = "SERIAL PRIMARY KEY" if _PG else "INTEGER PRIMARY KEY AUTOINCREMENT"
    con = _c()
    try:
        cur = con.cursor()
        cur.execute(f"CREATE TABLE IF NOT EXISTS records (id {pk}, entity TEXT, data TEXT)")
        if not _PG: con.commit()
    finally: con.close()
def _ensure():
    try: init_db()
    except Exception: pass
def listar(entity):
    _ensure(); con = _c()
    try:
        cur = con.cursor(); cur.execute(f"SELECT id, data FROM records WHERE entity = {_PH} ORDER BY id DESC", [entity])
        out = []
        for r in cur.fetchall():
            d = json.loads(r[1]) if r[1] else {}; d["id"] = r[0]; out.append(d)
        return out
    finally: con.close()
def crear(entity, data):
    _ensure(); con = _c()
    try:
        cur = con.cursor()
        if _PG:
            cur.execute(f"INSERT INTO records (entity, data) VALUES ({_PH},{_PH}) RETURNING id", [entity, json.dumps(data)]); nid = cur.fetchone()[0]
        else:
            cur.execute(f"INSERT INTO records (entity, data) VALUES ({_PH},{_PH})", [entity, json.dumps(data)]); con.commit(); nid = cur.lastrowid
        return {**data, "id": nid}
    finally: con.close()
def actualizar(entity, rid, data):
    _ensure(); con = _c()
    try:
        cur = con.cursor(); cur.execute(f"UPDATE records SET data = {_PH} WHERE id = {_PH} AND entity = {_PH}", [json.dumps(data), rid, entity])
        if not _PG: con.commit()
        return {**data, "id": rid}
    finally: con.close()
def borrar(entity, rid):
    _ensure(); con = _c()
    try:
        cur = con.cursor(); cur.execute(f"DELETE FROM records WHERE id = {_PH} AND entity = {_PH}", [rid, entity])
        if not _PG: con.commit()
        return {"ok": True}
    finally: con.close()
