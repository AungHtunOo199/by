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
    """
    စက်ထဲက အချိန်ကို လိမ်လို့မရအောင် အင်တာနက်ကနေ အချိန်ယူမယ်။
    """
    time_apis = [
        'http://worldtimeapi.org/api/timezone/Asia/Yangon',
        'http://worldclockapi.com/api/json/est/now',
        'https://timeapi.io/api/Time/current/zone?timeZone=Asia/Yangon'
    ]
    
    for api in time_apis:
        try:
            response = requests.get(api, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'datetime' in data:
                    return datetime.datetime.fromisoformat(data['datetime'].split('.')[0])
                elif 'currentDateTime' in data:
                    return datetime.datetime.fromisoformat(data['currentDateTime'].split('.')[0])
        except:
            continue
            
    # Fallback to google header time (ပိုစိတ်ချရတယ်)
    try:
        res = requests.get('http://www.google.com', timeout=5)
        date_str = res.headers['Date']
        return datetime.datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z')
    except:
        return None

def decrypt_token(token, device_id):
    try:
        decoded = base64.b64decode(token).decode()
        parts = decoded.split("|")
        if len(parts) != 3: return None
        
        signature, expiry_str, dev_id = parts
        
        # Signature စစ်ဆေးခြင်း (Keygen နဲ့ ပုံစံတူရမယ်)
        expected_sig_raw = f"{dev_id}{SECRET_KEY}{expiry_str}"
        expected_sig = hashlib.sha256(expected_sig_raw.encode()).hexdigest()[:10]
        
        if signature == expected_sig and dev_id == device_id:
            if expiry_str == "UNLIMITED":
                return "UNLIMITED"
            return datetime.datetime.strptime(expiry_str, '%Y-%m-%d')
    except:
        pass
    return None

def check_activation(device_id):
    token_path = "/sdcard/.osuta_token" if os.path.exists("/sdcard") else ".osuta_token"
    
    if not os.path.exists(token_path):
        return False, "NOT_ACTIVATED"
    
    with open(token_path, 'r') as f:
        token = f.read().strip()
    
    expiry_info = decrypt_token(token, device_id)
    if not expiry_info:
        return False, "INVALID_TOKEN"
    
    if expiry_info == "UNLIMITED":
        return True, "Unlimited"

    # အချိန်ကုန်မကုန် စစ်မယ်
    current_time = get_internet_time()
    
    # အင်တာနက်မရှိရင် ဝင်ခွင့်မပေးတာက ပိုလုံခြုံပါတယ် (အချိန်လိမ်လို့မရအောင်)
    if not current_time:
        print("\033[1;31m[!] Error: Internet connection required for security check!\033[0m")
        sys.exit()

    if current_time > expiry_info:
        # သက်တမ်းကုန်ရင် Token ဖိုင်ကိုပါ ဖျက်ပစ်မယ် (Anti-bypass)
        try: os.remove(token_path)
        except: pass
        return False, "EXPIRED"
    
    return True, expiry_info.strftime('%Y-%m-%d')

def get_device_id():
    # ၁။ Android ID (Termux)
    try:
        cmd = "settings get secure android_id"
        out = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode().strip()
        if out and out != "null":
            return hashlib.sha256(f"OSUTA_{out}".encode()).hexdigest()[:16].upper()
    except:
        pass

    # ၂။ HWID File Persistence (ID မပြောင်းအောင် သိမ်းထားမယ်)
    hwid_file = "/sdcard/.osuta_hwid" if os.path.exists("/sdcard") else ".osuta_hwid"
    if os.path.exists(hwid_file):
        with open(hwid_file, 'r') as f:
            return f.read().strip()

    # ၃။ Fallback to UUID
    node = uuid.getnode()
    new_hwid = hashlib.sha256(f"OSUTA_NODE_{node}".encode()).hexdigest()[:16].upper()
    
    try:
        with open(hwid_file, 'w') as f:
            f.write(new_hwid)
    except:
        pass
        
    return new_hwid
