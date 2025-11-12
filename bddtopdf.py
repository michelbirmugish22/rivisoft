import pdfkit
from jinja2 import Environment, FileSystemLoader
import sqlite3

# Connexion à la base de données
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Récupération des données
cursor.execute("SELECT * FROM 'riviapp_personne'")
data = cursor.fetchall()

# Configuration de Jinja2
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('template.html')

# Rendu du template avec les données
html_content = template.render(data=data)

# Sauvegarde du contenu HTML dans un fichier
with open('output.html', 'w') as file:
    file.write(html_content)

# Configuration de pdfkit
config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')

# Conversion du fichier HTML en PDF
pdfkit.from_file('output.html', 'output.pdf', configuration=config)
