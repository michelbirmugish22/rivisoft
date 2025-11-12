import io 
from reportlab.lib.pagesizes import A4, letter, landscape, portrait
from riviapp.rapports.classe_rp.classes_personnalisees import NumberedCanvas, CustomCanvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, Image, TableStyle
from reportlab.lib.colors import *
from django.http import HttpResponse
import qrcode
from io import BytesIO
from riviapp.models import *


def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

pol1 = ParagraphStyle('dd', fontName='Helvetica-Bold', fontSize=14, textColor='#FF0000',borderPadding=(0, 0, 5, 0), alignment=TA_CENTER)
pol2 = ParagraphStyle('dd',fontName='Helvetica', fontSize=12, alignment=TA_JUSTIFY)
empty_line_style = ParagraphStyle('empty', fontSize=12, spaceBefore=10, spaceAfter=10)
centrer = ParagraphStyle('cnet', alignment=TA_CENTER)
def liste_chambres(req):
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)
    contenu = []
    w,h=A4
    
    contenu.append(Image("media\images\logo_hnr_gerance.png",w-120,100))
    contenu.append(Paragraph("LISTE DES CHAMBRES", pol1))
    contenu.append(Paragraph("",empty_line_style))
    
    # ---------------------DONNEES DE LA BDD 
    from riviapp.models import  Chambre
    chambres = Chambre.objects.all().order_by('numero')
    data = [['ID','Numéro','Catégorie','Prix','Etat','Niveau','Bloc']]
    def get_etage(num_etage):
        if num_etage==0:
            return 'Rez-des-chaussez'
        elif num_etage == 1:
            return '1er niveau'
        elif num_etage == 2:
            return '2ème niveau'
        elif num_etage == 3:
            return '3ème niveau'
        else:
            return '4ème niveau'
    for cha in chambres:
        data.append([cha.id, cha.numero, cha.categorie.designation, f"{cha.categorie.prix} $", cha.statut, get_etage(int(cha.etage)), cha.bloc.designation])
    
    tab = Table(data)
    tab.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),red),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
        ('FONTSIZE',(0,0),(-1,-1),12),
        ('ALIGN',(1,0),(1,-1),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TEXTCOLOR',(0,0),(-1,0),white),
        ('GRID',(0,0),(-1,-1),.25,red)
    ]))
    contenu.append(tab)
    from datetime import datetime
    contenu.append(Paragraph("",empty_line_style))
    contenu.append(Paragraph(f"Imprimé par {req.user} à {datetime.now()}"))
    
    # Construire le PDF avec le canvas personnalisé avec le nombre des pages
    pdf.build(contenu, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    response = HttpResponse(buffer,content_type="application/pdf")
    response['Content-Disposition']='inline;filename="testpdf.pdf"'
    return response

def liste_rsv(req):
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=portrait(A4), leftMargin=72, 
    rightMargin=72,  # marge droite en points
    topMargin=72,  # marge supérieure en points
    bottomMargin=72  # marge inférieure en points
    )
    contenu = []
    w,h=A4
    
    contenu.append(Image("media\images\logo_hnr_gerance.png",w-120,100))
    contenu.append(Paragraph("LISTE DES RESERVATIONS", pol1))
    contenu.append(Paragraph("",empty_line_style))
    
    # ---------------------DONNEES DE LA BDD 
    from riviapp.models import  Reservation, Chambre, Categorie
    rsvs = Reservation.objects.all().order_by('-id')
    data = [['ID RSV','Client','Tél client','Catégorie Chb','Prix nuit','Check In','Check Out','Date rsv']]
    def get_etage(num_etage):
        if num_etage==0:
            return 'Rez-des-chaussez'
        elif num_etage == 1:
            return '1er niveau'
        elif num_etage == 2:
            return '2ème niveau'
        elif num_etage == 3:
            return '3ème niveau'
        else:
            return '4ème niveau'
    i=1
    for rsv in rsvs:
        data.append([Paragraph(f"{rsv.id}", centrer),Paragraph(f"{rsv.client.nom} {rsv.client.postnom}"),Paragraph(rsv.client.tel), Paragraph(rsv.categorie.designation), Paragraph(f"{rsv.prixvalide}"),Paragraph(f"{rsv.datearrivee.strftime("%d-%m-%Y")}"),Paragraph(f"{rsv.datesortie.strftime("%d-%m-%Y")}"),Paragraph(f"{rsv.datejr.strftime("%d-%m-%Y")}")])
        i+=1
    
    tab = Table(data)
    tab.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),red),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
        ('ALIGN',(1,0),(1,-1),'CENTER'),
        ('ALIGN',(0,0),(0,-1),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TEXTCOLOR',(0,0),(-1,0),white),
        ('GRID',(0,0),(-1,-1),.25,red)
    ]))
    contenu.append(tab)
    from datetime import datetime
    contenu.append(Paragraph("",empty_line_style))
    contenu.append(Paragraph(f"Fait à Bukavu, le {datetime.now().strftime('%d %B %Y')}"))
    contenu.append(Paragraph(f"Imprimé par {req.user.username.upper()}"))
    
    # Construire le PDF avec le canvas personnalisé avec le nombre des pages
    pdf.build(contenu, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    response = HttpResponse(buffer,content_type="application/pdf")
    response['Content-Disposition']='inline;filename="testpdf.pdf"'
    return response

def statut_chambres(req):
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)
    contenu = []
    w,h=A4
    
    contenu.append(Image("media\images\logo_hnr_gerance.png",w-120,100))
    contenu.append(Paragraph("STATUT DES CHAMBRES", pol1))
    contenu.append(Paragraph("",empty_line_style))
    
    # ---------------------DONNEES DE LA BDD 
    chambres = Chambre.objects.all().order_by('numero')
    data = [[]]
    bg_occuped = ParagraphStyle("bgo", backColor='#0000FF',textColor='#FFFFFF', fontSize=12, borderPadding=5,borderWidth=1)
    bg_vaccant = ParagraphStyle("bgo", backColor='#FFFFF9', fontSize=11, borderPadding=3,borderWidth=30)

    for cha in chambres:
        if cha.statut == 'Occupee':
            ci = Enregistrer.objects.filter(chambre=cha.id).last()
            data.append([Paragraph(f"{cha.numero} {ci.client.nom} {ci.client.postnom} ({ci.datearr.strftime('%d/%m/%Y')} - {ci.datesor.strftime('%d/%m/%Y')})",bg_occuped)])
        else:
            data.append([Paragraph(f"{cha.numero}",bg_vaccant)])
    
    tab = Table(data)
    tab.setStyle(TableStyle([
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
        ('FONTSIZE',(0,0),(-1,-1),12),
    ]))
    contenu.append(tab)
    from datetime import datetime
    contenu.append(Paragraph("",empty_line_style))
    contenu.append(Paragraph(f"Imprimé par {req.user} à {datetime.now()}"))
    
    # Construire le PDF avec le canvas personnalisé avec le nombre des pages
    pdf.build(contenu, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    response = HttpResponse(buffer,content_type="application/pdf")
    response['Content-Disposition']='inline;filename="testpdf.pdf"'
    return response

def liste_rsv(req):
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=portrait(A4), leftMargin=72, 
    rightMargin=72,  # marge droite en points
    topMargin=72,  # marge supérieure en points
    bottomMargin=72  # marge inférieure en points
    )
    contenu = []
    w,h=A4
    
    contenu.append(Image("media\images\logo_hnr_gerance.png",w-120,100))
    contenu.append(Paragraph("LISTE DES RESERVATIONS", pol1))
    contenu.append(Paragraph("",empty_line_style))
    
    # ---------------------DONNEES DE LA BDD 
    from riviapp.models import  Reservation, Chambre, Categorie
    rsvs = Reservation.objects.all().order_by('-id')
    data = [['ID RSV','Client','Tél client','Catégorie Chb','Prix nuit','Check In','Check Out','Date rsv']]
    def get_etage(num_etage):
        if num_etage==0:
            return 'Rez-des-chaussez'
        elif num_etage == 1:
            return '1er niveau'
        elif num_etage == 2:
            return '2ème niveau'
        elif num_etage == 3:
            return '3ème niveau'
        else:
            return '4ème niveau'
    i=1
    for rsv in rsvs:
        data.append([Paragraph(f"{rsv.id}", centrer),Paragraph(f"{rsv.client.nom} {rsv.client.postnom}"),Paragraph(rsv.client.tel), Paragraph(rsv.categorie.designation), Paragraph(f"{rsv.prixvalide}"),Paragraph(f"{rsv.datearrivee.strftime("%d-%m-%Y")}"),Paragraph(f"{rsv.datesortie.strftime("%d-%m-%Y")}"),Paragraph(f"{rsv.datejr.strftime("%d-%m-%Y")}")])
        i+=1
    
    tab = Table(data)
    tab.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),red),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
        ('ALIGN',(1,0),(1,-1),'CENTER'),
        ('ALIGN',(0,0),(0,-1),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TEXTCOLOR',(0,0),(-1,0),white),
        ('GRID',(0,0),(-1,-1),.25,red)
    ]))
    contenu.append(tab)
    from datetime import datetime
    contenu.append(Paragraph("",empty_line_style))
    contenu.append(Paragraph(f"Fait à Bukavu, le {datetime.now().strftime('%d %B %Y')}"))
    contenu.append(Paragraph(f"Imprimé par {req.user.username.upper()}"))
    
    # Construire le PDF avec le canvas personnalisé avec le nombre des pages
    pdf.build(contenu, canvasmaker=CustomCanvas)
    buffer.seek(0)
    response = HttpResponse(buffer,content_type="application/pdf")
    response['Content-Disposition']='inline;filename="testpdf.pdf"'
    return response


