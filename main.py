"""
Nairu AI - Application Streamlit
Créée par Leny et Eliott.

Assistant IA avec système de comptes, mémoire long terme, mode maintenance
et recherche web intégrée via l'API Groq.
"""

import streamlit as st
import json
import os
import hashlib
import secrets
import datetime
from groq import Groq
from duckduckgo_search import DDGS
import streamlit.components.v1 as components

# ==============================================================================
# --- 1. CONFIGURATION & CONSTANTES ---
# ==============================================================================

FICHIER_UTILISATEURS = "utilisateurs.json"
FICHIER_MEMOIRE = "memoire.json"
DATE_CREATION_NAIRU = datetime.datetime(2026, 6, 6, 22, 0)
COMPTES_ADMIN = ["admin_nairu_leny", "admin_nairu_eliott"]
MODELE_GROQ = "llama-3.3-70b-versatile"


# ==============================================================================
# --- 2. GESTION DES MOTS DE PASSE (HASHAGE) ---
# ==============================================================================

def hasher_mot_de_passe(mot_de_passe: str, sel: str | None = None) -> str:
    """Hash un mot de passe avec un sel aléatoire (PBKDF2-SHA256)."""
    if sel is None:
        sel = secrets.token_hex(16)
    empreinte = hashlib.pbkdf2_hmac(
        "sha256", mot_de_passe.encode("utf-8"), sel.encode("utf-8"), 100_000
    )
    return f"{sel}${empreinte.hex()}"


def verifier_mot_de_passe(mot_de_passe: str, hash_stocke: str) -> bool:
    """Vérifie un mot de passe face à son hash stocké (format sel$empreinte)."""
    try:
        sel, _ = hash_stocke.split("$")
    except ValueError:
        return False
    return hasher_mot_de_passe(mot_de_passe, sel) == hash_stocke


# ==============================================================================
# --- 3. ACCÈS AUX DONNÉES (UTILISATEURS & MÉMOIRE) ---
# ==============================================================================

def charger_utilisateurs() -> dict:
    if not os.path.exists(FICHIER_UTILISATEURS):
        base = {"comptes": {}, "banned_ips": [], "maintenance": False, "maintenance_fin": ""}
        sauvegarder_donnees(base)
        return base
    try:
        with open(FICHIER_UTILISATEURS, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"comptes": {}, "banned_ips": [], "maintenance": False, "maintenance_fin": ""}


