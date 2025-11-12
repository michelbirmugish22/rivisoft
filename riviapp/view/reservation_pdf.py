from django.http import HttpResponse
import io 
from riviapp.models import Client, Categorie, Reservation, Paiement
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image
from reportlab.lib.colors import red, white, black
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT

def index(req):
    nom_cli = Client.objects.get(id=int(req.POST['id_cli'])).nom + " " + Client.objects.get(id=int(req.POST['id_cli'])).postnom
    Reservation(
        mode = req.POST['mode'],
        prixvalide = req.POST['prix'],
        datearrivee = req.POST['date1'],
        datesortie = req.POST['date2'],
        nbadultes = req.POST['nbadulte'],
        nbenfants = req.POST['nbenfant'],
        nbchambre = req.POST['nbchamb'],
        autresinfos = req.POST['autre_info'],
        etat_rsv = 'Encours',
        client = Client.objects.get(id=req.POST['id_cli']),
        categorie = Categorie.objects.get(id=req.POST['id_cat'])
    ).save()
    if req.POST['montant']:
        difference = Reservation.objects.last().datesortie-Reservation.objects.last().datearrivee
        total_du = Reservation.objects.last().prixvalide * Reservation.objects.last().nbchambre * abs(difference.days)
        Paiement(
            montant = req.POST['montant'],
            mode = "Cash", #M-Pesa, Airtel money, Visa ou Cash
            libelle = "Avance réservation effectuée par "+ Client.objects.get(id=req.POST['id_cli']).nom,
            reste = float(total_du)-float(req.POST['montant']),
            reservation = Reservation.objects.last()
        ).save()
        print(f"Avance réservation effectuée par {Client.objects.get(id=req.POST['id_cli']).nom}")
    objs_dicts = {"obj": {}}
    for rsv in Reservation.objects.filter(etat_rsv='Encours'):
        objs_dicts["obj"][str(rsv.id)] = {
            'id':rsv.id,
            'prixvalide':rsv.prixvalide,
            'datearrivee':rsv.datearrivee,
            'datesortie':rsv.datesortie,
            'client':rsv.client.nom,
            'categorie':rsv.categorie.designation,
        }
    #=====================================================================================================================
    #SORTIE EN PDF =======================================================================================================
    #=====================================================================================================================
    arial14bold = ParagraphStyle('arial12bold',fontName='Helvetica-Bold',fontSize=14, alignment=TA_CENTER)
    arial12 = ParagraphStyle('arial12',fontName='Helvetica',fontSize=12, alignment=TA_JUSTIFY, spaceAfter=10)
    arial12italic = ParagraphStyle('arial12italic',fontName='Times-Italic',fontSize=12, alignment=TA_JUSTIFY)
    arial12bold = ParagraphStyle('arial12italic',fontName='Times-Bold',fontSize=12)
    ligne = ParagraphStyle('ligne_vide',spaceBefore=10,spaceAfter=10)

    rsv = Reservation.objects.last()
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)
    page = []
    W,H = A4
    page.append(Image('media\images\logo_hnr_gerance.png',W-140, 100))
    page.append(Paragraph("CONFIRMATION DE LA RESERVATION", arial14bold))
    page.append(Paragraph("",ligne))
    page.append(Paragraph(f'''Cher Monsieur/Madame {rsv.client.nom} {rsv.client.postnom},''', arial12))
    page.append(Paragraph("Au travers cette lettre, récevez des salutations de la part de l'Hôtel New Riviera Bukavu. Nous vous remercions de nous avoir choisi",arial12))
    page.append(Paragraph("",ligne))
    page.append(Paragraph("Nous sommes très émus de confirmer les informations suivantes : ",arial12))
    page.append(Paragraph(f'''Noms du client : <b>{rsv.client.nom} {rsv.client.postnom}</b>''', arial12))
    page.append(Paragraph(f'''Nombre des chambres réservées :<b> {rsv.nbchambre}</b>''', arial12))
    page.append(Paragraph(f'''Nombre des personnes attendues : <b>{rsv.nbadultes} ADULTES et {rsv.nbenfants} ENFANTS</b>''', arial12))
    page.append(Paragraph(f'''Types de chambre :<b> {rsv.categorie.designation}</b>''', arial12))
    page.append(Paragraph(f'''Date d'arrivée :<b> {rsv.datearrivee}</b>''', arial12))
    page.append(Paragraph(f'''Date de sortie :<b> {rsv.datesortie}</b>''', arial12))
    page.append(Paragraph(f'''Numéro de confirmation :<b> {rsv.id}</b>''', arial12))
    page.append(Paragraph(f'''Prix convenu :<b> {rsv.prixvalide}</b>''', arial12))
    page.append(Paragraph(f'''Somme payé en avance :<b> {Paiement.objects.get(reservation=rsv).montant}</b>''', arial12))
    page.append(Paragraph("-----------------------------------------------------------------------------------------------------------------------------------", ligne))
    page.append(Paragraph(f"Les tarifs ci-haut comprennent le petit déjeuner. Les check-in et check-out se font à 14h, heure de Bukavu (GMT+2). Veuillez utiliser votre numéro de reservation de chambre [<b>{rsv.id}</b>]. ", arial12))
    page.append(Paragraph("Politique d'Annulation",arial12bold))
    page.append(Paragraph("L'avis d'annulation et de modification doit être fourni 48h avant l'arrivée. En cas d'annulation ou de modification dans les 48 heures suivant la date d'arrivée, la valeur de d'une chambre sera majorée.",arial12italic))
    page.append(Paragraph("Les Taxes gouvernementales connexes sont succeptibles d'être modifiées sans préavis.",arial12italic))
    page.append(Paragraph("Nous sommes impatients de vous accueillir à l'Hôtel New Riviera Bukavu.", arial12italic))
    page.append(Paragraph("Pour plus des préoccupations, n'hésitez pas à nous contacter.", arial12italic))
    page.append(Paragraph("", ligne))
    page.append(Paragraph("Coordialement,", arial12))
    page.append(Paragraph(f"{req.user}", arial12bold))
    page.append(Paragraph(f"Réceptionniste, HOTEL NEW RIVIERA", arial12))
    pdf.build(page)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='Application/pdf')
    response['Content-Disposition'] = 'inline;filename="Reservation.pdf"'
    return response
