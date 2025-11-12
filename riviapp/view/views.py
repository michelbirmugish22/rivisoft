import os
from django.db.models import Count, Sum, F, Q
from django.db.models.functions import TruncDate, TruncMonth
from django.shortcuts import redirect, render, HttpResponse
from riviapp.serializer import * 
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from django.views import View
from django.core.mail import send_mail
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from riviapp.view.mes_methodes import model_vers_dict
from datetime import datetime, timedelta, timezone

# def sendmail(r):
#     if r.POST :
#         try:
#             send_mail(
#                 subject=r.POST['subject'],
#                 message=r.POST['msg'],
#                 from_email='michelbirmugish22@gmail.com',
#                 recipient_list=[r.POST['receiver']],
#                 fail_silently=False
#             )
#         except Exception as e:
#             return HttpResponse(e)
    
#     return render(r, "sendmail.html")


def get_avalable_modules(req):
    modules = Module.objects.all()
    app_name = Configuration.objects.last().name
    return JsonResponse({'modules':model_vers_dict(modules), 'app_name':app_name})


def load_notifications(req):
    objs_dicts = {"obj": {}}
    for c in Notification.objects.all() .order_by('-id'):
        objs_dicts["obj"][str(c.id)] = {
                'id':c.id,
                'texte':c.texte,
                'typen':c.typen,
                'daten':f"{datetime.ctime(c.daten)}",
                # 'daten':datetime.ctime(c.daten),
        }
    context = {
        'nb_notif' : Notification.objects.all().count()-3,
        'notifications':objs_dicts,
    }
    return JsonResponse(context)
# ------------------------------------------------------------------------------
def load_commande_fact(req):    
    context = {
        'commandes':model_vers_dict(CommandeVente.objects.filter(id=CommandeVente.objects.last().id)),
    }
    return JsonResponse(context)
# -------------------------------------------------------------------------------
@login_required(login_url='login')
def info_client_chambre(req, id_cli):
    occ = Enregistrer.objects.get(id=id_cli)
    dif_date = (datetime.now(timezone.utc) - occ.datearr).days
    donnees = {
        'titre':'Informations sur le client en chambre',
        'checkin':Enregistrer.objects.get(id=id_cli),
        'nb_jrs':dif_date+1,
        'tot_valeur':(dif_date+1)*occ.prixnuitee,
    }
    return render(req,"riviera/info_client_chambre.html", donnees)
# -------------------------------------------------------------------------------
@login_required(login_url='login')
def caisse(req):
    if req.method == 'POST':
        Caisse(
            libelle = req.POST['libelle'],
            operateur = Operateur.objects.get(id=req.POST['operateur']),
            mouvement = float(req.POST['montant']),
            utilisateur = req.user,
        ).save()
        return HttpResponse("Effectué")
    
    # somme = Caisse.objects.filter(operateur=5).aggregate(mvt=Sum('mouvement'))
    resultats = Caisse.objects.values('operateur__designation').annotate(mvt_total=Sum('mouvement'))
    donnees = {
        'titre':'CAISSE CENTRALE',
        'operateurs':Operateur.objects.all(),
        'somme_operateurs':resultats,
    }
    return render(req,"riviera/caisse.html", donnees)
# -------------------------------------------------------------------------------
@login_required(login_url='login')
def post_operation_caisse(req):
    p_caisse = False
    if req.POST['p_caisse'] == 1:
        p_caisse = True
    Operateur(
        designation=req.POST['designation'],
        p_caisse = p_caisse,
    ).save()
    return redirect('caisse')
# -------------------------------------------------------------------------------
@login_required(login_url='login')
def home(req):
    def getMois(num):
            mois = ["Janvier","Février","Mars","Avril","Mai","Juin","Juillet","Août","Septembre","Octobre","Novembre","Décembre"]
            return mois[num-1] if num >= 1 and num <= 12 else False
        
    ventes = PaiementFacture.objects.annotate(date_ven=TruncDate('date')).values('date_ven').annotate(somme=Sum('montant'))
    sommes = []
    dates = []
    for v in ventes:
        dates.append(v['date_ven'].strftime('%d-%m-%Y'))
        sommes.append(v['somme'])
    
    
    tot_vente = PaiementFacture.objects.annotate(date_jr=TruncDate('date')).filter(date_jr= datetime.now().date()).aggregate(somme=Sum('montant'))
    tot_vente_mois = PaiementFacture.objects.annotate(mois_actuelle=TruncMonth('date')).filter(mois_actuelle__month=datetime.now().month).aggregate(somme=Sum('montant'))

    def taux(statut):
        nb_cha = Chambre.objects.all().count()
        tx = Chambre.objects.filter(statut=statut).count()
        if nb_cha==0:
            return 0
        return round(tx*100/nb_cha,2)
    nb_chambres_occup_mois=Enregistrer.objects.annotate(chamb=F('nbpax')).values('chambre').annotate(nb_cha=Sum('chamb')).count()
    nb_chambres = Chambre.objects.all().count()
    donnees = {
        'titre':'Tableau de bord',
        'notifications':Notification.objects.all().order_by("-daten"),
        'nb_oc':Chambre.objects.filter(statut='Occupee').count(),
        'tx_oc':taux(statut='Occupee'),
        'nb_ch':nb_chambres,
        'pers':Enregistrer.objects.filter(still_in=1).aggregate(nb_pax=Count('nbpax')),
        'nb_chambres_occup_mois':nb_chambres_occup_mois,
        'taux_occ_mois_chambres':int(nb_chambres_occup_mois*100/nb_chambres),
        'checkins':Enregistrer.objects.filter(still_in = 1),
        'checkins_today':Enregistrer.objects.filter(still_in = 1).annotate(date_jr=TruncDate('datejr')).filter(date_jr=datetime.now().date()).count(),
        'checkout_today':Checkout.objects.annotate(date_jr=TruncDate('datejr')).filter(date_jr=datetime.now().date()).count(),
        'mois_actuelle':f"{getMois(datetime.now().month)} {datetime.now().year}",
        'sommes':sommes,
        'dates':dates,
        'total_vente_today':tot_vente['somme'] if tot_vente['somme'] is not None else 0.0,
        'tot_vente_mois':tot_vente_mois['somme'] if tot_vente_mois['somme'] is not None else 0.0,
        'premiere_vente':Paiement.objects.first().datejr,
        'derniere_vente':Paiement.objects.last().datejr,
        
    }
    return render(req, "riviera/home.html", donnees)

@login_required(login_url='login')
def index(req):
    donnees = {
        'titre':'Tableau de bord',
    }
    return render(req, "riviera/index.html", donnees)
@login_required(login_url='login')
def analyseia(req):
    import pyttsx3

        # Initialiser le moteur
    # moteur = pyttsx3.init() # Obtenir la liste des voix disponibles

    # Sélectionner une voix française
    # moteur.setProperty('voice', 'fr')
            # Définir le texte à lire
            
    texte = f"Hello {req.user.first_name}! I can predict the tornovers at points of sales. I'm your assistant, I was trained for this propose."
    texteAN = f"Bonjour {req.user.first_name}! Je peux prédire le Chiffre d'affaires sur les points des vente. Je suis votre assistant, j'ai été entrainné pour cette fin."

        # Lire le texte
    # moteur.say(texte),
    # moteur=moteur.runAndWait()

        # Exécuter le moteur
    madate = datetime.strptime('2024-09-13','%Y-%m-%d').date()
    def getChambre(num):
        return Chambre.objects.get(id=int(num))
    
    clients_en_chambre = Enregistrer.objects.annotate(total = F('prixnuitee')*F('nbjrs'), prix = F('prixnuitee')).values('chambre').annotate(total_sum=Sum('total'), prix_cha=Sum('prix')).order_by('chambre')
    # Afficher les résultats
    chambres = []
    total_sum_chambre = []
    prix_chambre = []
    for entry in clients_en_chambre:
        chambres.append(f"{(getChambre(entry['chambre']).categorie.designation[0:3]).upper()}{getChambre(entry['chambre']).numero}")
        total_sum_chambre.append(entry['total_sum'])
        prix_chambre.append(entry['prix_cha'])

    
    clients_par_jour = Enregistrer.objects.annotate(par_date=TruncDate("datejr")).values('par_date').annotate(nb_pax=Sum('nbpax'))
    nb=1;som=0
    for ci in clients_par_jour:
        print(f"Date : {ci['par_date']}  NB_CLI:{ci['nb_pax']}")
        som += ci['nb_pax']
        nb += 1
        
    visiteurs_moyenne_jour = round(som/nb,2)
    
    entrees_par_date = Caisse.objects.annotate(par_date=TruncDate('date')).values('par_date').annotate(mouv_par_date=Sum('mouvement')).filter(mouvement__gt=0)
    sorties_par_date = Caisse.objects.annotate(par_date=TruncDate('date')).values('par_date').annotate(mouv_par_date=Sum('mouvement')).filter(mouvement__lt=0)
    
    labels1 = []
    labels2 = []
    total_revenues = []
    total_depenses = []
    for entry in entrees_par_date:
        labels1.append(entry['par_date'].strftime("%d-%m-%Y"))
        total_revenues.append(abs(entry['mouv_par_date']))
    
    for sortie in sorties_par_date:
        labels2.append(sortie['par_date'].strftime("%d-%m-%Y"))
        total_depenses.append(abs(sortie['mouv_par_date']))
    
   
    
    donnees = {
        'titre':'Tendances et prédictions',
        'visiteurs_moyenne_jour':visiteurs_moyenne_jour,
        'total_revenues':total_revenues,
        'total_revenues':total_revenues,
        'total_depenses':total_depenses,
        'labels1':labels1,
        'labels2':labels2,
        'chambres':chambres,
        'total_sum_chambre':total_sum_chambre,
        'prix_chambre':prix_chambre
        
    }
    
    return render(req, "riviera/analyseia.html", donnees)
