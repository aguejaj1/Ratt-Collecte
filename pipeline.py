"""Extraction JSONPlaceholder -> PostgreSQL.

Le script est idempotent : les utilisateurs existants sont mis à jour.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import psycopg2
import requests
from psycopg2.extras import execute_values

API_URL = os.getenv("API_URL", "https://jsonplaceholder.typicode.com/users")
SNAPSHOT = Path(__file__).with_name("data_source.json")


def extraire_utilisateurs() -> list[dict]:
    """Télécharge les 10 utilisateurs, avec une copie locale de secours."""
    try:
        response = requests.get(API_URL, timeout=20)
        response.raise_for_status()
        utilisateurs = response.json()
        source = API_URL
    except requests.RequestException as exc:
        if not SNAPSHOT.exists():
            raise RuntimeError(f"API inaccessible et snapshot absent : {exc}") from exc
        contenu = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        utilisateurs = contenu.get("users", contenu)
        source = f"snapshot local ({SNAPSHOT.name})"

    if len(utilisateurs) != 10:
        raise ValueError(f"10 utilisateurs attendus, {len(utilisateurs)} reçus")
    print(f"Extraction réussie : {len(utilisateurs)} utilisateurs depuis {source}.")
    return utilisateurs


def connexion_postgresql():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "55432")),
        dbname=os.getenv("DB_NAME", "collecte"),
        user=os.getenv("DB_USER", "collecte"),
        password=os.getenv("DB_PASSWORD", "collecte"),
    )


def charger_utilisateurs(utilisateurs: list[dict]) -> None:
    lignes = [
        (
            u["id"],
            u["name"],
            u["email"],
            u["address"]["city"],
            float(u["address"]["geo"]["lat"]),
            float(u["address"]["geo"]["lng"]),
        )
        for u in utilisateurs
    ]

    with connexion_postgresql() as connexion, connexion.cursor() as curseur:
        curseur.execute(
            """
            CREATE TABLE IF NOT EXISTS utilisateurs (
                id INTEGER PRIMARY KEY,
                nom VARCHAR(120) NOT NULL,
                email VARCHAR(180) NOT NULL,
                ville VARCHAR(120) NOT NULL,
                latitude DOUBLE PRECISION NOT NULL,
                longitude DOUBLE PRECISION NOT NULL
            )
            """
        )
        execute_values(
            curseur,
            """
            INSERT INTO utilisateurs (id, nom, email, ville, latitude, longitude)
            VALUES %s
            ON CONFLICT (id) DO UPDATE SET
                nom = EXCLUDED.nom,
                email = EXCLUDED.email,
                ville = EXCLUDED.ville,
                latitude = EXCLUDED.latitude,
                longitude = EXCLUDED.longitude
            """,
            lignes,
        )
    print("Chargement PostgreSQL terminé (upsert).")


def main() -> int:
    try:
        charger_utilisateurs(extraire_utilisateurs())
        return 0
    except Exception as exc:  # message court et code d'échec pour l'automatisation
        print(f"Erreur du pipeline : {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
