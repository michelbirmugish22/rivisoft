from django.http import HttpResponse
import io

from reportlab.lib import colors 
from riviapp.models import * 
from riviapp.rapports.classe_rp.classes_personnalisees import CustomCanvas
from reportlab.lib.pagesizes import A4, letter, landscape, portrait
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image
from reportlab.lib.colors import *
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from num2words import num2words
from datetime import datetime, time, timedelta

def index(req):  
    
    style1 = ParagraphStyle("s1",fontName="Helvetica-Bold",fontSize=16, spaceBefore=10, spaceAfter=10, alignment=TA_CENTER)
    style2 = ParagraphStyle("s1",fontName="Helvetica",fontSize=11, spaceBefore=50, alignment=TA_JUSTIFY)
    style3 = ParagraphStyle("s3",fontName="Helvetica-Oblique",fontSize=9)
    buffer = io.BytesIO()
    # pdf = SimpleDocTemplate(buffer, pagesize=A4)
    pdf = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    page = []
    large, haut = A4
    page.append(Image("media\images\logo_hnr_gerance.png",large-120,80))
    page.append(Paragraph(f"RAPPORT RECEPTION DU {Account.objects.last().account_date_room.strftime("%d/%m/%Y")}", style1))
    
    listes = Enregistrer.objects.filter(still_in = 1)
    data = [["N°","CHAMBRE","NOMS & POSTNOMS","DATE ARRIVEE","PAX","SOCIETE"]]
    i=1
    for l in listes:
        data.append([Paragraph(f"{i}",style2),Paragraph(f"{l.chambre.numero}",style2),Paragraph(f"{l.client.nom} {l.client.postnom}",style2),Paragraph(f"{l.datearr.strftime("%d/%m/%Y")}",style2),Paragraph(f"{l.nbpax}",style2),Paragraph(f"{l.entreprise.nom}",style2)])
        i+=1
    tab = Table(data)
    tab.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),.5,"#333333"),
        ('VALIGN',(0,0),(-1,-1), "MIDDLE"),
        ('FACE',(0,0),(-1,0),"Helvetica-Bold")
    ]))
    
    page.append(tab)


   
    page.append(Table([[Paragraph("imprimé le "+ datetime.now().strftime("%d/%m/%Y  à %H:%M:%S")+" par " + req.user.username.upper(), ParagraphStyle("st",fontName='Times-Italic'))]]))
    pdf.build(page, canvasmaker=CustomCanvas)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"]=f'inline; filename="liste employés_.pdf"'
    return response