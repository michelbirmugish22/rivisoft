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
    # Convertion de la date HTML en Date Python
    date1 = datetime.strptime(req.POST['date1'], "%Y-%m-%d").date() if req.method == "POST" else datetime.strptime(req.GET['date1'], "%Y-%m-%d").date()
    # date2 = datetime.strptime(req.POST['date2'], "%Y-%m-%d").date() if req.method == "POST" else datetime.strptime(req.GET['date2'], "%Y-%m-%d").date()
    date2 = datetime.now().date()
    # Convertir les dates en datetime
    start_datetime = datetime.combine(date1, time.min)  # 2024-01-01 00:00:00
    end_datetime = datetime.combine(date2, time.max)      # 2024-12-31 23:59:59
    
    style1 = ParagraphStyle("s1",fontName="Helvetica-Bold",fontSize=14, alignment=TA_CENTER)
    style2 = ParagraphStyle("s1",fontName="Helvetica-Bold",fontSize=11, spaceBefore=5, alignment=TA_JUSTIFY)
    style3 = ParagraphStyle("s3",fontName="Helvetica-Oblique",fontSize=9)
    buffer = io.BytesIO()
    # pdf = SimpleDocTemplate(buffer, pagesize=A4)
    pdf = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    page = []
    large, haut = A4
    
    page.append(Image("media\images\logo_hnr_gerance.png",large,70))
    page.append(Paragraph(f"VALEUR DU STOCK DU {date1.strftime("%d/%m/%Y")} AU {date2.strftime("%d/%m/%Y")}", style1))




    page.append(Table([[""]]))
    data = [["","","","STOCK INITIAL","","","ENTREES","","","SORTIES","","","STOCK FINAL","","",]]
    data.append(["ID","Désignation","Unité","QTE","PU","PT","QTE","PU","PT","QTE","PU","PT","QTE","PU","PT"])
    
    commandes_achat = CommandeAchat.objects.filter(datea__gte=date1, datea__lte=date2)
    commandes_sortie = CommandeStock.objects.filter(datec__gte=date1, datec__lte=date2)
    total_entrees = 0
    total_sorties = 0

    i = 2; j=3; k=[];
    from django.db.models import Sum, F, FloatField, Q

    # Préparer les données
    # data = []

    # Calculer les totaux d'entrées et de sorties
    articles = Article.objects.annotate(
        total_entrees=Sum('lignecommandeachat__qte', filter=Q(lignecommandeachat__commandeachat__in=commandes_achat)),
        total_sorties=Sum('lignecommandestock__qte', filter=Q(lignecommandestock__commandestock__in=commandes_sortie)),
        qte_init=F('qte') + F('total_sorties') - F('total_entrees'),
        valeur_initial=F('prixu') * (F('qte') + F('total_sorties') - F('total_entrees')),
        valeur_entree=F('prixu') * F('total_entrees'),
        valeur_sortie=F('prixu') * F('total_sorties')
    ).select_related('groupe__stock')

    # Organiser les articles par groupe
    grouped_articles = {}
    for prod in articles:
        group_name = prod.groupe.designation
        if group_name not in grouped_articles:
            grouped_articles[group_name] = []
        grouped_articles[group_name].append(prod)
        
    total_general_initial = 0
    total_general_entrees = 0
    total_general_sorties = 0
    total_general_final = 0
    
    # Parcourir les groupes et les articles pour préparer les données pour l'affichage
    for group_name, prods in grouped_articles.items():
        i+=1
        k.append(i)
        data.append([f"{group_name}"])
        # Initialiser les totaux pour le groupe
        total_qte_init = 0.0
        total_valeur_initial = 0.0
        tot_entrees = 0.0
        total_valeur_entree = 0.0
        tot_sorties = 0.0
        total_valeur_sortie = 0.0
        total_valeur_total = 0.0
        
        for prod in prods:
            # Convertir les valeurs en types natifs avant d'arrondir
            # Vérifier si les valeurs sont None avant de les convertir
            qte_init = float(prod.qte_init) if prod.qte_init is not None else 0.0
            total_entrees = float(prod.total_entrees) if prod.total_entrees is not None else 0.0
            total_sorties = float(prod.total_sorties) if prod.total_sorties is not None else 0.0
            valeur_initial = float(prod.valeur_initial) if prod.valeur_initial is not None else 0.0
            valeur_entree = float(prod.valeur_entree) if prod.valeur_entree is not None else 0.0
            valeur_sortie = float(prod.valeur_sortie) if prod.valeur_sortie is not None else 0.0
            valeur_total = float(prod.qte * prod.prixu) if prod.qte is not None and prod.prixu is not None else 0.0
            
            # Ajouter les valeurs aux totaux du groupe
            total_qte_init += qte_init
            total_valeur_initial += valeur_initial
            tot_entrees += total_entrees
            total_valeur_entree += valeur_entree
            tot_sorties += total_sorties
            total_valeur_sortie += valeur_sortie
            total_valeur_total += valeur_total
            
            
            i+=1
            data.append([f"{prod.id}",f"{prod.designation}",f"{prod.unitmsr}",f"{qte_init}",f"{prod.prixu}",f"{round(valeur_initial,2)}",f"{total_entrees}",f"{prod.prixu}",f"{round(valeur_entree,2)}",f"{round(total_sorties,2)}",f"{prod.prixu}",f"{round(valeur_sortie,2)}",f"{prod.qte}",f"{prod.prixu}",f"{round(valeur_total,2)}"])
        i+=1
        data.append(["","Totaux","",f"{total_qte_init}","",f"{round(total_valeur_initial, 2)}",f"{tot_entrees}","",f"{round(total_valeur_entree, 2)}",f"{round(tot_sorties, 2)}","",f"{round(total_valeur_sortie, 2)}","","",f"{round(total_valeur_total, 2)}"])
        total_general_initial += total_valeur_initial
        total_general_entrees += total_valeur_entree
        total_general_sorties += total_valeur_sortie
        total_general_final += total_valeur_total
        
    data.append(["GRAND TOTAL","","","","",f"{round(total_general_initial,2)}","","",f"{round(total_general_entrees,2)}","","",f"{round(total_general_sorties,2)}","","",f"{round(total_general_final,2)}"]) 
    tab = Table(data)
     
    for kk in k:
        print(kk)
        tab.setStyle(TableStyle([
        ('SPAN', (0, kk-1), (-1, kk-1)),
        ("FACE",(0, kk-1), (-1, kk-1),"Helvetica-Bold"),
        ("FACE",(0, kk-2), (-1, kk-2),"Helvetica-BoldOblique"),
    ]))
    # for sto in Stock.objects.all():   
    #     for grp in Groupe_article.objects.filter(stock_id=sto.id):
    #         for prod in Article.objects.filter(groupe_id=grp.id):
    #             for com_a in commandes_achat:
    #                 for ligne in LigneCommandeAchat.objects.filter(article_id=prod.id, commandeachat=com_a):
    #                     total_entrees += ligne.qte
    #                     print(ligne)
                        
    #             for com_s in commandes_sortie:
    #                 for ligne in LigneCommandeStock.objects.filter(article_id=prod.id, commandestock=com_s):
    #                     total_sorties += ligne.qte

    #             id_prod = prod.id
    #             unitmsr_prod = prod.unitmsr
    #             designation = prod.designation
    #             qte_fin = prod.qte
    #             prixu_init = prod.prixu
    #             qte_entree = total_entrees
    #             qte_sortie = total_sorties
    #             valeur_entree = round(prod.prixu * total_entrees,2)
    #             valeur_sortie = round(prod.prixu * total_sorties,2)
    #             qte_init = qte_fin + qte_sortie - qte_entree  #Valeur du stock Initial 
    #             valeur_initial = round(prod.prixu * qte_init,2)
    #             #AFFICHAGE
    #             data.append([f"{id_prod}",f"{designation}",f"{unitmsr_prod}",f"{grp.designation}",f"{qte_init}",f"{prixu_init}",f"{valeur_initial}",f"{qte_entree}",f"{prixu_init}",f"{valeur_entree}",f"{qte_sortie}",f"{prixu_init}",f"{valeur_sortie}",f"{prod.qte}",f"{prod.prixu}",f"{prod.qte*prod.prixu}"])
   
                
       

    
    
    # d=[]
    # #Pour colorer le tableau ligne après ligne
    # lig=0
    # while lig <= j+k:
    #     for col in range(5):
    #         d.append(('BACKGROUND',(col,lig),(-1,lig), "#e9e9e9"))
    #     lig += 2
    # tab.setStyle(TableStyle(d))
        
    tab.setStyle(TableStyle([
        ("SPAN",(3,0),(5,0)),
        ("SPAN",(6,0),(8,0)),
        ("SPAN",(9,0),(11,0)),
        ("SPAN",(12,0),(14 ,0)),
        ("SPAN",(0,-1),(2 ,-1)),
        ("FACE",(0,-1),(-1 ,-1), "Helvetica-Bold"),
        ("FACE",(0,-2),(-1 ,-2), "Helvetica-BoldOblique"),
        ("TEXTCOLOR",(0,0),(-1,1),colors.white),
        ("BACKGROUND",(0,0),(-1,1),colors.red),
        ("GRID",(0,0),(-1,1),.5,colors.red),
        ("GRID",(0,0),(-1,-1),.1,"#909090"),
        ("BACKGROUND",(3,2),(5,-1),"#eeeefe"),
        ("BACKGROUND",(6,2),(8,-1),"#feeeef"),
        ("BACKGROUND",(9,2),(11,-1),"#eeeefe"),
        ("BACKGROUND",(12,2),(14,-1),"#feeeef"),
        ("ALIGN",(3,2),(-1,-1),"RIGHT"),
    ]))
    
    page.append(tab)
    page.append(Table([[""],[""]]))
    page.append(Table([[Paragraph("imprimé le "+ datetime.now().strftime("%d/%m/%Y  à %H:%M:%S")+" par " + req.user.username.upper(), ParagraphStyle("st",fontName='Times-Italic'))]]))
    pdf.build(page, canvasmaker=CustomCanvas)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"]=f'inline; filename="journal_de_caise_{date1}_au_{date2}.pdf"'
    return response