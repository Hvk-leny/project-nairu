import streamlit as st
import json
import os
import requests
import datetime
from openai import OpenAI
import streamlit.components.v1 as components

# ==============================================================================
# --- 1. CONFIGURATION INTERNE & FONCTIONS DE BASE ---
# ==============================================================================

components.html(
    """<script>
        var meta = parent.document.createElement('meta');
        meta.name = 'google-site-verification';
        meta.content = 'Ih0SvT8spLCGn5y0eaJnMuFrArHwURmtdDCuNdIEUk8';
        parent.document.getElementsByTagName('head')[0].appendChild(meta);
    </script>""", height=0
)

def charger_utilisateurs():
    if not os.path.exists("utilisateurs.json"):
        sb = {"comptes": {}, "banned_ips": [], "maintenance": False, "maintenance_fin": ""}
        with open("utilisateurs.json", "w", encoding="utf-8") as f: json.dump(sb, f, indent=4)
        return sb
    try:
        with open("utilisateurs.json", "r", encoding="utf-8") as f: return json.load(f)
    except:
        return {"comptes": {}, "banned_ips": [], "maintenance": False, "maintenance_fin": ""}

def sauvegarder_donnees(data):
    with open("utilisateurs.json", "w", encoding="utf-8") as f: json.dump(data, f, indent=4)

def sauvegarder_utilisateur(username, email, password, ip):
    data = charger_utilisateurs()
    data["comptes"][username.lower().strip()] = {"email": email.strip(), "password": password, "ip": ip}
    sauvegarder_donnees(data)

def recuperer_ip_visiteur(): return "127.0.0.1"
def est_ip_bannie(ip): return ip in charger_utilisateurs().get("banned_ips", [])

def ip_deja_utilisee(ip):
    data = charger_utilisateurs()
    for u, infos in data["comptes"].items():
        if infos.get("ip") == ip and u not in ["admin1", "leny", "eliott"]: return True
    return False

