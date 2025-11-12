from django.http import HttpResponse
import io 
from riviapp.models import *
from riviapp.rapports.classe_rp.classes_personnalisees import CustomCanvas
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image
from reportlab.lib.colors import *
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from num2words import num2words
from datetime import datetime, time
from django.utils import timezone

def index(req):

    
    # difference = datetime.date(req.POST['date2']) - datetime.date(req.POST['date1'])
    date_format = "%Y-%m-%d"  # Format de la date attendu (AAAA-MM-JJ)
    date1 = datetime.now()
    date2 = datetime.strptime(req.POST['date2'], "%Y-%m-%d").date()
    date2 = datetime.combine(date2, time.max)      #ex: 2024-12-31 23:59:59
    difference = date2 - date1
    
    timezone_locale = timezone.now().astimezone(timezone.get_current_timezone())
    print(f"La timezone locale est de : {timezone_locale}")
    ci=Enregistrer(
        datearr = date1,
        datesor = date2,
        provenance = req.POST['provenance'],
        destination = req.POST['destination'],
        prixnuitee= req.POST['prixnuitee'],
        avance= req.POST['avance'],
        nbpax=req.POST['nbpax'],
        nbjrs=difference.days,
        client = Client.objects.get(id=req.POST['id_cli']),
        entreprise = Entreprise.objects.get(id=req.POST['id_ese']),
        chambre = Chambre.objects.get(id=req.POST['id_chambre']),
    )
    piece=Piece_indentite(
        designation = req.POST['designation_piece'],
        numero = req.POST['numero_piece'],
        date_livre = req.POST['date_livre_piece'],
        date_expire = req.POST['date_expire_piece'],
        lieu_livre = req.POST['lieu_livre_piece'],
        client = Client.objects.get(id=req.POST['id_cli']),
    )
    cha=Chambre.objects.get(id=req.POST['id_chambre'])
    if cha.statut == 'Libre':
        ci.save()
        piece.save()
        cha.statut = 'Occupee'
        cha.save()
        if req.POST['avance'] and int(req.POST['avance']) > 0:
            difference = Enregistrer.objects.last().datesor-Enregistrer.objects.last().datearr
            total_du = Enregistrer.objects.last().prixnuitee * abs(difference.days)
            Paiement(
                montant = req.POST['avance'],
                mode = Operateur.objects.filter(p_caisse=1).first(), #M-Pesa, Airtel money, Visa ou Cash
                libelle = "Avance checkin chambre "+ Chambre.objects.get(id=req.POST['id_chambre']).numero + ", client : " + Client.objects.get(id=req.POST['id_cli']).nom,
                reste = float(total_du)-float(req.POST['avance']),
                occupation = Enregistrer.objects.last()
            ).save()
    # Récupération et conversion pour l'affichage
    print(ci)
    if ci.id is not None:
        enregistrement = Enregistrer.objects.get(id=ci.id)
        datejr_local = enregistrement.datejr.astimezone(timezone.get_current_timezone())
        print(f"Date locale enregistré est de : {datejr_local}")
    
    #=====================================================================================================================
    #SORTIE EN PDF =======================================================================================================
    #=====================================================================================================================
    arial14bold = ParagraphStyle('arial12bold',fontName='Helvetica-Bold',fontSize=14, alignment=TA_CENTER)
    arial12 = ParagraphStyle('arial12',fontName='Helvetica',fontSize=11, alignment=TA_JUSTIFY, spaceAfter=10)
    times10italic = ParagraphStyle('arial12italic',fontName='Times-Italic',fontSize=10,alignment=TA_CENTER)
    arial12bold = ParagraphStyle('arial12italic',fontName='Helvetica-Bold',fontSize=12, spaceBefore=10,spaceAfter=10,)
    ligne = ParagraphStyle('ligne_vide',spaceBefore=10,spaceAfter=10,fontSize=11, alignment=TA_CENTER)

    ci = Enregistrer.objects.last()
    piece = Piece_indentite.objects.filter(client_id=ci.client.id).last()
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)
    page = []
    W,H = A4
        
    data = [
        [Paragraph('Nationalité du client'),ci.client.nationalite],
        ['Profession ',ci.client.profession],
        ['Adresse de service ',ci.client.adresse_serv],
        ['Résidence en RDCongo ',ci.client.adresse_rdc],
        ['Date d''arrivée ',ci.datearr.strftime('%d %B %Y')],
        ['Provénance ',ci.provenance],
        ['Déstination ',ci.destination],
        ['Date de sortie ',ci.datesor.strftime('%d %B %Y')],
        ['Lieu et date de naissance ',f"{ci.client.lieu_nais} / {ci.client.date_nais}"],
        ['Nature de la pièce d\'identité ',piece.designation],
        ['Numéro de la pièce d\'identité ',piece.numero],
        ['Date de livraison et d''expiration',f"{piece.date_livre} - {piece.date_expire}"],
        ['Lieu de livraison ',piece.lieu_livre],
    ]
    tab = Table(data)
    
    tab.setStyle(TableStyle([
        ('FONTSIZE', (0,0),(-1,-1),11),
        ('GRID',(0,0),(-1,-1),.05,black),
        ('TEXTCOLOR',(1,0),(1,-1),blue),
        ('FONTNAME',(1,0),(1,-1),'Times-Italic'),
    ]))
        
    page.append(Image('media\images\logo_hnr_gerance.png',W-140, 100))
    page.append(Paragraph(f"BULLETIN DE LOGEMENT N°{ci.datejr.strftime('%Y')}/{ci.datejr.strftime('%d')}{hex(ci.id).upper()}-{ci.datejr.strftime('%m')}", arial14bold))
    page.append(Paragraph("",ligne))
    page.append(Paragraph("I. Informations principales ",arial12bold))
    diff_jrs = Enregistrer.objects.last().datesor-Enregistrer.objects.last().datearr
    bold = ParagraphStyle('bold', fontName='Helvetica-Bold',fontSize=10)
    t=Table([
        ["NOM DU CLIENT ",f": {ci.client.nom} ","POST NOM",f": {ci.client.postnom}","ORGANISATION",f": {ci.entreprise.nom}"],
        ["CHAMBRE ",Paragraph(f": {ci.chambre.numero}",bold),"CATEGORIE ",f": {ci.chambre.categorie.designation}","BLOC",f": {ci.chambre.bloc.designation}"],
        ["NB NUITEES ",f": {diff_jrs.days} jour(s)","PRIX UNIT ",f": {ci.prixnuitee} USD","AVANCE : ",f": {ci.avance} USD"],
    ])
    t.setStyle(TableStyle([
        ('FONTNAME',(1,0),(1,-1),'Helvetica-Bold'),
        ('FONTNAME',(3,0),(3,-1),'Helvetica-Bold'),
        ('FONTNAME',(5,0),(5,-1),'Helvetica-Bold'),
    ]))
    page.append(t)

    page.append(Paragraph("II. Autres Informations ",arial12bold))
    page.append(tab)
    page.append(Paragraph("III. Note importante ",arial12bold))
    page.append(Paragraph(f"Nous, HOTEL NEW RIVIERA, attestons avoir réçu Monsieur {ci.client.nom} {ci.client.postnom} en provénance de {ci.provenance} pour une durée de {diff_jrs.days} jour(s). Pour cela, nous lui avons logé dans la chambre {ci.chambre.numero} de la catégorie {ci.chambre.categorie.designation} tel qu'il l\'a souhaité.", arial12))
    
    page.append(Paragraph("",ligne));page.append(Paragraph("",ligne));page.append(Paragraph("",ligne))
    page.append(Paragraph(f"Fait à Bukavu le 21/08/2024 ",ligne))
    page.append(Paragraph("",ligne));page.append(Paragraph("",ligne))
    centrer=ParagraphStyle("ce",alignment=TA_CENTER,fontSize=9)
    page.append(Table([
        [Paragraph('Signature du Client',centrer),Paragraph('Signature du réceptionniste',centrer),Paragraph('Signature du Gérant',centrer)],
        ['','',''],
        
    ]))
    
    
    
    pdf.build(page, canvasmaker=CustomCanvas)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='Application/pdf')
    response['Content-Disposition'] = 'inline;filename="Reservation.pdf"'
    return response