# --------------------------------------------------------------
@login_required(login_url='login')
def informations(req):
    if req.method == 'POST':
        rem = Remuneration.objects.get(id=req.POST['id_rem'])
        def getMois(num):
            mois = ["Janvier","Février","Mars","Avril","Mai","Juin","Juillet","Août","Septembre","Octobre","Novembre","Décembre"]
            return mois[num-1] if num >= 1 and num <= 12 else False
        rem_data = {
            'id':rem.id,
            'noms':rem.employe.nom + " " + rem.employe.postnom,
            'fonction':rem.employe.fonction,
            'categorie':rem.employe.categorie.code,
            'salbase':rem.employe.categorie.salbase,
            'joursprestes':rem.joursprestes,
            'salbrut':round(rem.salbrut,2),
            'joursmaladie':rem.joursmaladie,
            'sal_jrs_maladie':round(rem.sal_jrs_maladie,2),
            'heure_supp':rem.heure_supp,
            'sal_heure_supp':rem.sal_heure_supp,
            'prime':rem.prime,
            'transport':rem.transport,
            'communication':rem.communication,
            'logement':rem.logement,
            'allocation_fam':rem.allocation_fam,
            'sal_anciennete':rem.sal_anciennete,
            'ipr':rem.ipr,
            'cnss':rem.cnss,
            'onem':rem.onem,
            'inpp':rem.inpp,
            'pret':round(rem.pret,2),
            'avancesursal':round(rem.avancesursal,2),
            'netapayer':round(rem.netapayer,2),
            'periode':f"{getMois(rem.mois)} {rem.annee}",
        } 
        return JsonResponse({"remuneration":rem_data})
    
    
    empl_ = req.GET.get("empl_category") if req.GET.get("empl_category") is not None else "all"
    annee_actuelle = int(req.GET.get("annee")) if req.GET.get("annee") is not None else int(datetime.now().date().strftime("%Y")) 
    mois_actuel = int(req.GET.get("mois")) if req.GET.get("mois") is not None else int(datetime.now().date().strftime("%m")) 
    
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
        
    if all:
        remunerations = Remuneration.objects.filter(mois=mois_actuel, annee=annee_actuelle).order_by('-id')
    if by_service:
        remunerations = Remuneration.objects.filter(mois=mois_actuel, annee=annee_actuelle, employe__service=id_ser).order_by('-id')
    if by_departement:
        remunerations = Remuneration.objects.filter(mois=mois_actuel, annee=annee_actuelle, employe__service__departement=id_dep).order_by('-id')
    if by_employee:
        remunerations = Remuneration.objects.filter(mois=mois_actuel, annee=annee_actuelle, employe=id_emp).order_by('-id')
        
    donnees = {
        'titre':'Informations sur le salaire des employés',
        'remunerations':remunerations,
        'employes':Employe.objects.all().order_by('nom'),
        'services':Service.objects.all().order_by('designation'),
        'departements':Departement.objects.all().order_by('designation'),
        'categories':Categorie_employe.objects.all().order_by('code'),
        'annees':[i for i in range(annee_actuelle-1, annee_actuelle+2)],
        'annee_actuelle':annee_actuelle,
        'mois_actuel':mois_actuel,
        'id_emp':id_emp if 'id_emp' in locals() else id_dep if 'id_dep' in locals() else id_ser if 'id_ser' in locals() else "all",
        'category':'E' if 'id_emp' in locals() else 'D' if 'id_dep' in locals() else 'S' if 'id_ser' in locals() else "all",
    }
    return render(req, "riviera/informations.html", donnees)
# --------------------------------------------------------------
@login_required(login_url='login')
def gest_clients(req):
    
    donnees = {
        'titre' :'Gestion des clients',
        'nbclients': Client.objects.all().count(),
        'clients': Client.objects.all().order_by("nom","postnom"),
    }
    return render(req, "riviera/gest_client.html", donnees)
def night_audit(req):   
    donnees = {
        'titre' :'CLÔTURE DE LA JOURNEE COMPTABLE',
        'date_du_jour': datetime.now().date(),
        'account': Account.objects.last(),
    }
    return render(req, "riviera/night_audit.html", donnees)
def make_night_audit(req):
    account = Account.objects.last()
    account.account_date_room = account.account_date_room + timedelta(days=1)
    account.account_date_pos = account.account_date_pos + timedelta(days=1)
    if account.account_date_room > datetime.now().date() or account.account_date_pos > datetime.now().date():
        return JsonResponse({'error':True})
    
    if account.account_date_room > datetime.now().date():
        account.account_date_room = datetime.now().date()
    if account.account_date_pos > datetime.now().date():
        account.account_date_pos = datetime.now().date()
    account.save()
    return HttpResponse("Night audit effectuée")
# ---------------------------------------------------------------------------------------------------------
# DEMANDE D'ACHAT PRODUIT
# ---------------------------------------------------------------------------------------------------------
def demande_achat(req):
    donnee = {
        'compteur':[i for i in range(1,21)],
        'titre':"Demande d'approvisionnement du stock",
        'articles':Article.objects.all(),
        'fournisseurs':Fournisseur.objects.all(),
        'operateurs':Operateur.objects.filter(p_caisse=1),
        'commandes':CommandeAchat.objects.exclude(etat = 'TERMINE').order_by('-etat'),
    }
    return render(req, "riviera/demande_achat.html", donnee)

def entree_stock(req):
    if req.method == 'POST':
        id_ca = req.POST['id_ca']
        return JsonResponse({'lignes':model_vers_dict(LigneCommandeAchat.objects.filter(commandeachat=id_ca))})
    donnee = {
        'compteur':[i for i in range(1,21)],
        'titre':"Entrée en stock",
        'commandes':CommandeAchat.objects.all().order_by('etat','-id'),
        'articles':Article.objects.all(),
        'fournisseurs':Fournisseur.objects.all(),
    }
    return render(req, "riviera/entree_stock.html", donnee)
# ---------------------------------------------------------------------------------------------------------
# DEMANDE PRODUITS EN STOCK
# ---------------------------------------------------------------------------------------------------------
def demande_stock(req):
    donnee = {
        'compteur':[i for i in range(1,21)],
        'titre':"Demande des produits et consommables en stock",
        'articles':Article.objects.all(),
        'commandes':CommandeStock.objects.all(),
    }
    return render(req, "riviera/demande_stock.html", donnee)

@csrf_exempt
def sortie_stock(req):
    if req.method == 'POST':
        id_ca = req.POST['id_ca']
        return JsonResponse({'lignes':model_vers_dict(LigneCommandeStock.objects.filter(commandestock=id_ca))})
    
    donnee = {
        'compteur':[i for i in range(1,21)],
        'titre':"Sortie en stock",
        'commandes':CommandeStock.objects.all().order_by('etat','-id'),
        'articles':Article.objects.all(),
        'fournisseurs':Fournisseur.objects.all(),
    }
    return render(req, "riviera/sortie_stock.html", donnee)

