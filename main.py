import streamlit as st
import json
import os
import datetime
from zoneinfo import ZoneInfo
from groq import Groq
from duckduckgo_search import DDGS

# ==============================================================================
# 1. CONFIGURATION DE LA PAGE & DESIGN TECH MINIMALISTE (SOMBRE ÉPURÉ)
# ==============================================================================
st.set_page_config(page_title="NAIRU - AI", page_icon="🤖", layout="wide")

st.markdown(
    """
    <style>
    /* Fond global sombre style interface de dev moderne */
    .stApp {
        background-color: #0d1117 !important;
    }

    /* Barre latérale gris anthracite propre */
    [data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 1px solid #30363d !important;
    }

    /* Conteneur des messages (Style bulles épurées en relief) */
    [data-testid="stChatMessage"] {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 12px !important;
        padding: 18px !important;
        margin-bottom: 12px !important;
    }
    
    [data-testid="stChatMessageUser"] {
        background-color: #21262d !important;
        border: 1px solid #388bfd !important; /* Ligne d'accentuation bleue pour l'utilisateur */
    }

    /* Barre de recherche ovale et moderne (Sans bordure blanche parasite) */
    div[data-testid="stChatInput"] {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    div[data-testid="stChatInput"] textarea {
        background-color: #161b22 !important;
        color: #c9d1d9 !important;
        border-radius: 24px !important;
        border: 1px solid #30363d !important;
        padding: 12px 20px !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5) !important;
    }
    div[data-testid="stChatInput"] textarea:focus {
        border-color: #388bfd !important;
    }

    /* Typographies et Boutons Tech */
    h1, h2, h3, h4, p, span, label, li {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif !important;
        color: #c9d1d9 !important;
    }
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    .stButton>button {
        background-color: #21262d !important;
        color: #c9d1d9 !important;
        border: 1px solid #30363d !important;
        border-radius: 6px !important;
        transition: all 0.2s ease !important;
    }
    .stButton>button:hover {
        background-color: #30363d !important;
        color: #ffffff !important;
        border-color: #8b949e !important;
    }
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
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(structure, f, indent=4)
        return structure
    with open(DB_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return {"users": {"eliott": {"code": "code1", "history": []}, "leny": {"code": "code2", "history": []}}}

def sauvegarder_base(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# Initialisation des variables d'état système
if "data" not in st.session_state: st.session_state.data = charger_base()
if "statut_connexion" not in st.session_state: st.session_state.statut_connexion = "Déconnecté"
if "conversations" not in st.session_state: st.session_state.conversations = {"Discussion 1": []}
if "current_chat" not in st.session_state: st.session_state.current_chat = "Discussion 1"

# ==============================================================================
# 3. COMPOSANT MOTEUR : RECHERCHE DUCKDUCKGO
# ==============================================================================
def chercher_web(requete):
    try:
        with DDGS() as ddgs:
            resultats = [r for r in ddgs.text(requete, max_results=3)]
            if resultats:
                return "\n\n".join([f"Source: {r['title']}\nContenu: {r['body']}" for r in resultats])
    except Exception:
        return "Impossible de récupérer les données du web en temps réel."
    return "Aucun résultat trouvé sur le web."

# ==============================================================================
# 4. PANNEAU CENTRAL D'ACCUEIL ET AUTHENTIFICATION
# ==============================================================================
if st.session_state.statut_connexion == "Déconnecté":
    st.title("🤖 Connexion à Nairu OS")
    
    col_x1, col_form, col_x2 = st.columns([1, 2, 1])
    with col_form:
        tab_login, tab_signup, tab_guest = st.tabs(["🔒 S'authentifier", "📝 Créer un compte d'équipe", "🎭 Accès Invité"])
        
        with tab_login:
            st.write("")
            nom_input = st.text_input("Prénom :", key="login_name").strip().lower()
            code_input = st.text_input("Code secret :", type="password", key="login_code").strip()
            if st.button("Valider l'accès", use_container_width=True):
                if nom_input in st.session_state.data["users"] and code_input == st.session_state.data["users"][nom_input]["code"]:
                    st.session_state.statut_connexion = nom_input
                    st.rerun()
                else:
                    st.error("Identifiants d'équipe introuvables ou incorrects.")
                    
        with tab_signup:
            st.write("")
            new_name = st.text_input("
