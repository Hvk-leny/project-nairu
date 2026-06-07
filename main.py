import streamlit as st
import json
import os
import datetime
from zoneinfo import ZoneInfo
from groq import Groq
from duckduckgo_search import DDGS

# ==============================================================================
# 1. CONFIGURATION DE LA PAGE & DESIGN TECH MINIMALISTE
# ==============================================================================
st.set_page_config(page_title="NAIRU - AI", page_icon="🤖", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background-color: #0d1117 !important; }
    [data-testid="stSidebar"] { background-color: #161b22 !important; border-right: 1px solid #30363d !important; }
    [data-testid="stChatMessage"] {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 12px !important;
        padding: 18px !important;
        margin-bottom: 12px !important;
    }
    [data-testid="stChatMessageUser"] { background-color: #21262d !important; border: 1px solid #388bfd !important; }
    div[data-testid="stChatInput"] { background-color: transparent !important; border: none !important; box-shadow: none !important; }
    div[data-testid="stChatInput"] textarea {
        background-color: #161b22 !important;
        color: #c9d1d9 !important;
        border-radius: 24px !important;
        border: 1px solid #30363d !important;
        padding: 12px 20px !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5) !important;
    }
    h1, h2, h3, h4, p, span, label, li { font-family: -apple-system, BlinkMacSystemFont, sans-serif !important; color: #c9d1d9 !important; }
    h1, h2, h3 { color: #ffffff !important; font-weight: 600 !important; }
    .stButton>button { background-color: #21262d !important; color: #c9d1d9 !important; border: 1px solid #30363d !important; border-radius: 6px !important; }
    .stButton>button:hover { background-color: #30363d !important; color: #ffffff !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================================================================
# 2. GESTION DE LA BASE DE DONNÉES JSON LOCAL
# ==============================================================================
DB_FILE = "database.json"

def charger_base():
    if not os.path.exists(DB_FILE):
        structure = {"users": {"eliott": {"code": "code1", "history": []}, "leny": {"code": "code2", "history": []}}}
        with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(structure, f, indent=4)
        return structure
    with open(DB_FILE, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except: return {"users": {"eliott": {"code": "code1", "history": []}, "leny": {"code": "code2", "history": []}}}

def sauvegarder_base(data):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(data, f, indent=4)

if "data" not in st.session_state: st.session_state.data = charger_base()
if "statut_connexion" not in st.session_state: st.session_state.statut_connexion = "Déconnecté"
if "conversations" not in st.session_state: st.session_state.conversations = {"Discussion 1": []}
if "current_chat" not in st.session_state: st.session_state.current_chat = "Discussion 1"

# ==============================================================================
# 3. MOTEUR DE RECHERCHE DUCKDUCKGO
# ==============================================================================
def chercher_web(requete):
    try:
        with DDGS() as ddgs:
            resultats = [r for r in ddgs.text(requete, max_results=3)]
            if resultats: return "\n\n".join([f"Source: {r['title']}\nContenu: {r['body']}" for r in resultats])
    except Exception: return "Impossible de récupérer les données du web."
    return "Aucun résultat trouvé."

# ==============================================================================
# 4. PANNEAU CENTRAL D'ACCUEIL (AUTHENTIFICATION STRICTE ELIOTT & LENY)
# ==============================================================================
if st.session_state.statut_connexion == "Déconnecté":
    st.title("🤖 Connexion à Nairu OS")
    
    col_x1, col_form, col_x2 = st.columns([1, 2, 1])
    with col_form:
        tab_login, tab_guest = st.tabs(["🔒 Connexion Développeurs", "🎭 Accès Invité"])
        
        with tab_login:
            st.write("")
            nom_input = st.text_input("Prénom du créateur (Eliott / Leny) :", key="login_name").strip().lower()
            code_input = st.text_input("Code secret :", type="password", key="login_code").strip()
            
            if st.button("Valider l'accès Master", use_container_width=True):
                if nom_input in st.session_state.data["users"]:
                    if code_input == st.session_state.data["users"][nom_input]["code"]:
                        st.session_state.statut_connexion = nom_input
                        st.rerun()
                    else:
                        st.error("❌ Code secret incorrect pour ce développeur.")
                else:
                    st.error("❌ Prénom non reconnu dans l'équipe Nairu.")
                    
        with tab_guest:
            st.write("")
            st.info("Le mode invité donne un accès de démonstration sans historique.")
            if st.button("Lancer l'instance Invité", use_container_width=True):
                st.session_state.statut_connexion = "Invité"
                st.rerun()

# ==============================================================================
# 5. INSTANCE LOGICIELLE (SI CONNECTÉ)
# ==============================================================================
else:
    user = st.session_state.statut_connexion
    
    if user == "Invité":
        st.title("✨ Espace Découverte Nairu")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div style="background:#161b22; padding:20px; border-radius:12px; border:1px solid #30363d;"><h4>📩 Demander un accès</h4><p>Contactez l\'équipe pour obtenir vos identifiants.</p><a href="https://www.instagram.com/eliott31tls" target="_blank"><button style="width:100%; padding:10px; background:#238636; border:none; border-radius:6px; font-weight:bold; color:white; cursor:pointer;">Envoyer un DM à Eliott</button></a></div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div style="background:#161b22; padding:20px; border-radius:12px; border:1px solid #30363d;"><h4>⚙️ Infos Nairu</h4><ul><li>Moteur Cloud : Groq API</li><li>Indexation : DuckDuckGo</li><li>Statut : Stable (2026)</li></ul></div>', unsafe_allow_html=True)
        st.write("")
        if st.button("⬅️ Quitter la démo", use_container_width=True):
            st.session_state.statut_connexion = "Déconnecté"
            st.rerun()

    else:
        client = Groq(api_key="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")
        
        with st.sidebar:
            st.subheader(f"👑 Créateur : {user.capitalize()}")
            if st.button("🛑 Déconnexion", use_container_width=True):
                st.session_state.statut_connexion = "Déconnecté"
                st.rerun()
            
            st.write("---")
            st.subheader("🛠️ Paramètres IA")
            option = st.radio("Pipeline :", ("Option Flash ⚡", "Option Réflexion 💬", "Option Passionné / Intéressé 🔥"))
            recherche_web = st.toggle("🌐 Interroger Internet", value=True)
            creativite = st.slider("🧠 Créativité :", 0.0, 1.0, 0.5, 0.1)
            
            st.write("---")
            st.subheader("⏳ Confidentialité")
            activer_ephemere = st.toggle("🗑️ Mode Éphémère (72h)", value=False)
            
            st.write("---")
            st.subheader("📁 Canaux")
            if st.button("➕ Nouveau canal", use_container_width=True):
                id_chat = f"Discussion {len(st.session_state.conversations) + 1}"
                st.session_state.conversations[id_chat] = []
                st.session_state.current_chat = id_chat
                st.rerun()
            
            liste_conversations = list(st.session_state.conversations.keys())
            choix_canal = st.selectbox("Canal actuel :", liste_conversations, index=liste_conversations.index(st.session_state.current_chat))
            if choix_canal != st.session_state.current_chat:
                st.session_state.current_chat = choix_canal
                st.rerun()

        if option == "Option Flash ⚡":
            system_instruction = "Tu es Nairu. Réponds de manière ultra rapide, concise et directe."
            model_name = "llama-3.1-8b-instant"
        elif option == "Option Réflexion 💬":
            system_instruction = "Tu es Nairu. Fais une synthèse complète, logique, structurée et technique."
            model_name = "llama-3.3-70b-versatile"
        else:
            system_instruction = "Tu es Nairu, expert automobile absolu. Réponds avec énormément d'enthousiasme et de passion mécanique."
            model_name = "llama-3.1-8b-instant"

        st.title(f"💬 {st.session_state.current_chat}")
        
        for msg in st.session_state.conversations[st.session_state.current_chat]:
            avatar_style = "⚡" if msg["role"] == "assistant" else None
            with st.chat_message(msg["role"], avatar=avatar_style): st.write(msg["content"])

        if prompt := st.chat_input("Écris ton message ici..."):
            with st.chat_message("user"): st.write(prompt)
            
            if not activer_ephemere:
                st.session_state.conversations[st.session_state.current_chat].append({"role": "user", "content": prompt})
            
            contexte_web = chercher_web(prompt) if recherche_web else ""
            
            with st.chat_message("assistant", avatar="⚡"):
                placeholder = st.empty()
                with st.spinner("Nairu analyse..."):
                    try:
                        messages_ia = [
                            {"role": "system", "content": f"Tu t'appelles impérativement Nairu. Tu as été codée de A à Z par tes deux développeurs de la région toulousaine, Eliott et Leny. Tu es leur assistant personnel. {system_instruction}"}
                        ]
                        if contexte_web: messages_ia.append({"role": "system", "content": f"Données Web :\n{contexte_web}"})
                        
                        for h_msg in st.session_state.conversations[st.session_state.current_chat][-6:]:
                            if h_msg["role"] != "system": messages_ia.append({"role": h_msg["role"], "content": h_msg["content"]})
                                
                        messages_ia.append({"role": "user", "content": prompt})
                        
                        completion = client.chat.completions.create(model=model_name, messages=messages_ia, temperature=creativite)
                        response_text = completion.choices[0].message.content
                        placeholder.write(response_text)
                        
                        if not activer_ephemere:
                            st.session_state.conversations[st.session_state.current_chat].append({"role": "assistant", "content": response_text})
                            st.session_state.data["users"][user]["history"] = st.session_state.conversations[st.session_state.current_chat]
                            sauvegarder_base(st.session_state.data)
                            
                    except Exception as error: placeholder.write(f"⚠️ Erreur Groq API Core : {error}")

        fuseau_france = ZoneInfo("Europe/Paris")
        heure_actuelle = datetime.datetime.now(fuseau_france).strftime("%H:%M")
        st.markdown(f'<div style="text-align: right; color: #8b949e; font-family: monospace; font-size: 12px; margin-top: 20px;">🕒 {heure_actuelle}</div>', unsafe_allow_html=True)

import streamlit as st
import json
import os
import datetime
from zoneinfo import ZoneInfo
from groq import Groq
from duckduckgo_search import DDGS

# ==============================================================================
# 1. CONFIGURATION DE LA PAGE & DESIGN TECH MINIMALISTE
# ==============================================================================
st.set_page_config(page_title="NAIRU - AI", page_icon="🤖", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background-color: #0d1117 !important; }
    [data-testid="stSidebar"] { background-color: #161b22 !important; border-right: 1px solid #30363d !important; }
    [data-testid="stChatMessage"] {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 12px !important;
        padding: 18px !important;
        margin-bottom: 12px !important;
    }
    [data-testid="stChatMessageUser"] { background-color: #21262d !important; border: 1px solid #388bfd !important; }
    div[data-testid="stChatInput"] { background-color: transparent !important; border: none !important; box-shadow: none !important; }
    div[data-testid="stChatInput"] textarea {
        background-color: #161b22 !important;
        color: #c9d1d9 !important;
        border-radius: 24px !important;
        border: 1px solid #30363d !important;
        padding: 12px 20px !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5) !important;
    }
    h1, h2, h3, h4, p, span, label, li { font-family: -apple-system, BlinkMacSystemFont, sans-serif !important; color: #c9d1d9 !important; }
    h1, h2, h3 { color: #ffffff !important; font-weight: 600 !important; }
    .stButton>button { background-color: #21262d !important; color: #c9d1d9 !important; border: 1px solid #30363d !important; border-radius: 6px !important; }
    .stButton>button:hover { background-color: #30363d !important; color: #ffffff !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================================================================
# 2. GESTION DE LA BASE DE DONNÉES JSON LOCAL
# ==============================================================================
DB_FILE = "database.json"

def charger_base():
    if not os.path.exists(DB_FILE):
        structure = {"users": {"eliott": {"code": "code1", "history": []}, "leny": {"code": "code2", "history": []}}}
        with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(structure, f, indent=4)
        return structure
    with open(DB_FILE, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except: return {"users": {"eliott": {"code": "code1", "history": []}, "leny": {"code": "code2", "history": []}}}

def sauvegarder_base(data):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(data, f, indent=4)

if "data" not in st.session_state: st.session_state.data = charger_base()
if "statut_connexion" not in st.session_state: st.session_state.statut_connexion = "Déconnecté"
if "conversations" not in st.session_state: st.session_state.conversations = {"Discussion 1": []}
if "current_chat" not in st.session_state: st.session_state.current_chat = "Discussion 1"

# ==============================================================================
# 3. MOTEUR DE RECHERCHE DUCKDUCKGO
# ==============================================================================
def chercher_web(requete):
    try:
        with DDGS() as ddgs:
