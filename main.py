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
            resultats = [r for r in ddgs.text(requete, max_results=4)]
            if not resultats:
                return "Aucun résultat trouvé sur le web pour cette recherche."
            
            contexte = ""
            for i, res in enumerate(resultats, 1):
                contexte += f"[{i}] Source : {res['title']}\nLien : {res['href']}\nInfos : {res['body']}\n---\n"
            return contexte
    except Exception as e:
        return f"Erreur lors de la recherche web : {str(e)}"

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
    /* 🔥 CORRECTION : On cache l'icône UNIQUEMENT dans l'expander pour libérer la Sidebar */
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

# Chargement de l'état de la maintenance depuis la bdd
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
        import datetime
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
# Si le site est en maintenance, que personne n'est connecté, et qu'on ne force pas l'accès admin
if st.session_state.mode_maintenance and st.session_state.statut_connexion == "Déconnecté" and not st.session_state.forcer_formulaire_admin:
    col_gauche, col_centre, col_droite = st.columns([1, 2, 1])
    with col_centre:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.error("### 🛠️ Site temporairement indisponible")
        st.info("Nairu AI est actuellement en cours de maintenance ou de mise à jour.")
        
        # Calcul et affichage du timer restant
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
        # Bouton secret pour ouvrir le formulaire de connexion
        if st.button("🔒 Connexion Administrateur", use_container_width=False):
            st.session_state.forcer_formulaire_admin = True
            st.rerun()
            
    st.stop() # On bloque l'affichage de l'accueil pour les autres

# Interface classique (visible si pas de maintenance, ou si l'admin force l'entrée)
elif st.session_state.statut_connexion == "Déconnecté":
    st.title("bienvenue sur nairu")
    col_gauche, col_centre, col_droite = st.columns([1, 2, 1])
    
    with col_centre:
        with st.container(border=True):
            if st.session_state.forcer_formulaire_admin:
                st.warning("⚠️ Mode Maintenance Actif - Accès réservé à l'Administrateur")
            
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
                            
                            # SÉCURITÉ : Si maintenance active, seul admin1 passe
                            if st.session_state.mode_maintenance and identifiant != "admin1":
                                st.error("🛑 Ce site est en maintenance. Seul le compte admin1 peut se connecter.")
                            else:
                                st.session_state.statut_connexion = "Connecté"
                                st.session_state.user_connecte = identifiant
                                st.session_state.forcer_formulaire_admin = False
                                st.success(f"Bienvenue {identifiant} !")
                                st.rerun()
                        else:
                            st.error("Identifiant ou mot de passe incorrect.")
                            
            with tab_register:
                st.markdown("### Créer un compte")
                if st.session_state.mode_maintenance:
                    st.error("❌ Les inscriptions sont fermées pendant la maintenance du site.")
                else:
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
                            elif nouvel_identifiant.lower().strip() in data_totale["comptes"]:
                                relative_error = st.error("Cet identifiant existe déjà !")
                            elif ip_deja_utilisee(user_ip):
                                st.error("❌ Un compte a déjà été créé avec votre connexion internet.")
                            else:
                                sauvegarder_utilisateur(nouvel_identifiant, nouvel_email, nouveau_code, user_ip)
                                st.success("🎉 Compte créé ! Vous pouvez vous connecter.")

        if st.session_state.forcer_formulaire_admin:
            if st.button("⬅️ Retour à la page de maintenance"):
                st.session_state.forcer_formulaire_admin = False
                st.rerun()

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
    user_actuel = str(st.session_state.user_connecte).lower().strip()
    
    # 🔴 SEUL LE COMPTE ADMIN1 A ACCÈS AU PANNEAU DE CONTRÔLE SÉCURITÉ & MAINTENANCE
    if user_actuel == "admin1":
        with st.sidebar:
            st.markdown("### 🛠️ Mode Administrateur")
            st.info(f"Connecté en tant que : {st.session_state.user_connecte}")
            
            # --- ⚙️ GESTION DE LA MAINTENANCE ---
            st.markdown("---")
            st.markdown("#### ⚙️ Gestion de la Maintenance")
            
            # Case à cocher pour activer/désactiver instantanément
            etat_maintenance = st.checkbox("Activer le mode maintenance", value=st.session_state.mode_maintenance)
            
            if etat_maintenance != st.session_state.mode_maintenance:
                data_totale = charger_utilisateurs()
                data_totale["maintenance"] = etat_maintenance
                if not etat_maintenance:
                    data_totale["maintenance_fin"] = "" # Reset du temps si on décoche
                sauvegarder_donnees(data_totale)
                st.session_state.mode_maintenance = etat_maintenance
                st.rerun()
                
            # Configuration du Timer si la maintenance est active
            if st.session_state.mode_maintenance:
                st.warning("⚠️ Le site est invisible pour les utilisateurs.")
                temps_minutes = st.number_input("Durée de la maintenance (en minutes) :", min_value=1, max_value=1440, value=30)
                if st.button("⏱️ Lancer / Mettre à jour le Timer", use_container_width=True):
                    data_totale = charger_utilisateurs()
                    heure_fin = datetime.datetime.now() + datetime.timedelta(minutes=temps_minutes)
                    data_totale["maintenance_fin"] = heure_fin.isoformat()
                    sauvegarder_donnees(data_totale)
                    st.success(f"Timer activé jusqu'à {heure_fin.strftime('%H:%M:%S')} !")
                    st.rerun()
            st.markdown("---")
            
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
    if st.session_state.mode_maintenance:
        st.sidebar.warning("⚠️ ATTENTION : Mode maintenance actif.")

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
                with st.spinner("Nairu fouille le web en direct et réfléchit..."):
                    
                    contexte_web = executer_recherche_web(prompt_utilisateur)
                    nom_utilisateur = st.session_state.user_connecte.capitalize()
                    
                    system_instruction = (
                        "Tu es Nairu, un assistant de recherche IA ultra-performant et connecté au web en temps réel, développé par Leny et Eliott.\n"
                        f"Tu es actuellement en train de discuter avec l'utilisateur connecté qui s'appelle : {nom_utilisateur}.\n"
                        f"Sache et retiens bien qu'il s'appelle {nom_utilisateur}. Tu dois t'en souvenir s'il te demande 'comment je m'appelle ?'.\n"
                        "Si l'utilisateur est Leny ou Eliott, agis avec eux de manière encore plus complice puisqu'ils sont tes créateurs.\n\n"
                        "Pour répondre à la question actuelle, sers-toi des résultats de recherche internet suivants :\n"
                        f"{contexte_web}\n\n"
                        "Règles importantes :\n"
                        "- Synthétise les informations trouvées de manière claire, concise et intelligente.\n"
                        "- Reste amical, moderne, naturel et efficace."
                    )
                    
                    historique_complet = [{"role": "system", "content": system_instruction}] + st.session_state.messages_chat
                    
                    reponse_brute = client_groq.chat.completions.create(
                        model="llama-3.3-70b-versatile", 
                        messages=historique_complet
                    )
                    texte_reponse = reponse_brute.choices[0].message.content
                    st.write(texte_reponse)
            
            st.session_state.messages_chat.append({"role": "assistant", "content": texte_reponse})
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Erreur Groq : {str(e)}")

    st.markdown("<br><hr>", unsafe_allow_html=True)
    if st.button("🔴 Déconnexion", use_container_width=True):
        st.session_state.statut_connexion = "Déconnecté"
        st.session_state.user_connecte = None
        st.session_state.messages_chat = []
        st.rerun()

# ==============================================================================
# --- 4.5 EXTENSION : SYSTÈME DE MÉMOIRE LONG TERME (STYLE CHATGPT) ---
# ==============================================================================
MEMOIRE_FILE = "memoire.json"

def charger_memoire():
    if not os.path.exists(MEMOIRE_FILE):
        with open(MEMOIRE_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4)
        return {}
    try:
        with open(MEMOIRE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def sauvegarder_memoire(data):
    with open(MEMOIRE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# Exécution de la logique de mémoire si l'utilisateur est connecté
if st.session_state.statut_connexion == "Connecté":
    user_actuel = st.session_state.user_connecte
    memoire_globale = charger_memoire()
    
    # Initialiser la mémoire de l'utilisateur si elle n'existe pas
    if user_actuel not in memoire_globale:
        memoire_globale[user_actuel] = []
        sauvegarder_memoire(memoire_globale)
        
    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.markdown("### 🧠 Mémoire à long terme de Nairu")
    
    # Interface de contrôle de la mémoire (style ChatGPT)
    col_mem_info, col_mem_action = st.columns([2, 1])
    
    with col_mem_info:
        st.write("Voici ce que Nairu a gardé en mémoire à votre sujet pour personnaliser vos futures discussions :")
        if not memoire_globale[user_actuel]:
            st.info("💡 Nairu n'a encore rien enregistré. Écrivez un souvenir ci-contre pour commencer !")
        else:
            for i, souvenir in enumerate(memoire_globale[user_actuel]):
                col_txt, col_del = st.columns([5, 1])
                with col_txt:
                    st.markdown(f"• {souvenir}")
                with col_del:
                    if st.button("🗑️", key=f"del_mem_{user_actuel}_{i}"):
                        memoire_globale[user_actuel].pop(i)
                        sauvegarder_memoire(memoire_globale)
                        st.success("Souvenir oublié !")
                        st.rerun()
                        
    with col_mem_action:
        with st.form(key=f"form_ajout_memoire_{user_actuel}", clear_on_submit=True):
            nouveau_souvenir = st.text_input("Ajouter un fait à retenir :", placeholder="Ex: Je m'appelle Falkon / J'aime Fortnite")
            bouton_mem = st.form_submit_button("Enregistrer le souvenir", use_container_width=True)
            
            if bouton_mem and nouveau_souvenir.strip() != "":
                memoire_globale[user_actuel].append(nouveau_souvenir.strip())
                sauvegarder_memoire(memoire_globale)
                st.success("Souvenir enregistré !")
                st.rerun()

    # --- INJECTION AUTOMATIQUE DE LA MÉMOIRE DANS GROQ ---
    # On récupère la liste des souvenirs pour l'intégrer au prompt système de manière invisible
    souvenirs_utilisateur = memoire_globale.get(user_actuel, [])
    contexte_memoire_systeme = ""
    if souvenirs_utilisateur:
        contexte_memoire_systeme = "\n- Faits importants à retenir absolument sur cet utilisateur (sa mémoire) :\n" + "\n".join([f"  * {s}" for s in souvenirs_utilisateur])
    
    # Note pour faire le lien avec ton code :
    # Pour que Groq lise ces souvenirs, il te suffira d'ajouter `{contexte_memoire_systeme}` 
    # à l'intérieur de ta variable `system_instruction` dans la section 4 de ton code actuel.
# ==============================================================================
