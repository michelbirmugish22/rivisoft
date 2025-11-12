from django.http import HttpResponse
import io 
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.colors import *
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A3
from reportlab.lib.units import mm, inch
from datetime import datetime as dt
from num2words import num2words
from riviapp.models import LigneCommandeVente, CommandeVente
# from rapports.classe_rp.classes_personnalisees import CustomCanvas
# Les styles
st1 = ParagraphStyle('st1', fontName='Helvetica-Bold',fontSize=12,firstLineIndent=5, alignment=TA_CENTER)
st2 = ParagraphStyle('st1', fontName='Helvetica-Bold',fontSize=9,firstLineIndent=5, alignment=TA_CENTER)
st3 = ParagraphStyle('st1', fontName='Helvetica-Oblique',fontSize=9,firstLineIndent=5, alignment=TA_CENTER)
st4 = ParagraphStyle('st1', fontName='Helvetica',fontSize=11,firstLineIndent=5)
st5 = ParagraphStyle('st1', fontName='Helvetica-Bold',fontSize=9)

def vente(request, id_fact):
    #Commande vente concernée
    fact = CommandeVente.objects.get(id=id_fact)
    
    buffer = io.BytesIO()
     # Définir les dimensions du papier thermique
    thermal_width = 2.77 * inch  # 80 mm de large
    thermal_height = 5.54 * inch  # 200 mm de long (ajustez selon vos besoins)
    page_size = (thermal_width, thermal_height)
    
    # pdf = SimpleDocTemplate(buffer, page_size=page_size)
    pdf = SimpleDocTemplate(buffer, page_size=A3)
    page = []
    
    page.append(Paragraph("HOTEL NEW RIVIERA - BUKAVU",st1))
    page.append(Paragraph("Avenue du Lac N°10, Ibanda/Bukavu",st3))
    page.append(Paragraph("+243 999 917 125 / +243 999 917 112",st3))
    page.append(Paragraph(f"PDV : {fact.pointvente.designation}",st2))
    page.append(Paragraph("----------------------------------------------------------------------",st3))
    
    data1 = []
    data1.append(['','','','',Paragraph(f'FACTURE N°{fact.id}',st5),'','','','','','',''])
    data1.append(['','','','',f'Date  : {dt.now().strftime("%d-%m-%Y %H:%M")}','','','','','','',''])
    data1.append(['','','','','Nom client : BIKANAAN SHUKRAAN #506','','','','','','',''])
    data1.append(['','','','',f'Nom serveur(se) : {request.user.username.upper()} {request.user.last_name}','','','','','','',''])
    colWidths = [20, 20, 20, 20,200, 14, 14, 14, 14, 14, 14, 14, 14]  # Largeurs des colonnes
    tab1 = Table(data1, colWidths=colWidths)
    page.append(tab1)
    

    data = []
    tot = 0;i=1
    data.append(['','','','','#','Désignation','QTE','PU','PTTC','','','',''])
    for ligne in LigneCommandeVente.objects.filter(commandevente=fact.id):
        data.append(['','','','',i,Paragraph(f"{ligne.menu.designation}"),ligne.qte,ligne.menu.prix,ligne.qte*ligne.menu.prix,'','','',''])
        tot += ligne.qte*ligne.menu.prix
        i+=1
    ht = tot-round(tot*.16,1);tva=round(tot*.16,1)
    data.append(['','','','','','TOTAL HT','','',ht,'','','',''])
    data.append(['','','','','','TVA 16%','','',tva,'','','',''])
    data.append(['','','','','','TOTAL TTC','','',ht+tva,'','','',''])
    
    colWidths = [20, 20, 20, 20, 15, 80, 30, 30, 40, 30, 20, 20, 20]  # Largeurs des colonnes
    # rowHeights = [20] * len(data)  # Hauteurs des lignes
    tab = Table(data, colWidths=colWidths)


    # tab = Table(data)
    
    tab.setStyle(TableStyle([
        # ('GRID',(0,0),(-1,-1),.1,black),
        ('BACKGROUND',(4,0),(8,0),"#f0f0f0"),
        ('GRID',(4,0),(8,-4),.001,black),
        ('VALIGN',(4,0),(8,-4),'MIDDLE'),
        ('GRID',(8,-3),(8,-1),.1,black),
        ('SPAN',(5,-3),(7,-3)),
        ('SPAN',(5,-2),(7,-2)),
        ('SPAN',(5,-1),(7,-1)),
        ('FACE',(5,-3),(7,-1),'Helvetica-Oblique'),
        ('FACE',(0,-1),(-1,-1),'Helvetica-Bold'),
        ('ALIGN',(5,-3),(7,-1),'RIGHT'),
        ('ALIGN',(6,1),(8,-1),'RIGHT'),
    ]))
    
    page.append(tab)
    page.append(Paragraph('....................................................................................', st3))
    page.append(Paragraph(f"Nous disons {num2words(ht+tva, lang='fr')} dollars américains",ParagraphStyle('a',firstLineIndent=120, strikeWidth=2,width=10, spaceAfter=5)))
    page.append(Paragraph(f"Etat de la facture : NON PAYEE",ParagraphStyle('a',firstLineIndent=120, spaceAfter=20)))
    page.append(Paragraph('....................................................................................', st3))
    page.append(Paragraph(f'~ Merci de nous avoir choisi. Bienvenue encore ! ~', st3))
    pdf.build(page)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"]=f'inline; filename="Facture_POS.pdf"'
    return response


















