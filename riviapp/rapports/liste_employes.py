from django.http import HttpResponse
import io

from reportlab.lib import colors 
from riviapp.models import * 
from riviapp.rapports.classe_rp.classes_personnalisees import CustomCanvas
from reportlab.lib.pagesizes import A4, letter, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image
from reportlab.lib.colors import *
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from num2words import num2words
from datetime import datetime, time, timedelta

def index(req):  
    
    empl_ = req.GET.get("empl_category_hidden") if req.GET.get("empl_category_hidden") is not None else "all"
    
    all = False
    by_service = False
    by_departement = False
    by_employee = False
    
    if "S" in empl_:
        by_service = True
        id_ser = int(empl_.replace("S",""))
    elif "D" in empl_:
        by_departement = True
        id_dep = int(empl_.replace("D",""))
    elif "all" in empl_:
        all = True
    else:
        by_employee = True
        id_emp = int(empl_)
        
    by_ = ""    
    if all:
        employes = Employe.objects.all().order_by('nom')
        by_ = 'TOUS'
    if by_service:
        employes = Employe.objects.filter(service=id_ser).order_by('nom')
        by_ = ("serv. " + employes.first().service.designation).upper()
    if by_departement:
        employes = Employe.objects.filter(service__departement=id_dep).order_by('nom')
        by_= ("dép. " + employes.first().service.departement.designation).upper()
    if by_employee:
        employes = Employe.objects.filter(id=id_emp).order_by('nom')
        by_=employes.first().nom.upper()
        
        
    style1 = ParagraphStyle("s1",fontName="Helvetica-Bold",fontSize=14, alignment=TA_CENTER)
    style2 = ParagraphStyle("s1",fontName="Helvetica-Bold",fontSize=9, spaceBefore=5, alignment=TA_JUSTIFY)
    style3 = ParagraphStyle("s3",fontName="Helvetica-Oblique",fontSize=9)
    buffer = io.BytesIO()
    # pdf = SimpleDocTemplate(buffer, pagesize=A4)
    pdf = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    page = []
    large, haut = A4
    # page.append(Image("media\images\logo_hnr_gerance.png",large,70))
    page.append(Paragraph(f"HOTEL NEW RIVIERA BUKAVU", style1))
    page.append(Paragraph(f"LISTE DES EMPLOYES - {by_}", ParagraphStyle("s1",fontName="Helvetica-Bold",fontSize=11, spaceBefore=10, alignment=TA_CENTER)))




    page.append(Table([[""]]))
    data=[[Paragraph("ID",style2),Paragraph("Nom & Postnom",style2),Paragraph("Fonction",style2),Paragraph("Service",style2),Paragraph("Département",style2),Paragraph("Niveau d'étude",style2),Paragraph("Etat Civil",style2),Paragraph("Sexe",style2),Paragraph("Nationnalité",style2),Paragraph("Contact",style2),Paragraph("Mail",style2),Paragraph("Âge",style2)]]
    for e in employes:
        data.append([Paragraph(f'{e.id}'),Paragraph(f'{e.nom} {e.postnom}'),Paragraph(f'{e.fonction}'),Paragraph(f'{e.service.designation}'),Paragraph(f'{e.service.departement.designation}'),Paragraph(f'{e.niveau_etu}'),Paragraph(f'{e.etat_civil}'),Paragraph(f'{e.sexe}'), Paragraph(f'{e.nationalite}'),Paragraph(f'{e.tel}'),Paragraph(f'{e.mail}'),Paragraph(f'{int((datetime.now().date()-e.date_naiss).days/365)}')])
    tab = Table(data)
    tab.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),.1,"#666666"),
    ]))
    page.append(tab)
    page.append(Table([[""],[""]]))
    page.append(Table([[Paragraph("imprimé le "+ datetime.now().strftime("%d/%m/%Y  à %H:%M:%S")+" par " + req.user.username.upper(), ParagraphStyle("st",fontName='Times-Italic'))]]))
    pdf.build(page, canvasmaker=CustomCanvas)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"]=f'inline; filename="liste employés_.pdf"'
    return response