@csrf_exempt
def rapports_stock(req):    
    donnee = {
        'titre':"Rapports du Stock",
        'com_stocks':CommandeStock.objects.all().order_by('etat','-id'),
        'com_achats':CommandeAchat.objects.all().order_by('etat','-id'),
        'articles':Article.objects.all(),
    }
    return render(req, "riviera/rapports_stock.html", donnee)
# ---------------------------------------------------------------------------------------------------------
# GESTION CLIENTS
# ---------------------------------------------------------------------------------------------------------
 
@method_decorator(csrf_exempt, name='dispatch')  
class PostGetClient(View):
    def get(self, req):
        id = int(req.GET['id'])
        client = Client.objects.get(id=id)
        
        client_data ={
                'id':client.id,
                'nom':client.nom,
                'postnom':client.postnom,
                'sexe':client.sexe,
                'nationalite':client.nationalite,
                'tel':client.tel,
                'mail':client.mail,
                'profession':client.profession,
                'adresse_serv':client.adresse_serv,
                'adresse_rdc':client.adresse_rdc,
                'lieu_nais':client.lieu_nais,
                'date_nais':client.date_nais,
            }
        return JsonResponse({'client':client_data})
    def post(self, req):
        client = Client(
            nom=req.POST['nom'], 
            postnom=req.POST['postnom'], 
            sexe=req.POST['sexe'],
            nationalite=req.POST['nationalite'],
            tel=req.POST['tel'], 
            mail=req.POST['mail'],
            profession=req.POST['profession'],
            adresse_serv=req.POST['adresse_serv'],
            adresse_rdc=req.POST['adresse_rdc'],
            lieu_nais=req.POST['lieu_nais'], 
            date_nais=req.POST['date_nais']
            )
        client.save()
        Notification(texte= f"Ajout d'un client nommé {client.nom} {client.postnom} est effectué par l'utilisateur {req.user}",typen="info").save()
        client_data ={
                'id':client.id,
                'nom':client.nom,
                'postnom':client.postnom,
                'sexe':client.sexe,
                'nationalite':client.nationalite,
                'tel':client.tel,
                'mail':client.mail,
                'profession':client.profession,
                'adresse_serv':client.adresse_serv,
                'adresse_rdc':client.adresse_rdc,
                'lieu_nais':client.lieu_nais,
                'date_nais':client.date_nais,
            }
        return JsonResponse({
            'msg' : 'Enregistrement de '+client.nom+' '+client.postnom+' a été effectué',
            'client':client_data
            })
@method_decorator(csrf_exempt, name='dispatch')
class PutClient(View):
    def post(self, req):
        client = Client.objects.get(id=req.POST['id'])
        client.nom=req.POST['nom']
        client.postnom=req.POST['postnom'] 
        client.sexe=req.POST['sexe'] 
        client.nationalite=req.POST['nationalite']
        client.tel=req.POST['tel']
        client.mail=req.POST['mail']
        client.adresse_serv=req.POST['adresse_serv']
        client.adresse_rdc=req.POST['adresse_rdc']
        client.profession=req.POST['profession']
        client.lieu_nais=req.POST['lieu_nais']
        client.date_nais=req.POST['date_nais']
        client.save()
        print(client)
        Notification(texte=f"La modification du client {client.nom} {client.postnom} est effectuée par l'utilisateur {req.user}",typen="warning").save()
        client_data ={
                'id':client.id,
                'nom':client.nom,
                'postnom':client.postnom,
                'sexe':client.sexe,
                'nationalite':client.nationalite,
                'tel':client.tel,
                'mail':client.mail,
                'profession':client.profession,
                'adresse_serv':client.adresse_serv,
                'adresse_rdc':client.adresse_rdc,
                'lieu_nais':client.lieu_nais,
                'date_nais':client.date_nais,
            }
        return JsonResponse({
            'msg' : 'La modification du client '+client.nom+' '+client.postnom+' a été effectuée.',
            'client':client_data
            })
@csrf_exempt        
def delete_client(req):
    try:
        client = Client.objects.get(id=req.POST['id'])
        Notification(texte=f"Le client {client.nom} {client.postnom} vient d'être supprimé par l'utilisateur {req.user}",typen="danger").save()
        client.delete()
        return JsonResponse({'msg':'Le client '+client.nom+ ' '+ client.postnom +' a été supprimé avec succès'})
    except Exception as e:
        return JsonResponse({'msg':e})

# ---------------------------------------------------------------------------------------------------------------------------
#GRUD BLOCS
@login_required(login_url='login')
def save_bloc(req):
    bloc = Bloc(
        designation=req.POST['designation'],
        nbchamax=req.POST['nbchamax'],
    )
    bloc.save()
    b = Bloc.objects.all().order_by('designation')
    Notification(texte=f"Le bloc {bloc.designation} vient d'être ajouté par {req.user}",  typen='secondary').save()
    return JsonResponse({
        'msg':'Le bloc '+bloc.designation+ ' a été ajouté avec succès', 'blocs':model_vers_dict(b)})
def edit_bloc(req):
    if req.method=='POST':
        bloc = Bloc(
            id=req.POST['id'],
            designation=req.POST['designation'],
            nbchamax=req.POST['nbchamax'], 
        )
        bloc.save()
        Notification(texte=f"Le bloc {bloc.designation} vient d'être modifié par {req.user}", typen='warning').save()
        return JsonResponse({'msg':'Le bloc '+bloc.designation+ ' a été modifié avec succès', 'blocs':model_vers_dict(Bloc.objects.all())})
    bloc = Bloc.objects.get(id=req.GET['id'])
    bloc_data = {
        'id':bloc.id,
        'designation':bloc.designation,
        'nbchamax':bloc.nbchamax,
    } 
    return JsonResponse({'bloc':bloc_data})
def delete_bloc(req):
    print("METHODE = "+req.method)
    bloc = Bloc.objects.get(id=req.POST['id'])
    bloc.delete()
    Notification(texte=f"Le bloc {bloc.designation} est supprimé par {req.user}", typen='danger').save()
    return JsonResponse({'msg':'Le bloc '+bloc.designation+ ' a été supprimé avec succès', 'blocs':model_vers_dict(Bloc.objects.all())})
 
# ---------------------------------------------------------------------------------------------------------------------------
#GRUD CATEGORIE
def save_cat(req):
    print(f"designation = {req.POST['designation']}")
    print(f"prix = {req.POST['prix']}")
    print(f"paxmax = {req.POST['paxmax']}")
    cat = Categorie(
        designation=req.POST['designation'],
        prix=req.POST['prix'],
        paxmax=req.POST['paxmax'],
    )
    cat.save()
    c = Categorie.objects.all().order_by('designation')
    Notification(texte=f"La catégorie {cat.designation} vient d'être ajoutée par {req.user}", typen="info").save()
    return JsonResponse({
        'msg':'La catégorie '+cat.designation+ ' a été ajoutée avec succès', 'categories':model_vers_dict(c)})
def edit_cat(req):
    if req.method=='POST':
        cat = Categorie(
            id=req.POST['id'],
            designation=req.POST['designation'],
            prix=req.POST['prix'],
            paxmax=req.POST['paxmax'],
        )
        cat.save()
        Notification(texte=f"La catégorie {cat.designation} vient d'être modifiée par {req.user}", typen='warning').save()
        return JsonResponse({'msg':'La catégorie '+cat.designation+ ' a été modifiée avec succès', 'categories':model_vers_dict(Categorie.objects.all())})
    cat = Categorie.objects.get(id=req.GET['id'])
    datas = {
        'id':cat.id,
        'designation':cat.designation,
        'prix':cat.prix,
        'paxmax':cat.paxmax,
    } 
    return JsonResponse({'cat':datas})
def delete_cat(req):
    cat = Categorie.objects.get(id=req.POST['id'])
    cat.delete()
    Notification(texte=f"La catégorie {cat.designation} est supprimée par {req.user}", typen='danger').save()
    return JsonResponse({'msg':'La catégorie '+cat.designation+ ' a été supprimée avec succès', 'categories':model_vers_dict(Categorie.objects.all())})
 
