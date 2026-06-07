import streamlit as st
import json
import os
from groq import Groq

# ==============================================================================
# --- 1. FONCTIONS DE LA BASE DE DONNÉES JSON ---
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
# --- 2. MISE EN PAGE & BIENVENUE ---
# ==============================================================================
st.set_page_config(
    page_title="NAIRU - AI",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Masquage des bugs d'icônes natifs
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

# Ton grand titre d'accueil
st.title("bienvenue sur nairu")
