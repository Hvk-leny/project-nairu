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
# --- EXTENSION : DESIGN FUTURISTE & EFFET AQUA / GLASSMORPHISM (IOS STYLE) ---
# ==============================================================================

st.markdown(
    """
    <style>
    /* 1. Fond d'écran futuriste avec un dégradé fluide aqua/sombre */
    .stApp {
        background: linear-gradient(135deg, #0d1b2a 0%, #0b253a 50%, #004b6e 100%);
        background-attachment: fixed;
    }

    /* 2. Effet "Eau/Verre" (Glassmorphism) sur les bulles de chat */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.06) !important;
        backdrop-filter: blur(12px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(12px) saturate(180%) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 18px !important;
        padding: 15px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2) !important;
        transition: all 0.3s ease;
    }

    /* Différenciation de la bulle utilisateur (style iOS bleuté transparent) */
    .stChatMessage[data-testid="stChatMessageUser"] {
        background-color: rgba(0, 119, 182, 0.2) !important;
        border: 1px solid rgba(0, 180, 216, 0.3) !important;
    }

    /* 3. Style de la barre latérale (Sidebar) façon panneau de contrôle transparent */
    [data-testid="stSidebar"] {
        background-color: rgba(13, 27, 42, 0.4) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }

    /* 4. Personnalisation des boutons (Style boutons d'iPhone en verre) */
    .stButton>button {
        background: rgba(255, 255, 255, 0.08) !important;
        color: #00b4d8 !important;
        border: 1px solid rgba(0, 180, 216, 0.4) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(5px) !important;
        font-weight: bold !important;
        transition: all 0.2s ease-in-out !important;
    }

    .stButton>button:hover {
        background: rgba(0, 180, 216, 0.2) !important;
        box-shadow: 0 0 15px rgba(0, 180, 216, 0.5) !important;
        color: #ffffff !important;
        transform: scale(1.02);
    }

    /* 5. Titres et textes flashys futuristes */
    h1, h2, h3, p, span, label {
        color: #e0e1dd !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }
    
    /* Couleur néon aqua pour le titre de configuration */
    .stSidebar subheader, .stSidebar title {
        color: #00b4d8 !important;
    }

    /* 6. Curseur de créativité (Slider) style néon */
    div[data-testid="stSlider"] [data-testid="stThumb"] {
        background-color: #00b4d8 !important;
        box-shadow: 0 0 10px #00b4d8 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================================================================
# --- EXTENSION : MODE INVITÉ (OPTION DM INSTA OU PRÉSENTATION) ---
# ==============================================================================

st.sidebar.write("---")
st.sidebar.subheader("👤 Espace Connexion")

# Initialisation du statut si non existant
if "statut_connexion" not in st.session_state:
    st.session_state.statut_connexion = "Déconnecté"

# Bouton pour activer le mode invité
if st.session_state.statut_connexion == "Déconnecté":
    if st.sidebar.button("🎭 Se connecter en tant qu'invité", use_container_width=True):
        st.session_state.statut_connexion = "Invité"
        st.rerun()

# Interface du Mode Invité
if st.session_state.statut_connexion == "Invité":
    st.write("---")
    
    st.markdown(
        """
        <div style="background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 18px; border: 1px solid rgba(0, 180, 216, 0.2); text-align: center; margin-bottom: 25px;">
            <h3 style="color: #00b4d8; margin-top: 0; margin-bottom: 5px;">✨ Bienvenue sur Nairu AI</h3>
            <p style="color: #gray; font-size: 14px; margin: 0;">Mode Invité • Accès Découverte</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Séparation en deux colonnes : DM Insta ou Présentation
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
                <p style="font-size: 13px; color: #e0e1dd; margin-bottom: 5px;"><b>Nairu</b> est un assistant virtuel intelligent de dernière génération conçu pour être performant, fluide et stylé.</p>
                <ul style="font-size: 12px; color: #a0a0a0; padding-left: 15px; margin: 0;">
                    <li>⚡ <b>Moteur Groq :</b> Réponses instantanées.</li>
                    <li>🌐 <b>Recherche Web :</b> Connecté à Internet.</li>
                    <li>🔥 <b>Mode Passionné :</b> Expert en mécanique et automobile.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Bouton pour faire machine arrière
    st.write("")
    if st.button("⬅️ Retour à la page de connexion", use_container_width=True):
        st.session_state.statut_connexion = "Déconnecté"
        st.rerun()
