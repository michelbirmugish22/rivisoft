import tempfile
from django.http import HttpResponse
import io

from reportlab.lib import colors 
from reportlab.lib.units import mm, inch
from riviapp.models import *
from riviapp.rapports.classe_rp.classes_personnalisees import CustomCanvas
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image
from reportlab.lib.colors import *
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from num2words import num2words
from datetime import datetime
from django.utils import timezone
from django.db.models import Count
from reportlab_qrcode import QRCodeImage #Pour générer le code QR

def index(req,id_emp, mois, annee):  
    def getMois(num):
        mois = ["Janvier","Février","Mars","Avril","Mai","Juin","Juillet","Août","Septembre","Octobre","Novembre","Décembre"]
        return mois[num-1] if num >= 1 and num <= 12 else False
            
    # Convertion de la date HTML en Date Python
    style1 = ParagraphStyle("s1",fontName="Helvetica-Bold",fontSize=14, alignment=TA_CENTER)
    style2 = ParagraphStyle("s1",fontName="Helvetica-Bold",fontSize=12, spaceBefore=5, alignment=TA_JUSTIFY)
    style3 = ParagraphStyle("s3",fontName="Helvetica-Oblique",fontSize=9)
    
    id_emp = id_emp if id_emp is not None else 3
    annee_actuelle = annee if annee is not None else int(datetime.now().date().strftime("%Y")) 
    mois_actuel = mois if mois is not None else int(datetime.now().date().strftime("%m")) 
    
    rem = Remuneration.objects.get(mois=mois_actuel, annee=annee_actuelle, employe=id_emp)
    
    
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)
    page = []
    large, haut = A4
    
    page.append(Image("media\images\logo_hnr_gerance.png",large-140,90))
    page.append(Paragraph(f"BULLETIN DE PAIE DU MOIS DE {getMois(mois_actuel).upper()} {annee_actuelle}", style1))
    page.append(Table([[""]]))
    jrs_payables = 30
    sal_jour = rem.employe.categorie.salbase / jrs_payables
    t=Table([
        ["NOM et POSTNOM ",f"{rem.employe.nom} {rem.employe.postnom}",""," ",Paragraph("Nombre des jours payables"),f": {jrs_payables}"],
        ["CATEGORIE ",f"{rem.employe.categorie.code}",""," ","Nombre des jours prestés",f": {rem.joursprestes}"],
        ["DEPARTEMENT ",f"{rem.employe.service.departement.designation}",""," ","Nbre des jours maladie",f": {rem.joursmaladie}"],
        ["SERVICE ",f"{rem.employe.service.designation}",""," ","Nbre des heures supplémentaires",f": {rem.heure_supp}"],
        ["FONCTION ",f"{rem.employe.fonction}",""," ","Nbre des jours de congé",f": {0}"],
        ["SALAIRE DE BASE ",f"USD {rem.employe.categorie.salbase}",""," ","",f""],
    ])
    t.setStyle(TableStyle([
        ('FONTNAME',(1,0),(1,-1),'Helvetica-Bold'),
        ('FONTNAME',(3,0),(3,-1),'Helvetica-Bold'),
        ('FONTNAME',(5,0),(5,-1),'Helvetica-Bold'),
    ]))
    page.append(t)


    page.append(Table([[""]]))
    tot_gain = rem.salbrut+rem.sal_jrs_maladie+rem.sal_heure_supp+rem.prime+rem.sal_anciennete+rem.transport+rem.transport+rem.allocation_fam
    tot_retenu = rem.ipr+rem.cnss+rem.avancesursal+rem.pret
    
    t=Table([
        [Paragraph("GAINS", style2),f"","",Paragraph("RETENUS", style2),f""],
        ["Salaire jours prestés ",f"{round(rem.salbrut,2)}","","IPR",f"{rem.ipr}"],
        ["Salaire jours maladie ",f"{round(rem.sal_jrs_maladie,2)}","","CNSS",f"{rem.cnss}"],
        ["Salaire heures supplémentaires ",f"{round(rem.sal_heure_supp,2)}","","ONEM",f"{rem.onem}"],
        ["Salaire jours congés ",f"{0.0}","","INPP",f"{rem.inpp}"],
        ["Primes ",f"{rem.prime}","","Retenues absences",f"{0.0}"],
        ["Ancienneté ",f"{round(rem.sal_anciennete,2)}","","Retenues maladie",f"{0.0}"],
        ["Transport ",f"{rem.transport}","","Avance sur salaire",f"{rem.avancesursal}"],
        ["Logement ",f"{rem.logement}","","Remboursement prêt",f"{rem.pret}"],
        ["Allocation familliale ",f"{rem.allocation_fam}","","",f" "],
        ["Total gains ",f"{round(tot_gain,2)}","","Total rétenus",f"{round(tot_retenu,2)}"],
    ])
    t.setStyle(TableStyle([
        ('GRID', (0,1),(1,-1),0.1,"#505050"),
        ('GRID', (3,1),(-1,-1),0.1,"#505050"),
        ('FACE', (0,-1),(-1,-1),"Helvetica-BoldOblique"),
    ]))
    page.append(t)
    page.append(Table([[""]]))
    page.append(Paragraph(f"NET A PAYER : {round(tot_gain-tot_retenu,2)} USD", style2))
    page.append(Paragraph(f"Nous disons : {num2words(round(tot_gain-tot_retenu,2), lang="fr")} dollars américains.", style3))

    
    
    # ---------------------------------------------------QRCODE
    data_qr = {
        # 'paiement_id':rem.id,
        'paiement_date':rem.dater.astimezone(timezone.get_current_timezone()).strftime("%d-%m-%Y"),
        # 'employee_id':rem.employe.id,
        'employee_name':rem.employe.nom + " " + rem.employe.postnom, 
        'employee_month_paid':getMois(rem.mois),
        'employee_amount_paid':f"{round(rem.netapayer,2)}  USD",
        # 'website':"hotellerie.groupetaverne.com",
    }
    qr_code = QRCodeImage(data_qr,size=80,fill_color="#ef0000",border=10)
    page.append(qr_code)
    # ---------------------------------------------------
    page.append(Table([[""]]))
    page.append(Table([[Paragraph("Bénéficiaire"),"","",Paragraph("Caissier Principal")]]))
    white=ParagraphStyle("wh",textColor=colors.white)
    t = Table([[Paragraph("xxxxxxxxxxxx xxxxxxxxxxx xxxxxxxxxxxx xxxxxxxxxxxxxx",white),"","",""]])
    t.setStyle(TableStyle([
        ('GRID',(0,0),(0,-1),0.5,"#666666"),
        ('GRID',(-1,0),(-1,-1),0.5,"#666666"),
        ]))
    page.append(t)
    
    #♥ Validation de paiement 
    if rem.paid == False:
        rem.paid = True 
        rem.date_paid = datetime.now()
        Caisse.objects.create(
            mouvement = - rem.netapayer,
            libelle = f"Paiement salaire agent {rem.employe.nom} {rem.employe.postnom} mois de {getMois(mois)} {annee}",
            operateur = Operateur.objects.filter(p_caisse=1).first(),
            utilisateur = req.user 
        )
        rem.save()
    
    
    page.append(Paragraph("imprimé le "+ datetime.now().strftime("%d/%m/%Y  à %H:%M:%S")+" par " + req.user.username.upper(), ParagraphStyle("st",fontName='Times-Italic',spaceBefore=10, alignment=TA_RIGHT)))
    pdf.build(page, canvasmaker=CustomCanvas)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"]=f'inline; filename="Bulletin {getMois(mois_actuel)} {annee_actuelle}-{rem.employe.nom} {rem.employe.postnom}.pdf"'
    return response