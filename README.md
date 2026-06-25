# Mini-projet — Collecte et exploration des données

Pipeline Python et notebook Jupyter utilisant les 10 utilisateurs de JSONPlaceholder et PostgreSQL.

## Exécution

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
docker compose up -d
python pipeline.py
jupyter notebook analyse.ipynb
```

Le conteneur PostgreSQL écoute sur le port local `55432` afin d'éviter les conflits avec une installation PostgreSQL existante.

La table `utilisateurs` contient les quatre champs demandés (`id`, `nom`, `email`, `ville`) ainsi que `latitude` et `longitude`, nécessaires à la carte.

Le pipeline effectue un *upsert* : il peut être relancé sans créer de doublons. Il interroge d’abord l’API demandée et utilise `data_source.json`, copie du dépôt officiel JSONPlaceholder, uniquement si l’API est temporairement indisponible.

## Fichiers produits

- `pipeline.py` : extraction et insertion PostgreSQL ;
- `analyse.ipynb` : requêtes SQL, graphique et carte Folium ;
- `map_utilisateurs.html` : carte interactive exportée ;
- `rapport.pdf` : synthèse de 3 pages ;
- `rapport.docx` : source modifiable du rapport.
