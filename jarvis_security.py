#!/usr/bin/env python3
"""
ระบบรักษาความปลอดภัย — ตรวจจับสิ่งผิดปกติ แจ้งเตือน
"""
import time
import hashlib
from datetime import datetime

class JARVIS_Security:
    def __init__(self):
        self.authorized_users = ["เจ้านาย"]
        self.alerts = []
        self.risk_log = []
    
    def verify_user(self, user_id, proof):
        """ตรวจสอบสิทธิ์"""
        user_hash = hashlib.sha256(proof.encode()).hexdigest()[:1]
        if user_id in self.authorized_users:
            self._log_access(user_id, "อนุญาต")
            return True, f"ยืนยันตัวตนสำเร็จ ครับ ท่าน {user_id}"
        else:
            self._log_access(user_id, "ปฏิเสธ")
            return False, "⚠️ ไม่พบสิทธิ์การใช้งาน"
    
    def _log_access(self, user, status):
        """บันทึกการเข้าใช้"""
        self.risk_log.append({
            "time": datetime.now().isoformat(),
            "user": user,
            "status": status
        })
    
    def check_safety(self, code_text):
        """ตรวจสอบโค้ดก่อนรัน"""
        danger_keywords = [
            "rm -rf", "format", "del /f", "DROP TABLE",
            "shutdown", "erase", "rmdir", "os.system('rm",
            "subprocess.*rm", "eval(", "exec("
        ]
        risk = []
        for kw in danger_keywords:
            if kw.lower() in code_text.lower():
                risk.append(f"พบคำสั่งอันตราย: {kw}")
        
        if risk:
            return False, "\n".join(risk) + "\n⚠️ ต้องการยืนยันก่อนดำเนินการ"
        return True, "✅ ปลอดภัย"
    
    def add_alert(self, level, message):
        """เพิ่มการแจ้งเตือน"""
        self.alerts.append({
            "time": datetime.now().isoformat(),
            "level": level,
            "msg": message
        })
    
    def get_alerts(self):
        """รายการแจ้งเตือน"""
        if not self.alerts:
            return "✅ ไม่มีเหตุการณ์ผิดปกติ"
        return "\n".join(f"[{a['level']}] {a['msg']} — {a['time'][:16]}" for a in self.alerts)

# ทดสอบ
if __name__ == "__main__":
    sec = JARVIS_Security()
    ok, msg = sec.check_safety("print('สวัสดี')")
    print(msg)
    ok, msg = sec.check_safety("os.system('rm -rf /')")
    print(msg)
                             
