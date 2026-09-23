#!/usr/bin/env python3
"""
ระบบเสียง JARVIS — ฟัง-พูด อัตโนมัติ
ทำงานเหมือนในหนัง: พูดเรียกได้ตลอด ไม่ต้องกดส่ง
"""
import os
import sys
import time
import threading
import json
from datetime import datetime

try:
    import pyttsx3
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False

class JARVIS_Voice:
    def __init__(self):
        self.active = True
        self.listening = False
        self.wake_word = "จาวิส"
        
        if VOICE_AVAILABLE:
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
            # เลือกเสียงที่ฟังดูเหมือน JARVIS
            for v in voices:
                if 'en' in v.language.lower():
                    self.engine.setProperty('voice', v.id)
                    break
            self.engine.setProperty('rate', 160)   # ความเร็วพอดี
            self.engine.setProperty('volume', 0.9) # ความดัง
    
    def speak(self, text):
        """ให้ JARVIS พูดออกมาผ่านลำโพง"""
        timestamp = datetime.now().strftime("%H:%M")
        print(f"🔊 JARVIS [{timestamp}]: {text}")
        
        if VOICE_AVAILABLE:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"⚠️ ระบบเสียงผิดพลาด: {e}")
        return True
    
    def greet(self):
        """ทักทายตามเวลา"""
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "สวัสดีตอนเช้า ครับ ท่าน"
        elif 12 <= hour < 18:
            return "สวัสดีตอนบ่าย ครับ ท่าน"
        else:
            return "สวัสดีตอนเย็น ครับ ท่าน"
    
    def listen_text(self):
        """รับข้อความจากผู้ใช้ (ใน TrebEbit ใช้พิมพ์แทนเสียง)"""
        try:
            return input("\n🎤 คุณพูดว่า: ")
        except (EOFError, KeyboardInterrupt):
            return ""
    
    def start_voice_loop(self, process_callback):
        """วงรอบฟังตลอดเวลา"""
        self.speak(self.greet())
        self.speak("ระบบจาวิสพร้อมทำงาน ครับ")
        
        while self.active:
            try:
                user_input = self.listen_text()
                if not user_input:
                    continue
                if user_input.lower() in ["จบ", "พักก่อน", "ปิดระบบ"]:
                    self.speak("รับทราบ ครับ ท่าน ขอให้มีวันที่ดี")
                    break
                
                # ส่งไปประมวลผล
                response = process_callback(user_input)
                self.speak(response)
                
            except KeyboardInterrupt:
                self.speak("ปิดระบบตามคำสั่ง ครับ")
                break
        
        print("🔇 ระบบเสียงปิดทำงาน")

# ทดสอบระบบ
if __name__ == "__main__":
    voice = JARVIS_Voice()
    voice.speak("ทดสอบระบบเสียงจาวิส ทำงานปกติ ครับ")
      
