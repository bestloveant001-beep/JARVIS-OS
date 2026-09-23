#!/usr/bin/env python3
"""
หน้าเว็บแดชบอร์ด JARVIS
เปิดผ่านเบราว์เซอร์มือถือได้เลย
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sqlite3
import time
import shutil
from datetime import datetime

# ===== ตั้งค่า =====
PORT = 8080
DB_FILE = "./jarvis_data/memory.db"
START_TIME = time.time()


# ===== อ่านข้อมูลระบบ =====
def get_system_stats():
    # เวลาทำงาน
    up_sec = int(time.time() - START_TIME)
    up_h = up_sec // 3600
    up_m = (up_sec % 3600) // 60
    
    # จำนวนสคริปต์
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM scripts")
        total = c.fetchone()[0]
        c.execute("SELECT name, updated_at FROM scripts ORDER BY updated_at DESC LIMIT 5")
        recent = c.fetchall()
        conn.close()
    except:
        total = 0
        recent = []
    
    # พื้นที่
    total_disk, used_disk, free_disk = shutil.disk_usage('.')
    used_pct = round(used_disk / total_disk * 100, 1)
    
    return {
        "time": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "uptime": f"{up_h} ชม. {up_m} นาที",
        "script_count": total,
        "recent": recent,
        "disk_used_pct": used_pct,
        "disk_used_gb": round(used_disk / 1024**3, 1),
        "disk_total_gb": round(total_disk / 1024**3, 1),
        "disk_free_gb": round(free_disk / 1024**3, 1)
    }


# ===== หน้าเว็บหลัก =====
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JARVIS — แดชบอร์ด</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box;font-family:'Segoe UI',sans-serif}
        body{background:#0a0a0f;color:#0ff;min-height:100vh;padding:20px}
        .container{max-width:700px;margin:0 auto}
        .header{text-align:center;margin-bottom:30px}
        .logo{font-size:28px;font-weight:bold;text-shadow:0 0 15px #0ff}
        .subtitle{color:#88f;margin-top:5px}
        .card{background:#111520;border:1px solid #0ff4;border-radius:12px;padding:20px;margin-bottom:15px;box-shadow:0 0 10px #0ff2}
        .card-title{font-size:18px;margin-bottom:15px;color:#0ff;border-bottom:1px solid #0ff3;padding-bottom:8px}
        .row{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #0ff1}
        .row:last-child{border:none}
        .label{color:#8cf}
        .value{font-weight:bold}
        .bar{height:10px;background:#1a1a2e;border-radius:5px;overflow:hidden;margin-top:8px}
        .bar-fill{height:100%;background:linear-gradient(90deg,#0ff,#08f);width:{{pct}}%;transition:0.5s}
        .script-item{padding:10px 0;border-bottom:1px solid #0ff2}
        .script-name{font-weight:bold}
        .script-time{font-size:12px;color:#669}
        .status-dot{display:inline-block;width:10px;height:10px;border-radius:50%;background:#0f0;margin-right:8px;animation:pulse 2s infinite}
        @keyframes pulse{0%{opacity:1}50%{opacity:0.3}100%{opacity:1}}
        .refresh{text-align:center;margin-top:20px}
        button{background:#0ff2;border:1px solid #0ff;color:#0ff;padding:10px 25px;border-radius:8px;cursor:pointer;font-size:16px}
        button:hover{background:#0ff4}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🤖 JARVIS</div>
            <div class="subtitle">ระบบอัจฉริยะ — แดชบอร์ด</div>
        </div>

        <div class="card">
            <div class="card-title">📊 สถานะระบบ</div>
            <div class="row"><span class="label">สถานะ</span><span class="value"><span class="status-dot"></span>ทำงานปกติ</span></div>
            <div class="row"><span class="label">เวลาปัจจุบัน</span><span class="value">{{time}}</span></div>
            <div class="row"><span class="label">ทำงานต่อเนื่อง</span><span class="value">{{uptime}}</span></div>
        </div>

        <div class="card">
            <div class="card-title">📁 สคริปต์</div>
            <div class="row"><span class="label">ทั้งหมด</span><span class="value">{{script_count}} รายการ</span></div>
            {{recent_list}}
        </div>

        <div class="card">
            <div class="card-title">💾 พื้นที่ใช้งาน</div>
            <div class="row"><span class="label">ใช้ไป</span><span class="value">{{disk_used_gb}} GB / {{disk_total_gb}} GB</span></div>
            <div class="bar"><div class="bar-fill" style="width:{{disk_used_pct}}%"></div></div>
            <div class="row"><span class="label">ว่าง</span><span class="value">{{disk_free_gb}} GB</span></div>
        </div>

        <div class="refresh">
            <button onclick="location.reload()">🔄 รีเฟรชข้อมูล</button>
        </div>
    </div>
</body>
</html>
"""


class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        stats = get_system_stats()
        
        # รายการล่าสุด
        if stats["recent"]:
            recent_list = "<div style='margin-top:10px'><b>ล่าสุด:</b>"
            for name, t in stats["recent"]:
                time_short = t[:16]
                recent_list += f"<div class='script-item'><span class='script-name'>{name}</span><br><span class='script-time'>{time_short}</span></div>"
            recent_list += "</div>"
        else:
            recent_list = "<p style='color:#669;margin-top:10px'>ยังไม่มีสคริปต์</p>"
        
        # เติมข้อมูล
        html = HTML_TEMPLATE
        html = html.replace("{{time}}", stats["time"])
        html = html.replace("{{uptime}}", stats["uptime"])
        html = html.replace("{{script_count}}", str(stats["script_count"]))
        html = html.replace("{{recent_list}}", recent_list)
        html = html.replace("{{disk_used_pct}}", str(stats["disk_used_pct"]))
        html = html.replace("{{disk_used_gb}}", str(stats["disk_used_gb"]))
        html = html.replace("{{disk_total_gb}}", str(stats["disk_total_gb"]))
        html = html.replace("{{disk_free_gb}}", str(stats["disk_free_gb"]))
        
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))
    
    def log_message(self, format, *args):
        pass  # ซ่อนข้อความแจ้งเตือน


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), DashboardHandler)
    print("="*50)
    print("🤖 JARVIS — แดชบอร์ดเว็บ")
    print(f"🌐 เปิดที่ลิงก์: http://localhost:{PORT}")
    print("📱 หรือลิงก์ที่ TrebEbit แจ้งด้านบน")
    print("กด Ctrl+C เพื่อปิด")
    print("="*50)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nปิดระบบแล้ว")
