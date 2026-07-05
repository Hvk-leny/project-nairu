import streamlit as st
import json
import os
import requests
import datetime
from groq import Groq
from duckduckgo_search import DDGS
import streamlit.components.v1 as components

# ==============================================================================
# --- 1. CONFIGURATION INTERNE & FONCTIONS DE BASE ---
# ==============================================================================

# 🔥 INJECTION SÉCURISÉE DIRECTEMENT DANS LE VRAI <HEAD> DU SITE POUR GOOGLE
components.html(
    """
    <script>
        // Le script cherche le "head" principal du site parent et y greffe la balise de validation
        var meta = parent.document.createElement('meta');
        meta.name = 'google-site-verification';
        meta.content = 'Ih0SvT8spLCGn5y0eaJnMuFrArHwURmtdDCuNdIEUk8';
        parent.document.getElementsByTagName('head')[0].appendChild(meta);
    </script>
    """,
    height=0, # Totalement invisible pour tes utilisateurs
)

def charger_utilisateurs():
    if not os.path.exists("utilisateurs.json"):
        structure_base = {"comptes": {}, "banned_ips": [], "maintenance": False, "maintenance_fin": ""}
        with open("utilisateurs.json", "w", encoding="utf-8") as f:
            json.dump(structure_base, f, indent=4)
        return structure_base
    try:
        with open("utilisateurs.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"comptes": {}, "banned_ips": [], "maintenance": False, "maintenance_fin": ""}

def sauvegarder_donnees(data):
    with open("utilisateurs.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def sauvegarder_utilisateur(username, email, password, ip):
    data = charger_utilisateurs()
    data["comptes"][username.lower().strip()] = {
        "email": email.strip(),
        "password": password,
        "ip": ip
    }
    sauvegarder_donnees(data)

def recuperer_ip_visiteur():
    return "127.0.0.1"

def est_ip_bannie(ip):
    data = charger_utilisateurs()
    return ip in data.get("banned_ips", [])

def ip_deja_utilisee(ip):
    data = charger_utilisateurs()
    for u, infos in data["comptes"].items():
        if infos.get("ip") == ip and u not in ["admin1", "leny", "eliott"]:
            return True
    return False

def executer_recherche_web(requete):
    return "Résultats de recherche simulés pour : " + requete

def charger_memoire():
    if not os.path.exists("memoire.json"):
        with open("memoire.json", "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4)
        return {}
    try:
        with open("memoire.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def sauvegarder_memoire(data):
    with open("memoire.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def calculer_age_nairu():
    try:
        creation = datetime.datetime(2026, 6, 6, 22, 0)
        maintenant = datetime.datetime.now()
        difference = maintenant - creation
        jours = difference.days
        heures = difference.seconds // 3600
        minutes = (difference.seconds // 60) % 60
        return f"{jours} jours, {heures} heures et {minutes} minutes"
    except:
        return "quelques semaines"

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
    /* 🔥 On cache l'icône UNIQUEMENT dans l'expander pour libérer la Sidebar */
    [data-testid="stExpander"] [data-testid="stIconMaterial"] { 
        font-size: 0px !important; 
        color: transparent !important; 
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

data_maintenance = charger_utilisateurs()

if "mode_maintenance" not in st.session_state:
    st.session_state.mode_maintenance = data_maintenance.get("maintenance", False)

if "statut_connexion" not in st.session_state:
    st.session_state.statut_connexion = "Déconnecté"

if "messages_chat" not in st.session_state:
    st.session_state.messages_chat = []

if "forcer_formulaire_admin" not in st.session_state:
    st.session_state.forcer_formulaire_admin = False

# Vérification automatique du Timer de maintenance
if st.session_state.mode_maintenance and data_maintenance.get("maintenance_fin"):
    try:
        fin_maintenance = datetime.datetime.fromisoformat(data_maintenance["maintenance_fin"])
        if datetime.datetime.now() > fin_maintenance:
            data_maintenance["maintenance"] = False
            data_maintenance["maintenance_fin"] = ""
            sauvegarder_donnees(data_maintenance)
            st.session_state.mode_maintenance = False
    except:
        pass

# ==============================================================================
# --- 3. INTERFACE DE CONNEXION / INSCRIPTION ---
# ==============================================================================
if st.session_state.mode_maintenance and st.session_state.statut_connexion == "Déconnecté" and not st.session_state.forcer_formulaire_admin:
    col_gauche, col_centre, col_droite = st.columns([1, 2, 1])
    with col_centre:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.error("### 🛠️ Site temporairement indisponible")
        st.info("Nairu AI est actuellement en cours de maintenance ou de mise à jour.")
        
        if data_maintenance.get("maintenance_fin"):
            try:
                fin = datetime.datetime.fromisoformat(data_maintenance["maintenance_fin"])
                restant = fin - datetime.datetime.now()
                minutes_restantes = max(0, int(restant.total_seconds() // 60))
                if minutes_restantes > 0:
                    st.warning(f"⏳ **Remise en place prévue dans environ :** {minutes_restantes} minute(s).")
                else:
                    st.warning(f"⏳ **Remise en place imminente...**")
            except:
                pass
        
        st.write("Si vous avez besoin d'un accès ou pour toute question, merci de contacter **Eliott** :")
        st.link_button("📸 Contacter Eliott sur Instagram", "https://instagram.com/eliott31tls", use_container_width=True)
        
        st.markdown("<br><br><hr>", unsafe_allow_html=True)
        if st.button("🔒 Connexion Administrateur", use_container_width=False):
            st.session_state.forcer_formulaire_admin = True
            st.rerun()
            
    st.stop()

elif st.session_state.statut_connexion == "Déconnecté":
    st.title("bienvenue sur nairu")
    col_gauche, col_centre, col_droite = st.columns([1, 2, 1])
    
    with col_centre:
        with st.container(border=True):
            if st.session_state.forcer_formulaire_admin:
                st.warning("⚠️ Mode Maintenance Actif - Accès réservé aux Administrateurs")
            
            tab_login, tab_register = st.tabs(["🔒 Connexion", "✨ Créer un compte"])
            
            with tab_login:
                st.markdown("### Connexion")
                with st.form(key="form_connexion"):
                    identifiant = st.text_input("Identifiant ou Prénom :", placeholder="exemple", key="login_username").strip().lower()
                    code_secret = st.text_input("Code secret :", type="password", placeholder="exemple", key="login_password")
                    bouton_connexion = st.form_submit_button("Se connecter", use_container_width=True)
                    
                    if bouton_connexion:
                        user_ip = recuperer_ip_visiteur()
                        data_totale = charger_utilisateurs()
                        
                        if est_ip_bannie(user_ip):
                            st.error("❌ Accès refusé. Votre connexion internet a été bannie de ce site.")
                        elif identifiant in data_totale["comptes"] and data_totale["comptes"][identifiant]["password"] == code_secret:
                            if st.session_state.mode_maintenance and identifiant not in ["admin_nairu_leny", "admin_nairu_eliott"]:
                                st.error("🛑 Ce site est en maintenance. Seuls les comptes admins peuvent se connecter.")
                            else:
                                st.session_state.statut_connexion = "Connecté"
                                st.session_state.user_connecte = identifiant
                                st.session_state.forcer_formulaire_admin = False
                                st.success(f"Bienvenue {identifiant} !")
                                st.rerun()
                        else:
                            st.error("Identifiant ou mot de