# ---------------------------------------------------------------------------------------------------------------------------
#GRUD CHAMBRE
# ---------------------------------------------------------------------------------------------------------------------------
def save_chambre(req):    
    chambre = Chambre(
        numero=req.POST['numero'],
        statut='Libre',
        etage=req.POST['niveau'],
        categorie=Categorie.objects.get(id=req.POST['categorie']),
        bloc=Bloc.objects.get(id=req.POST['bloc']),
    )
    chambre.save()
    c = Chambre.objects.all().order_by('numero')
    Notification(texte=f"La chambre {chambre.numero} vient d'être ajoutée par {req.user}",  typen='secondary').save()
    return JsonResponse({
        'msg':'La chambre '+chambre.numero+ ' a été ajoutée avec succès', 'chambres':model_vers_dict(c)})
def edit_chambre(req):
    if req.method=='POST':
        chambre = Chambre(
            id=req.POST['id'],
            numero=req.POST['numero'],
            statut='Libre',
            etage=req.POST['niveau'],
            categorie=Categorie.objects.get(id=req.POST['categorie']),
            bloc=Bloc.objects.get(id=req.POST['bloc']),
        )
        chambre.save()
        Notification(texte=f"La chambre {chambre.numero} vient d'être modifiée par {req.user}",  typen='warning').save()
        return JsonResponse({'msg':'Le bloc '+chambre.numero+ ' a été modifié avec succès', 'chambres':model_vers_dict(Chambre.objects.all())})
    cha = Chambre.objects.get(id=req.GET['id'])
    datas = {
        'id':cha.id,
        'numero':cha.numero,
        'niveau':cha.etage,
        'categorie':cha.categorie.id,
        'bloc':cha.bloc.id,
    }
    return JsonResponse({'cha':datas})
def delete_chambre(req):
    chambre = Chambre.objects.get(id=req.POST['id'])
    chambre.delete()
    Notification(texte=f"La chambre {chambre.numero} est supprimée par {req.user}", typen='danger').save()
    return JsonResponse({'msg':'La chambre '+chambre.numero+ ' a été supprimée avec succès', 'chambres':model_vers_dict(Chambre.objects.all())})
def chambres_dispos(req):
    rooms = Chambre.objects.filter(statut = "Libre")
    return JsonResponse({'rooms':model_vers_dict(rooms)})    
 
# ---------------------------------------------------------------------------------------------------------------------------
#CRUD BOUTIQUE ET SALLE
# ---------------------------------------------------------------------------------------------------------------------------
def save_bout(req):    
    boutique = Boutique(
        designation=req.POST['designation'],
        numero=req.POST['numero'],
        # image=req.FILES['image'],
        prixmensuel=req.POST['prixmensuel'],
        bloc=Bloc.objects.get(id=req.POST['bloc']),
    )
    boutique.save()
    cc = Boutique.objects.all().order_by('numero')
    Notification(texte=f"La boutique numéro {boutique.numero} vient d'être ajoutée par {req.user}", typen='secondary').save()
    objs_dicts = {"obj": {}}
    for c in cc:
        objs_dicts["obj"][str(c.id)] = {
            'id':c.id,
            'designation':c.designation,
            'numero':c.numero,
            'prixmensuel':c.prixmensuel,
            'image':str(c.image),
            'bloc':c.bloc.id,
        }
    return JsonResponse({
        'msg':'La boutique numéro '+boutique.numero+ ' a été ajoutée avec succès', 'boutiques':objs_dicts})
    
def edit_bout(req):
    if req.method=='POST':
        boutique = Boutique(
            id=req.POST['id'],
            designation=req.POST['designation'],
            numero=req.POST['numero'],
            # image=req.FILE['image'],
            prixmensuel=req.POST['prixmensuel'],
            bloc=Bloc.objects.get(id=req.POST['bloc']),
        )
        boutique.save()
        Notification(texte=f"La boutique numéro {boutique.numero} vient d'être modifiée par {req.user}", typen='warning').save()
        objs_dicts = {"obj": {}}
        for c in Boutique.objects.all():
            objs_dicts["obj"][str(c.id)] = {
                'id':c.id,
                'designation':c.designation,
                'numero':c.numero,
                'prixmensuel':c.prixmensuel,
                'image':str(c.image),
                'bloc':c.bloc.id,
            }
        return JsonResponse({'msg':'La boutique numéro '+boutique.numero+ ' a été modifiée avec succès', 'boutiques':objs_dicts})
    bout = Boutique.objects.get(id=req.GET['id'])
    datas = {
        'id':bout.id,
        'numero':bout.numero,
        'designation':bout.designation,
        'prixmensuel':bout.prixmensuel,
        'image':str(bout.image),
        'bloc':bout.bloc.id,
    }
    return JsonResponse({'bout':datas})
def delete_bout(req):
    boutique = Boutique.objects.get(id=req.POST['id'])
    boutique.delete()
    Notification(texte=f"La boutique {boutique.numero} est supprimée par {req.user}", typen='danger').save()
    objs_dicts = {"obj": {}}
    for c in Boutique.objects.all():
        objs_dicts["obj"][str(c.id)] = {
                'id':c.id,
                'designation':c.designation,
                'numero':c.numero,
                'prixmensuel':c.prixmensuel,
                'image':str(c.image),
                'bloc':c.bloc.id,
        }
    return JsonResponse({'msg':'La boutique numéro '+boutique.numero+ ' a été supprimée avec succès', 'boutiques':objs_dicts})

    
 
# ---------------------------------------------------------------------------------------------------------------------------
#CRUD SALLES
# ---------------------------------------------------------------------------------------------------------------------------
def save_salle(req):    
    salle = Salle(
        designation=req.POST['designation'],
        numero=req.POST['numero'],
        # image=req.FILES['image'],
        prixoccup=req.POST['prixoccup'],
        capacite=req.POST['capacite'],
        bloc=Bloc.objects.get(id=req.POST['bloc']),
    )
    salle.save()
    cc = Salle.objects.all().order_by('designation')
    Notification(texte=f"La salle numéro {salle.numero} vient d'être ajoutée par {req.user}", typen='secondary').save()
    objs_dicts = {"obj": {}}
    for c in cc:
        objs_dicts["obj"][str(c.id)] = {
            'id':c.id,
            'designation':c.designation,
            'numero':c.numero,
            'prixoccup':c.prixoccup,
            'capacite':c.capacite,
            'image':str(c.image),
            'bloc':c.bloc.id,
        }
    return JsonResponse({
        'msg':'La salle numéro '+salle.designation+'#'+salle.numero+ ' a été ajoutée avec succès', 'salles':objs_dicts})
    
def edit_salle(req):
    if req.method=='POST':
        salle = Salle(
            id=req.POST['id'],
            designation=req.POST['designation'],
            numero=req.POST['numero'],
            capacite=req.POST['capacite'],
            # image=req.FILE['image'],
            prixoccup=req.POST['prixoccup'],
            bloc=Bloc.objects.get(id=req.POST['bloc']),
        )
        salle.save()
        Notification(texte=f"La salle  {salle.designation}#{salle.numero} vient d'être modifiée par {req.user}", typen='warning').save()
        objs_dicts = {"obj": {}}
        for c in Salle.objects.all():
            objs_dicts["obj"][str(c.id)] = {
                'id':c.id,
                'designation':c.designation,
                'numero':c.numero,
                'capacite':c.capacite,
                'prixoccup':c.prixoccup,
                'image':str(c.image),
                'bloc':c.bloc.id,
            }
        return JsonResponse({'msg':'La salle '+salle.designation+'#'+salle.numero+ ' a été modifiée avec succès', 'salles':objs_dicts})
    salle = Salle.objects.get(id=req.GET['id'])
    datas = {
        'id':salle.id,
        'numero':salle.numero,
        'designation':salle.designation,
        'capacite':salle.capacite,
        'prixoccup':salle.prixoccup,
        'image':str(salle.image),
        'bloc':salle.bloc.id,
    }
    return JsonResponse({'salle':datas})
def delete_salle(req):
    salle = Salle.objects.get(id=req.POST['id'])
    salle.delete()
    Notification(texte=f"La salle {salle.numero} est supprimée par {req.user}", typen='danger').save()
    objs_dicts = {"obj": {}}
    for c in Salle.objects.all():
        objs_dicts["obj"][str(c.id)] = {
                'id':c.id,
                'designation':c.designation,
                'numero':c.numero,
                'capacite':c.capacite,
                'prixoccup':c.prixoccup,
                'image':str(c.image),
                'bloc':c.bloc.id,
        }
    return JsonResponse({'msg':'La salle numéro '+salle.designation+'#'+salle.numero+ ' a été supprimée avec succès', 'salles':objs_dicts})
