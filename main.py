import streamlit as st
import json
import os
import requests
import random
from groq import Groq

# ==============================================================================
# --- 1. FONCTION D'ENVOI DE MAIL VIA BREVO ---
# ==============================================================================
def envoyer_code_verification(email_destinataire):
    code = str(random.randint(100000, 999999))
    url = "https://api.brevo.com/v3/smtp/email"
    
    headers = {
        "accept": "application/json",
        "api-key": "xsmtpsib-4b98b43cd2774b9811ba0e6b91e919eb2cda02083eba9f1299ce8b51ae44ae05-OlOkVkE5bCGgzZt3",
        "content-type": "application/json"
    }
    
    data = {
        "sender": {"name": "Nairu AI", "email": "nairu.ia.toulouse@outlook.com"},
        "to": [{"email": email_destinataire}],
        "subject": "🔑 Code de vérification Nairu",
        "textContent": f"Bonjour,\n\nVoici votre code de vérification pour finaliser la création de votre compte Nairu :\n\n👉 {code}\n\nL'email sert uniquement à la création du compte. Pour vous connecter, utilisez votre identifiant et votre mot de passe.\n\nL'équipe Nairu (Eliott & Leny)"
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 201:
            return code
        else:
            print(f"Erreur Brevo : {response.text}")
            return None
    except Exception as e:
        print(f"Erreur connexion : {e}")
        return None

# ==============================================================================
# --- 2. FONCTIONS DE LA BASE DE DONNÉES JSON ---
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
# --- 3. MISE EN PAGE & LOGIQUE DES SESSIONS ---
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
# --- 4. INTERFACE DE CONNEXION / INSCRIPTION ---
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
            
            # --- ONGLET 2 : CRÉATION DE COMPTE ---
            with tab_register:
                st.markdown("### Créer un compte")
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
                            with st.spinner("Envoi du code de vérification par mail..."):
                                code_envoye = envoyer_code_verification(nouvel_email)
                                
                            if code_envoye:
                                st.session_state.temp_user = {
                                    "id": nouvel_identifiant,
                                    "email": nouvel_email,
                                    "password": nouveau_code,
                                    "code": code_envoye
                                }
                                st.success("📩 Un code de vérification vous a été envoyé par mail !")
                            else:
                                st.error("Impossible d'envoyer le mail. Vérifiez votre configuration Brevo.")

            # --- CASE POUR ENTRER LE CODE DE VÉRIFICATION ---
            if "temp_user" in st.session_state:
                st.markdown("---")
                st.markdown("### 🔑 Entrez le code reçu par mail")
                
                with st.form(key="form_verification_code"):
                    code_saisi = st.text_input("Code à 6 chiffres :", placeholder="123456")
                    bouton_valider_code = st.form_submit_button("Valider et créer le compte", use_container_width=True)
                    
                    if bouton_valider_code:
                        if code_saisi == st.session_state.temp_user["code"]:
                            sauvegarder_utilisateur(
                                st.session_state.temp_user["id"],
                                st.session_state.temp_user["email"],
                                st.session_state.temp_user["password"]
                            )
                            st.success("🎉 Compte validé et créé avec succès ! Connectez-vous dans l'onglet Connexion.")
                            del st.session_state.temp_user
                        else:
                            st.error("❌ Code incorrect. Réessayez.")

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
# --- 5. INTERFACE UNE FOIS CONNECTÉ (À COMPLÉTER PLUS TARD) ---
# ==============================================================================
else:
    st.write("Félicitations, tu es connecté à l'interface de Nairu ! Moteur prêt.")
    if st.button("🔴 Déconnexion"):
        st.session_state.statut_connexion = "Déconnecté"
        st.rerun()
