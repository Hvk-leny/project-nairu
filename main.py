import streamlit as st
import json
import os
import requests
from groq import Groq

# ==============================================================================
# --- 1. FONCTIONS DE LA BASE DE DONNÉES JSON (AVEC SÉCURITÉ IP) ---
# ==============================================================================
DB_FILE = "utilisateurs.json"

def recuperer_ip_visiteur():
    try:
        reponse = requests.get("https://api.ipify.org?format=json", timeout=3)
        return reponse.json().get("ip")
    except:
        return "127.0.0.1"

def charger_utilisateurs():
    if not os.path.exists(DB_FILE):
        default_db = {
            "comptes": {
                "exemple": {"email": "exemple@nairu.com", "password": "exemple", "ip": "0.0.0.0"},
                "admin1": {"email": "admin@nairu.com", "password": "adminnairu1", "ip": "127.0.0.1"}
            },
            "banned_ips": []
        }
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(default_db, f, indent=4)
        return default_db
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "comptes" not in data:
                data = {"comptes": data, "banned_ips": []}
            if "admin1" not in data["comptes"]:
                data["comptes"]["admin1"] = {"email": "admin@nairu.com", "password": "adminnairu1", "ip": "127.0.0.1"}
            return data
    except:
        return {"comptes": {}, "banned_ips": []}

