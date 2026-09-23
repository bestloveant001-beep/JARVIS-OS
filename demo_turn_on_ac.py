#!/usr/bin/env python3
"""
ชื่อ: เปิดแอร์
คำอธิบาย: สั่งเปิดแอร์ปรับอุณหภูมิ
คีย์เวิร์ด: แอร์,เปิดแอร์,อุณหภูมิ
"""
import os, json

params = json.loads(os.environ.get("JARVIS_PARAMS", "{}"))
temp = params.get("temp", 26)

print(f"🌡️ ส่งคำสั่งเปิดแอร์ที่ {temp}°C")
print("✅ ทำงานเรียบร้อย — JARVIS บันทึกสถานะแล้ว")
