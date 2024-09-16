import websocket
import json
import time
import threading
import os
import requests
from colorama import Fore, Style, init

init(autoreset=True)

def load_tokens(file='tokens.txt'):
    with open(file, 'r') as token_file:
        return [token.strip() for token in token_file.readlines() if token.strip()]

def choose_status():
    print(f"{Fore.MAGENTA}Choose your status:{Style.RESET_ALL}")
    print(f"{Fore.CYAN}1. Online")
    print(f"{Fore.RED}2. Do Not Disturb (DND)")
    print(f"{Fore.YELLOW}3. Idle")
    choice = input(f"{Fore.GREEN}Enter your choice (1/2/3): {Style.RESET_ALL}")
    
    if choice == '1':
        return "online"
    elif choice == '2':
        return "dnd"
    elif choice == '3':
        return "idle"
    else:
        print(f"{Fore.RED}Invalid choice. Defaulting to 'online'.")
        return "online"

def choose_activity():
    enable_activity = input(f"{Fore.GREEN}Do you want to appear as playing a game? (y/n): {Style.RESET_ALL}").lower()
    if enable_activity == 'y':
        game_name = input(f"{Fore.GREEN}Enter the name of the game: {Style.RESET_ALL}")
        return {"name": game_name, "type": 0}
    return None

def enable_streamer_mode():
    enable_streamer = input(f"{Fore.GREEN}Do you want to enable streamer mode? (y/n): {Style.RESET_ALL}").lower()
    if enable_streamer == 'y':
        return {
            "name": "Twitch",
            "type": 1,
            "url": "https://twitch.tv/your_channel"
        }
    return None

def send_auth(ws, token, status, activity, streamer_mode):
    auth_payload = {
        "op": 2,
        "d": {
            "token": token,
            "properties": {
                "$os": "windows",
                "$browser": "chrome",
                "$device": "pc"
            },
            "presence": {
                "status": status,
                "since": 0,
                "activities": [activity] if activity else [],
                "afk": False
            }
        }
    }
    
    if streamer_mode:
        auth_payload['d']['presence']['activities'].append(streamer_mode)
    
    ws.send(json.dumps(auth_payload))

def send_heartbeat(ws, interval):
    while True:
        heartbeat_payload = {
            "op": 1,
            "d": None
        }
        ws.send(json.dumps(heartbeat_payload))
        time.sleep(interval / 1000)

def on_message(ws, message, token, status, activity, streamer_mode):
    data = json.loads(message)
    if data['op'] == 10:
        heartbeat_interval = data['d']['heartbeat_interval']
        print(f"{Fore.GREEN}Connected with token: {Fore.CYAN}{token[:10]}...{Style.RESET_ALL}")
        threading.Thread(target=send_heartbeat, args=(ws, heartbeat_interval)).start()
        send_auth(ws, token, status, activity, streamer_mode)

def on_error(ws, error, token):
    print(f"{Fore.RED}Error for token: {Fore.CYAN}{token[:10]}... {Fore.RED}{error}")

def on_close(ws, token):
    print(f"{Fore.YELLOW}Connection closed for token: {Fore.CYAN}{token[:10]}...")

def on_open(ws, token):
    print(f"{Fore.GREEN}WebSocket opened for token: {Fore.CYAN}{token[:10]}...")

def connect_to_discord(token, status, activity, streamer_mode):
    gateway_url = "wss://gateway.discord.gg/?v=9&encoding=json"
    ws = websocket.WebSocketApp(gateway_url,
                                on_message=lambda ws, msg: on_message(ws, msg, token, status, activity, streamer_mode),
                                on_error=lambda ws, err: on_error(ws, err, token),
                                on_close=lambda ws: on_close(ws, token))
    ws.on_open = lambda ws: on_open(ws, token)
    ws.run_forever()

def start_tokens(tokens, status, activity, streamer_mode):
    threads = []
    for token in tokens:
        thread = threading.Thread(target=connect_to_discord, args=(token, status, activity, streamer_mode))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

def main():
    os.system('cls' if os.name == 'nt' else 'clear')

    tokens = load_tokens()
    
    if tokens:
        print(f"{Fore.MAGENTA}Loaded {len(tokens)} tokens from tokens.txt.{Style.RESET_ALL}")
        
        status = choose_status()
        activity = choose_activity()
        streamer_mode = enable_streamer_mode()
        
        start_tokens(tokens, status, activity, streamer_mode)

        input(f"{Fore.YELLOW}Press Enter to restart...{Style.RESET_ALL}")
        main()
    else:
        print(f"{Fore.RED}No tokens found in tokens.txt!{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
