import os, socket, requests
from pathlib import Path
from dotenv import load_dotenv

class Notifier:
    def __init__(self):
        self.last_ip = None
        load_dotenv(Path(__file__).parent.parent/'.env.ip_notify')
    
    def send_telegram(self, ip):
        if ip != self.last_ip:
            requests.post(
                f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}/sendMessage",
                data={"chat_id": os.getenv('CHAT_ID'), "text": f"👻 {socket.gethostname()} 🌐 {ip}"}
            )
            self.last_ip = ip

notifier = Notifier()
