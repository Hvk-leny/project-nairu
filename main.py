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
            f"- {r.get('title', '')} : {r.get('body', '')}" f
