# นำเข้าโมดูลทั้งหมดที่สร้างขึ้น
from jarvis_voice import JARVIS_Voice
from jarvis_monitor import JARVIS_Monitor
from jarvis_smart_home import JARVIS_SmartHome
from jarvis_memory import JARVIS_Memory
from jarvis_security import JARVIS_Security

# เริ่มทำงานทุกระบบ
voice = JARVIS_Voice()
monitor = JARVIS_Monitor()
home = JARVIS_SmartHome()
memory = JARVIS_Memory()
security = JARVIS_Security()

def process_command(cmd):
    cmd = cmd.strip()
    response = ""
    
    # === ระบบพื้นฐาน ===
    if cmd in ["เริ่ม", "เปิดระบบ"]:
        init_system()
        return "✅ JARVIS พร้อมทำงานเต็มรูปแบบ — พิมพ์ 'ช่วย' ดูคำสั่งทั้งหมด"
    
    if cmd in ["ช่วย", "help"]:
        return """
📖 คำสั่งทั้งหมดของ JARVIS:

🔊 ระบบเสียง
- พูดว่า [ข้อความ] → ให้ JARVIS พูดออกมา

📊 สถานะระบบ
- สถานะ / รายงาน → แสดงสภาพทั้งระบบ

🏠 บ้านอัจฉริยะ
- เปิด [ชื่ออุปกรณ์] → เปิดไฟ/แอร์/พัดลม
- ปิด [ชื่ออุปกรณ์] → ปิดอุปกรณ์
- สถานะอุปกรณ์ → ดูทุกอย่าง

🧠 หน่วยความจำ
- จดจำ [ข้อมูล] → บันทึกสิ่งที่บอก
- คิดถึง [คำ] → ค้นความทรงจำ
- ความชอบ [ชื่อ] = [ค่า] → บันทึกค่าที่ชอบ

🔒 ความปลอดภัย
- ตรวจสอบ [โค้ด] → เช็คความปลอดภัยก่อนรัน
- การแจ้งเตือน → ดูเหตุการณ์ทั้งหมด

📋 จัดการสคริปต์
- จำ [ชื่อ]\n[โค้ด] → บันทึกสคริปต์
- รัน [ชื่อ] → เรียกใช้
- ซิงค์ github → ส่งข้อมูลขึ้นคลาวด์
- จบ → ปิดระบบ
"""
    
    # === ระบบเสียง ===
    if cmd.startswith("พูดว่า "):
        text = cmd.split(" ", 1)[1]
        voice.speak(text)
        return f"🔊 พูดแล้ว: {text}"
    
    # === สถานะระบบ ===
    if cmd in ["สถานะ", "รายงาน", "ภาพรวม"]:
        return monitor.full_report()
    
    # === บ้านอัจฉริยะ ===
    res = home.match_command(cmd)
    if res:
        memory.remember_conversation(cmd, res)
        return res
    
    if cmd in ["สถานะอุปกรณ์", "อุปกรณ์"]:
        return "📋 สถานะอุปกรณ์:\n" + home.status_all()
    
    # === หน่วยความจำ ===
    if cmd.startswith("จดจำ "):
        fact = cmd.split(" ", 1)[1]
        memory.remember_conversation("ผู้ใช้บอกว่า", fact)
        return f"✅ จดจำแล้ว: {fact}"
    
    if cmd.startswith("คิดถึง "):
        kw = cmd.split(" ", 1)[1]
        found = memory.recall(kw)
        if found:
            return "🧠 พบความทรงจำ:\n" + "\n".join(f"- {f['user']}" for f in found)
        return "❌ ไม่พบข้อมูลที่เกี่ยวข้อง"
    
    # === ความปลอดภัย ===
    if cmd.startswith("ตรวจสอบ "):
        code = cmd.split(" ", 1)[1]
        ok, msg = security.check_safety(code)
        return msg
    
    if cmd == "การแจ้งเตือน":
        return security.get_alerts()
    
    # === จัดการสคริปต์ (จากเดิม) ===
    if cmd.startswith("จำ "):
        parts = cmd.split("\n", 1)
        head = parts[0].split(" ", 1)
        name = head[1] if len(head) > 1 else "ไม่มีชื่อ"
        code = parts[1] if len(parts) > 1 else ""
        safe, msg = security.check_safety(code)
        if not safe:
            return msg + "\nพิมพ์ 'ยืนยัน' เพื่อบันทึก"
        res = save_script(name, "บันทึกผ่านระบบหลัก", code)
        memory.remember_conversation(cmd, res)
        return res
    
    if cmd.startswith("รัน "):
        name = cmd.split(" ", 1)[1]
        res = run_script(name)
        memory.remember_conversation(cmd, res)
        return res
    
    if cmd == "ซิงค์ github":
        res = github_action("push", "backup/memory.json", json.dumps(memory.data, ensure_ascii=False))
        return res
    
    memory.remember_conversation(cmd, "ไม่เข้าใจคำสั่ง")
    return "ไม่เข้าใจ พิมพ์ 'ช่วย'"


if __name__ == "__main__":
    print("🤖 JARVIS — ระบบอัจฉริยะเต็มรูปแบบ")
    print("✨ ผสาน: เสียง | ควบคุมบ้าน | ความจำ | ความปลอดภัย")
    print("พิมพ์ 'เริ่ม' เพื่อเปิดใช้งาน หรือ 'ช่วย' ดูคำสั่งทั้งหมด\n")
    
    while True:
        try:
            inp = input("คุณ: ")
            if inp.lower() in ["จบ", "ออก", "ปิดระบบ"]:
                voice.speak("ปิดระบบตามคำสั่ง ครับ ขอบคุณที่ใช้บริการ")
                break
            resp = process_command(inp)
            print("JARVIS:", resp)
        except KeyboardInterrupt:
            break
    
    print("ปิดระบบแล้ว")
