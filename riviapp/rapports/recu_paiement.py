import io 
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.platypus import Table, Paragraph, SimpleDocTemplate, Image, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4 
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_RIGHT
from datetime import datetime, timedelta, timezone
from django.utils import timezone
from num2words import num2words
from riviapp.models import * 
from riviapp.rapports.classe_rp.classes_personnalisees import CustomCanvas

def index(req, num):
    style1 = ParagraphStyle("s1",fontName="Helvetica-Bold",fontSize=13, alignment=TA_JUSTIFY)
    style3 = ParagraphStyle("s3",fontName="Helvetica-Oblique",fontSize=9)
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)
    page = []
    large, haut = A4
    
    page.append(Image("media\images\logo_hnr_gerance.png",large-140,90))
    
    recu = Paiement.objects.get(id=num)
    nom_cli = f": {recu.occupation.client.nom} {recu.occupation.client.postnom}"

    tab = Table([
        ["CLIENT",f": {recu.occupation.client.nom} {recu.occupation.client.postnom}","",Paragraph("REçU DE VERSEMENT".upper(),style1)],
        ["ORGANISATION",f": {recu.occupation.entreprise.nom}","","DATE :",f": {datetime.now().strftime("%d / %m / %Y")}"],
        ["Adresse physique",f": {recu.occupation.client.adresse_serv}","","HEURE ",f": {datetime.now().strftime("%H:%M:%S")}"],
        ["Adresse mail",f": {recu.occupation.client.mail}","","NUMERO :",f": {recu.id}/{datetime.now().strftime("%Y")}"],
        ["Téléphone",f": {recu.occupation.client.tel}","","CHAMBRE ",f": #{recu.occupation.chambre.numero}"],
    ])
    tab.setStyle(TableStyle([
        ("SPAN",(-2,0),(-1,0)),
        # ("GRID",(0,0),(-1,-1),.1,colors.red)
    ]))
    page.append(tab)
    page.append(Table([[""]]))
    tab = Table([
        ["Désignation","Mode","Date/Heure","Valeur"],
        [Paragraph(f"{recu.libelle}"),f"{recu.mode}",f"{recu.datejr.strftime("%d/%m/%Y  %H:%M")}",f"{recu.montant} $"],
        [""],
        ["","","TOTAL VERSé".upper(),f"{recu.montant} $"],
        [Paragraph(f"Nous disons : {num2words(recu.montant,lang="fr").capitalize()} dollars américains.",style3)]

    ])
    tab.setStyle(TableStyle([
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("BACKGROUND",(0,0),(-1,0),colors.red),
        ("GRID",(0,0),(-1,0),.5,colors.red),
        ("BACKGROUND",(0,-1),(-1,-2),colors.red),
        ("TEXTCOLOR",(0,-1),(-1,-2),colors.white),
        ("FACE",(0,-2),(-1,-2),"Helvetica-Bold"),
        ("LEADING",(0,-3),(-1,-3),1),
        ("LEADING",(0,-4),(-1,-4),25),
        ("VALIGN",(0,-4),(-1,-4),"TOP"),
        ("ALIGN",(-1,0),(-1,-2),'RIGHT'),
        ("SPAN",(0,-1),(-1,-1)),
    ]))
    page.append(tab)
    page.append(Table([[""],[""]]))
    tab = Table([
        [Paragraph("COORDONNéES BANCAIRES".upper())],
        ["Nom de la Banque","EQUITY BANQUE COMMERCIALE DU CONGO","",Paragraph("Sign. du client",style3)],
        ["Intitulé du compte","HOTEL NEW RIVIERA / GROUPE TAVERNE"],
        ["Numéro de compte","2332 001 001 666 14 "],
        ["IBAN","000 110 502 332 001 001 666 14"],
        ["SWIFT CODE","BCDCCDI"]
    ])
    
    tab.setStyle(TableStyle([
        ("FONTSIZE",(0,0),(-1,-1),8),
        ("LEADING",(0,0),(-1,-1),5),
        ("SPAN",(0,0),(-1,0)),
        ("SPAN",(-1,1),(-1,-1)),
        ("VALIGN",(-1,1),(-1,-1),'TOP'),
        ("GRID",(-1,1),(-1,-1),.1,colors.red),
        ("BACKGROUND",(0,-3),(-2,-2),colors.yellow)
    ]))
    page.append(tab)
    page.append(Table([[""],[""]]))
    page.append(Table([["POUR ACQUIS"],[req.user.username.upper()]]))
    pdf.build(page)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"]=f'inline; filename="reçu_paiement {num}_{nom_cli}_#{recu.occupation.chambre.numero}.pdf"'
    return response
    
    
