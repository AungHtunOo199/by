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
                if dt_str:
                    return datetime.datetime.fromisoformat(dt_str.split('.')[0])
        except: continue
    try:
        res = requests.get('http://www.google.com', timeout=5)
        return datetime.datetime.strptime(res.headers['Date'], '%a, %d %b %Y %H:%M:%S %Z')
    except: return None

def decrypt_token(token, device_id):
    try:
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
    # Hidden path for token
    token_paths = ["/sdcard/.osuta_token", ".osuta_token", "/data/data/com.termux/files/home/.osuta_token"]
    token = None
    path_used = None
    for p in token_paths:
        if os.path.exists(p):
            with open(p, 'r') as f:
                token = f.read().strip()
                path_used = p
                break
    
    if not token: return False, "NOT_ACTIVATED"
    
    expiry_info = decrypt_token(token, device_id)
    if not expiry_info: return False, "INVALID_TOKEN"
    if expiry_info == "UNLIMITED": return True, "Unlimited"

    current_time = get_internet_time()
    if not current_time:
        print("\033[1;31m[!] Error: Internet connection required for security check!\033[0m")
        sys.exit()

    if current_time > expiry_info:
        try: os.remove(path_used)
        except: pass
        return False, "EXPIRED"
    return True, expiry_info.strftime('%Y-%m-%d')

def get_device_id():
    """
    Ultra-Stable HWID System for Android/Termux
    """
    # ၁။ Hidden Storage File (အငြိမ်ဆုံးနည်းလမ်း - တစ်ခါထုတ်ပြီးရင် ဘယ်တော့မှ မပြောင်းတော့ဘူး)
    # နေရာ ၃ ခုမှာ သိမ်းမယ်၊ တစ်ခုပျက်ရင် တစ်ခုကနေ ပြန်ယူမယ်
    hwid_paths = [
        "/sdcard/.osuta_sys_id", 
        "/data/data/com.termux/files/home/.osuta_sys_id",
        ".osuta_sys_id"
    ]
    
    for path in hwid_paths:
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    saved_id = f.read().strip()
                    if len(saved_id) == 16: return saved_id
        except: continue

    # ၂။ အကယ်၍ ဖိုင်မရှိသေးရင် Hardware Info တွေ စုစည်းပြီး အသစ်ထုတ်မယ်
    hw_info = ""
    
    # Get Android Prop (Model, Brand, Serial)
    props = ["ro.product.model", "ro.product.brand", "ro.serialno", "ro.build.id"]
    for prop in props:
        try:
            out = subprocess.check_output(f"getprop {prop}", shell=True, stderr=subprocess.DEVNULL).decode().strip()
            if out and out != "unknown": hw_info += out
        except: pass

    # Get Android ID (Settings)
    try:
        aid = subprocess.check_output("settings get secure android_id", shell=True, stderr=subprocess.DEVNULL).decode().strip()
        if aid and aid != "null": hw_info += aid
    except: pass

    # အကယ်၍ hardware info ဘာမှ ယူမရရင် UUID ကို သုံးမယ်
    if not hw_info:
        hw_info = str(uuid.getnode())

    # Final HWID Generation
    new_hwid = hashlib.sha256(f"OSUTA_PRO_{hw_info}".encode()).hexdigest()[:16].upper()

    # နေရာစုံမှာ ပြန်သိမ်းထားမယ် (နောင်တစ်ကြိမ် ပြောင်းမသွားအောင်)
    for path in hwid_paths:
        try:
            with open(path, 'w') as f:
                f.write(new_hwid)
        except: continue
        
    return new_hwid
