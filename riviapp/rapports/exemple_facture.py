import io
from django.http import FileResponse, HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from riviapp.models import Reservation, Categorie

def generate_invoice(request, reservation_id):
    # Récupérer les détails de la réservation depuis la base de données
    reservation = Reservation.objects.get(id=reservation_id)
    categories = Categorie.objects.all()

    # Créer un buffer pour recevoir les données du PDF
    buffer = io.BytesIO()

    # ----------------------------------------------------------------------------------
    # Créer l'objet PDF en utilisant le buffer comme "fichier"
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    # Ajouter des détails de la facture
    elements.append(Table([
        [f"Facture pour {reservation.client.nom}"],
        [f"Date: {reservation.datejr}"],
        [f"Réservation ID: {reservation.id}"]
    ]))

    # Ajouter les chambres de la réservation dans un tableau
    data = [["Chambre", "Type", "Prix (USD)"]]
    for categorie in categories:
        data.append([categorie.id, categorie.designation, categorie.prix])

    # Ajouter le total
    total = sum(categorie.prix for categorie in categories)
    data.append(["", "Total", total])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)

    # Construire le PDF
    doc.build(elements)
    # --------------------------

    # Revenir au début du buffer
    buffer.seek(0)
    
    # Retourner le PDF comme réponse POUR LE TELECHARGER AUTOMATIQUEMENT
    # return FileResponse(buffer, as_attachment=True, filename='facture_rsv.pdf') 

    # Retourner le PDF comme réponse HTTP POUR L'AFFICHER D'ABORD DANS LE NAVIGATEUR
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="facture_rsv.pdf"'
    return response