def historique(req, num):
    style1 = ParagraphStyle("s1",fontName="Helvetica-Bold",fontSize=13, alignment=TA_CENTER)
    style2 = ParagraphStyle("s1",fontName="Helvetica-Oblique",fontSize=10, spaceBefore=5, alignment=TA_JUSTIFY, backColor="#ffe9e9")
    style3 = ParagraphStyle("s3",fontName="Helvetica-Oblique",fontSize=9)
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)
    page = []
    large, haut = A4
    
    page.append(Image("media\images\logo_hnr_gerance.png",large-140,90))
    
    occ = Enregistrer.objects.get(id = num)
    recus = Paiement.objects.filter(occupation_id = num).all()

    tab = Table([
        [Paragraph("HISTORIQUE DES VERSEMENTS".upper(),style1)],
        ["CLIENT",f": {occ.client.nom} {occ.client.postnom}","","DATE :",f": {datetime.now().strftime("%d / %m / %Y")}"],
        ["ORGANISATION",f": {occ.entreprise.nom}","","HEURE ",f": {datetime.now().strftime("%H:%M:%S")}"],
        ["Adresse physique",f": {occ.client.adresse_serv}","","CHAMBRE ",f": #{occ.chambre.numero}"],
        ["Adresse mail",f": {occ.client.mail}","","D. Entrée",f": {occ.datearr.strftime('%d/%m/%Y  %H:%M')}"],
        ["Téléphone",f": {occ.client.tel}","","D. Sortie",f": {occ.datesor.strftime('%d/%m/%Y  %H:%M')}"],
    ])
    tab.setStyle(TableStyle([
        ("SPAN",(0,0),(-1,0)),
        ("ALIGN",(0,0),(-1,0),"CENTER"),
        # ("GRID",(0,0),(-1,-1),.1,colors.red)
    ]))
    page.append(tab)
    page.append(Table([[""]]))
    data = [["Désignation","Mode","Date/Heure","Valeur"],]
    
    j=0;total=0; tot_cash=0; tot_airtel=0; tot_mpesa=0; tot_equity=0
    
    for recu in recus:
        data.append([Paragraph(f"{recu.libelle}"),f"{recu.mode}",f"{recu.datejr.strftime("%d/%m/%Y  %H:%M")}",f"{recu.montant} $"])
        j += 1
        total += recu.montant
        if recu.mode == 'CASH' :
            tot_cash += recu.montant
        elif recu.mode == 'AIRTEL':
            tot_airtel += recu.montant
        elif recu.mode == 'M-PESA':
            tot_mpesa += recu.montant
        elif recu.mode == 'EQUITY':
            tot_equity += recu.montant
        
    data.append([""])
    data.append(["","","TOTAL VERSé".upper(),f"{total} $"])
    data.append([Paragraph(f"Nous disons : {num2words(total,lang="fr").capitalize()} dollars américains.",style3)])
    
    tab = Table(data)
    d=[]
    #Pour colorer le tableau ligne après ligne
    lig=0
    while lig <= j:
        for col in range(5):
            d.append(('BACKGROUND',(col,lig),(-1,lig), "#e9e9e9"))
        lig += 2
    tab.setStyle(TableStyle(d))
        
    tab.setStyle(TableStyle([
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("BACKGROUND",(0,0),(-1,0),colors.red),
        ("GRID",(0,0),(-1,0),.5,colors.red),
        ("BACKGROUND",(0,-1),(-1,-2),colors.red),
        ("TEXTCOLOR",(0,-1),(-1,-2),colors.white),
        ("FACE",(0,-2),(-1,-2),"Helvetica-Bold"),
        ("LEADING",(0,-3),(-1,-3),1),
        ("LEADING",(0,-4),(-1,-4),25),
        ("VALIGN",(0,-4),(-1,-4),"TOP"),
        ("ALIGN",(-1,0),(-1,-2),'RIGHT'),
        ("SPAN",(0,-1),(-1,-1)),
    ]))
    page.append(tab)
    tab = Table([
        ["CASH","AIRTEL MONEY","M-PESA","EQUITY BCDC"],
        [f"{tot_cash} $",f"{tot_airtel} $",f"{tot_mpesa} $",f"{tot_equity} $"]
    ])
    tab.setStyle(TableStyle([
        ('FACE',(0,0),(-1,0),"Helvetica-BoldOblique"),
        ('BACKGROUND',(0,0),(0,-1),"#a8ffe3"),
        ('BACKGROUND',(1,0),(1,-1),"#ffbebe"),
        ('BACKGROUND',(2,0),(2,-1),"#d6ffc2"),
        ('BACKGROUND',(3,0),(3,-1),"#fffdca"),
        ('ALIGN',(0,0),(-1,-1),"CENTER"),
        ('LEADING',(0,0),(-1,-1),10),
    ]))
    page.append(tab)
    dette = (occ.nbjrs * occ.prixnuitee)-total
    page.append(Paragraph(f"DETTE RESTANTE EN CE JOUR : {dette} $", style2))
    page.append(Paragraph(f"{num2words(dette, lang='fr')} dollars américains", style2))
    tab = Table([
        [Paragraph("COORDONNéES BANCAIRES".upper())],
        ["Nom de la Banque","EQUITY BANQUE COMMERCIALE DU CONGO","",Paragraph("Sign. du client",style3)],
        ["Intitulé du compte","HOTEL NEW RIVIERA / GROUPE TAVERNE"],
        ["Numéro de compte","2332 001 001 666 14 "],
        ["IBAN","000 110 502 332 001 001 666 14"],
        ["SWIFT CODE","BCDCCDI"]
    ])
    
    tab.setStyle(TableStyle([
        ("FONTSIZE",(0,0),(-1,-1),8),
        ("LEADING",(0,0),(-1,-1),5),
        ("SPAN",(0,0),(-1,0)),
        ("SPAN",(-1,1),(-1,-1)),
        ("VALIGN",(-1,1),(-1,-1),'TOP'),
        ("GRID",(-1,1),(-1,-1),.1,colors.red),
        ("BACKGROUND",(0,-3),(-2,-2),colors.yellow)
    ]))
    page.append(tab)
    page.append(Table([[""],[""]]))
    page.append(Table([["POUR ACQUIS"],[req.user.username.upper()]]))
    pdf.build(page)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"]=f'inline; filename="reçu_paiement {num}_#{recu.occupation.chambre.numero}.pdf"'
    return response





