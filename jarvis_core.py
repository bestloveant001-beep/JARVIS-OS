#!/usr/bin/env python3
"""
JARVIS OS — พร้อมแดชบอร์ด
TrebEbit ↔ GitHub | จดจำ-ใช้-ซิงค์ อัตโนมัติ
"""
import os
import sys
import json
import time
import urllib.request
import subprocess
import sqlite3
import base64
import shutil
from datetime import datetime

# ========== ตั้งค่า ==========
REPO = "bestloveant001-beep/JARVIS-OS"
TOKEN = os.getenv("GITHUB_TOKEN", "ใส่โทเคนของคุณ")
AUTO_SYNC = True
# ============================

DATA_DIR = "./jarvis_data"
DB_FILE = f"{DATA_DIR}/memory.db"
API_BASE = f"https://api.github.com/repos/{REPO}/contents"
HEADERS = {
    "Authorization": f"token {TOKEN}",
    "User-Agent": "JARVIS-Dashboard",
    "Content-Type": "application/json"
}
START_TIME = time.time()


# ========== เตรียมระบบ ==========
def init_system():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(f"{DATA_DIR}/scripts", exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS scripts (
        id TEXT PRIMARY KEY,
        name TEXT UNIQUE,
        desc TEXT,
        code TEXT,
        updated_at TEXT
    )""")
    conn.commit()
    conn.close()


# ========== GitHub ==========
def github_push(path, content, msg=None):
    if not TOKEN or not REPO:
        return False
    url = f"{API_BASE}/{path}"
    msg = msg or f"อัปเดต {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    try:
        sha = None
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS))
            sha = json.loads(r.read()).get("sha")
        except:
            pass
        payload = {
            "message": msg,
            "content": base64.b64encode(content.encode("utf-8")).decode()
        }
        if sha: payload["sha"] = sha
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"),
                                      headers=HEADERS, method="PUT")
        urllib.request.urlopen(req)
        return True
    except:
        return False


def github_pull(path):
    if not TOKEN or not REPO:
        return None
    try:
        url = f"{API_BASE}/{path}"
        req = urllib.request.Request(url, headers=HEADERS)
        data = json.loads(urllib.request.urlopen(req).read())
        return base64.b64decode(data["content"]).decode("utf-8")
    except:
        return None


# ========== จัดการสคริปต์ ==========
def save_script(name, desc, code):
    now = str(datetime.now())
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO scripts 
        (id, name, desc, code, updated_at) VALUES (?, ?, ?, ?, ?)
    """, (name, name, desc, code, now))
    conn.commit()
    conn.close()
    if AUTO_SYNC:
        github_push(f"scripts/{name}.py", code, f"เพิ่ม: {name}")
    return f"✅ จดจำแล้ว: {name}\nใช้ได้ทันที: รัน {name}"


def run_script(name):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT code FROM scripts WHERE id=?", (name,))
    row = c.fetchone()
    conn.close()
    if not row:
        return f"❌ ไม่พบ: {name}"
    temp = f"{DATA_DIR}/_run.py"
    with open(temp, "w", encoding="utf-8") as f:
        f.write(row[0])
    out = subprocess.run([sys.executable, temp], capture_output=True, text=True)
    res = out.stdout + out.stderr
    return f"--- ผลลัพธ์: {name} ---\n{res or '✅ เสร็จแล้ว'}"


def list_scripts():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT name, updated_at FROM scripts ORDER BY updated_at DESC")
    alls = c.fetchall()
    conn.close()
    if not alls:
        return "📋 ยังไม่มี — พิมพ์:\nจำ ชื่อ\nโค้ด"
    return "📋 รายการสคริปต์:\n" + "\n".join(f"{i+1}. {n} — {t[:16]}" for i, (n, t) in enumerate(alls))


def sync_from_github():
    if not TOKEN or not REPO:
        return "⚠️ ตั้งค่า GitHub ก่อน"
    try:
        url = f"{API_BASE}/scripts"
        req = urllib.request.Request(url, headers=HEADERS)
        files = json.loads(urllib.request.urlopen(req).read())
    except Exception as e:
        return f"❌ ดึงไม่ได้: {e}"
    count = 0
    for f in files:
        if f["name"].endswith(".py"):
            code = github_pull(f"scripts/{f['name']}")
            if code:
                save_script(f["name"].replace(".py", ""), "ซิงค์จาก GitHub", code)
                count += 1
    return f"✅ ซิงค์เสร็จ: {count} รายการ"


