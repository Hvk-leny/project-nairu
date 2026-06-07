import json
import os

DB_FILE = "utilisateurs.json"

def charger_utilisateurs():
    if not os.path.exists(DB_FILE):
        # Compte exemple par défaut avec un faux email pour la structure
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
            return json.load(f)
    except:
        return {}

def sauvegarder_utilisateur(username, email, password):
    comptes = charger_utilisateurs()
    # On stocke l'email et le mot de passe sous forme de sous-dictionnaire
    comptes[username] = {
        "email": email,
        "password": password
    }
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(comptes, f, indent=4)

# --- ONGLET 1 : CONNEXION USER ---
    with tab_login:
        st.markdown("### 🔒 Connexion Utilisateur")
        
        base_comptes = charger_utilisateurs()
        
        # --- Formulaire de Connexion ---
        with st.form(key="formulaire_connexion"):
            identifiant = st.text_input("Identifiant ou Prénom :", placeholder="exemple", key="login_username")
            code_secret = st.text_input("Code secret :", type="password", placeholder="exemple", key="login_password")
            bouton_soumettre = st.form_submit_button("Se connecter", use_container_width=True)
            
            if bouton_soumettre:
                # On vérifie si l'identifiant existe et si le mot de passe dans le dictionnaire correspond
                if identifiant in base_comptes and base_comptes[identifiant]["password"] == code_secret:
                    st.session_state.statut_connexion = "Connecté"
                    st.success(f"Connexion réussie ! Bienvenue {identifiant}.")
                    st.rerun()
                else:
                    st.error("Identifiant ou mot de passe incorrect.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- Formulaire de Création de Compte ---
        with st.expander("✨ Nouveau sur Nairu ? Créer un compte"):
            
            # Ton texte d'explication obligatoire
            st.markdown(
                """
                > ⚠️ **Note importante :** > * Pour vous connecter, utilisez uniquement votre **identifiant** et votre **mot de passe**.  
                > * L'**email** sert uniquement à la création du compte.
                """
            )
            
            with st.form(key="formulaire_inscription"):
                nouvel_identifiant = st.text_input("Choisis un identifiant :", key="reg_username")
                nouvel_email = st.text_input("Adresse Email :", placeholder="votre@email.com", key="reg_email")
                nouveau_code = st.text_input("Choisis un code secret :", type="password", key="reg_password")
                bouton_inscrire = st.form_submit_button("Créer mon compte", use_container_width=True)
                
                if bouton_inscrire:
                    if nouvel_identifiant.strip() == "" or nouvel_email.strip() == "" or nouveau_code.strip() == "":
                        st.warning("Veuillez remplir tous les champs (Identifiant, Email et Mot de passe).")
                    elif "@" not in nouvel_email or "." not in nouvel_email:
                        st.error("Veuillez entrer une adresse email valide.")
                    elif nouvel_identifiant in base_comptes:
                        st.error("Cet identifiant existe déjà !")
                    else:
                        # On enregistre les 3 infos d'un coup dans le JSON
                        sauvegarder_utilisateur(nouvel_identifiant, nouvel_email, nouveau_code)
                        st.success("🎉 Compte créé avec succès ! Vous pouvez maintenant vous connecter juste au-dessus avec votre identifiant.")
