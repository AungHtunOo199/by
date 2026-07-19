import hashlib
import base64
import datetime
import requests
import os
import uuid

# --- CONFIGURATION ---
SECRET_KEY = "OSUTA_PRIVATE_SECRET_2026"

def get_internet_time():
    try:
        response = requests.get('http://worldtimeapi.org/api/timezone/Asia/Yangon', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return datetime.datetime.fromisoformat(data['datetime'].split('.')[0])
    except:
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
        expected_sig = hashlib.sha256((dev_id + SECRET_KEY).encode()).hexdigest()[:8]
        if signature == expected_sig and dev_id == device_id:
            return datetime.datetime.strptime(expiry_str, '%Y-%m-%d')
    except:
        pass
    return None

def get_device_id():
    # ID သိမ်းမယ့် ဖိုင်လမ်းကြောင်း
    id_file = "/sdcard/.osuta_id" if os.path.exists("/sdcard") else ".osuta_id"
    
    # ၁။ အရင်က သိမ်းထားတဲ့ ID ရှိရင် အဲ့ဒါကိုပဲ ယူမယ်
    if os.path.exists(id_file):
        try:
            with open(id_file, 'r') as f:
                saved_id = f.read().strip()
                if saved_id: return saved_id
        except:
            pass

    # ၂။ မရှိသေးရင် ID အသစ်တစ်ခု တည်ဆောက်မယ်
    new_id = ""
    try:
        import subprocess
        # Android ID ကို အရင်ကြိုးစားယူမယ်
        new_id = subprocess.check_output("settings get secure android_id", shell=True).decode().strip()
    except:
        pass
    
    if not new_id or new_id == "null":
        # Android ID မရရင် Random UUID တစ်ခု ထုတ်မယ် (ဒါကလည်း ဖုန်းတစ်လုံးနဲ့ တစ်လုံး မတူပါဘူး)
        new_id = "OSUTA-" + str(uuid.uuid4()).split('-')[0].upper() + str(uuid.getnode())[-4:]

    # ၃။ ရလာတဲ့ ID ကို ဖိုင်ထဲမှာ အသေသိမ်းထားမယ်
    try:
        with open(id_file, 'w') as f:
            f.write(new_id)
    except:
        # Permission မရရင် local မှာပဲ သိမ်းမယ်
        with open(".osuta_id", 'w') as f:
            f.write(new_id)
            
    return new_id

def check_activation(device_id):
    token_path = "/sdcard/.osuta_token" if os.path.exists("/sdcard") else ".osuta_token"
    
    if not os.path.exists(token_path):
        # Local path မှာလည်း ထပ်စစ်မယ်
        if os.path.exists(".osuta_token"):
            token_path = ".osuta_token"
        else:
            return False, "NOT_ACTIVATED"
    
    with open(token_path, 'r') as f:
        token = f.read().strip()
    
    expiry_date = decrypt_token(token, device_id)
    if not expiry_date:
        return False, "INVALID_TOKEN"
    
    current_time = get_internet_time()
    if not current_time:
        current_time = datetime.datetime.now()

    if current_time > expiry_date:
        return False, "EXPIRED"
    
    return True, expiry_date.strftime('%Y-%m-%d')
