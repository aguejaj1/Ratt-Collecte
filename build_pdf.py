"""Génère le rapport PDF final (3 pages) avec ReportLab."""
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image, PageBreak, PageTemplate, Paragraph,
    Spacer, Table, TableStyle,
)

ROOT = Path(__file__).parent
USERS = json.loads((ROOT / "data_source.json").read_text(encoding="utf-8"))["users"]
NAVY = colors.HexColor("#1F4E79")
MUTED = colors.HexColor("#595959")


def decorate(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5); canvas.setFillColor(MUTED)
    canvas.drawRightString(7.5 * inch, 10.55 * inch, "COLLECTE ET EXPLORATION DES DONNÉES  |  MINI-PROJET")
    canvas.drawRightString(7.5 * inch, 0.45 * inch, f"Page {doc.page}")
    canvas.restoreState()


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TitleBlue", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=24, leading=27, textColor=NAVY, alignment=TA_LEFT, spaceAfter=6))
styles.add(ParagraphStyle(name="Subtitle", parent=styles["Normal"], fontName="Helvetica", fontSize=14, leading=18, textColor=MUTED, spaceAfter=18))
styles.add(ParagraphStyle(name="H1Blue", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=15, leading=18, textColor=NAVY, spaceBefore=10, spaceAfter=7))
styles.add(ParagraphStyle(name="H2Blue", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=NAVY, spaceBefore=7, spaceAfter=5))
styles.add(ParagraphStyle(name="BodyFr", parent=styles["BodyText"], fontName="Helvetica", fontSize=10, leading=13, spaceAfter=7))
styles.add(ParagraphStyle(name="CaptionFr", parent=styles["BodyText"], fontName="Helvetica-Oblique", fontSize=8, leading=10, textColor=MUTED, alignment=TA_CENTER, spaceAfter=7))


def P(text, style="BodyFr"):
    return Paragraph(text, styles[style])


def build():
    doc = BaseDocTemplate(str(ROOT / "rapport.pdf"), pagesize=letter, leftMargin=inch, rightMargin=inch, topMargin=0.85*inch, bottomMargin=0.7*inch, title="Mini-projet - Collecte et exploration des données", author="[Nom et prénom]")
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    doc.addPageTemplates([PageTemplate(id="all", frames=frame, onPage=decorate)])
    story = []

    story += [Spacer(1, 0.18*inch), P("RAPPORT DE MINI-PROJET", "TitleBlue"), P("Pipeline de données des utilisateurs JSONPlaceholder", "Subtitle")]
    story += [P("<b>Étudiant(e) :</b> [Nom et prénom] &nbsp;&nbsp;|&nbsp;&nbsp; <b>Année universitaire :</b> 2025-2026")]
    story += [P("1. Présentation du travail", "H1Blue")]
    story += [P("Ce mini-projet met en œuvre un pipeline complet de collecte, stockage et exploration. Le script Python interroge l’API JSONPlaceholder, extrait les dix utilisateurs et charge leurs informations dans une base PostgreSQL. Le notebook Jupyter exécute ensuite les requêtes SQL demandées, analyse les extensions d’e-mail et construit une carte interactive.")]
    story += [P("2. Pipeline et modèle de données", "H1Blue")]
    story += [P("Le chargement utilise un <i>upsert</i> PostgreSQL : une seconde exécution met à jour les lignes existantes au lieu de créer des doublons. La table <b>utilisateurs</b> comporte id (clé primaire), nom, email et ville. Les colonnes latitude et longitude ont été ajoutées pour conserver les coordonnées <i>address.geo</i> nécessaires à la carte.")]
    story += [P("Étapes réalisées", "H2Blue")]
    for t in ["Extraction HTTP des données JSON et validation du nombre de lignes.", "Transformation des champs imbriqués address.city et address.geo.", "Création de la table puis insertion idempotente des dix enregistrements.", "Connexion du notebook à PostgreSQL, analyses SQL et visualisations."]:
        story.append(P("• " + t))

    story.append(PageBreak())
    story += [P("3. Vérification de la base PostgreSQL", "H1Blue"), P("La capture ci-dessous présente les quatre champs demandés pour les dix lignes enregistrées. Elle est produite directement depuis une requête SELECT du notebook.")]
    img = Image(str(ROOT / "table_sql.png"), width=6.45*inch, height=2.78*inch)
    story += [img, P("Figure 1 — Table utilisateurs remplie dans PostgreSQL.", "CaptionFr")]
    story += [P("4. Résultats des requêtes SQL", "H1Blue"), P("La requête <b>COUNT(*)</b> retourne <b>10 utilisateurs</b>. Le filtrage par suffixe retourne quatre lignes :")]
    selected = [u for u in USERS if u["email"].lower().endswith((".net", ".biz"))]
    rows = [[P("<b>Nom</b>"), P("<b>E-mail</b>"), P("<b>Suffixe</b>")]] + [[P(u["name"]), P(u["email"]), P("."+u["email"].split(".")[-1].lower())] for u in selected]
    table = Table(rows, colWidths=[2*inch, 3.1*inch, 1.4*inch], repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#D9EAF7")),("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#AAB7C4")),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
    story += [table, P("Tableau 1 — Utilisateurs dont l’e-mail se termine par .net ou .biz.", "CaptionFr")]

    story.append(PageBreak())
    story += [P("5. Visualisations et interprétation", "H1Blue")]
    story += [Image(str(ROOT / "extensions_email.png"), width=5.4*inch, height=3.04*inch), P("Figure 2 — Répartition des utilisateurs par extension d’adresse e-mail.", "CaptionFr")]
    story += [P("<b>Lecture :</b> l’extension .biz domine avec 3 utilisateurs. Les sept autres extensions n’apparaissent qu’une fois chacune ; .net compte 1 utilisateur.")]
    story += [Image(str(ROOT / "map_preview.png"), width=5.55*inch, height=2.44*inch), P("Figure 3 — Aperçu statique des 10 marqueurs de la carte Folium interactive.", "CaptionFr")]
    story += [P("<b>Lecture :</b> les coordonnées de démonstration sont très dispersées. Dans <i>map_utilisateurs.html</i> et dans le notebook, chaque marqueur affiche le nom et la ville au survol ou au clic. Ces positions fictives ne représentent pas des domiciles réels.")]
    doc.build(story)
    print("rapport.pdf créé")


if __name__ == "__main__":
    build()
