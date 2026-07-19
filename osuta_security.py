import hashlib
import base64
import datetime
import requests
import os

# --- CONFIGURATION ---
SECRET_KEY = "OSUTA_PRIVATE_SECRET_2026" # Key ထုတ်တဲ့အခါ သုံးမယ့် လျှို့ဝှက်ကုဒ်

def get_internet_time():
    try:
        # Google သို့မဟုတ် Time API ကနေ အချိန်ယူမယ်
        response = requests.get('http://worldtimeapi.org/api/timezone/Asia/Yangon', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return datetime.datetime.fromisoformat(data['datetime'].split('.')[0])
    except:
        try:
            # Fallback to google header time
            res = requests.get('http://www.google.com', timeout=5)
            date_str = res.headers['Date']
            return datetime.datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z')
        except:
            return None

def decrypt_token(token, device_id):
    try:
        # Token ကို decode လုပ်ပြီး Device ID နဲ့ Expiry Date ကို ပြန်ထုတ်မယ်
        decoded = base64.b64decode(token).decode()
        # Format: SHA256(device_id+secret)[:8] + "|" + expiry_date + "|" + device_id
        parts = decoded.split("|")
        if len(parts) != 3: return None
        
        signature, expiry_str, dev_id = parts
        
        # စစ်ဆေးခြင်း
        expected_sig = hashlib.sha256((dev_id + SECRET_KEY).encode()).hexdigest()[:8]
        if signature == expected_sig and dev_id == device_id:
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
    
    expiry_date = decrypt_token(token, device_id)
    if not expiry_date:
        return False, "INVALID_TOKEN"
    
    current_time = get_internet_time()
    if not current_time:
        # အင်တာနက်မရှိရင် local time နဲ့ စစ်မယ် (သို့သော် security အတွက် အင်တာနက် လိုအပ်တယ်လို့ ပြောလို့ရပါတယ်)
        current_time = datetime.datetime.now()
        print("\033[1;33m[!] Warning: Using local time. Please connect to internet for security.\033[0m")

    if current_time > expiry_date:
        return False, "EXPIRED"
    
    return True, expiry_date.strftime('%Y-%m-%d')

def get_device_id():
    # Termux/Android မှာ device id ယူတဲ့ command
    try:
        import subprocess
        cmd = "settings get secure android_id"
        out = subprocess.check_output(cmd, shell=True).decode().strip()
        if out: return out
    except:
        pass
    # PC/Fallback
    import uuid
    return str(uuid.getnode())
