import json
import os

DB_FILE = "utilisateurs.json"

def charger_utilisateurs():
    if not os.path.exists(DB_FILE):
        # Compte exemple par défaut avec un faux email pour la structure
        default_db = {
            "exemple": {
                "email": "exemple@nairu.com",
                "password": "exemple"
            }
        }
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(default_db, f, indent=4)
        return default_db
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def sauvegarder_utilisateur(username, email, password):
    comptes = charger_utilisateurs()
    # On stocke l'email et le mot de passe sous forme de sous-dictionnaire
    comptes[username] = {
        "email": email,
        "password": password
    }
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(comptes, f, indent=4)
