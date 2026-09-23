#!/usr/bin/env python3
"""
ระบบควบคุมอุปกรณ์ — สั่งเปิดปิดไฟ แอร์ อุปกรณ์ต่างๆ
"""
import json
import time
from datetime import datetime

class SmartDevice:
    def __init__(self, name, device_type, location):
        self.name = name
        self.type = device_type
        self.location = location
        self.status = False
        self.last_changed = None
    
    def turn_on(self):
        self.status = True
        self.last_changed = datetime.now()
        return f"✅ เปิด{self.name} ที่{self.location} แล้ว"
    
    def turn_off(self):
        self.status = False
        self.last_changed = datetime.now()
        return f"✅ ปิด{self.name} ที่{self.location} แล้ว"
    
    def get_status(self):
        return f"{self.name}: {'🟢 เปิด' if self.status else '🔴 ปิด'}"


class JARVIS_SmartHome:
    def __init__(self):
        self.devices = {}
        self._init_default_devices()
    
    def _init_default_devices(self):
        """อุปกรณ์เริ่มต้น"""
        self.devices["ไฟห้องนั่งเล่น"] = SmartDevice("ไฟห้องนั่งเล่น", "แสง", "ห้องนั่งเล่น")
        self.devices["ไฟห้องนอน"] = SmartDevice("ไฟห้องนอน", "แสง", "ห้องนอน")
        self.devices["แอร์ห้องนอน"] = SmartDevice("แอร์ห้องนอน", "ความเย็น", "ห้องนอน")
        self.devices["พัดลม"] = SmartDevice("พัดลม", "ลม", "ห้องทำงาน")
    
    def control(self, device_name, action):
        """สั่งงานอุปกรณ์"""
        for name, dev in self.devices.items():
            if device_name in name or name in device_name:
                if action in ["เปิด", "on", "เปิดใช้งาน"]:
                    return dev.turn_on()
                elif action in ["ปิด", "off", "ปิดใช้งาน"]:
                    return dev.turn_off()
        return f"❌ ไม่พบอุปกรณ์ชื่อ: {device_name}"
    
    def status_all(self):
        """แสดงสถานะทุกอย่าง"""
        return "\n".join(dev.get_status() for dev in self.devices.values())
    
    def match_command(self, text):
        """จับคู่คำสั่งธรรมดา"""
        text = text.lower()
        action = None
        if any(w in text for w in ["เปิด", "ให้เปิด", "เปิดด้วย"]):
            action = "เปิด"
        elif any(w in text for w in ["ปิด", "ให้ปิด", "ดับ"]):
            action = "ปิด"
        
        if not action:
            return None
        
        # ค้นชื่ออุปกรณ์
        for name in self.devices.keys():
            if any(w in text for w in name.lower().split()):
                return self.control(name, action)
        
        return None

# ทดสอบ
if __name__ == "__main__":
    home = JARVIS_SmartHome()
    print(home.status_all())
    print(home.control("แอร์ห้องนอน", "เปิด"))
    print(home.control("ไฟห้องนั่งเล่น", "ปิด"))
  