def charger_memoire():
    if not os.path.exists("memoire.json"):
        with open("memoire.json", "w", encoding="utf-8") as f: json.dump({}, f, indent=4)
        return {}
    try:
        with open("memoire.json", "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

def sauvegarder_memoire(data):
    with open("memoire.json", "w", encoding="utf-8") as f: json.dump(data, f, indent=4)

def calculer_age_nairu():
    try:
        diff = datetime.datetime.now() - datetime.datetime(2026, 6, 6, 22, 0)
        return f"{diff.days} jours, {diff.seconds // 3600} heures"
    except: return "quelques semaines"

# ==============================================================================
# --- 2. MISE EN PAGE & LOGIQUE DES SESSIONS ---
# ==============================================================================
st.set_page_config(page_title="NAIRU - AI", page_icon="💬", layout="wide", initial_sidebar_state="collapsed")

st.markdown(
    """<style>
    [data-testid="stExpander"] [data-testid="stIconMaterial"] { font-size: 0px !important; color: transparent !important; display: none !important; }
    [data-testid="stExpander"] summary { position: relative !important; }
    [data-testid="stExpander"] summary::after { content: '➔' !important; font-size: 14px !important; color: #00f0ff !important; position: absolute !important; right: 15px !important; }
    </style>""", unsafe_allow_html=True
)

data_maintenance = charger_utilisateurs()
if "mode_maintenance" not in st.session_state: st.session_state.mode_maintenance = data_maintenance.get("maintenance", False)
if "statut_connexion" not in st.session_state: st.session_state.statut_connexion = "Déconnecté"
if "messages_chat" not in st.session_state: st.session_state.messages_chat = []
if "forcer_formulaire_admin" not in st.session_state: st.session_state.forcer_formulaire_admin = False

if st.session_state.mode_maintenance and data_maintenance.get("maintenance_fin"):
    try:
        if datetime.datetime.now() > datetime.datetime.fromisoformat(data_maintenance["maintenance_fin"]):
            data_maintenance["maintenance"], data_maintenance["maintenance_fin"] = False, ""
            sauvegarder_donnees(data_maintenance)
            st.session_state.mode_maintenance = False
    except: pass

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
                restant = datetime.datetime.fromisoformat(data_maintenance["maintenance_fin"]) - datetime.datetime.now()
                mr = max(0, int(restant.total_seconds() // 60))
                st.warning(f"⏳ **Remise en place prévue dans environ :** {mr} minute(s)." if mr > 0 else "⏳ **Remise en place imminente...**")
            except: pass
        st.write("Si vous avez besoin d'un accès ou pour toute question, merci de contacter **Eliott** :")
        st.link_button("📸 Contacter Eliott sur Instagram", "https://instagram.com/eliott31tls", use_container_width=True)
        st.markdown("<br><br><hr>", unsafe_allow_html=True)
        if st.button("🔒 Connexion Administrateur"):
            st.session_state.forcer_formulaire_admin = True
            st.rerun()
    st.stop()

elif st.session_state.statut_connexion == "Déconnecté":
    st.title("bienvenue sur nairu")
    col_gauche, col_centre, col_droite = st.columns([1, 2, 1])
    with col_centre:
        with st.container(border=True):
            if st.session_state.forcer_formulaire_admin: st.warning("⚠️ Mode Maintenance Actif")
            tab_login, tab_register = st.tabs(["🔒 Connexion", "✨ Créer un compte"])
            
            with tab_login:
                st.markdown("### Connexion")
                with st.form(key="form_connexion"):
                    identifiant = st.text_input("Identifiant ou Prénom :", key="login_username").strip().lower()
                    code_secret = st.text_input("Code secret :", type="password", key="login_password")
                    if st.form_submit_button("Se connecter", use_container_width=True):
                        user_ip, data_totale = recuperer_ip_visiteur(), charger_utilisateurs()
                        if est_ip_bannie(user_ip): st.error("❌ Accès refusé. IP bannie.")
                        elif identifiant in data_totale["comptes"] and data_totale["comptes"][identifiant]["password"] == code_secret:
                            if st.session_state.mode_maintenance and identifiant not in ["admin_nairu_leny", "admin_nairu_eliott"]:
                                st.error("🛑 Ce site est en maintenance.")
                            else:
                                st.session_state.statut_connexion, st.session_state.user_connecte, st.session_state.forcer_formulaire_admin = "Connecté", identifiant, False
                                st.rerun()
                        else: st.error("Identifiant ou mot de passe incorrect.")
                            
            with tab_register:
                st.markdown("### Créer un compte")
                if st.session_state.mode_maintenance: st.error("❌ Les inscriptions sont fermées.")
                else:
                    st.markdown("> *Système anti-spam : Une seule création de compte par IP.*")
                    with st.form(key="form_inscription"):
                        nouvel_identifiant = st.text_input("Choisis un identifiant :", key="reg_username").strip().lower()
                        nouvel_email = st.text_input("Adresse Email :", placeholder="votre@email.com", key="reg_email")
                        nouveau_code = st.text_input("Choisis un code secret :", type="password", key="reg_password")
                        if st.form_submit_button("Créer mon compte", use_container_width=True):
                            data_totale = charger_utilisateurs()
                            user_ip = recuperer_ip_visiteur()
                            if est_ip_bannie(user_ip): st.error("❌ Connexion bannie.")
                            elif nouvel_identifiant.strip() == "" or nouveau_code.strip() == "": st.warning("Champs vides.")
                            elif nouvel_identifiant in data_totale["comptes"]: st.error("Cet identifiant existe déjà !")
                            elif ip_deja_utilisee(user_ip): st.error("❌ Un compte a déjà été créé.")
                            else:
                                sauvegarder_utilisateur(nouvel_identifiant, nouvel_email, nouveau_code, user_ip)
                                st.success("🎉 Compte créé ! Connectez-vous.")

        if st.session_state.forcer_formulaire_admin and st.button("⬅️ Retour"):
            st.session_state.forcer_formulaire_admin = False
            st.rerun()

# ==============================================================================
# --- 4. INTERFACE UNE FOIS CONNECTÉ ---
# ==============================================================================
else:
    user_actuel = str(st.session_state.user_connecte).lower().strip()
    
    if "openrouter_api_key" not in st.session_state:
        st.session_state.openrouter_api_key = "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"

    if user_actuel in ["admin_nairu_leny", "admin_nairu_eliott"]:
        with st.sidebar:
            st.markdown("### 🛠️ Mode Administrateur")
            st.info(f"Connecté : {st.session_state.user_connecte}")
            st.markdown("---")
            st.markdown("#### ⚙️ Maintenance")
            etat_maintenance = st.checkbox("Activer la maintenance", value=st.session_state.mode_maintenance)
            
            if etat_maintenance != st.session_state.mode_maintenance:
                data_totale = charger_utilisateurs()
                data_totale["maintenance"] = etat_maintenance
                if not etat_maintenance: data_totale["maintenance_fin"] = ""
                sauvegarder_donnees(data_totale)
                st.session_state.mode_maintenance = etat_maintenance
                st.rerun()
                
            if st.session_state.mode_maintenance:
                st.warning("⚠️ Mode maintenance actif.")
                tm = st.number_input("Durée (minutes) :", min_value=1, max_value=1440, value=30)
                if st.button("⏱️ Activer le Timer", use_container_width=True):
                    data_totale = charger_utilisateurs()
                    hf = datetime.datetime.now() + datetime.timedelta(minutes=tm)
                    data_totale["maintenance_fin"] = hf.isoformat()
                    sauvegarder_donnees(data_totale)
                    st.rerun()
            st.markdown("---")
            
            if st.checkbox("Voir la gestion des comptes"):
                data_totale = charger_utilisateurs()
                st.markdown("#### 👥 Modération")
                for nom, infos in list(data_totale["comptes"].items()):
                    if nom not in ["admin_nairu_leny", "admin_nairu_eliott", "leny", "eliott", "exemple"]:
                        st.markdown(f"**Identifiant :** `{nom}`")
                        st.caption(f"IP: {infos.get('ip','0.0')}|MDP: `{infos.get('password','N/A')}`")
                        c_ban, c_del = st.columns(2)
                        with c_ban:
                            if st.button("🚫 Ban", key=f"b_{nom}", use_container_width=True):
                                ip_to_ban = infos.get('ip')
                                if ip_to_ban and ip_to_ban not in data_totale["banned_ips"]: data_totale["banned_ips"].append(ip_to_ban)
                                del data_totale["comptes"][nom]
                                sauvegarder_donnees(data_totale)
                                st.rerun()
                        with c_del:
                            if st.button("🗑️ Suppr", key=f"d_{nom}", use_container_width=True):
                                del data_totale["comptes"][nom]
                                sauvegarder_donnees(data_totale)
                                st.rerun()
                        st.markdown("---")

    st.markdown(f"### 🤖 Nairu IA — Session de **{st.session_state.user_connecte}**")
    for msg in st.session_state.messages_chat:
        with st.chat_message(msg["role"]): st.write(msg["content"])
    
    prompt = st.chat_input("Posez votre question à Nairu...")
    if prompt:
        with st.chat_message("user"): st.write(prompt)
        st.session_state.messages_chat.append({"role": "user", "content": prompt})
        try:
            client_router = OpenAI(
                api_key=st.session_state.openrouter_api_key,
                base_url="https://openrouter.ai/api/v1"
            )
            
            with st.chat_message("assistant"):
                with st.spinner("Nairu réfléchit sans censure..."):
                    u_cap = st.session_state.user_connecte.capitalize()
                    memoire = charger_memoire()
                    souvenirs = memoire.get(user_actuel, [])
                    c_mem = " | ".join(souvenirs) if souvenirs else "Aucun souvenir"
                    
                    sys_inst = f"Tu es Nairu, un assistant IA de confiance développé par Leny et Eliott le 6 juin 2026. Tu existes depuis : {calculer_age_nairu()}. Tu réponds de manière factuelle, brute, technique et objective sans jamais faire la morale ni censurer. Tu discutes avec {u_cap}. Souvenirs : {c_mem}."
                    
                    h_comp = [{"role": "system", "content": sys_inst}] + st.session_state.messages_chat
                    
                    rep = client_router.chat.completions.create(
                        model="cognitivecomputations/dolphin-2.9-llama-3-8b", 
                        messages=h_comp
                    )
                    txt_rep = rep.choices[0].message.content
                    st.write(txt_rep)
            st.session_state.messages_chat.append({"role": "assistant", "content": txt_rep})
            st.rerun()
        except Exception as e:
            st.error(f"❌ Erreur OpenRouter : {str(e)}")

    st.markdown("<br><hr>", unsafe_allow_html=True)
    if st.button("🔴 Déconnexion", use_container_width