def sauvegarder_donnees(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def sauvegarder_utilisateur(username, email, password, ip_address):
    data = charger_utilisateurs()
    data["comptes"][username] = {
        "email": email,
        "password": password,
        "ip": ip_address
    }
    sauvegarder_donnees(data)

def ip_deja_utilisee(ip_address):
    data = charger_utilisateurs()
    for nom, infos in data["comptes"].items():
        if infos.get("ip") == ip_address and nom not in ["exemple", "admin1"]:
            return True
    return False

def est_ip_bannie(ip_address):
    data = charger_utilisateurs()
    return ip_address in data.get("banned_ips", [])

# ==============================================================================
# --- 2. MISE EN PAGE & LOGIQUE DES SESSIONS ---
# ==============================================================================
st.set_page_config(
    page_title="NAIRU - AI",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(
    """
    <style>
    [data-testid="stIconMaterial"] {
        font-size: 0px !important;
        color: transparent !important;
        line-height: 0 !important;
        display: none !important;
    }
    [data-testid="stExpander"] summary {
        position: relative !important;
    }
    [data-testid="stExpander"] summary::after {
        content: '➔' !important;
        font-size: 14px !important;
        color: #00f0ff !important;
        position: absolute !important;
        right: 15px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("bienvenue sur nairu")

if "statut_connexion" not in st.session_state:
    st.session_state.statut_connexion = "Déconnecté"

# ==============================================================================
# --- 3. INTERFACE DE CONNEXION / INSCRIPTION ---
# ==============================================================================
if st.session_state.statut_connexion == "Déconnecté":
    
    col_gauche, col_centre, col_droite = st.columns([1, 2, 1])
    
    with col_centre:
        with st.container(border=True):
            tab_login, tab_register = st.tabs(["🔒 Connexion", "✨ Créer un compte"])
            
            # --- ONGLET 1 : CONNEXION ---
            with tab_login:
                st.markdown("### Connexion")
                
                with st.form(key="form_connexion"):
                    identifiant = st.text_input("Identifiant ou Prénom :", placeholder="exemple", key="login_username")
                    code_secret = st.text_input("Code secret :", type="password", placeholder="exemple", key="login_password")
                    bouton_connexion = st.form_submit_button("Se connecter", use_container_width=True)
                    
                    if bouton_connexion:
                        user_ip = recuperer_ip_visiteur()
                        data_totale = charger_utilisateurs() # Chargement global sécurisé
                        
                        if est_ip_bannie(user_ip):
                            st.error("❌ Accès refusé. Votre connexion internet a été bannie de ce site.")
                        elif identifiant == "admin1" and code_secret == "adminnairu1":
                            st.session_state.statut_connexion = "Connecté"
                            st.session_state.user_connecte = "admin1"
                            st.success("Accès Super-Admin accordé !")
                            st.rerun()
                        elif identifiant in data_totale["comptes"] and data_totale["comptes"][identifiant]["password"] == code_secret:
                            st.session_state.statut_connexion = "Connecté"
                            st.session_state.user_connecte = identifiant
                            st.success(f"Bienvenue {identifiant} !")
                            st.rerun()
                        else:
                            st.error("Identifiant ou mot de passe incorrect.")
            
            # --- ONGLET 2 : CRÉATION DE COMPTE (SÉCURISÉ PAR IP) ---
            with tab_register:
                st.markdown("### Créer un compte")
                st.markdown(
                    """
                    > ⚠️ **Note importante :** > * Pour vous connecter, utilisez votre **identifiant** et votre **mot de passe**.  
                    > * L'**email** sert uniquement à la création du compte.  
                    > * *Système anti-spam : Une seule création de compte est autorisée par connexion internet (IP).*
                    """
                )
                
                with st.form(key="form_inscription"):
                    nouvel_identifiant = st.text_input("Choisis un identifiant :", key="reg_username")
                    nouvel_email = st.text_input("Adresse Email :", placeholder="votre@email.com", key="reg_email")
                    nouveau_code = st.text_input("Choisis un code secret :", type="password", key="reg_password")
                    bouton_inscription = st.form_submit_button("Créer mon compte", use_container_width=True)
                    
                    if bouton_inscription:
                        data_totale = charger_utilisateurs()
                        
                        with st.spinner("Vérification de sécurité..."):
                            user_ip = recuperer_ip_visiteur()
                        
                        if est_ip_bannie(user_ip):
                            st.error("❌ Opération impossible. Votre connexion internet a été bannie.")
                        elif nouvel_identifiant.strip() == "" or nouvel_email.strip() == "" or nouveau_code.strip() == "":
                            st.warning("Veuillez remplir tous les champs.")
                        elif "@" not in nouvel_email or "." not in nouvel_email:
                            st.error("Veuillez entrer une adresse email valide.")
                        elif nouvel_identifiant in data_totale["comptes"]:
                            st.error("Cet identifiant existe déjà !")
                        elif ip_deja_utilisee(user_ip):
                            st.error("❌ Sécurité : Un compte a déjà été créé avec votre connexion internet.")
                        else:
                            sauvegarder_utilisateur(nouvel_identifiant, nouvel_email, nouveau_code, user_ip)
                            st.success("🎉 Compte créé avec succès ! Vous pouvez maintenant vous connecter.")

        # --- BLOC AUTONOME INFORMATIONS TOUT EN BAS ---
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("ℹ️ En savoir plus sur Nairu (Informations)"):
            st.markdown("### 🚀 À propos de Nairu")
            st.write(
                "Nous sommes **deux Toulousains passionnés de tech, Leny et Eliott**. "
                "Un soir, on a eu l'idée un peu folle de créer l'outil ultime de recherche "
                "tout en gardant vos données en parfaite sécurité. C'est comme ça que Nairu est né !"
            )
            st.markdown("---")
            st.markdown("### 🪲 Un problème ou un bug ?")
            st.write("Si vous rencontrez un problème technique ou si vous voulez nous faire un retour, signalez-le en DM :")
            st.link_button("💬 Signaler un problème sur Instagram", "https://instagram.com/eliott31tls")
            st.caption("Auteur principal : @eliott31tls")

# ==============================================================================
# --- 4. INTERFACE UNE FOIS CONNECTÉ ---
# ==============================================================================
else:
    # 🔴 CAS COMPTE SUPER-ADMINISTRATEUR (admin1)
    if st.session_state.user_connecte == "admin1":
        st.markdown("## 🛠️ PANNEAU DE CONTRÔLE SÉCURITÉ - NAIRU")
        st.info("Bienvenue Eliott ou Leny. Ici, vous gérez les utilisateurs et bloquez les attaques par spam.")
        
        data_totale = charger_utilisateurs()
        
        st.markdown("### 👥 Utilisateurs enregistrés et Adresses IP")
        
        for nom, infos in data_totale["comptes"].items():
            if nom != "admin1" and nom != "exemple":
                col_user, col_ip, col_action = st.columns([2, 2, 1])
                with col_user:
                    st.write(f"**Identifiant :** {nom} ({infos.get('email', 'Pas de mail')})")
                with col_ip:
                    st.code(infos.get('ip', '0.0.0.0'))
                with col_action:
                    if st.button(f"🚫 Bannir", key=f"ban_{nom}"):
                        user_ip_to_ban = infos.get('ip')
                        if user_ip_to_ban and user_ip_to_ban not in data_totale["banned_ips"]:
                            data_totale["banned_ips"].append(user_ip_to_ban)
                            del data_totale["comptes"][nom]
                            sauvegarder_donnees(data_totale)
                            st.success(f"IP {user_ip_to_ban} bannie et compte supprimé !")
                            st.rerun()

        # --- SECTION IP BANNIES ---
        st.markdown("---")
        st.markdown("### 🛑 Liste des adresses IP bloquées")
        if not data_totale.get("banned_ips"):
            st.write("*Aucune IP bloquée pour le moment. Le site est safe.*")
        else:
            for ip in data_totale["banned_ips"]:
                col_banned, col_unban = st.columns([4, 1])
                with col_banned:
                    st.error(f"IP Bloquée : {ip}")
                with col_unban:
                    if st.button("🔓 Débloquer", key=f"unban_{ip}"):
                        data_totale["banned_ips"].remove(ip)
                        sauvegarder_donnees(data_totale)
                        st.success(f"IP {ip} débloquée !")
                        st.rerun()

    # 🟢 CAS UTILISATEUR CLASSIQUE CONNECTÉ
    else:
        st.write(f"Félicitations {st.session_state.user_connecte}, tu es connecté à l'interface de Nairu ! Moteur prêt.")
    
    # BOUTON DE DÉCONNEXION COMMUN
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔴 Déconnexion", use_container_width=True):
        st.session_state.statut_connexion = "Déconnecté"
        st.session_state.user_connecte = None
        
        st.rerun()
sauvegarder_donnees({"comptes": charger_utilisateurs()["comptes"], "banned_ips": []})