def modele_factureçpos(request):
    buffer = io.BytesIO()
     # Définir les dimensions du papier thermique
    thermal_width = 2.77 * inch  # 80 mm de large
    thermal_height = 5.54 * inch  # 200 mm de long (ajustez selon vos besoins)
    page_size = (thermal_width, thermal_height)
    
    # pdf = SimpleDocTemplate(buffer, page_size=page_size)
    pdf = SimpleDocTemplate(buffer, page_size=A3)
    page = []
    
    page.append(Paragraph("HOTEL NEW RIVIERA - BUKAVU",st1))
    page.append(Paragraph("Avenue du Lac N°10, Ibanda/Bukavu",st3))
    page.append(Paragraph("+243 999 917 125 / +243 999 917 112",st3))
    page.append(Paragraph("PDV : RESTAURANT OKAPI",st2))
    page.append(Paragraph("----------------------------------------------------------------------",st3))
    
    data1 = []
    data1.append(['','','','',Paragraph('FACTURE N°89/65-96',st5),'','','','','','',''])
    data1.append(['','','','',f'Date  : {dt.now().strftime("%d-%m-%Y %H:%M")}','','','','','','',''])
    data1.append(['','','','','Nom client : BIKANAAN SHUKRAAN #506','','','','','','',''])
    data1.append(['','','','',f'Nom serveur(se) : {request.user.username.upper()} {request.user.last_name}','','','','','','',''])
    colWidths = [20, 20, 20, 20,200, 14, 14, 14, 14, 14, 14, 14, 14]  # Largeurs des colonnes
    tab1 = Table(data1, colWidths=colWidths)
    page.append(tab1)
    

    data = []
    data.append(['','','','','#','Désignation','QTE','PU','PTTC','','','',''])
    data.append(['','','','','1',Paragraph('Frites aux Saucissons'),2,8,16,'','','',''])
    data.append(['','','','','2',Paragraph('Poisson aux champigons de neige avec frites et salade de tomates'),3,20,60,'','','',''])
    data.append(['','','','','3','Grand Primus',3,4,12,'','','',''])
    data.append(['','','','','4','Coca cola 32CL',1,2,2,'','','','']);ht = 90-round(90*.16,1);tva=round(90*.16,1)
    data.append(['','','','','','TOTAL HT','','',ht,'','','',''])
    data.append(['','','','','','TVA 16%','','',tva,'','','',''])
    data.append(['','','','','','TOTAL TTC','','',ht+tva,'','','',''])
    
    colWidths = [20, 20, 20, 20, 15, 80, 30, 30, 40, 30, 20, 20, 20]  # Largeurs des colonnes
    # rowHeights = [20] * len(data)  # Hauteurs des lignes
    tab = Table(data, colWidths=colWidths)


    # tab = Table(data)
    
    tab.setStyle(TableStyle([
        # ('GRID',(0,0),(-1,-1),.1,black),
        ('BACKGROUND',(4,0),(8,0),"#f0f0f0"),
        ('GRID',(4,0),(8,-4),.001,black),
        ('VALIGN',(4,0),(8,-4),'MIDDLE'),
        ('GRID',(8,-3),(8,-1),.1,black),
        ('SPAN',(5,-3),(7,-3)),
        ('SPAN',(5,-2),(7,-2)),
        ('SPAN',(5,-1),(7,-1)),
        ('FACE',(5,-3),(7,-1),'Helvetica-Oblique'),
        ('FACE',(0,-1),(-1,-1),'Helvetica-Bold'),
        ('ALIGN',(5,-3),(7,-1),'RIGHT'),
        ('ALIGN',(6,1),(8,-1),'RIGHT'),
    ]))
    
    page.append(tab)
    page.append(Paragraph('....................................................................................', st3))
    page.append(Paragraph(f"Nous disons {num2words(ht+tva, lang='fr')} dollars américains",ParagraphStyle('a',firstLineIndent=120, strikeWidth=2,width=10, spaceAfter=5)))
    page.append(Paragraph(f"Etat de la facture : NON PAYEE",ParagraphStyle('a',firstLineIndent=120, spaceAfter=20)))
    page.append(Paragraph('....................................................................................', st3))
    page.append(Paragraph(f'~ Merci de nous avoir choisi. Bienvenue encore ! ~', st3))
    pdf.build(page)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"]=f'inline; filename="Facture_POS.pdf"'
    return response
