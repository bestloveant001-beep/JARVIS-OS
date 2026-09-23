#!/usr/bin/env python3
"""
JARVIS OS — รันบน TrebEbit โดยตรง
"""
import os
import sys
import json
import time
import urllib.request
import subprocess
import sqlite3
import base64
from datetime import datetime

DATA_DIR = "./jarvis_data"
DB_FILE = f"{DATA_DIR}/memory.db"
GITHUB_SYNC = os.getenv("ENABLE_GITHUB_SYNC", "true") == "true"
REPO = "bestloveant001-beep/JARVIS-OS"
TOKEN = "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"

def init_system():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(f"{DATA_DIR}/scripts", exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS scripts (
        id TEXT PRIMARY KEY,
        name TEXT,
        desc TEXT,
        keywords TEXT,
        code TEXT,
        source TEXT,
        updated_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS memory (
        key TEXT PRIMARY KEY,
        value TEXT,
        updated_at TEXT
    )""")
    conn.commit()
    conn.close()
    print("✅ JARVIS พร้อมทำงานบน TrebEbit")


def github_action(action, path="", content=""):
    if not TOKEN or not REPO:
        return "⚠️ ยังไม่ได้ตั้งค่า GitHub"
    
    api = f"https://api.github.com/repos/{REPO}/contents/{path}"
    headers = {
        "Authorization": f"token {TOKEN}",
        "User-Agent": "JARVIS-TrebEbit"
    }

    if action == "pull":
        try:
            req = urllib.request.Request(api, headers=headers)
            resp = urllib.request.urlopen(req)
            data = json.loads(resp.read())
            return base64.b64decode(data["content"]).decode("utf-8")
        except Exception as e:
            return f"❌ ดึงไม่ได้: {e}"

    if action == "push":
        try:
            sha = None
            try:
                r = urllib.request.urlopen(urllib.request.Request(api, headers=headers))
                resp_data = json.loads(r.read())
                sha = resp_data.get("sha")
            except Exception:
                pass

            payload = {
                "message": f"อัพเดท {datetime.now()}",
                "content": base64.b64encode(content.encode("utf-8")).decode()
            }
            if sha:
                payload["sha"] = sha

            headers_full = {
                "Authorization": f"token {TOKEN}",
                "User-Agent": "JARVIS-TrebEbit",
                "Content-Type": "application/json"
            }
            
            req = urllib.request.Request(
                api,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers_full,
                method="PUT"
            )
            urllib.request.urlopen(req)
            return f"✅ ส่งขึ้น GitHub แล้ว: {path}"
        except Exception as e:
            return f"❌ ส่งไม่ได้: {e}"


def save_script(name, desc, code, keywords=""):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "REPLACE INTO scripts VALUES (?, ?, ?, ?, ?, ?, ?)",
        (name, name, desc, keywords, code, "TrebEbit", str(datetime.now()))
    )
    conn.commit()
    conn.close()
    
    if GITHUB_SYNC:
        github_action("push", f"scripts/{name}.py", code)
    return f"✅ จดจำแล้ว: {name}"


def search_script(query):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT name, desc FROM scripts")
    res = []
    for n, d in c.fetchall():
        if any(w in (n + " " + d).lower() for w in query.lower().split()):
            res.append({"name": n, "desc": d})
    conn.close()
    return res


def run_script(name):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT code FROM scripts WHERE id=?", (name,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return "❌ ไม่พบสคริปต์"
    
    temp_path = f"{DATA_DIR}/temp_run.py"
    with open(temp_path, "w", encoding="utf-8") as f:
        f.write(row[0])
    
    out = subprocess.run(
        [sys.executable, temp_path],
        capture_output=True,
        text=True
    )
    return f"--- ผลลัพธ์ ---\n{out.stdout}{out.stderr}"


def process_command(cmd):
    cmd = cmd.strip()
    
    if cmd in ["เริ่ม", "init", "start"]:
        init_system()
        return "✅ พร้อมแล้ว! พิมพ์ 'ช่วย' ดูคำสั่ง"
    
    if cmd in ["สถานะ", "status"]:
        return f"ทำงานปกติ — ซิงค์ GitHub: {GITHUB_SYNC}"
    
    if cmd.startswith("จำ "):
        parts = cmd.split("\n", 1)
        head = parts[0].split(" ", 1)
        name = head[1] if len(head) > 1 else "ไม่มีชื่อ"
        code = parts[1] if len(parts) > 1 else ""
        return save_script(name, "บันทึกเอง", code)
    
    if cmd.startswith("หา "):
        q = cmd.split(" ", 1)[1]
        rs = search_script(q)
        if rs:
            return "\n".join(f"- {r['name']}: {r['desc']}" for r in rs)
        return "ไม่พบ"
    
    if cmd.startswith("รัน "):
        name = cmd.split(" ", 1)[1]
        return run_script(name)
    
    if cmd == "ซิงค์ github":
        return github_action("push", "backup/time.txt", str(datetime.now()))
    
    if cmd == "ช่วย":
        return """
📖 คำสั่ง:
เริ่ม           — เปิดระบบ
จำ ชื่อ\nโค้ด    — จดจำสคริปต์
หา คำค้น        — ค้นหา
รัน ชื่อ        — เรียกใช้
ซิงค์ github    — ส่งขึ้น
สถานะ          — ดูสถานะ
จบ             — ปิด
"""
    
    return "ไม่เข้าใจ พิมพ์ 'ช่วย'"


if __name__ == "__main__":
    print("🤖 JARVIS พร้อม! พิมพ์ 'เริ่ม' เพื่อเปิดใช้งาน")
    while True:
        try:
            inp = input("\nคุณ: ")
            if inp.lower() in ["จบ", "ออก", "exit"]:
                break
            print("JARVIS:", process_command(inp))
        except KeyboardInterrupt:
            break
    print("ปิดระบบแล้ว")