#---------------------------------------------------------------------------------------------------------------------------
# CRUD CATEGORIE EMPLOYES
#---------------------------------------------------------------------------------------------------------------------------
def save_categorie_employe(req):    
    cat = Categorie_employe(
        designation = req.POST.get('designation'),
        code = req.POST.get('code'),
        salbase = req.POST.get('salbase'),
    )
    cat.save()
    c = Categorie_employe.objects.all().order_by('code')
    Notification(texte=f"La catégorie {cat.designation} est créée par {req.user}",  typen='secondary').save()
    return JsonResponse({
        'msg':f"La catégorie {cat.designation} est créé avec succès.", 'categories':model_vers_dict(c)})
def edit_categorie_employe(req):
    if req.method == 'POST':
        cat = Categorie_employe.objects.get(id = req.POST.get('id'))
        cat.designation = req.POST.get('designation')
        cat.code = req.POST.get('code')
        cat.salbase = req.POST.get('salbase')
        cat.save()
        c = Categorie_employe.objects.all().order_by('designation')
        Notification(texte=f"La catégorie {cat.designation} est modifié par {req.user}",  typen='warning').save()
        return JsonResponse({
            'msg':f"La catégorie {cat.designation} est modifié avec succès.", 'categories':model_vers_dict(c)})
    c = Categorie_employe.objects.get(id=req.GET['id'])
    datas = {
        'id':c.id,
        'designation':c.designation,
        'code':c.code,
        'salbase':c.salbase,
    }
    return JsonResponse({'categories':datas})

def delete_categorie_employe(req):
    cat = Categorie_employe.objects.get(id = req.POST.get('id'))
    cat.delete()
    
    Notification(texte=f"La catégorie {cat.designation} est supprimé par {req.user}", typen='danger').save()
    c = Categorie_employe.objects.all().order_by('designation')
    objs_dicts = {"obj": {}}
    for c in Categorie_employe.objects.all():
        objs_dicts["obj"][str(c.id)] = {
                    'id':c.id,
                    'designation':c.designation,
                    'code':c.code,
                    'salbase':c.salbase,
        }
    return JsonResponse({'msg':f"La catégorie {cat.designation} est supprimé avec succès", 'categories':objs_dicts})


# ---------------------------------------------------------------------------------------------------------------------------
#GRUD EMPLOYES
# ---------------------------------------------------------------------------------------------------------------------------
def save_employe(req):    
    employe=Employe.objects.create(
    nom = req.POST.get("nom"),
    postnom = req.POST.get("postnom"),
    sexe = req.POST.get("sexe"),
    etat_civil = req.POST.get("etat_civil"),
    nb_enfant = req.POST.get("nb_enfant"),
    date_naiss = req.POST.get("date_naiss"),
    date_engage = req.POST.get("date_engage"), #Pour calculer son ancienneté
    mail = req.POST.get("mail"),
    adresse = req.POST.get("adresse"),
    tel = req.POST.get("tel"),
    niveau_etu = req.POST.get("niveau_etu"),
    fonction = req.POST.get("fonction"),
    nationalite = req.POST.get("nationalite"),
    categorie = Categorie_employe.objects.get(id=req.POST.get("categorie")),
    service = Service.objects.get(id=req.POST.get("service")),
    dossier = req.FILES.get("dossier"),
    )
    
    Notification(texte=f"L'employé {employe.nom} {employe.postnom} est créé par {req.user}",  typen='secondary').save()
    objs_dicts = {"obj": {}}
    for c in Employe.objects.all():
        objs_dicts["obj"][str(c.id)] = {
                'id':c.id,
                'nom':c.nom,
                'postnom':c.postnom,
                'sexe':c.sexe,
                'etat_civil':c.etat_civil,
                'nb_enfant':c.nb_enfant,
                'date_naiss':c.date_naiss,
                'date_engage':c.date_engage,
                'mail':c.mail,
                'tel':c.tel,
                'niveau_etu':c.niveau_etu,
                'adresse':c.adresse,
                'fonction':c.fonction,
                'nationalite':c.nationalite,
                'categorie':c.categorie,
                'dossier':str(c.dossier.name),
                'categorie':c.categorie.id,
                'service':c.service.id,
        }
    return JsonResponse({
        'msg':f"L'employé {employe.nom} {employe.postnom} est créé avec succès.", 'employes':objs_dicts})
def edit_employe(req):
    if req.method == 'POST':
        from django.utils.crypto import get_random_string
        dossier = req.FILES.get("dossier")
        if dossier:
            # Générer un nouveau nom de fichier unique
            extension = os.path.splitext(dossier.name)[1]
            nouveau_nom = f"{get_random_string(10)}{extension}"
            dossier.name = nouveau_nom
        else:
            dossier = Employe.objects.get(id=int(req.POST.get("id"))).dossier
        
        # dossier = req.FILES.get("dossier") if req.FILES.get("dossier") != None else Employe.objects.get(id=int(req.POST.get("id"))).dossier
        employe=Employe(
        id = req.POST.get("id"),
        nom = req.POST.get("nom"),
        postnom = req.POST.get("postnom"),
        sexe = req.POST.get("sexe"),
        etat_civil = req.POST.get("etat_civil"),
        nb_enfant = req.POST.get("nb_enfant"),
        date_naiss = req.POST.get("date_naiss"),
        date_engage = req.POST.get("date_engage"), #Pour calculer son ancienneté
        mail = req.POST.get("mail"),
        adresse = req.POST.get("adresse"),
        tel = req.POST.get("tel"),
        niveau_etu = req.POST.get("niveau_etu"),
        fonction = req.POST.get("fonction"),
        nationalite = req.POST.get("nationalite"),
        categorie = Categorie_employe.objects.get(id=req.POST.get("categorie")),
        service = Service.objects.get(id=req.POST.get("service")),
        dossier = dossier,
        )
        employe.save()
        c = MenuRestau.objects.all().order_by('designation')
        Notification(texte=f"Le informations sur l'employé {employe.nom} sont modifiées par {req.user}",  typen='warning').save()
        objs_dicts = {"obj": {}}
        for c in Employe.objects.all():
            objs_dicts["obj"][str(c.id)] = {
                'id':c.id,
                'nom':c.nom,
                'postnom':c.postnom,
                'sexe':c.sexe,
                'etat_civil':c.etat_civil,
                'nb_enfant':c.nb_enfant,
                'date_naiss':c.date_naiss,
                'date_engage':c.date_engage,
                'mail':c.mail,
                'tel':c.tel,
                'niveau_etu':c.niveau_etu,
                'adresse':c.adresse,
                'fonction':c.fonction,
                'nationalite':c.nationalite,
                'categorie':c.categorie,
                'dossier':str(c.dossier.name),
                'categorie':c.categorie.id,
                'service':c.service.id,
            }
        return JsonResponse({
            'msg':f"Le informations sur l'employé {employe.nom} sont modifiées avec succès.", 'employes':objs_dicts})
    c = Employe.objects.get(id=req.GET['id'])
    datas = {
        'id':c.id,
        'nom':c.nom,
        'postnom':c.postnom,
        'sexe':c.sexe,
        'etat_civil':c.etat_civil,
        'nb_enfant':c.nb_enfant,
        'date_naiss':c.date_naiss,
        'date_engage':c.date_engage,
        'mail':c.mail,
        'tel':c.tel,
        'niveau_etu':c.niveau_etu,
        'adresse':c.adresse,
        'fonction':c.fonction,
        'nationalite':c.nationalite,
        'categorie':c.categorie,
        'dossier':str(c.dossier.name),
        'categorie':c.categorie.id,
        'service':c.service.id,
    }
    return JsonResponse({'employes':datas})

