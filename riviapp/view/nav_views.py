from datetime import time, datetime
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum,Q,F
from django.db.models.functions import TruncDate
from django.shortcuts import render, HttpResponse
from riviapp.models import * 
from django.contrib.auth.decorators import login_required
from riviapp.view.envoi_mail import envoyer_mail

@login_required(login_url='login')
def menumaster(req):
    donnees = {
        'titre':'Création de Menu',
        'groupes':GroupeMenu.objects.all().order_by('designation'),
        'menus':MenuRestau.objects.all().order_by('designation')
    }
    return render(req, "riviera/menu_master.html", donnees)
# ----------------------------------------------------------------
@login_required(login_url='login')
def employes(req):
    donnees = {
        'titre':'Gestion des employers',
        'services':Service.objects.all().order_by('designation'),
        'employers':Employe.objects.all().order_by('nom'),
        'categories':Categorie_employe.objects.all().order_by('code')
    }
    return render(req, "riviera/employes.html", donnees)
# ----------------------------------------------------------------
@login_required(login_url='login')
def registre_employes(req):
    donnees = {
        'titre':'Registre des employés',
        'employes':Employe.objects.all().order_by('nom'),
    }
    return render(req, "riviera/registre_employes.html", donnees)
# --------------------------------------------------------------
@login_required(login_url='login')
def bases_salariales(req):
    annee_actuelle = int(datetime.now().date().strftime("%Y"))
    mois_actuel = int(datetime.now().date().strftime("%m"))
    donnees = {
        'titre':'Configuration d\'élements du salaire des employés',
        'employes':Employe.objects.all().order_by('nom'),
        'services':Service.objects.all().order_by('designation'),
        'departements':Departement.objects.all().order_by('designation'),
        'categories':Categorie_employe.objects.all().order_by('code'),
        'annees':[i for i in range(annee_actuelle-1, annee_actuelle+2)],
        'annee_actuelle':annee_actuelle,
        'mois_actuel':mois_actuel,
    }
    return render(req, "riviera/bases_salariales.html", donnees)
# --------------------------------------------------------------
@login_required(login_url='login')
def octroi_prets(req):
    donnees = {
        'titre':'Dettes et prêts des agents',
        'employes':Employe.objects.all().order_by('nom'),
        'services':Service.objects.all().order_by('designation'),
        'departements':Departement.objects.all().order_by('designation'),
        'categories':Categorie_employe.objects.all().order_by('code'),
    }
    return render(req, "riviera/octroi_prets.html", donnees)
# --------------------------------------------------------------

@login_required(login_url='login')
def bloc(req):
    donnees = {
        'titre':'Gestion des blocs',
        'blocs':Bloc.objects.all().order_by('designation')
    }
    return render(req, "riviera/bloc.html", donnees)
# ----------------------------------------------------------------
@login_required(login_url='login')
def chambre(req):
    donnees = {
        'titre':'Gestion des chambres',
        'chambres':Chambre.objects.all().order_by('numero'),
        'blocs':Bloc.objects.all().order_by('designation'),
        'categories':Categorie.objects.all().order_by('designation'),
    }
    return render(req, "riviera/chambre.html", donnees)
