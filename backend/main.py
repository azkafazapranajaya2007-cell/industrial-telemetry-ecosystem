from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel
import sqlite3
import os
from datetime import datetime

app = FastAPI(title="Zenith Industrial Telemetry Gateway", version="2.0.0")

API_KEY_SECRET = "zenith_secret_key_2026"
DB_PATH = "/app/data/telemetry.db"

def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            pressure_bar REAL,
            conveyor_rpm INTEGER,
            status TEXT,
            received_at TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            message TEXT,
            triggered_at TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

class TelemetryPayload(BaseModel):
    device_id: str
    pressure_bar: float
    conveyor_rpm: int
    status: str

@app.post("/api/telemetry")
def receive_telemetry(payload: TelemetryPayload, x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET:
        raise HTTPException(status_code=403, detail="Unauthorized: Invalid API Key")
    
    received_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO telemetry (device_id, pressure_bar, conveyor_rpm, status, received_at)
        VALUES (?, ?, ?, ?, ?)
    """, (payload.device_id, payload.pressure_bar, payload.conveyor_rpm, payload.status, received_at))
    
    if payload.pressure_bar > 5.2 or payload.status.upper() == "WARNING":
        alert_msg = f"WARNING: Tekanan tinggi terdeteksi ({payload.pressure_bar} bar) pada perangkat {payload.device_id}!"
        cursor.execute("""
            INSERT INTO alerts (device_id, message, triggered_at)
            VALUES (?, ?, ?)
        """, (payload.device_id, alert_msg, received_at))

    conn.commit()
    conn.close()
    
    return {"status": "success", "message": "Data telemetri aman dan berhasil disimpan dengan sistem alert."}

@app.get("/api/telemetry")
def get_telemetry(limit: int = 20):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM telemetry ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    
    cursor.execute("SELECT * FROM alerts ORDER BY id DESC LIMIT 5")
    alert_rows = cursor.fetchall()
    
    conn.close()
    
    data = [dict(row) for row in rows]
    alerts = [dict(row) for row in alert_rows]
    
    return {"status": "success", "data": data, "alerts": alerts}
