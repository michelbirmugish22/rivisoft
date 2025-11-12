from django.http import HttpResponse
import io

from reportlab.lib import colors 
from riviapp.models import Account, Caisse, Enregistrer, Client, Categorie, Chambre, Operateur, Paiement, Entreprise, PaiementFacture, Piece_indentite
from riviapp.rapports.classe_rp.classes_personnalisees import CustomCanvas
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image
from reportlab.lib.colors import *
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from num2words import num2words
from datetime import datetime, time, timedelta

def index(req):  
    # Convertion de la date HTML en Date Python
    date1 = datetime.strptime(req.POST['date1'], "%Y-%m-%d").date() if req.method == "POST" else datetime.strptime(req.GET['date1'], "%Y-%m-%d").date()
    date2 = datetime.strptime(req.POST['date2'], "%Y-%m-%d").date() if req.method == "POST" else datetime.strptime(req.GET['date2'], "%Y-%m-%d").date()
    # Convertir les dates en datetime
    start_datetime = datetime.combine(date1, time.min)  # 2024-01-01 00:00:00
    end_datetime = datetime.combine(date2, time.max)      # 2024-12-31 23:59:59
    
    operateur = req.POST['operateur2'] if req.method == "POST" else req.GET['operateur2']
    style1 = ParagraphStyle("s1",fontName="Helvetica-Bold",fontSize=14, alignment=TA_CENTER)
    style2 = ParagraphStyle("s1",fontName="Helvetica-Bold",fontSize=11, spaceBefore=5, alignment=TA_JUSTIFY)
    style3 = ParagraphStyle("s3",fontName="Helvetica-Oblique",fontSize=9)
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)
    page = []
    large, haut = A4
    
    page.append(Image("media\images\logo_hnr_gerance.png",large-140,90))
    page.append(Paragraph(f"JOURNAL DE CAISSE DU {date1.strftime("%d/%m/%Y")} AU {date2.strftime("%d/%m/%Y")}", style1))




    page.append(Table([[""]]))
    data = [["Date et heure","Libellé","Compte","Entrée","Sortie"],]
    
    j=0;total_D=0;total_C=0;

    #SELECT * FROM caisse WHERE caisse.date BETWEEN 'date1' AND 'date2':
    if operateur != "all":
        operator = Operateur.objects.get(id=operateur)
        liste_journaux = Caisse.objects.filter(date__gte=start_datetime, date__lte=end_datetime,operateur=operator)
    else:
        liste_journaux = Caisse.objects.filter(date__gte=start_datetime, date__lte=end_datetime)
    
    for journal in liste_journaux:
        data.append([Paragraph(f"{journal.date.strftime("%d/%m/%Y %H:%M")}"),f"{journal.libelle}",f"{journal.operateur.designation}",f"{journal.mouvement}" if journal.mouvement > 0 else "",f"{abs(journal.mouvement)}" if journal.mouvement < 0 else "" ])
        j += 1
        total_D += abs(journal.mouvement) if journal.mouvement > 0 else 0
        total_C += abs(journal.mouvement) if journal.mouvement < 0 else 0


    k=0;

    data.append(["SOLDES : ","","",f"{round(total_D,2)} $",f"{round(total_C,2)} $"])

    
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
        ("GRID",(0,0),(-1,-1),.1,"#d0d0d0"),
        ("BACKGROUND",(0,-1),(-1,-2),colors.red),
        ("TEXTCOLOR",(0,-1),(-1,-2),colors.white),
        ("FACE",(0,-1),(-1,-1),"Helvetica-Bold"),
        ("ALIGN",(0,-1),(-3,-1),"RIGHT"),
        # ("LEADING",(0,-3),(-1,-3),1),
        # ("LEADING",(0,-4),(-1,-4),10),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("ALIGN",(-2,0),(-1,-2),'RIGHT'),
        ("SPAN",(0,-1),(-3,-1)),
    ]))
    page.append(tab)
    page.append(Table([[""],[""]]))
    page.append(Table([[Paragraph("imprimé le "+ datetime.now().strftime("%d/%m/%Y  à %H:%M:%S")+" par " + req.user.username.upper(), ParagraphStyle("st",fontName='Times-Italic'))]]))
    pdf.build(page, canvasmaker=CustomCanvas)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"]=f'inline; filename="journal_de_caise_{date1}_au_{date2}.pdf"'
    return response