import streamlit as st
from groq import Groq

# ==============================================================================
# --- INTERRUPTEUR DE MAINTENANCE (METTRE À True POUR ACTIVER) ---
# ==============================================================================
MAINTENANCE_ACTIVE = True

if MAINTENANCE_ACTIVE:
    st.set_page_config(page_title="Nairu - Maintenance", page_icon="🛠️", layout="centered")
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.title("🛠️ Site en maintenance")
    st.subheader("Nairu s'offre une petite révision !")
    st.info(
        "L'application est actuellement en cours de mise à jour pour tout l'après-midi. "
        "Nous préparons de nouvelles fonctionnalités et optimisons les performances de l'IA."
    )
    st.markdown("---")
    st.write("⏳ **Retour prévu en fin de journée.** Merci pour votre patience !")
    st.link_button("💬 Me contacter sur Instagram", "https://instagram.com/Eliott31tls")
    
    st.stop() # Bloque le reste du code en dessous
# ==============================================================================
