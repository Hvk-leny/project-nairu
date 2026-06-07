import streamlit as st
import json
import os
from groq import Groq

# ==============================================================================
# --- 1. FONCTIONS DE LA BASE DE DONNÉES JSON ---
# ==============================================================================
DB_FILE = "utilisateurs.json"

def charger_utilisateurs():
    if not os.path.exists(DB_FILE):
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
            data = json.load(f)
            if data and "exemple" in data and isinstance(data["exemple"], str):
                raise ValueError("Ancienne structure")
            return data
    except:
        default_db = {
            "exemple": {
                "email": "exemple@nairu.com",
                "password": "exemple"
            }
        }
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(default_db, f, indent=4)
        return default_db

def sauvegarder_utilisateur(username, email, password):
    comptes = charger_utilisateurs()
    comptes[username] = {
        "email": email,
        "password": password
    }
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(comptes, f, indent=4)

# ==============================================================================
# --- 2. MISE EN PAGE & BIENVENUE ---
# ==============================================================================
st.set_page_config(
    page_title="NAIRU - AI",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Masquage des bugs d'icônes natifs
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

# Ton grand titre d'accueil
st.title("bienvenue sur nairu")
# ==============================================================================
# --- 3. LOGIQUE DES SESSIONS ET INTERFACE DE CONNEXION ---
# ==============================================================================

# On initialise le statut de connexion s'il n'existe pas encore
if "statut_connexion" not in st.session_state:
    st.session_state.statut_connexion = "Déconnecté"

# Si l'utilisateur est déconnecté, on affiche le rectangle de connexion au centre
if st.session_state.statut_connexion == "Déconnecté":
    
    # On crée 3 colonnes pour centrer le rectangle au milieu de l'écran (largeur 1/2/1)
    col_gauche, col_centre, col_droite = st.columns([1, 2, 1])
    
    with col_centre:
        # On ouvre un cadre visuel propre (un container) pour simuler le rectangle de l'interface
        with st.container(border=True):
            
            # Création des deux onglets à l'intérieur du rectangle
            tab_login, tab_register = st.tabs(["🔒 Connexion", "✨ Créer un compte"])
            
            # --- STRUCTURE DE L'ONGLET 1 : CONNEXION ---
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
            
            # --- STRUCTURE DE L'ONGLET 2 : CRÉATION DE COMPTE ---
            with tab_register:
                st.markdown("### Créer un compte")
                
                # Bloc d'explication obligatoire
                st.markdown(
                    """
                    > ⚠️ **Note importante :** > * Pour vous connecter, utilisez votre **identifiant** et votre **mot de passe**.  
                    > * L'**email** sert uniquement à la création du compte.
                    """
                )
                
                with st.form(key="form_inscription"):
                    nouvel_identifiant = st.text_input("Choisis un identifiant :", key="reg_username")
                    nouvel_email = st.text_input("Adresse Email :", placeholder="votre@email.com", key="reg_email")
                    nouveau_code = st.text_input("Choisis un code secret :", type="password", key="reg_password")
                    bouton_inscription = st.form_submit_button("Créer mon compte", use_container_width=True)
                    
                    if bouton_inscription:
                        base_comptes = charger_utilisateurs()
                        if nouvel_identifiant.strip() == "" or nouvel_email.strip() == "" or nouveau_code.strip() == "":
                            st.warning("Veuillez remplir tous les champs.")
                        elif "@" not in nouvel_email or "." not in nouvel_email:
                            st.error("Veuillez entrer une adresse email valide.")
                        elif nouvel_identifiant in base_comptes:
                            st.error("Cet identifiant existe déjà !")
                        else:
                            sauvegarder_utilisateur(nouvel_identifiant, nouvel_email, nouveau_code)
                            st.success("🎉 Compte créé ! Connecte-toi dans l'onglet d'à côté.")
                            # ==============================================================================
    # --- BLOC AUTONOME : INFORMATIONS (À POSER TOUT EN BAS) ---
    # ==============================================================================
    # On se remet au centre pour que ça s'aligne sous ton rectangle
    with col_centre:
        st.markdown("<br>", unsafe_allow_html=True) # Petit espace
        
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
            st.link_button(
                "💬 Signaler un problème sur Instagram", 
                "https://instagram.com/eliott31tls"
            )
            st.caption("Auteur principal : @eliott31tls")
