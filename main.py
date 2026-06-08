import streamlit as st
import json
import os
import requests
from groq import Groq
from duckduckgo_search import DDGS

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
    # Comptes permanents qui ne s'effaceront JAMAIS
    comptes_permanents = {
        "admin1": {"email": "admin@nairu.com", "password": "adminnairu1", "ip": "127.0.0.1"},
        "leny": {"email": "leny@nairu.com", "password": "lenynairu", "ip": "0.0.0.0"},
        "eliott": {"email": "eliott@nairu.com", "password": "eliottnairu", "ip": "0.0.0.0"},
        "exemple": {"email": "exemple@nairu.com", "password": "exemple", "ip": "0.0.0.0"}
    }

    if not os.path.exists(DB_FILE):
        default_db = {"comptes": comptes_permanents, "banned_ips": []}
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(default_db, f, indent=4)
        return default_db
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "comptes" not in data:
                data = {"comptes": {}, "banned_ips": []}
            
            # On réinjecte de force vos comptes pour être sûr qu'ils restent là
            for nom, infos in comptes_permanents.items():
                if nom not in data["comptes"]:
                    data["comptes"][nom] = infos
            return data
    except:
        return {"comptes": comptes_permanents, "banned_ips": []}

def sauvegarder_donnees(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def sauvegarder_utilisateur(username, email, password, ip_address):
    data = charger_utilisateurs()
    data["comptes"][username.lower()] = {
        "email": email,
        "password": password,
        "ip": ip_address
    }
    sauvegarder_donnees(data)

def ip_deja_utilisee(ip_address):
    data = charger_utilisateurs()
    for nom, infos in data["comptes"].items():
        if infos.get("ip") == ip_address and nom not in ["exemple", "admin1", "leny", "eliott"]:
            return True
    return False

def est_ip_bannie(ip_address):
    data = charger_utilisateurs()
    return ip_address in data.get("banned_ips", [])

def executer_recherche_web(requete):
    try:
        with DDGS() as ddgs:
            resultats = [r for r in ddgs.text(requete, max_results=3)]
            contexte = "\n".join([f"Titre: {res['title']}\nLien: {res['href']}\nExtrait: {res['body']}\n---" for res in resultats])
            return contexte
    except:
        return "Impossible d'accéder au web pour le moment."

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
    [data-testid="stIconMaterial"] { font-size: 0px !important; color: transparent !important; display: none !important; }
    [data-testid="stExpander"] summary { position: relative !important; }
    [data-testid="stExpander"] summary::after { content: '➔' !important; font-size: 14px !important; color: #00f0ff !important; position: absolute !important; right: 15px !important; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("bienvenue sur nairu")

if "statut_connexion" not in st.session_state:
    st.session_state.statut_connexion = "Déconnecté"

if "messages_chat" not in st.session_state:
    st.session_state.messages_chat = []

# ==============================================================================
# --- 3. INTERFACE DE CONNEXION / INSCRIPTION ---
# ==============================================================================
if st.session_state.statut_connexion == "Déconnecté":
    col_gauche, col_centre, col_droite = st.columns([1, 2, 1])
    
    with col_centre:
        with st.container(border=True):
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
                            st.session_state.statut_connexion = "Connecté"
                            st.session_state.user_connecte = identifiant
                            st.success(f"Bienvenue {identifiant} !")
                            st.rerun()
                        else:
                            st.error("Identifiant ou mot de passe incorrect.")
            
            with tab_register:
                st.markdown("### Créer un compte")
                st.markdown("> *Système anti-spam : Une seule création de compte par IP.*")
                with st.form(key="form_inscription"):
                    nouvel_identifiant = st.text_input("Choisis un identifiant :", key="reg_username")
                    nouvel_email = st.text_input("Adresse Email :", placeholder="votre@email.com", key="reg_email")
                    nouveau_code = st.text_input("Choisis un code secret :", type="password", key="reg_password")
                    bouton_inscription = st.form_submit_button("Créer mon compte", use_container_width=True)
                    
                    if bouton_inscription:
                        data_totale = charger_utilisateurs()
                        with st.spinner("Vérification..."):
                            user_ip = recuperer_ip_visiteur()
                        
                        if est_ip_bannie(user_ip):
                            st.error("❌ Connexion bannie.")
                        elif nouvel_identifiant.strip() == "" or nouveau_code.strip() == "":
                            st.warning("Veuillez remplir les champs.")
                        elif nouvel_identifiant.lower() in data_totale["comptes"]:
                            st.error("Cet identifiant existe déjà !")
                        elif ip_deja_utilisee(user_ip):
                            st.error("❌ Un compte a déjà été créé avec votre connexion internet.")
                        else:
                            sauvegarder_utilisateur(nouvel_identifiant, nouvel_email, nouveau_code, user_ip)
                            st.success("🎉 Compte créé ! Vous pouvez vous connecter.")

        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("ℹ️ En savoir plus sur Nairu (Informations)"):
            st.markdown("### 🚀 À propos de Nairu")
            st.write("Nous sommes deux Toulousains passionnés de tech, Leny et Eliott...")
            
            col_eliott, col_leny = st.columns(2)
            with col_eliott:
                st.markdown("**⭐ Eliott**")
                st.link_button("📸 Instagram d'Eliott", "https://instagram.com/eliott31tls", use_container_width=True)
            with col_leny:
                st.markdown("**⚡ Leny**")
                st.link_button("📸 Instagram de Leny", "https://www.instagram.com/hvk.leny/", use_container_width=True)
                st.link_button("📺 YouTube de Leny", "https://www.youtube.com/@Hvk_Falkon", use_container_width=True)

# ==============================================================================
# --- 4. INTERFACE UNE FOIS CONNECTÉ ---
# ==============================================================================
else:
    # 🔴 PANNEAU DE CONTRÔLE ADMIN POUR LENY & ELIOTT
    if st.session_state.user_connecte in ["admin1", "leny", "eliott"]:
        with st.sidebar:
            st.markdown("### 🛠️ Mode Administrateur")
            st.info(f"Connecté en tant que : {st.session_state.user_connecte}")
            
            if st.checkbox("Voir la gestion des comptes"):
                data_totale = charger_utilisateurs()
                st.markdown("#### 👥 Modération des comptes")
                
                for nom, infos in list(data_totale["comptes"].items()):
                    if nom not in ["admin1", "leny", "eliott", "exemple"]:
                        st.markdown(f"**Identifiant :** `{nom}`")
                        st.caption(f"IP : {infos.get('ip', '0.0.0.0')} | Email : {infos.get('email', 'N/A')}")
                        
                        col_btn_ban, col_btn_del = st.columns(2)
                        
                        with col_btn_ban:
                            if st.button(f"🚫 Bannir", key=f"ban_{nom}", use_container_width=True):
                                user_ip_to_ban = infos.get('ip')
                                if user_ip_to_ban and user_ip_to_ban not in data_totale["banned_ips"]:
                                    data_totale["banned_ips"].append(user_ip_to_ban)
                                del data_totale["comptes"][nom]
                                sauvegarder_donnees(data_totale)
                                st.success(f"Banni !")
                                st.rerun()
                                
                        with col_btn_del:
                            if st.button(f"🗑️ Supprimer", key=f"del_{nom}", use_container_width=True):
                                del data_totale["comptes"][nom]
                                sauvegarder_donnees(data_totale)
                                st.success(f"Supprimé !")
                                st.rerun()
                        st.markdown("---")
                
                st.markdown("#### 🛑 IP Bloquées")
                if not data_totale.get("banned_ips"):
                    st.write("*Aucune IP bloquée.*")
                else:
                    for ip in data_totale["banned_ips"]:
                        col_ip_text, col_ip_unban = st.columns([2, 1])
                        with col_ip_text:
                            st.code(ip)
                        with col_ip_unban:
                            if st.button("🔓", key=f"unban_{ip}", use_container_width=True):
                                data_totale["banned_ips"].remove(ip)
                                sauvegarder_donnees(data_totale)
                                st.success("Débloquée")
                                st.rerun()

    # 🟢 CHAT IA POUR TOUT LE MONDE
    st.markdown(f"### 🤖 Nairu IA — Session de **{st.session_state.user_connecte}**")
    
    for msg in st.session_state.messages_chat:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    prompt_utilisateur = st.chat_input("Posez votre question à Nairu...")
    
    if prompt_utilisateur:
        with st.chat_message("user"):
            st.write(prompt_utilisateur)
        st.session_state.messages_chat.append({"role": "user", "content": prompt_utilisateur})
        
        try:
            client_groq = Groq(api_key=st.secrets["GROQ_API_KEY"])
            with st.chat_message("assistant"):
                with st.spinner("Nairu fouille le web et réfléchit..."):
                    contexte_web = executer_recherche_web(prompt_utilisateur)
                    system_instruction = f"Tu es Nairu, une IA de recherche créée par Leny et Eliott. Utilise ces infos web si besoin : {contexte_web}"
                    
                    historique_complet = [{"role": "system", "content": system_instruction}] + st.session_state.messages_chat
                    reponse_brute = client_groq.chat.completions.create(model="llama3-8b-8192", messages=historique_complet)
                    texte_reponse = reponse_brute.choices[0].message.content
                    st.write(texte_reponse)
            st.session_state.messages_chat.append({"role": "assistant", "content": texte_reponse})
        except:
            st.error("❌ Erreur de clé API Groq.")

    st.markdown("<br><hr>", unsafe_allow_html=True)
    if st.button("🔴 Déconnexion", use_container_width=True):
        st.session_state.statut_connexion = "Déconnecté"
        st.session_state.user_connecte = None
        st.session_state.messages_chat = []
        st.rerun()
        