# ========== 📊 แดชบอร์ดหลัก ==========
def get_dashboard():
    """สร้างหน้าแดชบอร์ด"""
    # ข้อมูลเวลา
    up_sec = int(time.time() - START_TIME)
    up_h = up_sec // 3600
    up_m = (up_sec % 3600) // 60
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # ข้อมูลสคริปต์
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM scripts")
    total = c.fetchone()[0]
    c.execute("SELECT name, updated_at FROM scripts ORDER BY updated_at DESC LIMIT 3")
    recent = c.fetchall()
    conn.close()

    # ข้อมูลพื้นที่
    total_disk, used_disk, free_disk = shutil.disk_usage('.')
    used_pct = round(used_disk / total_disk * 100, 1)

    # สถานะ GitHub
    gh_status = "✅ เชื่อมต่อ" if (TOKEN and len(TOKEN) > 10 and REPO) else "❌ ไม่ได้ตั้งค่า"
    sync_mode = "อัตโนมัติ" if AUTO_SYNC else "ปิด"

    # สร้างหน้า
    board = f"""
╔══════════════════════════════════════════╗
║     🤖 JARVIS — แดชบอร์ดระบบ              ║
╠══════════════════════════════════════════╣
║ � เวลาปัจจุบัน:   {now}
║ ⏱️  ทำงานต่อเนื่อง: {up_h} ชม. {up_m} นาที
╠══════════════════════════════════════════╣
║ 📁 สคริปต์:       {total} รายการ
"""
    if recent:
        board += "║ 📌 ล่าสุด:        "
        board += " | ".join(f"{n}" for n, _ in recent) + "\n"
    else:
        board += "║ 📌 ล่าสุด:        ยังไม่มี\n"

    board += f"""╠══════════════════════════════════════════╣
║ ☁️ GitHub:        {gh_status}
║ 🔄 ซิงค์:         {sync_mode}
╠══════════════════════════════════════════╣
║ 💾 พื้นที่:       {used_pct}%
║    ใช้ไป:         {round(used_disk/1024**3, 1)} GB / {round(total_disk/1024**3, 1)} GB
║    ว่าง:          {round(free_disk/1024**3, 1)} GB
╠══════════════════════════════════════════╣
║ 📋 คำสั่งด่วน:
║    จดจำ → จำ ชื่อ\nโค้ด
║    ใช้งาน → รัน ชื่อ
║    ดูทั้งหมด → รายการ
║    กู้คืน → ซิงค์
║    ออก → จบ
╚══════════════════════════════════════════╝
พิมพ์ 'แดชบอร์ด' เพื่อรีเฟรช
"""
    return board


# ========== ประมวลผลคำสั่ง ==========
def process_command(cmd):
    cmd = cmd.strip()

    if cmd in ["เริ่ม", "init", "start"]:
        init_system()
        return get_dashboard()

    if cmd in ["แดชบอร์ด", "สถานะ", "dashboard"]:
        return get_dashboard()

    if cmd in ["ช่วย", "help"]:
        return """
📖 คู่มือการใช้งาน:

📊 แดชบอร์ด
- แดชบอร์ด / สถานะ → ดูภาพรวมทั้งระบบ

📝 จดจำสคริปต์
จำ ชื่อสคริปต์
โค้ดที่นี่...

▶️ เรียกใช้
รัน ชื่อสคริปต์

📋 ดูรายการ
รายการ

☁️ กู้คืน/ซิงค์
ซิงค์

🚪 ปิดระบบ
จบ / ออก
"""

    if cmd.startswith("จำ "):
        parts = cmd.split("\n", 1)
        if len(parts) < 2:
            return "⚠️ รูปแบบ:\nจำ ชื่อ\nโค้ด"
        name = parts[0].split(" ", 1)[1].strip()
        code = parts[1].strip()
        return save_script(name, "เพิ่มผ่านมือถือ", code)

    if cmd.startswith("รัน "):
        name = cmd.split(" ", 1)[1].strip()
        return run_script(name)

    if cmd == "รายการ":
        return list_scripts()

    if cmd == "ซิงค์":
        return sync_from_github()

    if cmd in ["จบ", "ออก", "exit"]:
        return "ปิดระบบแล้ว ข้อมูลปลอดภัยครับ ✅"

    return "ไม่เข้าใจ พิมพ์ 'ช่วย'"


# ========== เริ่มทำงาน ==========
if __name__ == "__main__":
    print("🤖 JARVIS OS — พร้อมแดชบอร์ด")
    print("พิมพ์ 'เริ่ม' เพื่อเปิดใช้งาน\n")

    while True:
        try:
            inp = input("คุณ: ")
            if inp.lower() in ["จบ", "ออก", "exit"]:
                print("JARVIS: ปิดระบบแล้ว")
                break
            print("JARVIS:", process_command(inp))
        except KeyboardInterrupt:
            print("\nปิดระบบแล้ว")
            break
