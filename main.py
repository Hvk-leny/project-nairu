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
# 3. MOTEUR DE RECHERCHE DUCKDUCKGO (ALIGNEMENT FIXÉ)
# ==============================================================================
def chercher_web(requete):
    try:
        with DDGS() as ddgs:
            resultats = [r for r in ddgs.text(requete, max_results=3)]
            if resultats: 
                return "\n\n".join([f"Source: {r['title']}\nContenu: {r['body']}" for r in resultats])
    except Exception: 
        return "Impossible de récupérer les données du web."
    return "Aucun résultat trouvé."

# ==============================================================================
# 4. PANNEAU CENTRAL D'ACCUEIL ÉPURÉ
# ==============================================================================
if st.session_state.statut_connexion == "Déconnecté":
    st.title("bienvenue sur nairu")
    
    col_x1, col_form, col_x2 = st.columns([1, 2, 1])
    with col_form:
        tab_login, tab_guest = st.tabs(["🔒 Connexion ", "🎭 Accès Invité"])
        
        with tab_login:
            st.write("")
            nom_input = st.text_input("Identifiant ou Prénom :", key="login_name").strip().lower()
            code_input = st.text_input("Code secret :", type="password", key="login_code").strip()
            
            if st.button("se connecter", use_container_width=True):
                if nom_input in st.session_state.data["users"]:
                    if code_input == st.session_state.data["users"][nom_input]["code"]:
                        st.session_state.statut_connexion = nom_input
                        st.rerun()
                    else:
                        st.error("❌ Code secret incorrect.")
                else:
                    st.error("❌ Identifiant non reconnu.")
                    if st.session_state.statut_connexion == "Déconnecté":
                         st.title("Connexion à Nairu")
    

# ==============================================================================
# --- CORRECTION FINALE : SÉCURISATION DES ICÔNES TEXTUELLES ---
# ==============================================================================
st.markdown(
    """
    <style>
    /* On cible le composant exact que Streamlit utilise pour afficher ses icônes */
    [data-testid="stIconMaterial"] {
        font-size: 0px !important;
        color: transparent !important;
        line-height: 0 !important;
        display: none !important;
        width: 0 !important;
        height: 0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================================================================
# --- STRUCTURE DE L'ÉCRAN : ZONE PRINCIPALE À GAUCHE / TASKBAR À DROITE ---
# ==============================================================================

# On sépare l'écran en 2 colonnes (80% pour le chat, 20% pour la barre de droite)
col_discussion, col_taskbar = st.columns([4, 1])

# --- 1. ZONE DE DISCUSSION (À GAUCHE) ---
with col_discussion:
    st.title("💬 Discussion 1")
    
    # C'est ICI et UNIQUEMENT ici que doit se trouver ton affichage de messages
    # (Supprime bien le st.chat_input qui traînait tout seul ailleurs dans le fichier)
    st.chat_input("Écris ton message ici...")

# --- 2. NOUVELLE TASKBAR (À DROITE) ---
with col_taskbar:
    st.markdown("### 🛠️ Paramètres IA")
    
    pipeline = st.radio(
        "Pipeline :",
        ["Option Flash ⚡", "Option Réflexion 💬", "Option Passionné 🔥"],
        key="pipeline_droite" # Une clé unique pour éviter tout autre conflit
    )
    
    internet = st.toggle("🌐 Interroger Internet", value=True, key="internet_droite")
    creativite = st.slider("☁️ Créativité :", 0.0, 1.0, 0.50, key="slider_droite")
    
    st.markdown("---")
    st.markdown("### ⏳ Confidentialité")
    mode_ephemere = st.toggle("🗑️ Mode Éphémère (72h)", key="ephemere_droite")
    st.markdown("### ⏳ Confidentialité")
    mode_ephemere = st.toggle("🗑️ Mode Éphémère (72h)")
