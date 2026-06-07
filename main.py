import streamlit as st
import json
import os
from datetime import datetime
import g4f

st.set_page_config(page_title="NAIRU - AI", page_icon="🤖", layout="centered")

DB_FILE = "database.json"

def charger_base():
    if not os.path.exists(DB_FILE):
        structure_initiale = {
            "users": {
                "eliott": {"code": "code1", "history": []},
                "leny": {"code": "code2", "history": []}
            }
        }
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(structure_initiale, f, indent=4)
        return structure_initiale
    
    with open(DB_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return {"users": {"eliott": {"code": "code1", "history": []}, "leny": {"code": "code2", "history": []}}}

def sauvegarder_base(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

if "data" not in st.session_state:
    st.session_state.data = charger_base()
if "connecte" not in st.session_state:
    st.session_state.connecte = False
if "username" not in st.session_state:
    st.session_state.username = ""

# --- CONNEXION ---
if not st.session_state.connecte:
    st.title("🔑 Connexion à Nairu")
    prenom_input = st.text_input("Prénom :").strip().lower()
    code_input = st.text_input("Code secret :", type="password").strip()
    
    if st.button("Se connecter", use_container_width=True):
        if prenom_input in st.session_state.data["users"]:
            if code_input == st.session_state.data["users"][prenom_input]["code"]:
                st.session_state.connecte = True
                st.session_state.username = prenom_input
                st.rerun()
            else:
                st.error("Code secret incorrect.")
        else:
            st.error("Prénom non reconnu.")

# --- CHAT SITE WEB ---
else:
    prenom = st.session_state.username
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.subheader(f"👋 Créateur : {prenom.capitalize()}")
    with col2:
        if st.button("🔄 Reset Chat", use_container_width=True):
            st.session_state.data["users"][prenom]["history"] = []
            sauvegarder_base(st.session_state.data)
            st.rerun()
    with col3:
        if st.button("🚪 Déconnexion", use_container_width=True):
            st.session_state.connecte = False
            st.session_state.username = ""
            st.rerun()

    st.markdown("---")
    chat_container = st.container()
    
    with chat_container:
        with st.chat_message("assistant"):
            st.write(f"Bonjour {prenom.capitalize()} ! En quoi puis-je t'aider aujourd'hui ?")
        for msg in st.session_state.data["users"][prenom]["history"]:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    if prompt := st.chat_input("Écris ton message ici..."):
        with chat_container:
            with st.chat_message("user"):
                st.write(prompt)
        
        if prompt.lower() == "heure":
            reponse_ia = f"Il est actuellement {datetime.now().strftime('%H:%M')} à Toulouse."
        elif prompt.lower() == "utilisateur":
            st.session_state.connecte = False
            st.session_state.username = ""
            st.rerun()
        else:
            with chat_container:
                with st.chat_message("assistant"):
                    placeholder = st.empty()
                    placeholder.markdown("*Nairu réfléchit...*")
                    
                    messages_ia = [
                        {"role": "system", "content": "Tu t'appelles impérativement Nairu. Tu as été codée de A à Z par tes deux développeurs passionnés de la région toulousaine, Eliott et Leny. Tu es leur assistant personnel. Tu ne dois JAMAIS mentionner Opera, Aria, OpenAI ou une autre entreprise informatique. Si on te demande qui t'a créé, réponds fièrement que ce sont Eliott et Leny."}
                    ]
                    for h_msg in st.session_state.data["users"][prenom]["history"]:
                        messages_ia.append(h_msg)
                    messages_ia.append({"role": "user", "content": prompt})
                    
                    try:
                        response = g4f.ChatCompletion.create(model=g4f.models.default, messages=messages_ia)
                        if any(word in response.lower() for word in ["opera", "aria", "logiciel"]):
                            response = "Je m'appelle Nairu. J'ai été créé de A à Z par mes deux développeurs, Eliott et Leny !"
                        placeholder.write(response)
                        reponse_ia = response
                    except:
                        placeholder.write("⚠️ Erreur de connexion au serveur IA.")
                        reponse_ia = None

        if reponse_ia:
            st.session_state.data["users"][prenom]["history"].append({"role": "user", "content": prompt})
            st.session_state.data["users"][prenom]["history"].append({"role": "assistant", "content": reponse_ia})
            sauvegarder_base(st.session_state.data)
# --- CONFIGURATION GROQ ET RECHERCHE ---
from groq import Groq
from duckduckgo_search import DDGS

client = Groq(api_key="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")

st.sidebar.title("⚡ Configuration de Nairu")

# Sélection du Mode
option = st.sidebar.radio(
    "Choisis le mode de fonctionnement :",
    ("Option Flash ⚡", "Option Réflexion 💬", "Option Passionné / Intéressé 🔥")
)

# Case à cocher pour activer/désactiver le web
recherche_web = st.sidebar.toggle("🌐 Activer la recherche Internet (DuckDuckGo)", value=True)

# Curseur de créativité (Temperature)
creativite = st.sidebar.slider(
    "🧠 Niveau de créativité de l'IA :",
    min_value=0.0,
    max_value=1.0,
    value=0.5,
    step=0.1,
    help="Plus la valeur est haute, plus l'IA est originale et surprenante."
)

# Réglage du comportement selon l'option choisie
if option == "Option Flash ⚡":
    st.sidebar.info("Mode Flash : Réponses courtes et ultra rapides.")
    system_instruction = "Tu es Nairu. Réponds de manière ultra rapide, concise, claire et directe, va droit au but."
    model_name = "llama-3.1-8b-instant"

elif option == "Option Réflexion 💬":
    st.sidebar.info("Mode Réflexion : Analyse profonde et structurée.")
    system_instruction = "Tu es Nairu. Prends le temps de bien analyser les données du web fournies pour faire une synthèse complète, logique et technique."
    model_name = "llama-3.3-70b-versatile"

elif option == "Option Passionné / Intéressé 🔥":
    st.sidebar.info("Mode Passionné : Expert automobile absolu ! Réponds avec enthousiasme.")
    system_instruction = "Tu es Nairu, un expert automobile absolu. Réponds avec énormément d'enthousiasme et de passion. Utilise un ton de connaisseur et appuie-toi sur les infos récentes."
    model_name = "llama-3.1-8b-instant"

# --- FONCTION DE RECHERCHE DUCKDUCKGO ---
def chercher_web(requete):
    try:
        with DDGS() as ddgs:
            resultats = [r for r in ddgs.text(requete, max_results=3)]
            if resultats:
                contexte = "\n\n".join([f"Source: {r['title']}\nContenu: {r['body']}" for r in resultats])
                return contexte
    except Exception:
        return "Impossible de récupérer les données du web en temps réel."
    return "Aucun résultat trouvé sur le web."

# --- APPEL À L'IA ET AFFICHAGE EN BULLES ---
if 'prompt' in locals() and prompt:
    # Affichage du message de l'utilisateur dans une vraie bulle
    with st.chat_message("user"):
        st.write(prompt)

    # Si la recherche est activée, on va chercher sur DuckDuckGo
    contexte_web = ""
    if recherche_web:
        with st.spinner("🔍 Recherche sur DuckDuckGo en cours..."):
            contexte_web = chercher_web(prompt)

    try:
        # Préparation des messages pour l'IA
        messages_ia = [{"role": "system", "content": system_instruction}]
        
        # Si on a des infos du web, on les injecte pour donner le contexte récent
        if contexte_web:
            messages_ia.append({
                "role": "system", 
                "content": f"Voici les données actuelles trouvées sur Internet (nous sommes en 2026) pour t'aider à répondre avec précision :\n{contexte_web}"
            })
            
        messages_ia.append({"role": "user", "content": prompt})

        # Appel API Groq
        completion = client.chat.completions.create(
            model=model_name,
            messages=messages_ia,
            temperature=creativite,
        )
        response_text = completion.choices[0].message.content
        
        # Affichage de la réponse de Nairu dans sa bulle avec l'icône éclair
        with st.chat_message("assistant", avatar="⚡"):
            st.write(response_text)
            
    except Exception as e:
        st.error(f"Erreur Nairu (Groq) : {e}")

# --- AFFICHAGE DE L'HEURE DE FRANCE SOUS LA BARRE DE SAISIE ---
import datetime
from zoneinfo import ZoneInfo

# Récupération de l'heure avec le fuseau horaire de Paris/France
fuseau_france = ZoneInfo("Europe/Paris")
heure_actuelle = datetime.datetime.now(fuseau_france).strftime("%H:%M")

# Alignement à droite en petit texte sous la barre
st.markdown(
    f"""
    <div style="text-align: right; margin-top: 10px; color: gray; font-family: monospace; font-size: 12px;">
        🕒 {heure_actuelle}
    </div>
    """, 
    unsafe_allow_html=True
)

# ==============================================================================
# --- EXTENSION : SYSTÈME MULTI-CONVERSATIONS & HISTORIQUE (AJOUTÉ EN PLUS) ---
# ==============================================================================

# 1. INITIALISATION DE L'HISTORIQUE DANS LA BARRE LATÉRALE
if "conversations" not in st.session_state:
    st.session_state.conversations = {
        "Discussion 1": []
    }
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Discussion 1"

st.sidebar.write("---")
st.sidebar.subheader("💬 Vos Discussions")

# Bouton pour créer une nouvelle conversation
if st.sidebar.button("➕ Nouvelle conversation", use_container_width=True):
    nouvel_id = f"Discussion {len(st.session_state.conversations) + 1}"
    st.session_state.conversations[nouvel_id] = []
    st.session_state.current_chat = nouvel_id
    st.rerun()

# Liste des conversations pour basculer de l'une à l'autre
chat_options = list(st.session_state.conversations.keys())
choix_chat = st.sidebar.selectbox(
    "Ouvrir une discussion :", 
    chat_options, 
    index=chat_options.index(st.session_state.current_chat)
)

# Si l'on change de discussion
if choix_chat != st.session_state.current_chat:
    st.session_state.current_chat = choix_chat
    st.rerun()

# 2. SAUVEGARDE DU MESSAGE ACTUEL DANS L'HISTORIQUE
if 'prompt' in locals() and prompt:
    # On vérifie si ce message n'est pas déjà le dernier enregistré pour éviter les doublons
    historique_actuel = st.session_state.conversations[st.session_state.current_chat]
    if not historique_actuel or historique_actuel[-1]["content"] != prompt:
        st.session_state.conversations[st.session_state.current_chat].append({"role": "user", "content": prompt})
        
        # Si Nairu a généré une réponse juste au-dessus, on la capture et on l'enregistre aussi
        if 'response_text' in locals():
            st.session_state.conversations[st.session_state.current_chat].append({"role": "assistant", "content": response_text})

# 3. REDESSINER L'HISTORIQUE PROPREMENT À L'ÉCRAN
st.write("---")
st.write(f"📝 *Historique de la session active : {st.session_state.current_chat}*")
for msg in st.session_state.conversations[st.session_state.current_chat]:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.write(msg["content"])
    else:
        with st.chat_message("assistant", avatar="⚡"):
            st.write(msg["content"])

# --- AFFICHAGE DE L'HEURE DE FRANCE SOUS LA BARRE DE SAISIE ---
import datetime
from zoneinfo import ZoneInfo

fuseau_france = ZoneInfo("Europe/Paris")
heure_actuelle = datetime.datetime.now(fuseau_france).strftime("%H:%M")

st.markdown(
    f"""
    <div style="text-align: right; margin-top: 20px; color: gray; font-family: monospace; font-size: 12px;">
        🕒 {heure_actuelle}
    </div>
    """, 
    unsafe_allow_html=True
)

# ==============================================================================
# --- EXTENSION : DESIGN JARVIS NÉON (CYAN GLOW & HUD FUTURISTE) ---
# ==============================================================================

st.markdown(
    """
    <style>
    /* 1. Fond d'écran Jarvis : Noir profond avec une grille numérique subtile */
    .stApp {
        background: radial-gradient(circle at center, #00111c 0%, #000814 100%) !important;
        background-attachment: fixed;
    }

    /* 2. Effet Néon Cyan sur les bulles de l'assistant Nairu / Jarvis */
    .stChatMessage {
        background-color: rgba(0, 8, 20, 0.6) !important;
        border: 1px solid #00f0ff !important;
        border-radius: 4px !important; /* Forme plus carrée et informatique */
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.2), inset 0 0 10px rgba(0, 240, 255, 0.1) !important;
        padding: 15px !important;
        margin-bottom: 15px !important;
        font-family: 'Courier New', Courier, monospace !important;
    }

    /* Bulle de l'utilisateur avec un Néon Orange/Gold de l'armure d'Iron Man */
    .stChatMessage[data-testid="stChatMessageUser"] {
        background-color: rgba(20, 10, 0, 0.5) !important;
        border: 1px solid #ffaa00 !important;
        box-shadow: 0 0 15px rgba(255, 170, 0, 0.2), inset 0 0 10px rgba(255, 170, 0, 0.1) !important;
    }

    /* 3. Barre latérale style "HUD Tactique" */
    [data-testid="stSidebar"] {
        background-color: rgba(0, 10, 18, 0.85) !important;
        border-right: 2px solid #00f0ff !important;
        box-shadow: 5px 0 15px rgba(0, 240, 255, 0.1) !important;
    }

    /* 4. Boutons futuristes avec effet de chargement holographique */
    .stButton>button {
        background: transparent !important;
        color: #00f0ff !important;
        border: 1px solid #00f0ff !important;
        border-radius: 2px !important;
        font-family: 'Courier New', Courier, monospace !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        transition: all 0.3s ease !important;
    }

    .stButton>button:hover {
        background: rgba(0, 240, 255, 0.15) !important;
        box-shadow: 0 0 20px #00f0ff, inset 0 0 10px #00f0ff !important;
        color: #ffffff !important;
    }

    /* 5. Curseurs (Sliders) et éléments actifs qui brillent */
    div[data-testid="stSlider"] [data-testid="stThumb"] {
        background-color: #00f0ff !important;
        box-shadow: 0 0 15px #00f0ff !important;
        border-radius: 0px !important;
    }
    
    div[data-testid="stSlider"] [data-testid="stTrack"] {
        background-color: rgba(0, 240, 255, 0.2) !important;
    }

    /* 6. Police d'écriture style Terminal Informatique */
    h1, h2, h3, p, span, label, li {
        font-family: 'Courier New', Courier, monospace !important;
        color: #a0e0ff !important;
        text-shadow: 0 0 2px rgba(0, 240, 255, 0.5) !important;
    }

    /* Titres qui clignotent ou brillent en Cyan Néon */
    h1, h2, h3 {
        color: #00f0ff !important;
        letter-spacing: 1px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Petit message d'initialisation façon I.A de Stark
if 'jarvis_boot' not in st.session_state:
    st.toast("Système Nairu (Protocol Jarvis) : En ligne. Systèmes opérationnels à 100%.", icon="🤖")
    st.session_state.jarvis_boot = True

# ==============================================================================
# --- CORRECTION : BOUTON INVITÉ SUR LA PAGE D'ACCUEIL "BIENVENUE SUR NAIRU" ---
# ==============================================================================

# Si l'utilisateur n'est pas connecté, on affiche le bouton au centre de la page
if "statut_connexion" not in st.session_state:
    st.session_state.statut_connexion = "Déconnecté"

if st.session_state.statut_connexion == "Déconnecté":
    # On crée un espace sous ton message "Bienvenue sur Nairu"
    st.write("")
    
    # Bouton de connexion invité centré sur la page principale
    if st.button("🎭 Se connecter en tant qu'invité", use_container_width=True):
        st.session_state.statut_connexion = "Invité"
        st.rerun()

# Si le mode invité est activé, on affiche les deux options (Insta et Présentation)
if st.session_state.statut_connexion == "Invité":
    st.write("---")
    
    st.markdown(
        """
        <div style="background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 18px; border: 1px solid rgba(0, 180, 216, 0.2); text-align: center; margin-bottom: 25px;">
            <h3 style="color: #00b4d8; margin-top: 0; margin-bottom: 5px;">✨ Bienvenue sur Nairu AI</h3>
            <p style="color: gray; font-size: 14px; margin: 0;">Mode Invité • Accès Découverte</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Les deux options : DM Insta et Présentation
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(
            """
            <div style="background: rgba(255, 255, 255, 0.03); padding: 20px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.05); text-align: center; height: 100%;">
                <p style="font-size: 30px; margin: 0;">📩</p>
                <h4 style="margin: 10px 0 5px 0; color: #ffffff;">Nous contacter</h4>
                <p style="font-size: 13px; color: #a0a0a0; margin-bottom: 20px;">Tu as une question, une idée, ou tu veux ton propre compte d'accès ? Envoie un DM !</p>
                <a href="https://www.instagram.com/eliott31tls" target="_blank" style="text-decoration: none;">
                    <button style="background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%); color: white; border: none; padding: 10px 20px; border-radius: 10px; font-weight: bold; cursor: pointer; width: 100%; box-shadow: 0 4px 15px rgba(230, 104, 60, 0.3);">
                        DM sur @eliott31tls
                    </button>
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col2:
        st.markdown(
            """
            <div style="background: rgba(255, 255, 255, 0.03); padding: 20px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.05); height: 100%;">
                <p style="font-size: 30px; margin: 0; text-align: center;">🤖</p>
                <h4 style="margin: 10px 0 10px 0; color: #ffffff; text-align: center;">Présentation de l'IA</h4>
                <p style="font-size: 13px; color: #e0e1dd; margin-bottom: 5px;"><b>Nairu</b> est un assistant virtuel intelligent conçu pour être performant, fluide et stylé.</p>
                <ul style="font-size: 12px; color: #a0a0a0; padding-left: 15px; margin: 0;">
                    <li>⚡ <b>Moteur Groq :</b> Réponses instantanées.</li>
                    <li>🌐 <b>Recherche Web :</b> Connecté à Internet.</li>
                    <li>🔥 <b>Mode Passionné :</b> Expert en mécanique et automobile.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Bouton pour revenir à la page de bienvenue de départ
    st.write("")
    if st.button("⬅️ Retour à la page d'accueil", use_container_width=True):
        st.session_state.statut_connexion = "Déconnecté"
        st.rerun()

# ==============================================================================
# --- EXTENSION : THÈME ROLEX LUXURY (VERT IMPÉRIAL, OR & SIDEBAR GLISSANTE) ---
# ==============================================================================

st.markdown(
    """
    <style>
    /* 1. Fond d'écran : Le vert profond texturé signature de Rolex */
    .stApp {
        background-color: #002b19 !important;
        background-image: radial-gradient(circle at center, #004d2e 0%, #001f12 100%) !important;
        background-attachment: fixed !important;
    }

    /* 2. Barre de recherche flottante : Noir mat, liseré Or et ombre douce */
    div[data-testid="stChatInput"] {
        border-radius: 4px !important; /* Forme plus rectiligne et horlogère */
        border: 1px solid #A37E2C !important;
        background-color: #111111 !important;
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.6) !important;
        transition: transform 0.3s ease, box-shadow 0.3s ease !important;
    }
    
    div[data-testid="stChatInput"] textarea {
        color: #ffffff !important;
    }

    /* 3. Barre latérale magique : Version feutrée Or et Sombre */
    [data-testid="stSidebar"] {
        position: fixed !important;
        left: -290px !important;
        top: 0 !important;
        bottom: 0 !important;
        width: 320px !important;
        background-color: rgba(17, 17, 17, 0.95) !important;
        backdrop-filter: blur(15px) !important;
        -webkit-backdrop-filter: blur(15px) !important;
        border-right: 2px solid #A37E2C !important;
        transition: left 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
        z-index: 999991 !important;
        padding-left: 20px !important;
    }

    /* Détecteur de survol pour la souris sur le bord gauche */
    [data-testid="stSidebar"]::before {
        content: "" !important;
        position: absolute !important;
        top: 0 !important;
        right: -30px !important;
        width: 40px !important;
        height: 100% !important;
        background: transparent !important;
    }

    [data-testid="stSidebar"]:hover {
        left: 0 !important;
        box-shadow: 15px 0 40px rgba(0, 0, 0, 0.5) !important;
    }

    [data-testid="stSidebarCollapseButton"] {
        display: none !important;
    }

    /* 4. Bulles de message : Style écrin de montre */
    .stChatMessage {
        background-color: rgba(17, 17, 17, 0.6) !important;
        border: 1px solid rgba(163, 126, 44, 0.2) !important;
        border-radius: 6px !important;
        color: #e5e5e5 !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
    }

    /* Message de l'utilisateur surligné d'or */
    .stChatMessage[data-testid="stChatMessageUser"] {
        background-color: rgba(163, 126, 44, 0.1) !important;
        border: 1px solid #A37E2C !important;
    }

    /* 5. Textes et titres en blanc cassé et Or */
    h1, h2, h3, h4, p, span, label, li {
        font-family: "Playfair Display", "Georgia", serif !important; /* Police plus classique et haut de gamme */
        color: #f5f5f5 !important;
    }
    
    h1, h2, h3, .stSidebar subheader {
        color: #A37E2C !important; /* Couleur Or pour les grands titres */
        font-weight: 500 !important;
        letter-spacing: 1px !important;
    }

    /* 6. Boutons et curseurs en Or */
    .stButton>button {
        background-color: transparent !important;
        color: #A37E2C !important;
        border: 1px solid #A37E2C !important;
        border-radius: 4px !important;
        font-family: inherit !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        transition: all 0.2s ease !important;
    }

    .stButton>button:hover {
        background-color: #A37E2C !important;
        color: #111111 !important;
        box-shadow: 0 0 15px rgba(163, 126, 44, 0.4) !important;
    }
    
    div[data-testid="stSlider"] [data-testid="stThumb"] {
        background-color: #A37E2C !important;
        box-shadow: 0 0 10px rgba(163, 126, 44, 0.5) !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================================================================
# --- CORRECTIF : ALIGNEMENT DU TEXTE DES BULLES (ANTI-CHEVAUCHEMENT) ---
# ==============================================================================

st.markdown(
    """
    <style>
    /* Force le conteneur du message à s'organiser proprement en ligne */
    [data-testid="stChatMessage"] {
        display: flex !important;
        align-items: center !important;
        gap: 15px !important; /* Crée un espace de sécurité entre l'avatar et le texte */
    }

    /* Empêche les textes de l'icône et du message de se marcher dessus */
    [data-testid="stChatMessage"] .stMarkdown {
        padding-left: 10px !important;
        margin: 0 !important;
        display: inline-block !important;
    }
    
    /* Nettoyage des résidus de texte parasites en arrière-plan */
    [data-testid="stChatMessageContent"] {
        margin-left: 5px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================================================================
# --- EXTENSION : SUPPRESSION DU BANDEAU D'ACCUEIL PARASITE ---
# ==============================================================================

st.markdown(
    """
    <style>
    /* Masque de force le premier message de bienvenue inutile qui bugue */
    div.stChatMessage:has(span:-webkit-any(:contains("smart_toy"), :contains("Bonjour Eliott"))) {
        display: none !important;
    }
    
    /* Version de secours au cas où : si le texte contient exactement ce bloc, on cache */
    div[data-testid="stChatMessage"]:first-of-type {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================================================================
# --- EXTENSION : BARRE DE RECHERCHE ULTRA-ARRONDIE (STYLE GEMINI) ---
# ==============================================================================

st.markdown(
    """
    <style>
    /* Force la barre de recherche à devenir parfaitement ronde/ovale */
    div[data-testid="stChatInput"] {
        border-radius: 50px !important; /* Arrondi maximal style pilule */
        padding-left: 15px !important;
        padding-right: 15px !important;
        border: 1px solid rgba(0, 0, 0, 0.1) !important;
        background-color: #ffffff !important;
    }

    /* Ajuste la zone de texte à l'intérieur pour suivre l'arrondi */
    div[data-testid="stChatInput"] textarea {
        border-radius: 50px !important;
        padding-top: 10px !important;
        padding-bottom: 10px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================================================================
# --- CORRECTIF : FIX DES BORDS BLANCS SUR LA BARRE DE RECHERCHE ---
# ==============================================================================

st.markdown(
    """
    <style>
    /* On nettoie le bloc global qui entoure la barre de texte */
    div[data-testid="stChatInput"] {
        background-color: transparent !important; /* Enlève le fond blanc qui dépasse */
        border: none !important;
        box-shadow: none !important;
    }

    /* On applique le style arrondi et l'ombre uniquement sur la vraie zone de texte interne */
    div[data-testid="stChatInput"] textarea {
        background-color: #ffffff !important;
        color: #2c3e50 !important;
        border-radius: 24px !important;
        border: 1px solid rgba(0, 0, 0, 0.08) !important;
        padding: 12px 20px !important;
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.15), 0 4px 10px rgba(0, 0, 0, 0.08) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }

    /* Petit effet quand on clique sur la zone de texte */
    div[data-testid="stChatInput"] textarea:focus {
        transform: translateY(-2px) !important;
        box-shadow: 0 18px 35px rgba(0, 0, 0, 0.22) !important;
    }

    /* On cache le conteneur inutile qui forçait la couleur blanche derrière */
    div[data-testid="stChatInput"] > div {
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================================================================
# --- EXTENSION : ÉCRAN DE CONNEXION PREMIUM (APPLE, GOOGLE, EMAIL) ---
# ==============================================================================

# On s'assure que l'utilisateur est déconnecté pour afficher l'écran d'accueil
if "statut_connexion" not in st.session_state:
    st.session_state.statut_connexion = "Déconnecté"

if st.session_state.statut_connexion == "Déconnecté":
    st.write("---")
    
    # Conteneur central style carte flottante
    st.markdown(
        """
        <div style="background: rgba(255, 255, 255, 0.75); padding: 30px; border-radius: 24px; border: 1px solid rgba(0, 0, 0, 0.05); text-align: center; max-width: 450px; margin: 0 auto; box-shadow: 0 15px 35px rgba(0,0,0,0.08);">
            <h2 style="color: #2c3e50; margin-top: 0; font-weight: 600;">Rejoindre Nairu AI</h2>
            <p style="color: #7f8c8d; font-size: 14px; margin-bottom: 25px;">Connectez-vous ou créez un compte pour commencer</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Organisation des boutons au centre
    col_space1, col_center, col_space2 = st.columns([1, 2, 1])
    
    with col_center:
        # 1. BOUTON GOOGLE (HTML personnalisé pour le style original)
        st.markdown(
            """
            <a href="#" style="text-decoration: none;">
                <div style="display: flex; align-items: center; justify-content: center; background-color: #ffffff; color: #5f6368; border: 1px solid #dadce0; padding: 10px 15px; border-radius: 12px; font-weight: bold; font-family: -apple-system, sans-serif; font-size: 14px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); cursor: pointer;">
                    <img src="https://fonts.gstatic.com/s/i/productlogos/googleg/v6/web-24dp/logo_googleg_color_24dp.png" style="width: 18px; margin-right: 10px;">
                    Continuer avec Google
                </div>
            </a>
            """,
            unsafe_allow_html=True
        )
        
        # 2. BOUTON APPLE
        st.markdown(
            """
            <a href="#" style="text-decoration: none;">
                <div style="display: flex; align-items: center; justify-content: center; background-color: #000000; color: #ffffff; padding: 10px 15px; border-radius: 12px; font-weight: bold; font-family: -apple-system, sans-serif; font-size: 14px; margin-bottom: 20px; cursor: pointer;">
                    <svg style="width: 16px; fill: white; margin-right: 10px;" viewBox="0 0 170 170">
                        <path d="M150.37 130.25c-2.45 5.66-5.35 10.87-8.71 15.66-4.58 6.53-8.33 11.05-11.22 13.56-4.48 4.12-9.28 6.23-14.42 6.35-3.69 0-8.14-1.05-13.32-3.18-5.19-2.12-9.97-3.17-14.34-3.17-4.58 0-9.49 1.05-14.75 3.17-5.26 2.13-9.5 3.24-12.74 3.35-4.34.13-9.13-1.78-14.36-5.75-3.72-2.87-7.72-7.71-11.97-14.52-7.5-11.96-12.87-24.99-16.12-39.09-3.25-14.1-3.25-26.68 0-37.73 3.12-10.74 8.24-19.39 15.36-25.96 7.11-6.57 15.11-9.87 24-9.9 4.35 0 9.21 1.22 14.58 3.66 5.38 2.44 8.78 3.66 10.21 3.66 1.12 0 4.61-1.28 10.48-3.84 5.87-2.56 10.73-3.75 14.58-3.57 15.48.87 27.11 6.57 34.91 17.11-14.23 8.61-21.2 20.2-20.91 34.78.29 11.39 4.41 20.89 12.35 28.48 8 7.58 17.41 11.72 28.25 12.43-1.63 4.76-3.87 9.56-6.72 14.39zm-31.25-115.82c0 8.36-3.1 16-9.31 22.91-6.2 6.9-13.52 11.08-21.94 12.54-.12-1.37-.18-2.5-.18-3.38 0-8.5 3.35-16.51 10.05-24 6.7-7.49 14.5-11.58 23.41-12.28.13 1.25.18 2.25.18 3.21z"/>
                    </svg>
                    Continuer avec Apple
                </div>
            </a>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<p style='text-align: center; color: #7f8c8d; font-size: 12px; margin-bottom: 15px;'>— OU —</p>", unsafe_allow_html=True)

        # 3. OPTIONS MAIL (Formulaire Streamlit discret intégré)
        with st.expander("✉️ Continuer avec une adresse e-mail"):
            choix_action = st.radio("Vous souhaitez :", ("Se connecter", "Créer un compte"), horizontal=True)
            
            email_input = st.text_input("Adresse e-mail :", placeholder="exemple@mail.com", key="auth_email")
            mdp_input = st.text_input("Mot de passe :", type="password", key="auth_mdp")
            
            if choix_action == "Se connecter":
                if st.button("🔑 Connexion", use_container_width=True):
                    if email_input and mdp_input:
                        st.success(f"Tentative de connexion pour {email_input}...")
                        # Ici se mettra la logique de vérification plus tard
                    else:
                        st.error("Veuillez remplir tous les champs.")
            else:
                if st.button("✨ Créer mon compte", use_container_width=True):
                    if email_input and mdp_input:
                        st.success("Compte enregistré ! En attente de validation.")
                    else:
                        st.error("Veuillez remplir tous les champs.")

# ==============================================================================
# --- EXTENSION MODIFIÉE : CONNEXION PREMIUM AVEC FORMULAIRE APPLE ---
# ==============================================================================

# Initialisation des états de connexion et des sous-menus
if "statut_connexion" not in st.session_state:
    st.session_state.statut_connexion = "Déconnecté"
if "action_connexion" not in st.session_state:
    st.session_state.action_connexion = "Menu Principal"

if st.session_state.statut_connexion == "Déconnecté":
    st.write("---")
    
    # 1. SI ON EST SUR LE MENU PRINCIPAL
    if st.session_state.action_connexion == "Menu Principal":
        st.markdown(
            """
            <div style="background: rgba(255, 255, 255, 0.75); padding: 30px; border-radius: 24px; border: 1px solid rgba(0, 0, 0, 0.05); text-align: center; max-width: 450px; margin: 0 auto; box-shadow: 0 15px 35px rgba(0,0,0,0.08);">
                <h2 style="color: #2c3e50; margin-top: 0; font-weight: 600;">Rejoindre Nairu AI</h2>
                <p style="color: #7f8c8d; font-size: 14px; margin-bottom: 25px;">Choisissez un mode de connexion</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        col_space1, col_center, col_space2 = st.columns([1, 2, 1])
        
        with col_center:
            # BOUTON GOOGLE
            st.markdown(
                """
                <div style="display: flex; align-items: center; justify-content: center; background-color: #ffffff; color: #5f6368; border: 1px solid #dadce0; padding: 10px 15px; border-radius: 12px; font-weight: bold; font-family: -apple-system, sans-serif; font-size: 14px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); cursor: pointer;">
                    <img src="https://fonts.gstatic.com/s/i/productlogos/googleg/v6/web-24dp/logo_googleg_color_24dp.png" style="width: 18px; margin-right: 10px;">
                    Continuer avec Google
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # BOUTON APPLE TRUQUÉ POUR AGIR COMME UN VRAI BOUTON STREAMLIT
            if st.button("🍏 Continuer avec Apple", use_container_width=True):
                st.session_state.action_connexion = "Connexion Apple"
                st.rerun()

            st.markdown("<p style='text-align: center; color: #7f8c8d; font-size: 12px; margin-vertical: 10px;'>— OU —</p>", unsafe_allow_html=True)

            # FORMULAIRE MAIL CLASSIQUE
            with st.expander("✉️ Continuer avec une adresse e-mail"):
                choix_action = st.radio("Vous souhaitez :", ("Se connecter", "Créer un compte"), horizontal=True, key="radio_mail")
                email_input = st.text_input("Adresse e-mail :", placeholder="exemple@mail.com", key="auth_email")
                mdp_input = st.text_input("Mot de passe :", type="password", key="auth_mdp")
                
                if choix_action == "Se connecter":
                    if st.button("🔑 Connexion", use_container_width=True):
                        st.success(f"Connexion e-mail réussie pour {email_input}")
                else:
                    if st.button("✨ Créer mon compte", use_container_width=True):
                        st.success("Compte e-mail créé !")

    # 2. INTÉGRATION : SI L'UTILISATEUR A CLIQUÉ SUR APPLE
    elif st.session_state.action_connexion == "Connexion Apple":
        st.markdown(
            """
            <div style="background: #000000; padding: 30px; border-radius: 24px; text-align: center; max-width: 450px; margin: 0 auto; box-shadow: 0 15px 35px rgba(0,0,0,0.2);">
                <h2 style="color: #ffffff; margin-top: 0; font-weight: 600;">Connexion avec Apple ID</h2>
                <p style="color: #a1a1a6; font-size: 14px; margin-bottom: 25px;">Utilisez votre identifiant Apple pour vous connecter à Nairu</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        col_space1, col_center, col_space2 = st.columns([1, 2, 1])
        
        with col_center:
            st.write("")
            apple_user = st.text_input("Identifiant Apple (Email) :", placeholder="nom@icloud.com", key="apple_email")
            apple_mdp = st.text_input("Mot de passe d'application :", type="password", key="apple_password")
            
            if st.button("🔒 Se connecter au compte Apple", use_container_width=True):
                if apple_user and apple_mdp:
                    st.success(f"Compte Apple lié avec succès : {apple_user}")
                    st.session_state.statut_connexion = "Connecté"
                    st.session_state.action_connexion = "Menu Principal"
                    st.rerun()
                else:
                    st.error("Veuillez remplir les informations Apple ID.")
                    
            if st.button("⬅️ Retour aux choix", use_container_width=True):
                st.session_state.action_connexion = "Menu Principal"
                st.rerun()

# ==============================================================================
# --- EXTENSION CONFORME : CONNEXION & CRÉATION DE COMPTE (NOM & MDP) ---
# ==============================================================================

# Initialisation des variables de session
if "statut_connexion" not in st.session_state:
    st.session_state.statut_connexion = "Déconnecté"

if st.session_state.statut_connexion == "Déconnecté":
    st.write("---")
    
    # Carte centrale flottante style Marbre Blanc
    st.markdown(
        """
        <div style="background: rgba(255, 255, 255, 0.8); padding: 30px; border-radius: 24px; border: 1px solid rgba(0, 0, 0, 0.05); text-align: center; max-width: 420px; margin: 0 auto; box-shadow: 0 15px 35px rgba(0,0,0,0.06);">
            <h2 style="color: #2c3e50; margin-top: 0; font-weight: 600; font-size: 24px;">Nairu AI</h2>
            <p style="color: #7f8c8d; font-size: 13px; margin-bottom: 20px;">Connectez-vous ou créez un profil d'équipe</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Alignement du formulaire au centre
    col_space1, col_center, col_space2 = st.columns([1, 2, 1])
    
    with col_center:
        st.write("")
        
        # Onglets discrets Streamlit pour basculer entre Connexion et Inscription
        onglet_connexion, onglet_inscription = st.tabs(["🔒 Se connecter", "📝 Créer un compte"])
        
        # --- TAB 1 : CONNEXION ---
        with onglet_connexion:
            st.write("")
            nom_user = st.text_input("👤 Nom d'utilisateur :", placeholder="Ex: Eliott ou Leny", key="login_nom")
            mdp_user = st.text_input("🔑 Mot de passe :", type="password", placeholder="••••••••", key="login_mdp")
            
            st.write("")
            if st.button("🚀 Valider la connexion", use_container_width=True, key="btn_login"):
                if nom_user and mdp_user:
                    nom_propre = nom_user.strip()
                    st.session_state.statut_connexion = nom_propre
                    st.success(f"Connexion réussie ! Bienvenue {nom_propre}.")
                    st.rerun()
                else:
                    st.error("⚠️ Veuillez remplir tous les champs pour vous connecter.")
                    
        # --- TAB 2 : CRÉATION DE COMPTE ---
        with onglet_inscription:
            st.write("")
            nouveau_nom = st.text_input("👤 Choisissez un nom d'utilisateur :", placeholder="Ex: Invite123", key="signup_nom")
            nouveau_mdp = st.text_input("🔑 Choisissez un mot de passe :", type="password", placeholder="••••••••", key="signup_mdp")
            confirmer_mdp = st.text_input("🔄 Confirmez le mot de passe :", type="password", placeholder="••••••••", key="signup_mdp_conf")
            
            st.write("")
            if st.button("✨ Enregistrer le compte", use_container_width=True, key="btn_signup"):
                if nouveau_nom and nouveau_mdp and confirmer_mdp:
                    if nouveau_mdp == confirmer_mdp:
                        nom_cree = nouveau_nom.strip()
                        # Simulation de création : connecte directement l'utilisateur après inscription
                        st.session_state.statut_connexion = nom_cree
                        st.success(f"Compte créé avec succès ! Bienvenue à bord, {nom_cree}.")
                        st.rerun()
                    else:
                        st.error("⚠️ Les mots de passe ne correspondent pas.")
                else:
                    st.error("⚠️ Veuillez remplir tous les champs pour créer un compte.")