def delete_employe(req):
    employe = Employe.objects.get(id=int(req.POST.get['id']))
    employe.delete()
    Notification(texte=f"L'employé {employe.nom} {employe.postnom} est supprimé par {req.user}", typen='danger').save()
    c = Employe.objects.all().order_by('nom')
    objs_dicts = {"obj": {}}
    for c in Employe.objects.all():
        objs_dicts["obj"][str(c.id)] = {
            'id':c.id,
            'nom':c.nom,
            'postnom':c.postnom,
            'sexe':c.sexe,
            'etat_civil':c.etat_civil,
            'nb_enfant':c.nb_enfant,
            'date_naiss':c.date_naiss,
            'date_engage':c.date_engage,
            'mail':c.mail,
            'tel':c.tel,
            'niveau_etu':c.niveau_etu,
            'adresse':c.adresse,
            'fonction':c.fonction,
            'nationalite':c.nationalite,
            'categorie':c.categorie,
            'dossier':str(c.dossier.name),
            'categorie':c.categorie.id,
            'service':c.service.id,
        }
    return JsonResponse({'msg':f"L'employé {employe.nom} {employe.postnom} supprimé avec succès", 'menus':objs_dicts})
    
    
# ---------------------------------------------------------------------------------------------------------------------------
#GRUD MENU
# ---------------------------------------------------------------------------------------------------------------------------
def save_menu(req):    
    menu = MenuRestau(
        designation = req.POST.get('designation'),
        prix = req.POST.get('prix'),
        typem = req.POST.get('typem'),
        datefin = req.POST.get('datefin'),
        commentaire = req.POST.get('commentaire'),
        urlimage = req.FILES.get('urlimage'),
        groupe = GroupeMenu.objects.get(id=req.POST.get('groupe')),
    )
    menu.save()
    c = MenuRestau.objects.all().order_by('designation')
    Notification(texte=f"Le Menu {menu.designation} est créé par {req.user}",  typen='secondary').save()
    objs_dicts = {"obj": {}}
    for c in MenuRestau.objects.all():
        objs_dicts["obj"][str(c.id)] = {
                'id':c.id,
                'designation':c.designation,
                'prix':c.prix,
                'typem':c.typem,
                'datefin':c.datefin,
                'urlimage':str(c.urlimage.name),
                'groupe':c.groupe.id,
        }
    return JsonResponse({
        'msg':f"Le Menu {menu.designation} est créé avec succès.", 'menus':objs_dicts})
def edit_menu(req):
    if req.method == 'POST':
        menu = MenuRestau.objects.get(id = req.POST.get('id'))
        menu.designation = req.POST.get('designation')
        menu.prix = req.POST.get('prix')
        menu.typem = req.POST.get('typem')
        menu.datefin = req.POST.get('datefin')
        menu.commentaire = req.POST.get('commentaire')
        if req.FILES.get('urlimage') is not None:
            menu.urlimage = req.FILES.get('urlimage')
        menu.groupe = GroupeMenu.objects.get(id=req.POST.get('groupe'))
        
        menu.save()
        c = MenuRestau.objects.all().order_by('designation')
        Notification(texte=f"Le Menu {menu.designation} est modifié par {req.user}",  typen='warning').save()
        objs_dicts = {"obj": {}}
        for c in MenuRestau.objects.all():
            objs_dicts["obj"][str(c.id)] = {
                    'id':c.id,
                    'designation':c.designation,
                    'prix':c.prix,
                    'typem':c.typem,
                    'datefin':c.datefin,
                    'urlimage':str(c.urlimage.name),
                    'groupe':c.groupe.id,
            }
        return JsonResponse({
            'msg':f"Le Menu {menu.designation} est créé avec succès.", 'menus':objs_dicts})
    c = MenuRestau.objects.get(id=req.GET['id'])
    datas = {
        'id':c.id,
        'designation':c.designation,
        'prix':c.prix,
        'typem':c.typem,
        'datefin':c.datefin,
        'urlimage':str(c.urlimage.name),
        'groupe':c.groupe.id,
        'commentaire':c.commentaire,
    }
    return JsonResponse({'menu':datas})

def delete_menu(req):
    menu = MenuRestau.objects.get(id=int(req.POST.get['id']))
    menu.delete()
    Notification(texte=f"Le menu {menu.designation} est supprimé par {req.user}", typen='danger').save()
    c = MenuRestau.objects.all().order_by('designation')
    objs_dicts = {"obj": {}}
    for c in MenuRestau.objects.all():
        objs_dicts["obj"][str(c.id)] = {
                    'id':c.id,
                    'designation':c.designation,
                    'prix':c.prix,
                    'typem':c.typem,
                    'datefin':c.datefin,
                    'urlimage':str(c.urlimage.name),
                    'groupe':c.groupe.id,
        }
    return JsonResponse({'msg':f'Le menu {menu.designation} est supprimé avec succès', 'menus':objs_dicts})

#---------------------------------------------------------------------------------------------------------------------------
# CRUD GROUP DE MENU
#---------------------------------------------------------------------------------------------------------------------------
def save_groupemenu(req):    
    grp = GroupeMenu(
        designation = req.POST.get('designation')
    )
    grp.save()
    c = GroupeMenu.objects.all().order_by('designation')
    Notification(texte=f"Le Menu {grp.designation} est créé par {req.user}",  typen='secondary').save()
    return JsonResponse({
        'msg':f"Le Menu {grp.designation} est créé avec succès.", 'groupes':model_vers_dict(c)})
def edit_groupemenu(req):
    if req.method == 'POST':
        grp = GroupeMenu.objects.get(id = req.POST.get('id'))
        grp.designation = req.POST.get('designation')
        grp.save()
        c = GroupeMenu.objects.all().order_by('designation')
        Notification(texte=f"Le Groupe de Menu {grp.designation} est modifié par {req.user}",  typen='warning').save()
        return JsonResponse({
            'msg':f"Le Menu {grp.designation} est modifié avec succès.", 'groupes':model_vers_dict(c)})
    c = GroupeMenu.objects.get(id=req.GET['id'])
    datas = {
        'id':c.id,
        'designation':c.designation,
    }
    return JsonResponse({'groupe':datas})

def delete_groupemenu(req):
    grp = GroupeMenu.objects.get(id = req.POST.get('id'))
    grp.delete()
    
    Notification(texte=f"Le Groupe de Menu {grp.designation} est supprimé par {req.user}", typen='danger').save()
    c = GroupeMenu.objects.all().order_by('designation')
    objs_dicts = {"obj": {}}
    for c in GroupeMenu.objects.all():
        objs_dicts["obj"][str(c.id)] = {
                    'id':c.id,
                    'designation':c.designation
        }
    return JsonResponse({'msg':f'Le groupe {grp.designation} est supprimé avec succès', 'groupes':objs_dicts})
# ---------------------------------------------------------------------------------------------------------------------------
#GRUD POINTS DE VENTE
#---------------------------------------------------------------------------------------------------------------------------
def save_pdv(req):
    pdv = PointVente(
        designation=req.POST['designation'],
    )
    pdv.save()
    b = PointVente.objects.all().order_by('designation')
    Notification(texte=f"Le point de vente {pdv.designation} vient d'être ajouté par {req.user}",  typen='secondary').save()
    return JsonResponse({
        'msg':'Le point de vente '+pdv.designation+ ' a été ajouté avec succès', 'pdvs':model_vers_dict(b)})
def edit_pdv(req):
    if req.method=='POST':
        pdv = PointVente(
            id=req.POST['id'],
            designation=req.POST['designation'],
        )
        pdv.save()
        Notification(texte=f"Le point de vente {pdv.designation} vient d'être modifié par {req.user}", typen='warning').save()
        return JsonResponse({'msg':'Le point de vente '+pdv.designation+ ' a été modifié avec succès', 'pdvs':model_vers_dict(PointVente.objects.all())})
    pdv = PointVente.objects.get(id=req.GET['id'])
    pdv_data = {
        'id':pdv.id,
        'designation':pdv.designation,
    } 
    return JsonResponse({'pdv':pdv_data})
def delete_pdv(req):
    pdv = PointVente.objects.get(id=req.POST['id'])
    pdv.delete()
    Notification(texte=f"Le point de vente {pdv.designation} est supprimé par {req.user}", typen='danger').save()
    return JsonResponse({'msg':'Le point de vente '+pdv.designation+ ' a été supprimé avec succès', 'pdvs':model_vers_dict(PointVente.objects.all())})
# ---------------------------------------------------------------------------------------------------------------------------
#GRUD ENTREPRISE
#---------------------------------------------------------------------------------------------------------------------------
def save_entreprise(req):
    ese = Entreprise(
        nom=req.POST['nom'],
        activite=req.POST['activite'],
        adresse=req.POST['adresse'],
        notre_relation=req.POST['notre_relation'],
    )
    ese.save()
    b = Entreprise.objects.all().order_by('nom')
    Notification(texte=f"L'Entreprise {ese.nom} vient d'être ajoutée par {req.user}",  typen='secondary').save()
    return JsonResponse({
        'msg':'L''Entreprise'+ese.nom+ ' a été ajoutée avec succès', 'entreprises':model_vers_dict(b)})
