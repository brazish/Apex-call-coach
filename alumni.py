import json
import os
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path("alumni_db.json")

def load_db():
    if not DB_PATH.exists():
        return {"clients": []}
    try:
        return json.loads(DB_PATH.read_text())
    except:
        return {"clients": []}

def save_db(db):
    DB_PATH.write_text(json.dumps(db, indent=2, default=str))

def add_client(name, phone, discharge_date, notes=""):
    db = load_db()
    client_id = f"ppr_{int(datetime.now().timestamp())}"
    phone_clean = phone.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if not phone_clean.startswith("+"):
        phone_clean = "+1" + phone_clean
    client = {
        "id": client_id,
        "name": name,
        "phone": phone_clean,
        "discharge_date": str(discharge_date),
        "notes": notes,
        "status": "active",
        "flag": None,
        "conversations": [],
        "scheduled": {
            "24h": False,
            "72h": False,
            "7d": False
        },
        "created_at": str(datetime.now())
    }
    db["clients"].append(client)
    save_db(db)
    return client_id

def get_client(client_id):
    db = load_db()
    for c in db["clients"]:
        if c["id"] == client_id:
            return c
    return None

def add_message(client_id, role, body, sid=None):
    """role: 'outbound' or 'inbound'"""
    db = load_db()
    for c in db["clients"]:
        if c["id"] == client_id:
            c["conversations"].append({
                "role": role,
                "body": body,
                "sid": sid,
                "timestamp": str(datetime.now())
            })
            save_db(db)
            return
    raise ValueError(f"Client {client_id} not found")

def set_flag(client_id, flag_type, message=""):
    """flag_type: 'relapse', 'crisis', 'interested', 'no_response', None"""
    db = load_db()
    for c in db["clients"]:
        if c["id"] == client_id:
            c["flag"] = {"type": flag_type, "message": message, "at": str(datetime.now())}
            save_db(db)
            return

def mark_scheduled(client_id, checkpoint):
    db = load_db()
    for c in db["clients"]:
        if c["id"] == client_id:
            c["scheduled"][checkpoint] = True
            save_db(db)
            return

def get_due_checkpoints(client):
    """Returns list of checkpoints that are due but not yet sent"""
    discharge = datetime.fromisoformat(str(client["discharge_date"]))
    now = datetime.now()
    due = []
    checkpoints = {
        "24h":  discharge + timedelta(hours=24),
        "72h":  discharge + timedelta(hours=72),
        "7d":   discharge + timedelta(days=7),
    }
    for key, send_time in checkpoints.items():
        if now >= send_time and not client["scheduled"].get(key, False):
            due.append(key)
    return due

def get_all_clients():
    return load_db().get("clients", [])

def update_client_status(client_id, status):
    db = load_db()
    for c in db["clients"]:
        if c["id"] == client_id:
            c["status"] = status
            save_db(db)
            return
