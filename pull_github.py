#!/usr/bin/env python3
"""ดึงสคริปต์ทั้งหมดจาก GitHub มาเข้าฐานความจำ"""
import os, json
from jarvis_core import github_action, save_script, DATA_DIR

repo = os.getenv("GITHUB_REPO", "")
token = os.getenv("GITHUB_TOKEN", "")
if not repo or not token:
    print("ตั้งค่า GITHUB_REPO และ GITHUB_TOKEN ก่อน")
    exit()

import urllib.request
headers = {"Authorization": f"token {token}", "User-Agent": "JARVIS"}
url = f"https://api.github.com/repos/{repo}/contents/scripts"
try:
    resp = urllib.request.urlopen(urllib.request.Request(url, headers=headers))
    files = json.loads(resp.read())
except Exception as e:
    print("ดึงรายการไม่ได้:", e)
    exit()

for f in files:
    if f["name"].endswith(".py") and f["name"] != "index.json":
        code = github_action("pull", f"scripts/{f['name']}")
        name = f["name"].replace(".py","")
        save_script(name, "ดึงจาก GitHub", code)
        print(f"✅ เพิ่ม: {name}")

print("\n🎉 ดึงเข้าฐานความจำครบทั้งหมด!")
  