def facture_client_chambre(req, num):
    style1 = ParagraphStyle("s1",fontName="Helvetica-Bold",fontSize=13, alignment=TA_JUSTIFY)
    style2 = ParagraphStyle("s1",fontName="Helvetica-Bold",fontSize=11, spaceBefore=5, alignment=TA_JUSTIFY)
    style3 = ParagraphStyle("s3",fontName="Helvetica-Oblique",fontSize=9)
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)
    page = []
    large, haut = A4
    
    page.append(Image("media\images\logo_hnr_gerance.png",large-140,90))
    
    occ = Enregistrer.objects.get(id = num)
    recus = Paiement.objects.filter(occupation_id = num).all()

    tab = Table([
        ["CLIENT",f": {occ.client.nom} {occ.client.postnom}","",Paragraph(f"FACTURE N° HNR-{occ.id}/{datetime.now().strftime("%m-%y")}".upper(),style1)],
        ["ORGANISATION",f": {occ.entreprise.nom}","","DATE :",f": {datetime.now().strftime("%d/%m/%Y")}"],
        ["Adresse physique",f": {occ.client.adresse_serv}","","CHAMBRE ",f": #{occ.chambre.numero}"],
        ["Adresse mail",f": {occ.client.mail}","","D. Entrée",f": {occ.datearr.strftime('%d/%m/%Y  %H:%M')}"],
        ["Téléphone",f": {occ.client.tel}","","D. Sortie",f": {occ.datesor.strftime('%d/%m/%Y  %H:%M')}"],
    ])
    tab.setStyle(TableStyle([
        ("SPAN",(3,0),(-1,0)),
        # ("GRID",(0,0),(-1,-1),.1,colors.red)
    ]))
    page.append(tab)
    page.append(Table([[""]]))
    data = [["Date","Désignation","Débit","Crédit"],]
    
    j=0;total_D=0; tot_cash=0; 
    # dif_date = (datetime.now()-occ.datearr).days()
    dif_date = (datetime.now(timezone.utc) - occ.datearr).days
    new_date = occ.datearr
    for i in range(dif_date+1):
        data.append([Paragraph(f"{new_date.strftime("%d/%m/%Y")}"),f"Accomodation chambre {occ.chambre.categorie.designation} #{occ.chambre.numero}",f"{occ.prixnuitee} $",""])
        j += 1
        total_D += occ.prixnuitee
        new_date += timedelta(days=1)

    k=0;total_C=0
    
    for recu in recus:
        data.append([f"{recu.datejr.strftime("%d/%m/%Y  %H:%M")}",Paragraph(f"{recu.libelle}"),"",f"{recu.montant} $"])
        k += 1
        total_C += recu.montant
        
    data.append([""])
    data.append(["","TOTAL",f"{total_D} $",f"{total_C} $"])
    data.append([Paragraph(f"",style3)])
    
    tab = Table(data)
    d=[]
    #Pour colorer le tableau ligne après ligne
    lig=0
    while lig <= j+k:
        for col in range(5):
            d.append(('BACKGROUND',(col,lig),(-1,lig), "#e9e9e9"))
        lig += 2
    tab.setStyle(TableStyle(d))
        
    tab.setStyle(TableStyle([
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("BACKGROUND",(0,0),(-1,0),colors.red),
        ("GRID",(0,0),(-1,0),.5,colors.red),
        ("BACKGROUND",(0,-1),(-1,-2),colors.red),
        ("TEXTCOLOR",(0,-1),(-1,-2),colors.white),
        ("FACE",(0,-2),(-1,-2),"Helvetica-Bold"),
        ("LEADING",(0,-3),(-1,-3),1),
        ("LEADING",(0,-4),(-1,-4),10),
        ("VALIGN",(0,-4),(-1,-4),"TOP"),
        ("ALIGN",(-2,0),(-1,-2),'RIGHT'),
        ("SPAN",(0,-1),(-1,-1)),
    ]))
    page.append(tab)
    dette = total_D-total_C
    page.append(Paragraph(f"SOLDE DEBITEUR : {dette} $", style2))
    page.append(Paragraph(f"Nous disons : « {num2words(dette, lang='fr').capitalize()} dollars américains  »", style3))
    page.append(Paragraph(f"We say : « {num2words(dette, lang='en').capitalize()} United State Dollars  »", style3))
    page.append(Table([[""]]))
    tab = Table([
        [Paragraph("COORDONNéES BANCAIRES".upper())],
        ["Nom de la Banque","EQUITY BANQUE COMMERCIALE DU CONGO","",Paragraph("Sign. du client",style3)],
        ["Intitulé du compte","HOTEL NEW RIVIERA / GROUPE TAVERNE"],
        ["Numéro de compte","2332 001 001 666 14 "],
        ["IBAN","000 110 502 332 001 001 666 14"],
        ["SWIFT CODE","BCDCCDI"]
    ])
    
    tab.setStyle(TableStyle([
        ("FONTSIZE",(0,0),(-1,-1),8),
        ("LEADING",(0,0),(-1,-1),5),
        ("SPAN",(0,0),(-1,0)),
        ("SPAN",(-1,1),(-1,-1)),
        ("VALIGN",(-1,1),(-1,-1),'TOP'),
        ("GRID",(-1,1),(-1,-1),.1,colors.red),
        ("BACKGROUND",(0,-3),(-2,-2),colors.yellow)
    ]))
    page.append(tab)
    page.append(Table([[""],[""]]))
    page.append(Table([["POUR ACQUIS"],[req.user.username.upper()]]))
    pdf.build(page, canvasmaker=CustomCanvas)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"]=f'inline; filename="reçu_paiement {num}.pdf"'
    return response




