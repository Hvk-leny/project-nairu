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
import streamlit as st
import google.generativeai as genai
# --- CONFIGURATION GEMINI ET INTERFACE ---
# Activation de ta clé API Gemini
genai.configure(api_key="AQ.Ab8RN6KqmDWeAQNop2WUxrlaTUvgIROB9Bh8kjX-UwT1dJRS7w")

# Création du menu dans la barre latérale
st.sidebar.title("⚡ Configuration du Néron")
option = st.sidebar.radio(
    "Choisis le mode de fonctionnement :",
    ("Option Flash ⚡", "Option Réflexion 🧠", "Option Passionné / Intéressé 🔥")
)

# Réglage du comportement du Néron selon l'option choisie
if option == "Option Flash ⚡":
    st.sidebar.info("Mode Flash : Réponses courtes et ultra rapides.")
    system_instruction = "Tu es Néron. Réponds de manière ultra rapide, concise, claire et directe, va droit au but."
    model_name = "gemini-1.5-flash"
    
elif option == "Option Réflexion 🧠":
    st.sidebar.info("Mode Réflexion : Analyse profonde et structurée.")
    system_instruction = "Tu es Néron. Prends le temps de bien analyser. Donne une réponse très détaillée, logique, technique et approfondie."
    model_name = "gemini-1.5-pro" # Modèle plus puissant pour la réflexion
    
elif option == "Option Passionné / Intéressé 🔥":
    st.sidebar.info("Mode Passionné : Expert auto à 100% !")
    system_instruction = "Tu es Néron, un expert automobile absolu. Réponds avec énormément d'enthousiasme et de passion. Utilise un ton dynamique et fais des parallèles avec la mécanique, la prépa ou la haute performance (moteurs comme le B58, châssis) dès que possible."
    model_name = "gemini-1.5-flash"
# ----------------------------------------
# --- APPEL À GEMINI ---
        try:
            # On prépare le modèle Gemini avec le comportement choisi
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system_instruction
            )
            
            # On envoie le message de l'utilisateur à Gemini
            # (Remplace 'user_input' par le nom de ta variable si besoin)
            response = model.generate_content(user_input)
            
            # La réponse textuelle de Gemini est disponible dans : response.text
            # Tu peux l'afficher avec st.write(response.text) ou l'ajouter à ton historique
            
        except Exception as e:
            st.error(f"Erreur Gemini : {e}")
        # ----------------------