def sauvegarder_donnees(data: dict) -> None:
    with open(FICHIER_UTILISATEURS, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def sauvegarder_utilisateur(username: str, email: str, mot_de_passe: str, ip: str) -> None:
    data = charger_utilisateurs()
    data["comptes"][username.lower().strip()] = {
        "email": email.strip(),
        "password": hasher_mot_de_passe(mot_de_passe),
        "ip": ip,
    }
    sauvegarder_donnees(data)


def charger_memoire() -> dict:
    if not os.path.exists(FICHIER_MEMOIRE):
        sauvegarder_memoire({})
        return {}
    try:
        with open(FICHIER_MEMOIRE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def sauvegarder_memoire(data: dict) -> None:
    with open(FICHIER_MEMOIRE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# ==============================================================================
# --- 4. UTILITAIRES (IP, RECHERCHE WEB, ÂGE DE NAIRU) ---
# ==============================================================================

def recuperer_ip_visiteur() -> str:
    """
    Récupère l'IP du visiteur.
    Sur Streamlit Cloud, l'IP réelle n'est pas exposée nativement à l'app :
    ce placeholder retourne une valeur fixe. Pour une vraie détection,
    il faut passer par un service tiers (ex: ipify) côté client ou un proxy.
    """
    return "127.0.0.1"


def est_ip_bannie(ip: str) -> bool:
    return ip in charger_utilisateurs().get("banned_ips", [])


def ip_deja_utilisee(ip: str) -> bool:
    data = charger_utilisateurs()
    exceptions = ["admin1", "leny", "eliott"] + COMPTES_ADMIN
    for utilisateur, infos in data["comptes"].items():
        if infos.get("ip") == ip and utilisateur not in exceptions:
            return True
    return False


def executer_recherche_web(requete: str, nb_resultats: int = 3) -> str:
    """Effectue une vraie recherche DuckDuckGo et renvoie un résumé texte."""
    try:
        with DDGS() as ddgs:
            resultats = list(ddgs.text(requete, max_results=nb_resultats))
        if not resultats:
            return "Aucun résultat trouvé."
        return "\n".join(
            f"- {r.get('title', '')} : {r.get('body', '')}" for r in resultats
        )
    except Exception:
        return "Recherche web indisponible pour le moment."


def calculer_age_nairu() -> str:
    try:
        diff = datetime.datetime.now() - DATE_CREATION_NAIRU
        return f"{diff.days} jours, {diff.seconds // 3600} heures"
    except Exception:
        return "quelques semaines"


# ==============================================================================
# --- 5. CONFIGURATION DE LA PAGE ---
# ==============================================================================

st.set_page_config(page_title="NAIRU - AI", page_icon="💬", layout="wide", initial_sidebar_state="collapsed")

components.html(
    """<script>
        var meta = parent.document.createElement('meta');
        meta.name = 'google-site-verification';
        meta.content = 'Ih0SvT8spLCGn5y0eaJnMuFrArHwURmtdDCuNdIEUk8';
        parent.document.getElementsByTagName('head')[0].appendChild(meta);
    </script>""",
    height=0,
)

st.markdown(
    """<style>
    [data-testid="stExpander"] [data-testid="stIconMaterial"] { font-size: 0px !important; color: transparent !important; display: none !important; }
    [data-testid="stExpander"] summary { position: relative !important; }
    [data-testid="stExpander"] summary::after { content: '➔' !important; font-size: 14px !important; color: #00f0ff !important; position: absolute !important; right: 15px !important; }
    </style>""",
    unsafe_allow_html=True,
)

# ==============================================================================
# --- 6. ÉTAT DE SESSION ---
# ==============================================================================

data_maintenance = charger_utilisateurs()

if "mode_maintenance" not in st.session_state:
    st.session_state.mode_maintenance = data_maintenance.get("maintenance", False)
if "statut_connexion" not in st.session_state:
    st.session_state.statut_connexion = "Déconnecté"
if "messages_chat" not in st.session_state:
    st.session_state.messages_chat = []
if "forcer_formulaire_admin" not in st.session_state:
    st.session_state.forcer_formulaire_admin = False

# Fin automatique de la maintenance si le timer est écoulé
if st.session_state.mode_maintenance and data_maintenance.get("maintenance_fin"):
    try:
        if datetime.datetime.now() > datetime.datetime.fromisoformat(data_maintenance["maintenance_fin"]):
            data_maintenance["maintenance"], data_maintenance["maintenance_fin"] = False, ""
            sauvegarder_donnees(data_maintenance)
            st.session_state.mode_maintenance = False
    except (ValueError, TypeError):
        pass

# ==============================================================================
# --- 7. PAGE DE MAINTENANCE ---
# ==============================================================================

if st.session_state.mode_maintenance and st.session_state.statut_connexion == "Déconnecté" and not st.session_state.forcer_formulaire_admin:
    col_gauche, col_centre, col_droite = st.columns([1, 2, 1])
    with col_centre:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.error("### 🛠️ Site temporairement indisponible")
        st.info("Nairu AI est actuellement en cours de maintenance ou de mise à jour.")

        if data_maintenance.get("maintenance_fin"):
            try:
                restant = datetime.datetime.fromisoformat(data_maintenance["maintenance_fin"]) - datetime.datetime.now()
                minutes_restantes = max(0, int(restant.total_seconds() // 60))
                if minutes_restantes > 0:
                    st.warning(f"⏳ **Remise en place prévue dans environ :** {minutes_restantes} minute(s).")
                else:
                    st.warning("⏳ **Remise en place imminente...**")
            except (ValueError, TypeError):
                pass

        st.write("Si vous avez besoin d'un accès ou pour toute question, merci de contacter **Eliott** :")
        st.link_button("📸 Contacter Eliott sur Instagram", "https://instagram.com/eliott31tls", use_container_width=True)
        st.markdown("<br><br><hr>", unsafe_allow_html=True)

        if st.button("🔒 Connexion Administrateur"):
            st.session_state.forcer_formulaire_admin = True
            st.rerun()
    st.stop()

# ==============================================================================
# --- 8. CONNEXION / INSCRIPTION ---
# ==============================================================================

elif st.session_state.statut_connexion == "Déconnecté":
    st.title("Bienvenue sur Nairu")
    col_gauche, col_centre, col_droite = st.columns([1, 2, 1])

    with col_centre:
        with st.container(border=True):
            if st.session_state.forcer_formulaire_admin:
                st.warning("⚠️ Mode Maintenance Actif")

            tab_login, tab_register = st.tabs(["🔒 Connexion", "✨ Créer un compte"])

            # --- Connexion ---
            with tab_login:
                st.markdown("### Connexion")
                with st.form(key="form_connexion"):
                    identifiant = st.text_input("Identifiant ou Prénom :", key="login_username").strip().lower()
                    code_secret = st.text_input("Code secret :", type="password", key="login_password")

                    if st.form_submit_button("Se connecter", use_container_width=True):
                        user_ip = recuperer_ip_visiteur()
                        data_totale = charger_utilisateurs()
                        compte = data_totale["comptes"].get(identifiant)

                        if est_ip_bannie(user_ip):
                            st.error("❌ Accès refusé. IP bannie.")
                        elif compte and verifier_mot_de_passe(code_secret, compte["password"]):
                            if st.session_state.mode_maintenance and identifiant not in COMPTES_ADMIN:
                                st.error("🛑 Ce site est en maintenance.")
                            else:
                                st.session_state.statut_connexion = "Connecté"
                                st.session_state.user_connecte = identifiant
                                st.session_state.forcer_formulaire_admin = False
                                st.rerun()
                        else:
                            st.error("Identifiant ou mot de passe incorrect.")

            # --- Inscription ---
            with tab_register:
                st.markdown("### Créer un compte")
                if st.session_state.mode_maintenance:
                    st.error("❌ Les inscriptions sont fermées.")
                else:
                    st.markdown("> *Système anti-spam : Une seule création de compte par IP.*")
                    with st.form(key="form_inscription"):
                        nouvel_identifiant = st.text_input("Choisis un identifiant :", key="reg_username")
                        nouvel_email = st.text_input("Adresse Email :", placeholder="votre@email.com", key="reg_email")
                        nouveau_code = st.text_input("Choisis un code secret :", type="password", key="reg_password")

                        if st.form_submit_button("Créer mon compte", use_container_width=True):
                            data_totale = charger_utilisateurs()
                            user_ip = recuperer_ip_visiteur()

                            if est_ip_bannie(user_ip):
                                st.error("❌ Connexion bannie.")
                            elif nouvel_identifiant.strip() == "" or nouveau_code.strip() == "":
                                st.warning("Champs vides.")
                            elif nouvel_identifiant.lower().strip() in data_totale["comptes"]:
                                st.error("Cet identifiant existe déjà !")
                            elif ip_deja_utilisee(user_ip):
                                st.error("❌ Un compte a déjà été créé.")
                            else:
                                sauvegarder_utilisateur(nouvel_identifiant, nouvel_email, nouveau_code, user_ip)
                                st.success("🎉 Compte créé ! Connectez-vous.")

        if st.session_state.forcer_formulaire_admin and st.button("⬅️ Retour"):
            st.session_state.forcer_formulaire_admin = False
            st.rerun()

# ==============================================================================
# --- 9. INTERFACE UNE FOIS CONNECTÉ ---
# ==============================================================================

else:
    user_actuel = str(st.session_state.user_connecte).lower().strip()

    # Clé API récupérée depuis les secrets Streamlit (jamais en dur dans le code)
    if "groq_api_key" not in st.session_state:
        st.session_state.groq_api_key = st.secrets.get("GROQ_API_KEY", "")

    if not st.session_state.groq_api_key:
        st.error("⚠️ Clé API Groq manquante. Configurez `GROQ_API_KEY` dans les secrets Streamlit.")
        st.stop()

    # --- Panneau Administrateur ---
    if user_actuel in COMPTES_ADMIN:
        with st.sidebar:
            st.markdown("### 🛠️ Mode Administrateur")
            st.info(f"Connecté : {st.session_state.user_connecte}")
            st.markdown("---")
            st.markdown("#### ⚙️ Maintenance")

            etat_maintenance = st.checkbox("Activer la maintenance", value=st.session_state.mode_maintenance)
            if etat_maintenance != st.session_state.mode_maintenance:
                data_totale = charger_utilisateurs()
                data_totale["maintenance"] = etat_maintenance
                if not etat_maintenance:
                    data_totale["maintenance_fin"] = ""
                sauvegarder_donnees(data_totale)
                st.session_state.mode_maintenance = etat_maintenance
                st.rerun()

            if st.session_state.mode_maintenance:
                st.warning("⚠️ Mode maintenance actif.")
                duree_minutes = st.number_input("Durée (minutes) :", min_value=1, max_value=1440, value=30)
                if st.button("⏱️ Activer le Timer", use_container_width=True):
                    data_totale = charger_utilisateurs()
                    heure_fin = datetime.datetime.now() + datetime.timedelta(minutes=duree_minutes)
                    data_totale["maintenance_fin"] = heure_fin.isoformat()
                    sauvegarder_donnees(data_totale)
                    st.rerun()

            st.markdown("---")

            if st.checkbox("Voir la gestion des comptes"):
                data_totale = charger_utilisateurs()
                st.markdown("#### 👥 Modération")
                comptes_proteges = COMPTES_ADMIN + ["leny", "eliott", "exemple"]

                for nom, infos in list(data_totale["comptes"].items()):
                    if nom in comptes_proteges:
                        continue
                    st.markdown(f"**Identifiant :** `{nom}`")
                    st.caption(f"IP : {infos.get('ip', '0.0')} | Email : {infos.get('email', 'N/A')}")

                    c_ban, c_del = st.columns(2)
                    with c_ban:
                        if st.button("🚫 Ban", key=f"b_{nom}", use_container_width=True):
                            ip_a_bannir = infos.get("ip")
                            if ip_a_bannir and ip_a_bannir not in data_totale["banned_ips"]:
                                data_totale["banned_ips"].append(ip_a_bannir)
                            del data_totale["comptes"][nom]
                            sauvegarder_donnees(data_totale)
                            st.rerun()
                    with c_del:
                        if st.button("🗑️ Suppr", key=f"d_{nom}", use_container_width=True):
                            del data_totale["comptes"][nom]
                            sauvegarder_donnees(data_totale)
                            st.rerun()
                    st.markdown("---")

    # --- Zone de chat ---
    st.markdown(f"### 🤖 Nairu IA — Session de **{st.session_state.user_connecte}**")

    for msg in st.session_state.messages_chat:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    prompt = st.chat_input("Posez votre question à Nairu...")
    if prompt:
        with st.chat_message("user"):
            st.write(prompt)
        st.session_state.messages_chat.append({"role": "user", "content": prompt})

        try:
            client_groq = Groq(api_key=st.session_state.groq_api_key)
            with st.chat_message("assistant"):
                with st.spinner("Nairu réfléchit..."):
                    contexte_web = executer_recherche_web(prompt)
                    nom_utilisateur = st.session_state.user_connecte.capitalize()
                    memoire = charger_memoire()
                    souvenirs = memoire.get(user_actuel, [])
                    contexte_memoire = " | ".join(souvenirs) if souvenirs else "Aucun souvenir"

                    instructions_systeme = (
                        f"Tu es Nairu, assistant IA créé par Leny et Eliott le 6 juin 2026. "
                        f"Âge : {calculer_age_nairu()}. Tu parles avec {nom_utilisateur}. "
                        f"Souvenirs de l'utilisateur : {contexte_memoire}. "
                        f"Infos web : {contexte_web}. "
                        f"Reste amical, synthétique et moderne."
                    )

                    historique_complet = (
                        [{"role": "system", "content": instructions_systeme}] + st.session_state.messages_chat
                    )
                    reponse = client_groq.chat.completions.create(model=MODELE_GROQ, messages=historique_complet)
                    texte_reponse = reponse.choices[0].message.content
                    st.write(texte_reponse)

            st.session_state.messages_chat.append({"role": "assistant", "content": texte_reponse})
            st.rerun()

        except Exception as e:
            st.error(f"❌ Erreur Groq : {str(e)}")

    st.markdown("<br><hr>", unsafe_allow_html=True)
    if st.button("🔴 Déconnexion", use_container_width=True):
        st.session_state.statut_connexion = "Déconnecté"
        st.session_state.user_connecte = None
        st.session_state.messages_chat = []
        st.rerun()

    # ==========================================================================
    # --- 10. MÉMOIRE À LONG TERME ---
    # ==========================================================================

    memoire = charger_memoire()
    if user_actuel not in memoire:
        memoire[user_actuel] = []
        sauvegarder_memoire(memoire)

    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.markdown("### 🧠 Mémoire à long terme de Nairu")
    c_m_inf, c_m_act = st.columns([2, 1])

    with c_m_inf:
        st.write("Ce que Nairu sait sur vous :")
        if not memoire[user_actuel]:
            st.info("💡 Rien pour l'instant.")
        else:
            for i, souvenir in enumerate(memoire[user_actuel]):
                ct, cd = st.columns([5, 1])
                ct.markdown(f"• {souvenir}")
                if cd.button("🗑️", key=f"dm_{user_actuel}_{i}"):
                    memoire[user_actuel].pop(i)
                    sauvegarder_memoire(memoire)
                    st.rerun()

    with c_m_act:
        with st.form(key=f"fa_{user_actuel}", clear_on_submit=True):
            nouveau_fait = st.text_input("Ajouter un fait à retenir :", placeholder="Ex: J'adore l'automobile")
            if st.form_submit_button("Enregistrer", use_container_width=True) and nouveau_fait.strip() != "":
                memoire[user_actuel].append(nouveau_fait.strip())
                sauvegarder_memoire(memoire)
                st.rerun()

# ==============================================================================
# --- 11. PIED DE PAGE GLOBAL ---
# ==============================================================================

st.markdown(
    "<p style='text-align: center; color: gray; font-size: 14px; margin-top: 50px;'>"
    "© 2026 Nairu AI — Créée par Eliott et Leny.</p>",
    unsafe_allow_html=True,
)
