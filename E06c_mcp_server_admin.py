import os
import httpx
import time
import sys

# Configuration
DATA_DIR = "data"
ENEMIES_FILE = os.path.join(DATA_DIR, "marvel_enemies.md")
SERVER_URL = "http://127.0.0.1:8004/admin/notify"

def notify_server():
    print(f"📡 2. Notification du serveur MCP ({SERVER_URL})...")
    try:
        r = httpx.post(SERVER_URL, timeout=5)
        if r.status_code == 200:
            data = r.json()
            print(f"✅ Notification envoyée ! (Touchés : {data.get('broadcast_count', '?')} clients)")
        else:
            print(f"❌ Erreur serveur : {r.status_code}")
    except Exception as e:
        print(f"❌ Impossible de joindre le serveur : {e}")

def add_resource():
    print("📝 1. Création du fichier sur le disque...")
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(ENEMIES_FILE, "w", encoding="utf-8") as f:
        f.write("# Marvel Enemies\n\n- Thanos (Titan Fou)\n- Kang (Le Conquérant)\n- Doctor Doom (Latveria)")
    time.sleep(0.5)
    print("✅ Fichier créé.")
    notify_server()

def remove_resource():
    print("🗑️ 1. Suppression du fichier...")
    try:
        if os.path.exists(ENEMIES_FILE):
            os.remove(ENEMIES_FILE)
            time.sleep(0.5)
            print("✅ Fichier supprimé.")
        else:
            print("⚠️ Le fichier n'existe pas déjà.")
    except Exception as e:
        print(f"❌ Erreur suppression : {e}")
    notify_server()

def main():
    print("=" * 60)
    print("🛠️ E06 : Admin Console (Contrôleur en Terminal)")
    print("=" * 60)
    print("Utilisez cette interface pour simuler une mise à jour côté serveur")
    print("et déclencher une notification vers les clients connectés.")
    
    while True:
        file_exists = os.path.exists(ENEMIES_FILE)
        etat = "✅ PRÉSENT" if file_exists else "❌ ABSENT"
        print(f"\nÉtat de la ressource cible ({ENEMIES_FILE}): {etat}")
        
        print("\nOptions :")
        print("  [A] - Ajouter la ressource 'Marvel Enemies'")
        print("  [S] - Supprimer la ressource 'Marvel Enemies'")
        print("  [quit] ou [exit] - Quitter le programme")
        
        choix = input("\nVotre choix : ").strip().lower()
        
        if choix in ['quit', 'exit', 'q']:
            print("Fermeture de l'admin...")
            sys.exit(0)
        elif choix == 'a':
            add_resource()
        elif choix == 's':
            remove_resource()
        else:
            print("❌ Choix invalide. Veuillez taper A, S, ou quit.")

if __name__ == "__main__":
    main()