# ----------------------------------------------------------------
@login_required(login_url='login')
def statut_chambre(req):
    from django.db.models import OuterRef, Subquery, Max
    # Sous-requête pour obtenir le dernier enregistrement pour chaque chambre
    latest_enregistrement = Enregistrer.objects.filter(
        chambre=OuterRef('pk')
    ).order_by('-datearr')
    # Requête principale pour obtenir la liste des chambres avec le dernier enregistrement si occupée
    chambres = Chambre.objects.annotate(
        checkin_id=Subquery(latest_enregistrement.values('id')[:1])
    )
    # Précharger les enregistrements correspondants
    enregistrements = Enregistrer.objects.filter(
        id__in=[chambre.checkin_id for chambre in chambres]
    )
    # Associer les enregistrements aux chambres
    chambre_dict = {chambre.id: chambre for chambre in chambres}
    for enregistrement in enregistrements:
        chambre_dict[enregistrement.chambre_id].checkin = enregistrement
    # for chambre in chambres:
    #     print(f"Chambre: {chambre.numero}, Statut: {chambre.statut}")
    #     if hasattr(chambre, 'checkin'):
    #         print(f"Dernier enregistrement: {chambre.checkin.datearr}")
    def taux(statut):
        nb_cha = Chambre.objects.all().count()
        tx = Chambre.objects.filter(statut=statut).count()
        return round(tx*100/nb_cha,2)
    donnees = {
        'titre':'Statut des chambres',
        'chambres':chambres,
        'nb_oc':Chambre.objects.filter(statut='Occupee').count(),
        'tx_oc':taux(statut='Occupee'),
        'nb_bl':Chambre.objects.filter(statut='Bloquee').count(),
        'tx_bl':taux(statut='Bloquee'),
        'nb_hs':Chambre.objects.filter(statut='HS').count(),
        'tx_hs':taux(statut='HS'),
        'nb_sl':Chambre.objects.filter(statut='Sale').count(),
        'tx_sl':taux(statut='Sale'),
        'nb_lb':Chambre.objects.filter(statut='Libre').count(),
        'tx_lb':taux(statut='Libre'),
        'nb_rsv':Chambre.objects.filter(statut='Rsv').count(),
        'tx_rsv':taux(statut='Rsv'),
        'nb_ch':Chambre.objects.all().count(),
        # 'checkins':Enregistrer.objects.filter(still_in = 1),
    }
    return render(req, "riviera/statut_cha.html", donnees)

# ----------------------------------------------------------------
@login_required(login_url='login')
def statut_salles(req):
    salles = Salle.objects.all()
    def taux(statut):
        nb_cha = Chambre.objects.all().count()
        tx = Chambre.objects.filter(statut=statut).count()
        return round(tx*100/nb_cha,2)
    donnees = {
        'titre':'Statut des salles',
        'salles':salles,
    }
    return render(req, "riviera/statut_salles.html", donnees)
def rsv_salle_form(req):
    id_salle = req.GET['id_salle']   
    from datetime import datetime
    date_sys = Account.objects.get(id=1).account_date_room
    date_sys = datetime.combine(date_sys, time.max).date()
    
    salle = Salle.objects.get(id=id_salle)
    entreprise = Entreprise.objects.all()
    occupation = Enregistrer.objects.filter(still_in=1)

    donnees = {
        'titre':'Réservation',
        'salle':salle,
        'entreprises':entreprise,
        'occupations':occupation,
    }
    return render(req, "riviera/rsv_salle_form.html", donnees)

@login_required(login_url='login')
def deposit_form(req):
    id_ci = req.GET['id_ci']   
    from datetime import datetime
    date_sys = Account.objects.get(id=1).account_date_room
    date_sys = datetime.combine(date_sys, time.max).date()
    
    enregistrement = Enregistrer.objects.get(id=id_ci)
    
    #Calcul de la différence entre la date réelle de sortie du client et la date du jour dans le système.
    diff = (date_sys - enregistrement.datearr.astimezone(timezone.get_current_timezone()).date()).days #En jours

    nbjr = diff if diff > enregistrement.nbjrs else enregistrement.nbjrs
    prix = float(enregistrement.prixnuitee)
    avance = float(enregistrement.avance)
    
    print(f"NBJR={nbjr}, prix={type(prix)}, avance={type(avance)}")
    reste = ((nbjr) * prix ) - avance
    
    payements_extras_rec = Paiement.objects.filter(occupation=id_ci, extra=True).aggregate(tot_mnt=Sum('montant'))
    dette_extras_pdv = PaiementFacture.objects.filter(occupation=id_ci).aggregate(tot_mnt=Sum('montant'))
    
    dette_extras = dette_extras_pdv["tot_mnt"] if dette_extras_pdv["tot_mnt"] is not None else 0.0
    payements_extras = payements_extras_rec["tot_mnt"] if payements_extras_rec["tot_mnt"] is not None else 0.0
    
    dette_extras = dette_extras - payements_extras
    
    print(f"DETTES EXTRAS = {dette_extras} -TYPE={type(dette_extras)}")
    print(f"RESTE = {reste} -TYPE={type(reste)}")
    donnees = {
        'titre':'Déposit / Paiement',
        'operateurs':Operateur.objects.all(),
        'checkin':enregistrement,
        'nuitees':nbjr,
        'dette_extras':float(dette_extras),
        'reste':float(reste),
        'total_a_payer':float(reste)+float(dette_extras),
    }
    print(f"===========================\ID_CI = {id_ci }\n Chambre {enregistrement.chambre.numero} Paiement\n ===============")
    return render(req, "riviera/deposit.html", donnees)
