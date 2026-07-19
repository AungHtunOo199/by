import sys
import os
import time
import osuta_security

# ANSI Color Codes
G = "\033[1;32m" # Green
R = "\033[1;31m" # Red
Y = "\033[1;33m" # Yellow
C = "\033[1;36m" # Cyan
W = "\033[1;37m" # White
RESET = "\033[0m"

def show_logo():
    os.system('clear' if os.name == 'posix' else 'cls')
    print(f"""{C}
  ██████  ███████ ██    ██ ████████  █████  
 ██    ██ ██      ██    ██    ██    ██   ██ 
 ██    ██ ███████ ██    ██    ██    ███████ 
 ██    ██      ██ ██    ██    ██    ██   ██ 
  ██████  ███████  ██████     ██    ██   ██ 
{RESET}
{G}         [ OSUTA BYPASS PREMIUM TOOL ]          {RESET}
{Y} ---------------------------------------------- {RESET}
{W}  Author   : OSUTA                              {RESET}
{W}  Version  : 1.1.0 (Commercial)                 {RESET}
{W}  Telegram : @osuta247                          {RESET}
{Y} ---------------------------------------------- {RESET}
""")

def main():
    dev_id = osuta_security.get_device_id()
    
    # Activation Check
    status, result = osuta_security.check_activation(dev_id)
    
    if not status:
        show_logo()
        if result == "NOT_ACTIVATED":
            print(f"{R}      [!] YOUR DEVICE IS NOT ACTIVATED! [!]{RESET}")
        elif result == "INVALID_TOKEN":
            print(f"{R}      [!] INVALID ACTIVATION TOKEN! [!]{RESET}")
        elif result == "EXPIRED":
            print(f"{R}      [!] YOUR LICENSE HAS EXPIRED! [!]{RESET}")
        
        print(f"\n{W}  YOUR DEVICE ID: {Y}{dev_id}{RESET}")
        print(f"{W}  Please send your ID to Admin to get Key.{RESET}")
        print(f"{C}  Telegram: @osuta247{RESET}")
        
        token = input(f"\n{G}  Enter Activation Token: {RESET}").strip()
        if token:
            token_path = "/sdcard/.osuta_token" if os.path.exists("/sdcard") else ".osuta_token"
            try:
                with open(token_path, 'w') as f:
                    f.write(token)
                print(f"\n{G}  [+] Token saved! Please restart the tool.{RESET}")
            except:
                with open(".osuta_token", 'w') as f:
                    f.write(token)
                print(f"\n{G}  [+] Token saved locally! Please restart the tool.{RESET}")
        sys.exit()

    # If Activated, load original tool
    try:
        import ko
        ko.check_activation = lambda: True
        ko.Logo = show_logo
    except ImportError:
        print(f"{R}[-] Error: ko module not found!{RESET}")
        sys.exit(1)

    while True:
        show_logo()
        print(f"{G}  [+] Status: Activated (Expires: {result}){RESET}")
        print(f"{Y} ---------------------------------------------- {RESET}")
        print(f"{W}  [1] ADB Connect Tool{RESET}")
        print(f"{W}  [2] Auto Bypass (Scan + Ruijie){RESET}")
        print(f"{W}  [3] Exit Tool{RESET}")
        print(f"{Y} ---------------------------------------------- {RESET}")
        
        choice = input(f"{C}  Select Option >> {RESET}").strip()
        
        if choice == '1':
            ko.option_adb_connect()
        elif choice == '2':
            ko.option_auto_bypass()
        elif choice == '3':
            print(f"\n{G}[+] Thank you for using OSUTA! Goodbye.{RESET}")
            break
        else:
            print(f"\n{R}[-] Invalid Option!{RESET}")
            time.sleep(1)

if __name__ == "__main__":
    main()