def edit_entreprise(req):
    if req.method=='POST':
        ese = Entreprise(
            id=req.POST['id'],
            nom=req.POST['nom'],
            activite=req.POST['activite'],
            adresse=req.POST['adresse'],
            notre_relation=req.POST['notre_relation'],
        )
        ese.save()
        Notification(texte=f"L'entreprise {ese.nom} vient d'être modifiée par {req.user}", typen='warning').save()
        return JsonResponse({'msg':'L''entreprise '+ese.nom+ ' a été modifiée avec succès', 'entreprises':model_vers_dict(Entreprise.objects.all())})
    ese = Entreprise.objects.get(id=req.GET['id'])
    data = {
        'id':ese.id,
        'nom':ese.nom,
        'adresse':ese.adresse,
        'activite':ese.activite,
        'notre_relation':ese.notre_relation,
    } 
    return JsonResponse({'ese':data})
def delete_entreprise(req):
    ese = Entreprise.objects.get(id=req.POST['id'])
    ese.delete()
    Notification(texte=f"L'entreprise {ese.nom} est supprimé par {req.user}", typen='danger').save()
    return JsonResponse({'msg':'L''entreprise '+ese.nom+ ' a été supprimé avec succès', 'entreprises':model_vers_dict(Entreprise.objects.all())})
# ---------------------------------------------------------------------------------------------------------------------------
#GRUD ENTREPRISE
#---------------------------------------------------------------------------------------------------------------------------
def save_fournisseur(req):
    fss = Fournisseur(
        nom=req.POST['nom'],
        postnom=req.POST['postnom'],
        tel=req.POST['tel'],
        mail=req.POST['mail'],
        adresse_serv=req.POST['adresse'],
        type_ese=req.POST['type_ese'],
        utilisateur = req.user,
    )
    fss.save()
    b = Fournisseur.objects.all().order_by('nom')
    Notification(texte=f"Le fournisseur {fss.nom} vient d'être ajouté par {req.user}",  typen='secondary').save()
    return JsonResponse({
        'msg':'Le fourniisseur '+fss.nom+ ' a été ajouté avec succès', 'fournisseurs':model_vers_dict(b)})
def edit_fournisseur(req):
    if req.method=='POST':
        fss = Fournisseur(
            id=req.POST['id'],
            nom=req.POST['nom'],
            postnom=req.POST['postnom'],
            tel=req.POST['tel'],
            mail=req.POST['mail'],
            adresse_serv=req.POST['adresse'],
            type_ese=req.POST['type_ese'],
            utilisateur = req.user,
        )
        fss.save()
        Notification(texte=f"Le fournisseur {fss.nom} vient d'être modifié par {req.user}", typen='warning').save()
        return JsonResponse({'msg':'Le fournisseur '+fss.nom+ ' a été modifié avec succès', 'fournisseurs':model_vers_dict(Fournisseur.objects.all())})
    fss = Fournisseur.objects.get(id=req.GET['id'])
    data = { 
        'id':fss.id,
        'nom':fss.nom,
        'postnom':fss.postnom,
        'tel':fss.tel,
        'mail':fss.mail,
        'adresse':fss.adresse_serv,
        'type_ese':fss.type_ese,
    } 
    return JsonResponse({'fournisseur':data})
def delete_fournisseur(req):
    fss = Fournisseur.objects.get(id=req.POST['id'])
    fss.delete()
    Notification(texte=f"Le fournisseur {fss.nom} est supprimé par {req.user}", typen='danger').save()
    return JsonResponse({'msg':'Le fournisseur '+fss.nom+ ' a été supprimé avec succès', 'fournisseurs':model_vers_dict(Fournisseur.objects.all())})
#---------------------------------------------------------------------------------------------------------------------------
#GRUD DEPARTEMENT ET SERVICE
#---------------------------------------------------------------------------------------------------------------------------
def save_departement(req):
    dep = Departement(
        designation=req.POST['designation'],
    )
    dep.save()
    b = Departement.objects.all().order_by('designation')
    Notification(texte=f"Le département {dep.designation} vient d'être ajouté par {req.user}",  typen='secondary').save()
    return JsonResponse({
        'msg':'Le département '+dep.designation+ ' a été ajouté avec succès', 'departements':model_vers_dict(b)})
def edit_departement(req):
    if req.method=='POST':
        dep = Departement(
            id=req.POST['id'],
            designation=req.POST['designation'],
        )
        dep.save()
        Notification(texte=f"Le département {dep.designation} vient d'être modifié par {req.user}", typen='warning').save()
        return JsonResponse({'msg':'Le département '+dep.designation+ ' a été modifié avec succès', 'departements':model_vers_dict(Departement.objects.all())})
    dep = Departement.objects.get(id=req.GET['id'])
    dep_data = {
        'id':dep.id,
        'designation':dep.designation,
    } 
    return JsonResponse({'departement':dep_data})
def delete_departement(req):
    dep = Departement.objects.get(id=req.POST['id'])
    dep.delete()
    Notification(texte=f"Le département {dep.designation} est supprimé par {req.user}", typen='danger').save()
    return JsonResponse({'msg':'Le département '+dep.designation+ ' a été supprimé avec succès', 'departements':model_vers_dict(Departement.objects.all())})
#-----------------------------------------------------------------------------------
def save_service(req):
    ser = Service(
        designation=req.POST['designation'],
        departement=Departement.objects.get(id=req.POST['departement']),
    )
    ser.save()
    b = Service.objects.all().order_by('designation')
    Notification(texte=f"Le département {ser.designation} vient d'être ajouté par {req.user}",  typen='secondary').save()
    return JsonResponse({
        'msg':'Le département '+ser.designation+ ' a été ajouté avec succès', 'services':model_vers_dict(b)})
def edit_service(req):
    if req.method=='POST':
        ser = Service(
            id=req.POST['id'],
            designation=req.POST['designation'],
            departement=Departement.objects.get(id=req.POST['departement']),
        )
        ser.save()
        Notification(texte=f"Le service {ser.designation} vient d'être modifié par {req.user}", typen='warning').save()
        return JsonResponse({'msg':'Le service '+ser.designation+ ' a été modifié avec succès', 'services':model_vers_dict(Service.objects.all())})
    ser = Service.objects.get(id=req.GET['id'])
    dep_data = {
        'id':ser.id,
        'designation':ser.designation,
        'departement':ser.departement.id,
    } 
    return JsonResponse({'service':dep_data})
def delete_service(req):
    ser = Service.objects.get(id=req.POST['id'])
    ser.delete()
    Notification(texte=f"Le service {ser.designation} est supprimé par {req.user}", typen='danger').save()
    return JsonResponse({'msg':'Le service '+ser.designation+ ' a été supprimé avec succès', 'services':model_vers_dict(Service.objects.all())})

#---------------------------------------------------------------------------------------------------------------------------
#GRUD GROUPE STOCK
#---------------------------------------------------------------------------------------------------------------------------
def save_stock(req):
    stock = Stock(
        designation=req.POST['designation'],
        utilisateur = req.user,
    )
    stock.save()
    b = Stock.objects.all().order_by('designation')
    Notification(texte=f"Le stock {stock.designation} vient d'être ajouté par {req.user}",  typen='secondary').save()
    return JsonResponse({
        'msg':'Le stock '+stock.designation+ ' a été ajouté avec succès', 'stocks':model_vers_dict(b)})
def edit_stock(req):
    if req.method=='POST':
        stock = Stock(
            id=req.POST['id'],
            designation=req.POST['designation'],
            utilisateur = req.user,
        )
        stock.save()
        Notification(texte=f"Le stock {stock.designation} vient d'être modifié par {req.user}", typen='warning').save()
        return JsonResponse({'msg':'Le stock '+stock.designation+ ' a été modifié avec succès', 'stocks':model_vers_dict(Stock.objects.all())})
    stock = Stock.objects.get(id=req.GET['id'])
    stock_data = {
        'id':stock.id,
        'designation':stock.designation,
    } 
    return JsonResponse({'pdv':stock_data})
