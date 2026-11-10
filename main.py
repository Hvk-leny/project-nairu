import streamlit as st
import os
import datetime
from openai import OpenAI
import streamlit.components.v1 as components

# ==============================================================================
# --- CONFIGURATION DE LA CLÉ API ---
# ==============================================================================
CLE_OPENROUTER = os.getenv(
    "OPENROUTER_API_KEY", 
    "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"
)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=CLE_OPENROUTER,
)

# ==============================================================================
# --- 1. FONCTIONS DE BASE & CONFIGURATION INTERNE ---
# ==============================================================================

components.html(
    """<script>
        var meta = parent.document.createElement('meta');
        meta.name = 'google-site-verification';
        meta.content = 'Ih0SvT8spLCGn5y0eaJnMuFrArHwURmtdDCuNdIEUk8';
        parent.document.getElementsByTagName('head')[0].appendChild(meta);
    </script>""", height=0
)

def calculer_age_nairu():
    try:
        diff = datetime.datetime.now() - datetime.datetime(2026, 6, 6, 22, 0)
        return f"{diff.days} jours, {diff.seconds // 3600} heures"
    except Exception:
        return "quelques semaines"

# ==============================================================================
# --- 2. MISE EN PAGE & GESTION DU THÈME ---
# ==============================================================================
st.set_page_config(
    page_title="NAIRU - AI", 
    page_icon="💬", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.markdown(
    """<style>
    [data-testid="stExpander"] [data-testid="stIconMaterial"] { font-size: 0px !important; color: transparent !important; display: none !important; }
    [data-testid="stExpander"] summary { position: relative !important; }
    [data-testid="stExpander"] summary::after { content: '➔' !important; font-size: 14px !important; color: #00f0ff !important; position: absolute !important; right: 15px !important; }
    </style>""", 
    unsafe_allow_html=True
)

if "messages_chat" not in st.session_state:
    st.session_state.messages_chat = []

# ==============================================================================
# --- 3. BARRE LATÉRALE ---
# ==============================================================================
with st.sidebar:
    st.title("NAIRU AI")
    st.caption(f"⏱️ Actif depuis : {calculer_age_nairu()}")
    st.divider()
    
    if st.button("🗑️ Effacer la conversation", use_container_width=True):
        st.session_state.messages_chat = []
        st.rerun()

# ==============================================================================
# --- 4. INTERFACE DE DISCUSSION PRINCIPALE ---
# ==============================================================================
st.title("Discussion avec NAIRU")

# Affichage de l'historique des échanges
for message in st.session_state.messages_chat:
    with st
