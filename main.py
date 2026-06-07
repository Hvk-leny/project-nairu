# ==============================================================================
# --- CONFIGURATION INITIALE ET PAGE D'ACCUEIL ---
# ==============================================================================
st.set_page_config(
    page_title="NAIRU - AI",
    page_icon="💬",
    layout="wide",                     # Permet d'occuper tout l'écran pour le mode colonnes
    initial_sidebar_state="collapsed"   # On masque la barre latérale d'origine
)

# --- SÉCURITÉ CSS : Masquage des icônes natives et style de la flèche expander ---
st.markdown(
    """
    <style>
    /* On fait disparaître les icônes de texte génériques de Streamlit pour éviter les bugs */
    [data-testid="stIconMaterial"] {
        font-size: 0px !important;
        color: transparent !important;
        line-height: 0 !important;
        display: none !important;
    }
    
    /* On force l'affichage d'une jolie flèche personnalisée pour l'expander de l'espace invité */
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

# --- LE GRAND TITRE D'ACCUEIL ---
st.title("bienvenue sur nairu")