def delete_stock(req):
    stock = Stock.objects.get(id=req.POST['id'])
    stock.delete()
    Notification(texte=f"Le stock {stock.designation} est supprimé par {req.user}", typen='danger').save()
    return JsonResponse({'msg':'Le stock '+stock.designation+ ' a été supprimé avec succès', 'stocks':model_vers_dict(Stock.objects.all())})
#---------------------------------------------------------------------------------------------------------------------------
#GRUD GROUPE ARTICLE
#---------------------------------------------------------------------------------------------------------------------------
def save_groupe_article(req):
    gp = Groupe_article(
        designation=req.POST['designation'],
        stock = Stock.objects.get(id=req.POST['id_stock']),
        utilisateur = req.user,
    )
    gp.save()
    b = Groupe_article.objects.all().order_by('designation')
    Notification(texte=f"Le groupe d'article {gp.designation} vient d'être ajouté par {req.user}",  typen='secondary').save()
    return JsonResponse({
        'msg':'Le stock '+gp.designation+ ' a été ajouté avec succès', 'groupes':model_vers_dict(b)})
def edit_groupe_article(req):
    if req.method=='POST':
        gp = Groupe_article(
            id=req.POST['id'],
            designation=req.POST['designation'],
            stock = Stock.objects.get(id=req.POST['id_stock']),
            utilisateur = req.user,
        )
        gp.save()
        Notification(texte=f"Le groupe {gp.designation} vient d'être modifié par {req.user}", typen='warning').save()
        return JsonResponse({'msg':'Le groupe d\'article '+gp.designation+ ' a été modifié avec succès', 'stocks':model_vers_dict(Groupe_article.objects.all())})
    gp = Groupe_article.objects.get(id=req.GET['id'])
    gp_data = {
        'id':gp.id,
        'stock':gp.stock.id,
        'designation':gp.designation,
    } 
    return JsonResponse({'groupes':gp_data})
def delete_groupe_article(req):
    gp = Groupe_article.objects.get(id=req.POST['id'])
    gp.delete()
    Notification(texte=f"Le groupe d'article {gp.designation} est supprimé par {req.user}", typen='danger').save()
    return JsonResponse({'msg':'Le groupe d\'article '+gp.designation+ ' a été supprimé avec succès', 'groupes':model_vers_dict(Groupe_article.objects.all())})
#---------------------------------------------------------------------------------------------------------------------------
#GRUD ARTICLE
#---------------------------------------------------------------------------------------------------------------------------
def save_article(req):
    art = Article(
        designation=req.POST['designation'],
        qte= req.POST['qte'],
        prixu = req.POST['prix'],
        last_pachat = req.POST['prix'],
        unitmsr = req.POST['unitmsr'],
        groupe = Groupe_article.objects.get(id=req.POST['groupe']),
        utilisateur = req.user,
    )
    art.save()
    b = Article.objects.all().order_by('designation')
    Notification(texte=f"Le groupe d'article {art.designation} vient d'être ajouté par {req.user}",  typen='secondary').save()
    return JsonResponse({
        'msg':'Le stock '+art.designation+ ' a été ajouté avec succès', 'articles':model_vers_dict(b)})
def edit_article(req):
    if req.method=='POST':
        print(f"Utilisateur = {req.user}")
        art = Article(
            id=req.POST['id'],
            designation=req.POST['designation'],
            qte= req.POST['qte'],
            prixu = req.POST['prix'],
            last_pachat = req.POST['prix'],
            unitmsr = req.POST['unitmsr'],
            groupe = Groupe_article.objects.get(id=req.POST['groupe']),
            utilisateur = Utilisateur.objects.get(username=req.user),
        )
        art.save()
        Notification(texte=f"Le produit du stock {art.designation} vient d'être modifié par {req.user}", typen='warning').save()
        return JsonResponse({'msg':'Le produit d\'article '+art.designation+ ' a été modifié avec succès', 'articles':model_vers_dict(Article.objects.all())})
    art = Article.objects.get(id=req.GET['id'])
    art_data = {
        'id':art.id,
        'groupe':art.groupe.id,
        'unitmsr':art.unitmsr,
        'qte':art.qte,
        'prixu':art.prixu,
        'designation':art.designation,
    } 
    return JsonResponse({'article':art_data})
def delete_article(req):
    art = Article.objects.get(id=req.POST['id'])
    art.delete()
    Notification(texte=f"Le produit d'article {art.designation} est supprimé par {req.user}", typen='danger').save()
    return JsonResponse({'msg':'Le produit d\'article '+art.designation+ ' a été supprimé avec succès', 'articles':model_vers_dict(Article.objects.all())})
#---------------------------------------------------------------------------------------------------------------------------
#GRUD AUTRES REVENUES
#---------------------------------------------------------------------------------------------------------------------------
def save_arevenu(req):
    arevenu = AutreRevenu(
        designation=req.POST['designation'],
    )
    arevenu.save()
    b = AutreRevenu.objects.all().order_by('designation')
    Notification(texte=f"Le révenu {arevenu.designation} vient d'être ajouté par {req.user}",  typen='secondary').save()
    return JsonResponse({
        'msg':'Le révenu '+arevenu.designation+ ' a été ajouté avec succès', 'arevenus':model_vers_dict(b)})
def edit_arevenu(req):
    if req.method=='POST':
        arevenu = AutreRevenu(
            id=req.POST['id'],
            designation=req.POST['designation'],
        )
        arevenu.save()
        Notification(texte=f"Le révenu {arevenu.designation} vient d'être modifié par {req.user}", typen='warning').save()
        return JsonResponse({'msg':'Le révenu '+arevenu.designation+ ' a été modifié avec succès', 'arevenus':model_vers_dict(AutreRevenu.objects.all())})
    arevenu = AutreRevenu.objects.get(id=req.GET['id'])
    arevenu_data = {
        'id':arevenu.id,
        'designation':arevenu.designation,
    } 
    return JsonResponse({'arevenu':arevenu_data})
def delete_arevenu(req):
    arevenu = AutreRevenu.objects.get(id=req.POST['id'])
    arevenu.delete()
    Notification(texte=f"Le révenu {arevenu.designation} est supprimé par {req.user}", typen='danger').save()
    return JsonResponse({'msg':'Le révenu '+arevenu.designation+ ' a été supprimé avec succès', 'arevenus':model_vers_dict(AutreRevenu.objects.all())})
#---------------------------------------------------------------------------------------------------------------------------
#GRUD AUTRES TARIF
#---------------------------------------------------------------------------------------------------------------------------
def save_atarif(req):
    tar = TarifAutreRevenu(
        designation=req.POST['designation'],
        prix=float(req.POST['prix']),
        autrerevenu=AutreRevenu.objects.get(id=req.POST['autrerevenu']),
    )
    tar.save()
    b = TarifAutreRevenu.objects.all().order_by('designation')
    Notification(texte=f"Le tarif {tar.designation} vient d'être ajouté par {req.user}",  typen='secondary').save()
    return JsonResponse({
        'msg':'Le tarif '+tar.designation+ ' a été ajouté avec succès', 'tarifs':model_vers_dict(b)})
def edit_atarif(req):
    if req.method=='POST':
        arevenu = TarifAutreRevenu(
            id=req.POST['id'],
            designation=req.POST['designation'],
            prix=float(req.POST['prix']),
            autrerevenu=AutreRevenu.objects.get(id=req.POST['autrerevenu']),
        )
        arevenu.save()
        Notification(texte=f"Le tarif {arevenu.designation} vient d'être modifié par {req.user}", typen='warning').save()
        return JsonResponse({'msg':'Le tarif '+arevenu.designation+ ' a été modifié avec succès', 'tarifs':model_vers_dict(TarifAutreRevenu.objects.all())})
    arevenu = TarifAutreRevenu.objects.get(id=req.GET['id'])
    arevenu_data = {
        'id':arevenu.id,
        'designation':arevenu.designation,
        'prix':arevenu.prix,
        'autrerevenu':arevenu.autrerevenu.id,
    } 
    return JsonResponse({'tarif':arevenu_data})
def delete_atarif(req):
    arevenu = TarifAutreRevenu.objects.get(id=req.POST['id'])
    arevenu.delete()
    Notification(texte=f"Le tarif {arevenu.designation} est supprimé par {req.user}", typen='danger').save()
    return JsonResponse({'msg':'Le tarif '+arevenu.designation+ ' a été supprimé avec succès', 'tarifs':model_vers_dict(AutreRevenu.objects.all())})


