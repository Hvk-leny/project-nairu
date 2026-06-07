import streamlit as st
import json
import os
import requests
from groq import Groq

# ==============================================================================
# --- 1. FONCTIONS DE LA BASE DE DONNÉES JSON (AVEC SÉCURITÉ IP) ---
# ==============================================================================
DB_FILE = "utilisateurs.json"

# Fonction magique et ultra-rapide pour choper l'IP de l'utilisateur
def recuperer_ip_visiteur():
    try:
        # On interroge un mini-service gratuit qui renvoie juste l'IP publique
        reponse = requests.get("https://api.ipify.org?format=json", timeout=3)
        return reponse.json().get("ip")
    except:
        return "127.0.0.1" # IP de secours si le service est indisponible

def charger_utilisateurs():
    if not os.path.exists(DB_FILE):
        # Compte exemple d'origine avec une fausse IP pour la structure
        default_db = {
            "exemple": {
                "email": "exemple@nairu.com",
                "password": "exemple",
                "ip": "0.0.0.0"
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

def sauvegarder_utilisateur(username, email, password, ip_address):
    comptes = charger_utilisateurs()
    comptes[username] = {
        "email": email,
        "password": password,
        "ip": ip_address # On enregistre son IP précieusement
    }
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(comptes, f, indent=4)

# Fonction pour vérifier si une IP a déjà créé un compte sur le site
def ip_deja_utilisee(ip_address):
    comptes = charger_utilisateurs()
    for nom, infos in comptes.items():
        # Si l'IP existe déjà et que ce n'est pas le compte admin "exemple"
        if infos.get("ip") == ip_address and nom != "exemple":
            return True
    return False

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
                base_comptes = charger_utilisateurs()
                
                with st.form(key="form_connexion"):
                    identifiant = st.text_input("Identifiant ou Prénom :", placeholder="exemple", key="login_username")
                    code_secret = st.text_input("Code secret :", type="password", placeholder="exemple", key="login_password")
                    bouton_connexion = st.form_submit_button("Se connecter", use_container_width=True)
                    
                    if bouton_connexion:
                        if identifiant in base_comptes and base_comptes[identifiant]["password"] == code_secret:
                            st.session_state.statut_connexion = "Connecté"
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
                        base_comptes = charger_utilisateurs()
                        
                        # Étape 1 : On récupère l'IP du visiteur en direct
                        with st.spinner("Vérification de sécurité..."):
                            user_ip = recuperer_ip_visiteur()
                        
                        # Étape 2 : Les vérifications de sécurité
                        if nouvel_identifiant.strip() == "" or nouvel_email.strip() == "" or nouveau_code.strip() == "":
                            st.warning("Veuillez remplir tous les champs.")
                        elif "@" not in nouvel_email or "." not in nouvel_email:
                            st.error("Veuillez entrer une adresse email valide.")
                        elif nouvel_identifiant in base_comptes:
                            st.error("Cet identifiant existe déjà !")
                        elif ip_deja_utilisee(user_ip):
                            # 🔥 LA SÉCURITÉ MAGIQUE : On bloque si l'IP a déjà servi !
                            st.error("❌ Sécurité : Un compte a déjà été créé avec votre connexion internet.")
                        else:
                            # Tout est OK, on enregistre l'IP avec le reste dans le JSON
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
    st.write("Félicitations, tu es connecté à l'interface de Nairu ! Moteur prêt.")
    if st.button("🔴 Déconnexion"):
        st.session_state.statut_connexion = "Déconnecté"
        st.rerun()
