#!/usr/bin/env python3
"""
หน่วยความจำ — จดจำทุกอย่างที่คุยกัน เรียนรู้ความชอบ
"""
import json
import os
from datetime import datetime

class JARVIS_Memory:
    def __init__(self, path="./jarvis_data/memory.json"):
        self.path = path
        self.data = {
            "conversations": [],
            "preferences": {},
            "facts": [],
            "learned_commands": {}
        }
        self._load()
    
    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except:
                pass
    
    def _save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def remember_conversation(self, user_text, jarvis_response):
        """จดจำบทสนทนา"""
        self.data["conversations"].append({
            "time": datetime.now().isoformat(),
            "user": user_text,
            "jarvis": jarvis_response
        })
        # เก็บล่าสุดแค่ 100 ข้อความ
        if len(self.data["conversations"]) > 100:
            self.data["conversations"] = self.data["conversations"][-100:]
        self._save()
    
    def set_preference(self, key, value):
        """บันทึกความชอบ"""
        self.data["preferences"][key] = value
        self._save()
        return f"✅ จดจำแล้ว: {key} = {value}"
    
    def get_preference(self, key, default=None):
        """เรียกคืนความชอบ"""
        return self.data["preferences"].get(key, default)
    
    def recall(self, keyword):
        """ค้นความทรงจำ"""
        kw = keyword.lower()
        found = []
        for talk in self.data["conversations"]:
            if kw in talk["user"].lower() or kw in talk["jarvis"].lower():
                found.append(talk)
        return found[:5]  # แสดง 5 ล่าสุด
    
    def get_recent(self, limit=5):
        """บทสนทนาล่าสุด"""
        return self.data["conversations"][-limit:]
    
    def learn_command(self, trigger, action):
        """เรียนรู้คำสั่งใหม่"""
        self.data["learned_commands"][trigger] = action
        self._save()
        return f"✅ เรียนรู้คำสั่งใหม่: พูดว่า '{trigger}' จะทำ: {action}"

# ทดสอบ
if __name__ == "__main__":
    mem = JARVIS_Memory()
    print("หน่วยความจำทำงานปกติ")
    mem.remember_conversation("สวัสดี", "สวัสดีครับ")
    print("บันทึกเรียบร้อย")