# ----------------------------------------------------------------
@login_required(login_url='login')
def checkout_form(req):
    if req.method == 'POST':
        checkout = Checkout.objects.create(
            checkin = Enregistrer.objects.get(id=req.POST.get('checkin')),
            datesor = Account.objects.last().account_date_room,
            nuitees = req.POST.get("nuitees"),
            montant_extra = req.POST.get("montant_extra"),
            montant_accom = req.POST.get("montant_accom"),
            credit = True if req.POST.get('entreprise') is not None else False,
            # client = Enregistrer.objects.get(id=req.POST.get('client')),
            # entreprise = Entreprise.objects.get(id=req.POST.get('entreprise')) if req.POST.get('entreprise') is not None else None,
        )
        if checkout is not None:
            enreg = Enregistrer.objects.get(id=req.POST.get('checkin'))
            enreg.still_in = 0
            enreg.save()
            cha = Chambre.objects.get(id=enreg.chambre.id)
            cha.statut = "Sale"
            cha.save()
            
            ci=Enregistrer.objects.get(id=req.POST.get('checkin'))
            sexe = "Monsieur" if ci.client.sexe == 'M' else 'Madame'
            envoyer_mail("Gratitude",f"Bonjour {sexe} {ci.client.nom} {ci.client.postnom}, merci d'avoir choisi l'Hôel New Riviera Bukavu. Bienvenu encore !","michelbirmugish22@gmail.com",{ci.client.mail})
            
        return JsonResponse({'msg':f"Le client {checkout.checkin.client.nom} de la chambre {checkout.checkin.chambre.numero} a été réglé avec succès."})
        
    id_ci = req.GET.get("id_ci")
    occ = Enregistrer.objects.get(id = id_ci)

    date_sys = Account.objects.get(id=1).account_date_room
    date_sys = datetime.combine(date_sys, time.max).date()
    
    #Calcul de la différence entre la date réelle de sortie du client et la date du jour dans le système.
    diff = (date_sys - occ.datearr.astimezone(timezone.get_current_timezone()).date()).days #En jours

    nbjr = diff #Le checkout concerne les jours valablement logés. Donc la date d'arrivée moins la date du système.
    prix = float(occ.prixnuitee)
    avance = float(occ.avance)
    
    total_accom = nbjr * prix 
    total_accom = total_accom if total_accom >= 0 else 0.0
    reste_accom = total_accom - avance
    
    payements_extras_rec = Paiement.objects.filter(occupation=id_ci, extra=True).aggregate(tot_mnt=Sum('montant'))
    dette_extras_pdv = PaiementFacture.objects.filter(occupation=id_ci).aggregate(tot_mnt=Sum('montant'))
    
    total_dette_extras = dette_extras_pdv["tot_mnt"] if dette_extras_pdv["tot_mnt"] is not None else 0.0
    total_payements_extras = payements_extras_rec["tot_mnt"] if payements_extras_rec["tot_mnt"] is not None else 0.0
    
    dette_extras = total_dette_extras - total_payements_extras
    
    dette_totale = reste_accom + dette_extras
    total_a_payer = total_dette_extras + total_accom
    enregistrement = {
            'titre':'Check out / Réglément',
            'id':occ.id,
            'checkin':occ,
            'new_datesor':date_sys,
            'nuitees':int(nbjr),
            'total_accom':total_accom,
            'reste_accom':reste_accom,
            'total_dette_extras':total_dette_extras,
            'total_a_payer':total_a_payer,
            'dette_extras':dette_extras,
            'dette_totale':dette_totale,
            'entreprises':Entreprise.objects.all(),
            'enregistrements':Enregistrer.objects.filter(still_in=1, entreprise=occ.entreprise),
        }
    return render(req, "riviera/checkout.html", enregistrement)