def facture_client_chambre2(req, num):
    style1 = ParagraphStyle("s1",fontName="Helvetica-Bold",fontSize=13, alignment=TA_JUSTIFY)
    style2 = ParagraphStyle("s1",fontName="Helvetica-Bold",fontSize=11, spaceBefore=5, alignment=TA_JUSTIFY)
    style3 = ParagraphStyle("s3",fontName="Helvetica-Oblique",fontSize=9)
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)
    page = []
    large, haut = A4
    
    page.append(Image("media\images\logo_hnr_gerance.png",large-140,90))
    
    chambre = Chambre.objects.get(id = num)
    num = Enregistrer.objects.filter(chambre = chambre).last().id
    
    occ = Enregistrer.objects.get(id = num)
    recus = Paiement.objects.filter(occupation_id = num).all()
    fact_pdv = PaiementFacture.objects.filter(occupation = occ).all()
    account_date_room = Account.objects.last().account_date_room
    date_arrivee = occ.datearr.astimezone(timezone.get_current_timezone()).strftime('%d/%m/%Y  %H:%M')
    date_sortie = occ.datesor.astimezone(timezone.get_current_timezone()).strftime('%d/%m/%Y  %H:%M') if  occ.datesor.date() > account_date_room else account_date_room.strftime("%d/%m/%Y %H:%M")
    tab = Table([
        ["CLIENT",f": {occ.client.nom} {occ.client.postnom}","",Paragraph(f"FACTURE N° HNR-{occ.id}/{datetime.now().strftime("%m-%y")}".upper(),style1)],
        ["ORGANISATION",f": {occ.entreprise.nom}","","DATE :",f": {datetime.now().strftime("%d/%m/%Y")}"],
        ["Adresse physique",f": {occ.client.adresse_serv}","","CHAMBRE ",f": #{occ.chambre.numero}"],
        ["Adresse mail",f": {occ.client.mail}","","D. Entrée",f": {date_arrivee}"],
        ["Téléphone",f": {occ.client.tel}","","D. Sortie",f": {date_sortie}"],
    ])
    tab.setStyle(TableStyle([
        ("SPAN",(3,0),(-1,0)),
    ]))
    page.append(tab)
    page.append(Table([[""]]))
    data = [["Date","Désignation","Débit","Crédit"],]
    
    j=0;total_D=0; tot_cash=0; 
    datearr = occ.datearr.astimezone(timezone.get_current_timezone()).date()  # Conversion de DateTimeField en date
    
    dif_date = (account_date_room - datearr).days
    
    new_date = datearr
    for i in range(dif_date):
        data.append([Paragraph(f"{new_date.strftime("%d/%m/%Y")}"),f"Accomodation chambre {occ.chambre.categorie.designation} #{occ.chambre.numero}",f"{occ.prixnuitee} $",""])
        j += 1
        total_D += occ.prixnuitee
        new_date += timedelta(days=1)

    k=0;total_C=0
        
    for recu in fact_pdv:
        data.append([f"{recu.date.astimezone(timezone.get_current_timezone()).strftime("%d/%m/%Y  %H:%M")}",Paragraph(f"{recu.vente.pointvente.designation} - Facture n° {recu.vente.id}"),f"{recu.montant} $",""])
        k += 1
        total_D += recu.montant
        
    for recu in recus:
        data.append([f"{recu.datejr.astimezone(timezone.get_current_timezone()).strftime("%d/%m/%Y  %H:%M")}",Paragraph(f"{recu.libelle}"),"",f"{recu.montant} $"])
        k += 1
        total_C += recu.montant
        
    data.append([""])
    data.append(["","TOTAL",f"{total_D} $",f"{total_C} $"])
    data.append([Paragraph(f"",style3)])
    
    tab = Table(data)
    d=[]
    #Pour colorer le tableau ligne après ligne
    lig=0
    while lig <= j+k:
        for col in range(5):
            d.append(('BACKGROUND',(col,lig),(-1,lig), "#e9e9e9"))
        lig += 2
    tab.setStyle(TableStyle(d))
        
    tab.setStyle(TableStyle([
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("BACKGROUND",(0,0),(-1,0),colors.red),
        ("GRID",(0,0),(-1,0),.5,colors.red),
        ("BACKGROUND",(0,-1),(-1,-2),colors.red),
        ("TEXTCOLOR",(0,-1),(-1,-2),colors.white),
        ("FACE",(0,-2),(-1,-2),"Helvetica-Bold"),
        ("LEADING",(0,-3),(-1,-3),1),
        ("LEADING",(0,-4),(-1,-4),10),
        ("VALIGN",(0,-4),(-1,-4),"TOP"),
        ("ALIGN",(-2,0),(-1,-2),'RIGHT'),
        ("SPAN",(0,-1),(-1,-1)),
    ]))
    page.append(tab)
    dette = total_D-total_C
    page.append(Paragraph(f"SOLDE DEBITEUR : {dette} $", style2))
    page.append(Paragraph(f"Nous disons : « {num2words(dette, lang='fr').capitalize()} dollars américains  »", style3))
    page.append(Paragraph(f"We say : « {num2words(dette, lang='en').capitalize()} United State Dollars  »", style3))
    page.append(Table([[""]]))
    tab = Table([
        [Paragraph("COORDONNéES BANCAIRES".upper())],
        ["Nom de la Banque","EQUITY BANQUE COMMERCIALE DU CONGO","",Paragraph("Sign. du client",style3)],
        ["Intitulé du compte","HOTEL NEW RIVIERA / GROUPE TAVERNE"],
        ["Numéro de compte","2332 001 001 666 14 "],
        ["IBAN","000 110 502 332 001 001 666 14"],
        ["SWIFT CODE","BCDCCDI"]
    ])
    
    tab.setStyle(TableStyle([
        ("FONTSIZE",(0,0),(-1,-1),8),
        ("LEADING",(0,0),(-1,-1),5),
        ("SPAN",(0,0),(-1,0)),
        ("SPAN",(-1,1),(-1,-1)),
        ("VALIGN",(-1,1),(-1,-1),'TOP'),
        ("GRID",(-1,1),(-1,-1),.1,colors.red),
        ("BACKGROUND",(0,-3),(-2,-2),colors.yellow)
    ]))
    page.append(tab)
    page.append(Table([[""],[""]]))
    page.append(Table([["POUR ACQUIS"],[req.user.username.upper()]]))
    pdf.build(page, canvasmaker=CustomCanvas)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"]=f'inline; filename="reçu_paiement {num}.pdf"'
    return response