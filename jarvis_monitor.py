#!/usr/bin/env python3
"""
ระบบตรวจสอบสถานะ — แสดงข้อมูลเหมือนหน้าจอในห้องปฏิบัติการ
"""
import os
import sys
import time
import platform
import shutil
from datetime import datetime

class JARVIS_Monitor:
    def __init__(self):
        self.start_time = time.time()
    
    def get_system_info(self):
        """ข้อมูลเครื่องพื้นฐาน"""
        return {
            "ระบบปฏิบัติการ": platform.system(),
            "เวลาทำงาน": self._uptime(),
            "เวลาปัจจุบัน": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "แพลตฟอร์ม": platform.machine()
        }
    
    def get_storage_info(self):
        """พื้นที่เก็บข้อมูล"""
        total, used, free = shutil.disk_usage('.')
        return {
            "ทั้งหมด": f"{round(total/1024/1024/1024, 1)} GB",
            "ใช้ไป": f"{round(used/1024/1024/1024, 1)} GB",
            "ว่าง": f"{round(free/1024/1024/1024, 1)} GB",
            "เปอร์เซ็นต์ใช้": f"{round(used/total*100, 1)}%"
        }
    
    def get_network_status(self):
        """ตรวจสอบการเชื่อมต่อ"""
        import urllib.request
        try:
            urllib.request.urlopen("https://github.com", timeout=3)
            return "✅ เชื่อมต่ออินเทอร์เน็ตปกติ"
        except:
            return "❌ ไม่มีการเชื่อมต่อ"
    
    def _uptime(self):
        """เวลาทำงานต่อเนื่อง"""
        sec = int(time.time() - self.start_time)
        h = sec // 3600
        m = (sec % 3600) // 60
        return f"{h} ชม. {m} นาที"
    
    def full_report(self):
        """สร้างรายงานสถานะทั้งระบบ"""
        info = self.get_system_info()
        storage = self.get_storage_info()
        net = self.get_network_status()
        
        return f"""
📊 === รายงานสถานะระบบ JARVIS ===
🕐 เวลาปัจจุบัน:     {info['เวลาปัจจุบัน']}
⚙️  ระบบปฏิบัติการ:   {info['ระบบปฏิบัติการ']}
⏱️  ทำงานต่อเนื่อง:    {info['เวลาทำงาน']}
💾 พื้นที่ใช้งาน:      {storage['ใช้ไป']} / {storage['ทั้งหมด']}
📡 สถานะเครือข่าย:     {net}
================================
"""

# ทดสอบ
if __name__ == "__main__":
    mon = JARVIS_Monitor()
    print(mon.full_report())
      
