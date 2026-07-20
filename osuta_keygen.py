import hashlib
import base64
import datetime

# --- CONFIGURATION (MUST MATCH osuta_security.py) ---
SECRET_KEY = "OSUTA_PRIVATE_SECRET_2026"

def generate_token(device_id, days):
    # Unlimited key အတွက် နှစ်ပေါင်း ၁၀၀ ပေါင်းထည့်မယ်
    if days == 9999:
        expiry_date = datetime.datetime(2126, 1, 1)
        expiry_str = "UNLIMITED"
    else:
        expiry_date = datetime.datetime.now() + datetime.timedelta(days=days)
        expiry_str = expiry_date.strftime('%Y-%m-%d')
    
    # Signature လုပ်မယ် (လိမ်လို့မရအောင် Device ID နဲ့ ပေါင်းစစ်မယ်)
    signature_raw = f"{device_id}{SECRET_KEY}{expiry_str}"
    signature = hashlib.sha256(signature_raw.encode()).hexdigest()[:10]
    
    # Data တွေကို ပေါင်းပြီး base64 လုပ်မယ်
    raw_data = f"{signature}|{expiry_str}|{device_id}"
    token = base64.b64encode(raw_data.encode()).decode()
    return token

def main():
    print("\033[1;36m")
    print("==========================================")
    print("      OSUTA ADMIN PREMIUM KEYGEN v2       ")
    print("==========================================")
    print("\033[0m")
    
    dev_id = input("\033[1;37m[>] Enter User Device ID: \033[0m").strip().upper()
    if not dev_id:
        print("\033[1;31m[-] Device ID cannot be empty!\033[0m")
        return

    print("\n\033[1;32m[ SELECT VALIDITY ]\033[0m")
    print(" [1] 1 Day")
    print(" [2] 3 Days")
    print(" [3] 7 Days (1 Week)")
    print(" [4] 30 Days (1 Month)")
    print(" [5] 365 Days (1 Year)")
    print(" [6] Unlimited")
    print(" [7] Custom Days")
    
    choice = input("\n\033[1;36mSelect Option >> \033[0m").strip()
    
    days = 0
    if choice == '1': days = 1
    elif choice == '2': days = 3
    elif choice == '3': days = 7
    elif choice == '4': days = 30
    elif choice == '5': days = 365
    elif choice == '6': days = 9999
    elif choice == '7':
        try:
            days = int(input("\033[1;37mEnter number of days: \033[0m"))
        except ValueError:
            print("\033[1;31m[-] Invalid number!\033[0m")
            return
    else:
        print("\033[1;31m[-] Invalid choice!\033[0m")
        return

    key = generate_token(dev_id, days)
    
    print("\n" + "="*42)
    print(f"\033[1;32m[+] SUCCESS! KEY GENERATED\033[0m")
    print(f"\033[1;37mDevice ID : {dev_id}\033[0m")
    print(f"\033[1;37mValidity  : {'Unlimited' if days == 9999 else str(days) + ' Days'}\033[0m")
    print("-" * 42)
    print(f"\033[1;33m{key}\033[0m")
    print("-" * 42)
    print("\033[1;37m(Copy and send the key above to user)\033[0m")
    print("="*42 + "\n")

if __name__ == "__main__":
    main()
