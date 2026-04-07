import os
from dotenv import load_dotenv
import phoenix as px
import time

load_dotenv()

# Correction du port déprécié
os.environ["PHOENIX_PORT"] = "6006"

print("====================================")
print("[PHOENIX SERVER] 🦅 Initialisation...")
print("====================================")

# Lancement du serveur local Phoenix
session = px.launch_app()
print(f"[PHOENIX SERVER] 🌐 Serveur Démarré et accessible via : {session.url}")
print("[PHOENIX SERVER] 📡 En attente de traces...")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("[PHOENIX SERVER] 🛑 Arrêt du serveur.")
