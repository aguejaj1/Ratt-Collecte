"""Construit le notebook demandé de façon déterministe."""
import nbformat as nbf

nb = nbf.v4.new_notebook()
nb.metadata.update({"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}})
cells = []
cells.append(nbf.v4.new_markdown_cell("""# Analyse des utilisateurs JSONPlaceholder

Ce notebook se connecte à PostgreSQL, exécute les requêtes SQL demandées et crée les deux visualisations. Les coordonnées stockées proviennent de `address.geo` dans l'API."""))
cells.append(nbf.v4.new_code_cell("""import os
from pathlib import Path
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import folium
from IPython.display import display

plt.style.use('seaborn-v0_8-whitegrid')
connexion = psycopg2.connect(
    host=os.getenv('DB_HOST', '127.0.0.1'), port=int(os.getenv('DB_PORT', '55432')),
    dbname=os.getenv('DB_NAME', 'collecte'), user=os.getenv('DB_USER', 'collecte'),
    password=os.getenv('DB_PASSWORD', 'collecte')
)
print('Connexion PostgreSQL établie.')"""))
cells.append(nbf.v4.new_markdown_cell("## 1. Nombre total d'utilisateurs"))
cells.append(nbf.v4.new_code_cell("""with connexion.cursor() as curseur:
    curseur.execute('SELECT COUNT(*) FROM utilisateurs')
    total = curseur.fetchone()[0]
print(f"Nombre total d'utilisateurs : {total}")"""))
cells.append(nbf.v4.new_markdown_cell("## 2. Utilisateurs ayant une adresse `.net` ou `.biz`"))
cells.append(nbf.v4.new_code_cell("""requete_domaines = '''
SELECT id, nom, email, ville
FROM utilisateurs
WHERE LOWER(email) LIKE '%.net' OR LOWER(email) LIKE '%.biz'
ORDER BY id
'''
utilisateurs_filtres = pd.read_sql_query(requete_domaines, connexion)
display(utilisateurs_filtres)"""))
cells.append(nbf.v4.new_markdown_cell("## 3. Capture de la table SQL remplie"))
cells.append(nbf.v4.new_code_cell("""utilisateurs = pd.read_sql_query('SELECT * FROM utilisateurs ORDER BY id', connexion)
display(utilisateurs)

fig, ax = plt.subplots(figsize=(12, 4.8))
ax.axis('off')
table = ax.table(cellText=utilisateurs[['id','nom','email','ville']].values,
                 colLabels=['id','nom','email','ville'], loc='center', cellLoc='left')
table.auto_set_font_size(False); table.set_fontsize(8.5); table.scale(1, 1.45)
for (row, col), cell in table.get_celld().items():
    if row == 0:
        cell.set_facecolor('#1F4E78'); cell.set_text_props(color='white', weight='bold')
    elif row % 2 == 0:
        cell.set_facecolor('#EAF1F8')
ax.set_title('Table PostgreSQL : utilisateurs', fontsize=15, weight='bold', pad=15)
plt.tight_layout(); plt.savefig('table_sql.png', dpi=180, bbox_inches='tight'); plt.show()"""))
cells.append(nbf.v4.new_markdown_cell("## 4. Graphique des extensions d'adresses e-mail"))
cells.append(nbf.v4.new_code_cell("""utilisateurs['extension'] = utilisateurs['email'].str.lower().str.extract(r'(\\.[a-z]+)$')
extensions = utilisateurs['extension'].value_counts().sort_values(ascending=False)
display(extensions.rename('nombre'))

fig, ax = plt.subplots(figsize=(8, 4.5))
barres = ax.bar(extensions.index, extensions.values, color='#2E75B6', edgecolor='#17365D')
ax.bar_label(barres, padding=3)
ax.set(title="Nombre d'utilisateurs par extension d'adresse e-mail", xlabel='Extension', ylabel="Nombre d'utilisateurs")
ax.set_ylim(0, max(extensions.values) + 1)
plt.tight_layout(); plt.savefig('extensions_email.png', dpi=180, bbox_inches='tight'); plt.show()"""))
cells.append(nbf.v4.new_markdown_cell("""**Commentaire.** L'extension `.biz` est la plus fréquente (3 utilisateurs). Les sept autres extensions représentées apparaissent une seule fois ; `.net` concerne un utilisateur."""))
cells.append(nbf.v4.new_markdown_cell("## 5. Carte interactive des utilisateurs"))
cells.append(nbf.v4.new_code_cell("""centre = [utilisateurs['latitude'].mean(), utilisateurs['longitude'].mean()]
carte = folium.Map(location=centre, zoom_start=2, tiles='OpenStreetMap')
for ligne in utilisateurs.itertuples():
    folium.Marker(
        [ligne.latitude, ligne.longitude],
        popup=folium.Popup(f'<b>{ligne.nom}</b><br>{ligne.ville}', max_width=250),
        tooltip=f'{ligne.nom} — {ligne.ville}'
    ).add_to(carte)
carte.fit_bounds([[utilisateurs.latitude.min(), utilisateurs.longitude.min()],
                  [utilisateurs.latitude.max(), utilisateurs.longitude.max()]])
carte.save('map_utilisateurs.html')
carte"""))
cells.append(nbf.v4.new_markdown_cell("""**Commentaire.** Les marqueurs sont dispersés sur plusieurs continents. Ces coordonnées sont des données de démonstration de JSONPlaceholder et ne doivent pas être interprétées comme des adresses réelles."""))
cells.append(nbf.v4.new_code_cell("connexion.close(); print('Connexion fermée.')"))
nb['cells'] = cells
nbf.write(nb, 'analyse.ipynb')
print('analyse.ipynb créé')
