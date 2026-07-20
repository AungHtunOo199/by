import hashlib
import base64
import datetime
import requests
import os
import subprocess
import uuid
import sys

# --- CONFIGURATION ---
SECRET_KEY = "OSUTA_PRIVATE_SECRET_2026"

def get_token_path():
    """Token သိမ်းမယ့်နေရာကို တစ်သမတ်တည်းဖြစ်အောင် သတ်မှတ်မယ်"""
    paths = ["/sdcard/.osuta_token", "/data/data/com.termux/files/home/.osuta_token", ".osuta_token"]
    for p in paths:
        try:
            # စမ်းရေးကြည့်မယ်၊ ရတဲ့နေရာကို သုံးမယ်
            with open(p, 'a') as f: pass
            return p
        except: continue
    return ".osuta_token"

def get_internet_time():
    time_apis = [
        'http://worldtimeapi.org/api/timezone/Asia/Yangon',
        'https://timeapi.io/api/Time/current/zone?timeZone=Asia/Yangon'
    ]
    for api in time_apis:
        try:
            response = requests.get(api, timeout=5)
            if response.status_code == 200:
                data = response.json()
                dt_str = data.get('datetime') or data.get('currentDateTime')
                if dt_str: return datetime.datetime.fromisoformat(dt_str.split('.')[0])
        except: continue
    try:
        res = requests.get('http://www.google.com', timeout=5)
        return datetime.datetime.strptime(res.headers['Date'], '%a, %d %b %Y %H:%M:%S %Z')
    except: return None

def decrypt_token(token, device_id):
    try:
        token = token.strip()
        decoded = base64.b64decode(token).decode()
        parts = decoded.split("|")
        if len(parts) != 3: return None
        signature, expiry_str, dev_id = parts
        expected_sig = hashlib.sha256(f"{dev_id}{SECRET_KEY}{expiry_str}".encode()).hexdigest()[:10]
        if signature == expected_sig and dev_id == device_id:
            return "UNLIMITED" if expiry_str == "UNLIMITED" else datetime.datetime.strptime(expiry_str, '%Y-%m-%d')
    except: pass
    return None

def check_activation(device_id):
    path = get_token_path()
    if not os.path.exists(path): return False, "NOT_ACTIVATED"
    
    with open(path, 'r') as f:
        token = f.read().strip()
    
    if not token: return False, "NOT_ACTIVATED"
    
    expiry_info = decrypt_token(token, device_id)
    if not expiry_info: return False, "INVALID_TOKEN"
    if expiry_info == "UNLIMITED": return True, "Unlimited"

    current_time = get_internet_time()
    if not current_time:
        print("\033[1;31m[!] Error: Internet connection required for security check!\033[0m")
        sys.exit()

    if current_time > expiry_info:
        try: os.remove(path)
        except: pass
        return False, "EXPIRED"
    return True, expiry_info.strftime('%Y-%m-%d')

def get_device_id():
    hwid_paths = ["/sdcard/.osuta_sys_id", "/data/data/com.termux/files/home/.osuta_sys_id", ".osuta_sys_id"]
    for path in hwid_paths:
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    sid = f.read().strip()
                    if len(sid) == 16: return sid
        except: continue

    hw_info = ""
    props = ["ro.product.model", "ro.product.brand", "ro.serialno"]
    for prop in props:
        try:
            out = subprocess.check_output(f"getprop {prop}", shell=True, stderr=subprocess.DEVNULL).decode().strip()
            if out and out != "unknown": hw_info += out
        except: pass
    try:
        aid = subprocess.check_output("settings get secure android_id", shell=True, stderr=subprocess.DEVNULL).decode().strip()
        if aid and aid != "null": hw_info += aid
    except: pass
    
    if not hw_info: hw_info = str(uuid.getnode())
    new_hwid = hashlib.sha256(f"OSUTA_PRO_{hw_info}".encode()).hexdigest()[:16].upper()

    for path in hwid_paths:
        try:
            with open(path, 'w') as f: f.write(new_hwid)
        except: continue
    return new_hwid