@login_required(login_url='login')
def salle(req):
    donnees = {
        'titre':'Gestion des salles et Boutiques',
        'salles':Salle.objects.all(),
        'boutiques':Boutique.objects.all(),
        'blocs':Bloc.objects.all(),
    }
    return render(req, "riviera/salle.html", donnees)

# ----------------------------------------------------------------
@login_required(login_url='login')
def pdv(req):
    donnees = {
        'titre':'Points de vente',
        'pdvs':PointVente.objects.all(),
    }
    return render(req, "riviera/pdv.html", donnees)
# ----------------------------------------------------------------
@login_required(login_url='login')
def entreprise(req):
    donnees = {
        'titre':'Créations des Entreprises parténaires',
        'entreprises':Entreprise.objects.all(),
    }
    return render(req, "riviera/entreprise.html", donnees)
# ----------------------------------------------------------------
@login_required(login_url='login')
def fournisseur(req):
    donnees = {
        'titre':'Créations des nos fournisseurs',
        'fournisseurs':Fournisseur.objects.all(),
    }
    return render(req, "riviera/fournisseur.html", donnees)
# ------------------------------------------------------------------
@login_required(login_url='login')
def departement(req):
    donnees = {
        'titre':'Création des départements',
        'departements':Departement.objects.all(),
        'services':Service.objects.all(),
    }
    return render(req, "riviera/departement.html", donnees)
#-------------------------------------------------------------------
@login_required(login_url='login')
def stock(req):
    donnees = {
        'titre':'Création des Stocks',
        'stocks':Stock.objects.all(),
    }
    return render(req, "riviera/stock.html", donnees)
@login_required(login_url='login')
def arevenu(req):
    donnees = {
        'titre':'Création des autres revenues',
        'arevenus':AutreRevenu.objects.all(),
        'tarifs':TarifAutreRevenu.objects.all(),
    }
    return render(req, "riviera/autrerevenu.html", donnees)

@login_required(login_url='login')
def fact(req):
    date1 = req.GET.get("date1")
    date2 = req.GET.get("date2")
    if date1 and date2:
        from datetime import date 
        d1 = date.fromisoformat(date1)
        d2 = date.fromisoformat(date2)
    else:
        from datetime import timedelta
        today = datetime.now().date()
        d1 = today - timedelta(days=10)
        d2 = today
    commandes=LigneCommandeVente.objects.all()
    reglements = PaiementFacture.objects.annotate(date_jr=TruncDate('date')).filter(date_jr__range=(d1,d2))
    donnees = {
        'compteur':[i for i in range(1,21)],
        'titre':'FACTURATION',
        'date_pdv':Account.objects.last().account_date_pos,
        'checkins':Enregistrer.objects.filter(still_in=1),
        'entreprises':Entreprise.objects.all(),
        'pdvs':PointVente.objects.all(),
        'menus':MenuRestau.objects.all(),
        'factures':CommandeVente.objects.filter(etat='Commande', total__gt=-1).order_by('-id'),
        'reglements':reglements,
        'commandes':commandes,
        'date1':d1,
        'date2':d2,
    }
    print("Date du jour ets : ", donnees['date_pdv'])
    return render(req, "riviera/facturation.html", donnees)

def reservation(req):
    donnees = {
        'compteur':[i for i in range(1,21)],
        'titre':'RESERVATION CHAMBRE',
        'clients':Client.objects.all(),
        'categories':Categorie.objects.all(),
        'reservations':Reservation.objects.filter(etat_rsv='Encours'),
    }
    return render(req, "riviera/rsv.html", donnees)
def checkin_page(req):
    donnees = {
        'compteur':[i for i in range(1,21)],
        'titre':'ENREGISTREMENT (CHECK IN)',
        'chambres':Chambre.objects.filter(statut = 'Libre'),
        'clients':Client.objects.all(),
        'categories':Categorie.objects.all(),
        'entreprises':Entreprise.objects.all(),
        'reservations':Reservation.objects.filter(etat_rsv='Encours'),
        'checkins':Enregistrer.objects.filter(still_in = 1),
    }
    return render(req,"riviera/checkin.html", donnees)
    
def article(req):
    donnees = {
        'titre':'Création d\'Articles',
        'stocks':Stock.objects.all(),
        'groupes':Groupe_article.objects.all(),
        'articles':Article.objects.all(),
    }
    return render(req, "riviera/article.html", donnees)