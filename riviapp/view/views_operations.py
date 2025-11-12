from datetime import datetime, time
from django.shortcuts import render, HttpResponse, redirect # type: ignore
from django.db.models import Sum, F # type: ignore
from django.db.models.functions import TruncDate
from django.http import JsonResponse # type: ignore
from riviapp.view.mes_methodes import model_vers_dict
from riviapp.view.envoi_mail import envoyer_mail
from riviapp.models import * 

def vente(req):
    date = Account.objects.last().account_date_pos
    id_client = req.POST['id_client']
    id_pdv = req.POST['pdv']
    
    # Je réunitialise d'abord les tableaux
    id_prod = {}
    qte_ven = {}
    pu_prod = {}
    tot_v = 0 

    print(f"Point de vente : {PointVente.objects.get(id=id_pdv).designation}")
    print("Date = ",date)
    vente = CommandeVente(
        datev = date,
        etat = "Commande",
        typev = "RAS",
        total = 0,
        caissier = Utilisateur.objects.get(username=req.user.username),
        pointvente = PointVente.objects.get(id=id_pdv),
        client= Client.objects.get(id=id_client)
    )
    vente.save()
    
    for i in range(1,21):  
        if 'id_prod' + str(i) in req.POST and len(req.POST['qte_ven'+str(i)]) > 0:
            id_prod[i] = int(req.POST['id_prod'+str(i)])
            qte_ven[i] = int(req.POST['qte_ven'+str(i)])
            pu_prod[i] = MenuRestau.objects.get(id=id_prod[i]).prix
            tot_v += qte_ven[i] * pu_prod[i]
            
            ligne_vente = LigneCommandeVente(
                qte = qte_ven[i],
                menu = MenuRestau.objects.get(id=id_prod[i]),
                commandevente = vente,
            )
            ligne_vente.save()
    #MAJ Commande Vente. On met le total
    vente.total = tot_v
    vente.datev = date
    vente.save()
    return HttpResponse("C Bon")  


def annuler_facture(req):
    id_com = req.POST['id_com']
    com = CommandeVente.objects.get(id=id_com)
    com.etat = 'Annulee'
    com.save()
    return HttpResponse("Annulée")  

def payer_facture_vente(req):
    id_com = req.POST['id_com']
    mnt_fact = req.POST['mnt_fact']
    mode = req.POST['mode']
    com = CommandeVente.objects.get(id=id_com)
    com.etat = 'PAYEE'
    com.save()
    paie = PaiementFacture()
    paie.montant = mnt_fact
    paie.mode = mode
    if mode == 'CHAMBRE':
        paie.occupation = Enregistrer.objects.get(id=req.POST['payer_chambre'])
    else:
        paie.numero = req.POST['numero_mode']
    paie.vente = com
    paie.utilisateur = req.user
    paie.save()
    return HttpResponse("Payement effectué")  

# ==============================================================================================
def reservation(req):
    nom_cli = Client.objects.get(id=int(req.POST['id_cli'])).nom + " " + Client.objects.get(id=int(req.POST['id_cli'])).postnom
    Reservation(
        mode = req.POST['mode'],
        prixvalide = req.POST['prix'],
        datearrivee = req.POST['date1'],
        datesortie = req.POST['date2'],
        nbadultes = req.POST['nbadulte'],
        nbenfants = req.POST['nbenfant'],
        nbchambre = req.POST['nbchamb'],
        autresinfos = req.POST['autre_info'],
        etat_rsv = 'Encours',
        client = Client.objects.get(id=req.POST['id_cli']),
        categorie = Categorie.objects.get(id=req.POST['id_cat'])
    ).save()
    if req.POST['montant']:
        difference = Reservation.objects.last().datesortie-Reservation.objects.last().datearrivee
        total_du = Reservation.objects.last().prixvalide * Reservation.objects.last().nbchambre * abs(difference.days)
        Paiement(
            montant = req.POST['montant'],
            mode = "Cash", #M-Pesa, Airtel money, Visa ou Cash
            libelle = "Avance réservation effectuée par "+ Client.objects.get(id=req.POST['id_cli']).nom,
            reste = float(total_du)-float(req.POST['montant']),
            reservation = Reservation.objects.last()
        ).save()
        print(f"Avance réservation effectuée par {Client.objects.get(id=req.POST['id_cli']).nom}")
    objs_dicts = {"obj": {}}
    for rsv in Reservation.objects.filter(etat_rsv='Encours'):
        objs_dicts["obj"][str(rsv.id)] = {
            'id':rsv.id,
            'prixvalide':rsv.prixvalide,
            'datearrivee':rsv.datearrivee,
            'datesortie':rsv.datesortie,
            'client':rsv.client.nom,
            'categorie':rsv.categorie.designation,
        }
    # return redirect(to='reservation_pdf', id_rsv =Reservation.objects.last().id)
    return JsonResponse({'msg':f'La réservation de {nom_cli} est enregistrée avec succès', 'reservations':objs_dicts})

def edit_reservation(req):
    nom_cli = Client.objects.get(id=int(req.POST['id_cli'])).nom + " " + Client.objects.get(id=int(req.POST['id_cli'])).postnom
    Reservation(
        id = req.POST['id_rsv'],
        mode = req.POST['mode'],
        prixvalide = req.POST['prix'],
        datearrivee = req.POST['date1'],
        datesortie = req.POST['date2'],
        nbadultes = req.POST['nbadulte'],
        nbenfants = req.POST['nbenfant'],
        nbchambre = req.POST['nbchamb'],
        autresinfos = req.POST['autre_info'],
        etat_rsv = 'Encours',
        client = Client.objects.get(id=req.POST['id_cli']),
        categorie = Categorie.objects.get(id=req.POST['id_cat'])
    ).save()
    objs_dicts = {"obj": {}}
    for rsv in Reservation.objects.filter(etat_rsv='Encours'):
        objs_dicts["obj"][str(rsv.id)] = {
            'id':rsv.id,
            'prixvalide':rsv.prixvalide,
            'datearrivee':rsv.datearrivee,
            'datesortie':rsv.datesortie,
            'client':rsv.client.nom,
            'categorie':rsv.categorie.designation,
        }
    # return JsonResponse({'msg':f'La réservation de {nom_cli} est modifiée avec succès', 'reservations':objs_dicts})
    from riviapp.view.reservation_pdf import index
    return index(req=req, id=Reservation.objects.last().id)

def delete_reservation(req):
    rsv = Reservation.objects.get(id=req.POST['id_rsv'])
    rsv.etat_rsv='annulee'
    rsv.raison_annul=req.POST['raison_annul']
    rsv.save()
    
    objs_dicts = {"obj": {}}
    for rsv in Reservation.objects.filter(etat_rsv='Encours'):
        objs_dicts["obj"][str(rsv.id)] = {
            'id':rsv.id,
            'prixvalide':rsv.prixvalide,
            'datearrivee':rsv.datearrivee,
            'datesortie':rsv.datesortie,
            'client':rsv.client.nom,
            'categorie':rsv.categorie.designation,
        }
    return JsonResponse({'msg':f'La réservation est annulée avec succès', 'reservations':objs_dicts})

def get_one_reservations(req):
    rsv = Reservation.objects.get(id=req.GET['id'])
    datas = {
        'id':rsv.id,
        'mode':rsv.mode,
        'prixvalide':rsv.prixvalide,
        'datearrivee':rsv.datearrivee,
        'datesortie':rsv.datesortie,
        'nbadultes':rsv.nbadultes,
        'nbenfants':rsv.nbenfants,
        'nbchambre':rsv.nbchambre,
        'autresinfos':rsv.autresinfos,
        'etat_rsv':rsv.etat_rsv,
        'client':rsv.client.id,
        'categorie':rsv.categorie.id,
    }
    return JsonResponse({'reservations':datas})
# -----------------------------------------------------------------------------------------------------
def checkin(req):
    Enregistrer(
        datearr = req.POST['date1'],
        datesor = req.POST['date2'],
        provenance = req.POST['provenance'],
        destination = req.POST['destination'],
        prixnuitee= req.POST['prixnuitee'],
        avance= req.POST['avance'],
        nbpax=req.POST['nbpax'],
        client = Client.objects.get(id=req.POST['id_cli']),
        entreprise = Entreprise.objects.get(id=req.POST['id_ese']),
        chambre = Chambre.objects.get(id=req.POST['id_chambre']),
    ).save()
    Piece_indentite(
        designation = req.POST['designation_piece'],
        numero = req.POST['numero_piece'],
        date_livre = req.POST['date_livre_piece'],
        date_expire = req.POST['date_expire_piece'],
        lieu_livre = req.POST['lieu_livre_piece'],
        client = Client.objects.get(id=req.POST['id_cli']),
    ).save()
    if req.POST['avance']:
        difference = Enregistrer.objects.last().datesor-Enregistrer.objects.last().datearr
        total_du = Enregistrer.objects.last().prixnuitee * abs(difference.days)
        Paiement(
            montant = req.POST['avance'],
            mode = "Cash", #M-Pesa, Airtel money, Visa ou Cash
            libelle = "Avance checkin chambre "+ Chambre.objects.get(id=req.POST['id_chambre']).numero + ", client : " + Client.objects.get(id=req.POST['id_cli']).nom,
            reste = float(total_du)-float(req.POST['avance']),
            occupation = Enregistrer.objects.last()
        ).save()
    objs_dicts = {"obj": {}}
    for occ in Enregistrer.objects.all():
        objs_dicts["obj"][str(occ.id)] = {
            'id':occ.id,
            'datejr':occ.datejr,
            'datearr':occ.datearr,
            'datesor':occ.datesor,
            'provenance':occ.provenance,
            'destination':occ.destination,
            'prixnuitee':occ.prixnuitee,
            'avance':occ.avance,
            'nbpax':occ.nbpax,
            'still_in':occ.still_in,
            'client':occ.client.nom,
            'entreprise':occ.entreprise.nom,
            'chambre':occ.chambre.numero,
        }
    return JsonResponse({'msg':f'L''enregistrement du client {nom_cli} dans la chambre {chambre} est effectué avec succès', 'enregistrements':objs_dicts})
    
def change_status_chambre(req):
    if req.method =="POST":
        chambre = Chambre.objects.get(id=int(req.POST.get("room_id")))
        saved = False
        if chambre.statut != "Occupee":
            if req.POST.get("room_state") == "S":
                chambre.statut = "Sale"
            elif req.POST.get("room_state") == "N":
                chambre.statut = "Libre"
            elif req.POST.get("room_state") == "B":
                chambre.statut = "Bloquee"
            elif req.POST.get("room_state") == "H":
                chambre.statut = "HS"
            if req.POST.get("room_state") == "R":
                chambre.statut = "Rsv"
            chambre.save()
            
        
            if req.POST.get("room_state") == "B" or req.POST.get("room_state") == "H" or req.POST.get("room_state") == "R":
                statut = Statut_chambre.objects.create(
                chambre = Chambre.objects.get(id=int(req.POST.get("room_id"))),
                reservee = True if req.POST.get("room_state") == "R" else False,
                bloquee = True if req.POST.get("room_state") == "B" else False,
                hors_service = True if req.POST.get("room_state") == "H" else False,
                echeance = datetime.strptime(req.POST.get("echeance_state"),"%Y-%m-%d").date(),
                raison = req.POST.get("raison_state"),
                )
            
            saved = True 
            
        if saved:
            msg = "Le statut changé avec succès"
        else:
            msg = "Impossible de changer le statut car la chambre est déjà occupée."
        
        return JsonResponse({'msg':msg, 'statut':req.POST.get("room_state")})
    
    #METHODE GET
    chambre = Chambre.objects.get(id=int(req.GET['room_id']))
    statut_chambre = None
    if chambre.statut=='Bloquee' or chambre.statut=='HS' or chambre.statut=='Rsv':
        statut_chambre = Statut_chambre.objects.filter(chambre=chambre.id).last()
        
    raison = statut_chambre.raison if statut_chambre is not None else "Nettoyée et libre" if chambre.statut == 'Libre' else 'Pas encore nettoyée mais bientôt'
    echeance = statut_chambre.echeance if statut_chambre is not None else "RAS"
    print(f"La raison est : {raison}")
    status = {
        "id_chambre":chambre.id,
        "num_chambre":chambre.numero,
        "categ_chambre":chambre.categorie.designation,
        "statut":chambre.statut,
        "raison":raison,
        "echeance":echeance,
    }
    
    return JsonResponse({"infos_status":status})


def deposit_chambre(req):
    
    id_ci = req.POST['id_ci']
    mode = int(req.POST['mode'])
    concerne = "ACCOMMODATION" if req.POST['concerne'] == "A" else "EXTRA"
    montant = float(req.POST['montant'])
    libelle = req.POST['libelle']
    
    checkin = Enregistrer.objects.get(id=id_ci)
    
    nom_cli = Client.objects.get(id=checkin.client.id).nom + " " + Client.objects.get(id=checkin.client.id).postnom
    chambre = Chambre.objects.get(id=checkin.chambre.id).numero 
    
    nbjrs = checkin.nbjrs
    total_du = checkin.prixnuitee * nbjrs
    checkin = checkin
    avance = checkin.avance
    
    paie=Paiement(
        montant = montant,
        mode = Operateur.objects.get(id=mode),
        libelle = libelle+" - "+concerne,
        extra = True if concerne == "EXTRA" else False,
        reste = float(total_du)- avance - (montant  if concerne != "EXTRA" else 0.0),
        occupation = checkin
    )
    paie.save()
    checkin.avance = checkin.avance + (montant if concerne != "EXTRA" else 0.0)
    checkin.save()
    Caisse(
        libelle = f" {libelle} - {concerne} ",
        operateur = Operateur.objects.get(id=mode),
        mouvement = float(paie.montant),
        utilisateur = req.user,
    ).save()
    return JsonResponse({'msg':f'Le paiement du client {nom_cli} pour la chambre {chambre} est effectué avec succès','id_recu':paie.id})

# ---------------------------------------------------------------------------------------------------------------------
def commande_achat(req):
    typea = req.POST['mode']
    id_fss = req.POST['id_client']
    
    # Je réunitialise d'abord les tableaux
    id_prod = {}
    qte_ven = {}
    pu_prod = {}
    tot_v = 0 
    
    achat = CommandeAchat(
        typea = typea,
        etat = "ENCOURS",
        total = 0,
        remarque = "RAS",
        fournisseur = Fournisseur.objects.get(id=id_fss),
        utilisateur = req.user
    )
    achat.save()
    
    for i in range(1,21):  
        if 'id_prod' + str(i) in req.POST and len(req.POST['qte_ven'+str(i)]) > 0:
            id_prod[i] = int(req.POST['id_prod'+str(i)])
            qte_ven[i] = int(req.POST['qte_ven'+str(i)])
            pu_prod[i] = float(req.POST['prix_unit'+str(i)])
            tot_v += qte_ven[i] * pu_prod[i]
            
            ligne_achat = LigneCommandeAchat(
                qte = qte_ven[i],
                prix = pu_prod[i],
                model = "",
                article = Article.objects.get(id=id_prod[i]),
                commandeachat = achat,
            )
            ligne_achat.save()
    #MAJ Commande achat. On met le total
    achat.total = round(tot_v,2)
    achat.save()
    return HttpResponse("C Bon")  
def authoriser_commande_achat(req):
    id_ca = req.POST['id_ca']
    achat = CommandeAchat.objects.get(id=id_ca) 
    achat.etat = "AUTHORISE1"
    auth = Autorisation(
        valide=True,
        remarque="RAS",
        utilisateur=req.user
    )
    auth.save()
    achat.autorisation1 = auth
    achat.save()
    
    Caisse(
        libelle = f"Achat stock n°{id_ca} Chez {achat.fournisseur.nom} {achat.fournisseur.postnom}",
        operateur = Operateur.objects.get(id=req.POST['operateur']),
        mouvement = -float(achat.total),
        utilisateur = req.user,
    ).save()
    return HttpResponse("C Bon")  
    
def entree_stock(req):
    achat = CommandeAchat.objects.get(id=req.POST['id_ca']) 
    achat.date_stockage = datetime.now()
    achat.etat = "TERMINE"
    achat.save()
    # CALCUL DU COUT UNITAIRE MOYEN PONDERE DES ENTREES (CUMPE)
    # CUMPE = (Coût d’achat du stock initial + coût d’achat de la nouvelle entrée en stock) / (Quantité initialement en stock + quantité nouvellement entrée en stock)
    lignes = LigneCommandeAchat.objects.filter(commandeachat=achat)
    for prod in lignes:
        article = Article.objects.get(id=prod.article.id)
        CUMPE = ((article.prixu*article.qte) + (prod.prix*prod.qte))/(article.qte + prod.qte)
        article.qte = article.qte + prod.qte 
        article.prixu = round(CUMPE,2)
        article.last_pachat = prod.prix
        article.save()
    return HttpResponse("Effectué")  

# --------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------
def commande_stock(req):
    remarque = req.POST['remarque']
    
    # Je réunitialise d'abord les tableaux
    id_prod = {}
    qte_ven = {}
    pu_prod = {}
    tot_v = 0 
    
    stock = CommandeStock(
        remarque = remarque,
        etat = "ENCOURS",
        total = 0,
        utilisateur = req.user
    )
    stock.save()
    
    for i in range(1,21):  
        if 'id_prod' + str(i) in req.POST and len(req.POST['qte_ven'+str(i)]) > 0:
            id_prod[i] = int(req.POST['id_prod'+str(i)])
            qte_ven[i] = int(req.POST['qte_ven'+str(i)])
            # tot_v += qte_ven[i] * pu_prod[i]
            
            ligne_stock = LigneCommandeStock(
                qte = qte_ven[i],
                article = Article.objects.get(id=id_prod[i]),
                commandestock = stock,
            )
            ligne_stock.save()
    #MAJ Commande stock. On met le total
    stock.total = round(tot_v,2)
    stock.save()
    return HttpResponse("C Bon")
def authoriser_commande_stock(req):
    id_ca = req.POST['id_ca']
    achat = CommandeAchat.objects.get(id=id_ca) 
    achat.etat = "AUTHORISE1"
    auth = Autorisation(
        valide=True,
        remarque="RAS",
        utilisateur=req.user
    )
    auth.save()
    achat.autorisation1 = auth
    achat.save()
    
    Caisse(
        libelle = f"Achat stock n°{id_ca} Chez {achat.fournisseur.nom} {achat.fournisseur.postnom}",
        operateur = Operateur.objects.get(id=req.POST['operateur']),
        mouvement = -float(achat.total),
        utilisateur = req.user,
    ).save()
    return HttpResponse("C Bon")  
    
def sortie_stock(req):
    sortie = CommandeStock.objects.get(id=req.POST['id_ca']) 
    sortie.date_livraison = datetime.now()
    sortie.etat = "LIVREE"
    sortie.save()
    #On actualise la quantité du produit demandé
    lignes = LigneCommandeStock.objects.filter(commandestock=sortie)
    for prod in lignes:
        article = Article.objects.get(id=prod.article.id)
        article.qte = article.qte - prod.qte 
        article.save()
    return HttpResponse("Effectué")  

# --------------------------------------------------------------------------

def octroyer_pret(req):
    if req.method == 'POST':
        mode =req.POST.get("mode")
        employe = req.POST.get("employe")
        montant = req.POST.get("montant")
        motif = req.POST.get("motif")

        periode = req.POST.get("periode")    
        DetteEmploye.objects.create(
            montant = montant,
            motif = motif,
            avance_sur_salaire = True if int(mode) == 1 else False,
            pret = True if int(mode) == 2 else False,
            periodes_couverture = periode,
            reste = montant,
            employe = Employe.objects.get(id=employe),
        )    
        return JsonResponse({"msg":"Effectué"})
    
    
    dette = DetteEmploye.objects.filter(employe=req.GET['id']).last()
    reste = dette.reste
    if reste > 0 :
        return JsonResponse({"msg":"La dette antérieure n'est pas encore reglée. Impossible d'octroyer une nouvelle !","error":True})
    
    periode = dette.periodes_couverture
    #COnversion de la chaine et récupération
    periode_ = []
    for paire in periode.split(";"):
        nombre = paire.split(",")
        periode_.append((int(nombre[0]),int(nombre[1])))

    for m,a in periode_:
        print(f"{m}ème mois année {a}")
    
    return JsonResponse({"msg":"Trouvé","error":False})
# --------------------------------------------------------------------------
def remuneration_employes(req):
    #Conversion des la chaine empl_ pour trouver si c'est tous les agents, par service, par departement ou individuel
    empl_ = req.POST.get("empl_")
    action = req.POST.get("action")
    value = req.POST.get("value")
    print("ACTION = ",action)
    print("VALUE = ",value)
    if action == "jrs_prestes":
        joursprestes =  value
    if action == "jrs_maladie":
        jrs_maladie =  value
    if action == "hrs_supp":
        hrs_supp =  value
    if action == "prime":
        prime =  value
    if action == "transport":
        transport =  value
    if action == "communication":
        communication =  value
    if action == "logement":
        logement =  value
    if action == "allocation_fam":
        allocation_fam =  value
    if action == "ipr":
        ipr =  value
    if action == "cnss":
        cnss =  value
        
    mois = req.POST.get("mois")
    annee = req.POST.get("annee")
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
        
        
    def envoyer_mail_paiement(mois, annee, employe):
        NetPaie = Remuneration.objects.filter(mois=mois, annee=annee,employe=employe).last().netapayer
        mois = Remuneration.objects.filter(mois=mois, annee=annee,employe=employe).last().mois
        annee = Remuneration.objects.filter(mois=mois, annee=annee,employe=employe).last().annee
        envoyer_mail("HOTEL NEW RIVIERA BUKAVU- Paie des agents (Info)",f"Bonjour cher {employe.nom} {employe.postnom}, nous vous espéront en parfaite santé. Nous voulions juste vous informer que votre paie est disponnible.\nVous allez toucher {round(NetPaie,2)} $ pour ce {mois}ème mois de {annee}. Pour d'amples détails, veuillez passer à la caisse.  Merci!","michelbirmugish22@gmail.com",employe.mail)
          
    # --------------------------------------------------TOUS ------------    
    if all:
        for employe in Employe.objects.all():
            
            remun = Remuneration.objects.filter(mois=mois, annee=annee,employe=employe).last()
            employe = employe
            saljr = employe.categorie.salbase / 30
            joursprestes = joursprestes if 'joursprestes' in locals() else remun.joursprestes if remun is not None else 0
            salbrut = float(joursprestes) * float(saljr)
            joursmaladie = joursmaladie if 'joursmaladie' in locals() else remun.joursmaladie if remun is not None else 0
            sal_jrs_maladie = joursmaladie * saljr
            heure_supp = heure_supp if 'heure_supp' in locals() else remun.heure_supp if remun is not None else 0
            sal_heure_supp = heure_supp * (saljr/24)
            prime = prime if 'prime' in locals() else remun.prime if remun is not None else 0
            transport = transport if 'transport' in locals() else remun.transport if remun is not None else 0
            communication = communication if 'communication' in locals() else remun.communication if remun is not None else 0
            logement = logement if 'logement' in locals() else remun.logement if remun is not None else 0
            allocation_fam = allocation_fam if 'allocation_fam' in locals() else remun.allocation_fam if remun is not None else 0
            sal_anciennete = sal_anciennete if 'sal_anciennete' in locals() else remun.sal_anciennete if remun is not None else 0
            ipr = ipr if 'ipr' in locals() else remun.ipr if remun is not None else 0
            cnss = cnss if 'cnss' in locals() else remun.cnss  if remun is not None else 0
            onem = onem if 'onem' in locals() else remun.onem  if remun is not None else 0
            inpp = inpp if 'inpp' in locals() else remun.inpp  if remun is not None else 0
            
            #Calcul de la dette de l'aggent
            dette_employe = DetteEmploye.objects.filter(employe=employe.id).last()
            periode_dette = []
            nb_periodes = 0
            
            if dette_employe is not None:
                for periode in dette_employe.periodes_couverture.split(";"):
                    nombre = periode.split(",")
                    periode_dette.append((int(nombre[0]),int(nombre[1])))
                    nb_periodes += 1    
                    
                for m,a in periode_dette:
                    if int(mois) == int(m) and int(annee) == int(a):
                        dette_periode = round(dette_employe.montant / nb_periodes,2)
                #Fin calcul de la dette de l'agent et attribution 
            if dette_employe is not None: 
                avancesursal = dette_periode if 'dette_periode' in locals() and dette_employe.avance_sur_salaire == 1 else 0
                pret = dette_periode if 'dette_periode' in locals() and dette_employe.pret == 1 else 0
            else:
                avancesursal =  0
                pret =  0
            print("Dette employé est : ",dette_employe)
            netapayer = (float(salbrut) + float(sal_jrs_maladie) + float(sal_heure_supp) + float(prime) + float(transport) + float(communication) + float(logement) + float(allocation_fam) + float(sal_anciennete)) - (float(cnss) + float(ipr) + float(avancesursal)+float(pret))
            mois = mois
            annee = annee
            
            rem = Remuneration(
                id = remun.id if remun else None,
                employe = employe,
                saljr = saljr,
                joursprestes = joursprestes,
                salbrut = salbrut, 
                joursmaladie = joursmaladie,
                sal_jrs_maladie = sal_jrs_maladie,
                heure_supp = heure_supp,
                sal_heure_supp = sal_heure_supp,
                prime = prime,
                transport = transport,
                communication = communication,
                logement = logement,
                allocation_fam = allocation_fam,
                sal_anciennete = sal_anciennete,
                ipr = ipr,
                cnss = cnss,
                onem = onem,
                inpp = inpp,
                pret = pret,
                avancesursal = avancesursal,
                netapayer = netapayer,
                mois = mois,
                annee = annee,
                # date_paid = remun.date_paid if remun is not None else None,
                # paid = remun.paid if remun is not None else None 
            )
            if remun is not None and remun.paid == False:
                rem.save()
                
            if remun is None:
                rem.save()
            #Actualisation du reste de la dette 
            # dette_employe.reste = (dette_employe.reste - avancesursal) if  dette_employe is not None and dette_employe.avance_sur_salaire == 1 else (dette_employe.reste - pret) if dette_employe is not None and dette_employe.pret == 1 else dette_employe.reste
            # print("Dette actualisée : ", dette_employe.reste)
            # dette_employe.save()
            
            # The above code is calling a function `envoyer_mail_paiement` with three arguments
            # `mois`, `annee`, and `employe`. This function is likely used to send an email related to
            # payment for a specific month and year to a particular employee.
            envoyer_mail_paiement(mois, annee, employe)
    
    
    # --------------------------------------------------PAR SERVICE ------------
       
    if by_service:
        print("ID SER",id_ser)
        for employe in Employe.objects.filter(service=id_ser):
            remun = Remuneration.objects.filter(mois=mois, annee=annee,employe=employe).last()
            employe = employe
            saljr = employe.categorie.salbase / 30
            joursprestes = joursprestes if 'joursprestes' in locals() else remun.joursprestes if remun is not None else 0
            salbrut = float(joursprestes) * float(saljr)
            joursmaladie = joursmaladie if 'joursmaladie' in locals() else remun.joursmaladie if remun is not None else 0
            sal_jrs_maladie = joursmaladie * saljr
            heure_supp = heure_supp if 'heure_supp' in locals() else remun.heure_supp if remun is not None else 0
            sal_heure_supp = heure_supp * (saljr/24)
            prime = prime if 'prime' in locals() else remun.prime if remun is not None else 0
            transport = transport if 'transport' in locals() else remun.transport if remun is not None else 0
            communication = communication if 'communication' in locals() else remun.communication if remun is not None else 0
            logement = logement if 'logement' in locals() else remun.logement if remun is not None else 0
            allocation_fam = allocation_fam if 'allocation_fam' in locals() else remun.allocation_fam if remun is not None else 0
            sal_anciennete = sal_anciennete if 'sal_anciennete' in locals() else remun.sal_anciennete if remun is not None else 0
            ipr = ipr if 'ipr' in locals() else remun.ipr if remun is not None else 0
            cnss = cnss if 'cnss' in locals() else remun.cnss  if remun is not None else 0
            onem = onem if 'onem' in locals() else remun.onem  if remun is not None else 0
            inpp = inpp if 'inpp' in locals() else remun.inpp  if remun is not None else 0
            
            #Calcul de la dette de l'aggent
            dette_employe = DetteEmploye.objects.filter(employe=employe.id).last()
            periode_dette = []
            nb_periodes = 0
            for periode in dette_employe.periodes_couverture.split(";"):
                nombre = periode.split(",")
                periode_dette.append((int(nombre[0]),int(nombre[1])))
                nb_periodes += 1    
                  
            for m,a in periode_dette:
                if int(mois) == int(m) and int(annee) == int(a):
                    dette_periode = round(dette_employe.montant / nb_periodes,2)
            #Fin calcul de la dette de l'agent et attribution 
            
            avancesursal = dette_periode if 'dette_periode' in locals() and dette_employe.avance_sur_salaire == 1 else 0
            pret = dette_periode if 'dette_periode' in locals() and dette_employe.pret == 1 else 0
            
            netapayer = (float(salbrut) + float(sal_jrs_maladie) + float(sal_heure_supp) + float(prime) + float(transport) + float(communication) + float(logement) + float(allocation_fam) + float(sal_anciennete)) - (float(cnss) + float(ipr) + float(avancesursal)+float(pret))
            mois = mois
            annee = annee
            
            rem = Remuneration(
                id = remun.id if remun else None,
                employe = employe,
                saljr = saljr,
                joursprestes = joursprestes,
                salbrut = salbrut, 
                joursmaladie = joursmaladie,
                sal_jrs_maladie = sal_jrs_maladie,
                heure_supp = heure_supp,
                sal_heure_supp = sal_heure_supp,
                prime = prime,
                transport = transport,
                communication = communication,
                logement = logement,
                allocation_fam = allocation_fam,
                sal_anciennete = sal_anciennete,
                ipr = ipr,
                cnss = cnss,
                onem = onem,
                inpp = inpp,
                pret = pret,
                avancesursal = avancesursal,
                netapayer = netapayer,
                mois = mois,
                annee = annee,
            )
            if remun.paid == False:
                rem.save()
            # envoyer_mail_paiement(mois, annee, employe)
    
    # --------------------------------------------------PAR DEPARTEMENT ------------
       
    if by_departement:
        print("ID DEP",id_dep)
        for employe in Employe.objects.filter(service__departement=id_dep):
            remun = Remuneration.objects.filter(mois=mois, annee=annee,employe=employe).last()
            employe = employe
            saljr = employe.categorie.salbase / 30
            joursprestes = joursprestes if 'joursprestes' in locals() else remun.joursprestes if remun is not None else 0
            salbrut = float(joursprestes) * float(saljr)
            joursmaladie = joursmaladie if 'joursmaladie' in locals() else remun.joursmaladie if remun is not None else 0
            sal_jrs_maladie = joursmaladie * saljr
            heure_supp = heure_supp if 'heure_supp' in locals() else remun.heure_supp if remun is not None else 0
            sal_heure_supp = heure_supp * (saljr/24)
            prime = prime if 'prime' in locals() else remun.prime if remun is not None else 0
            transport = transport if 'transport' in locals() else remun.transport if remun is not None else 0
            communication = communication if 'communication' in locals() else remun.communication if remun is not None else 0
            logement = logement if 'logement' in locals() else remun.logement if remun is not None else 0
            allocation_fam = allocation_fam if 'allocation_fam' in locals() else remun.allocation_fam if remun is not None else 0
            sal_anciennete = sal_anciennete if 'sal_anciennete' in locals() else remun.sal_anciennete if remun is not None else 0
            ipr = ipr if 'ipr' in locals() else remun.ipr if remun is not None else 0
            cnss = cnss if 'cnss' in locals() else remun.cnss  if remun is not None else 0
            onem = onem if 'onem' in locals() else remun.onem  if remun is not None else 0
            inpp = inpp if 'inpp' in locals() else remun.inpp  if remun is not None else 0
            
            #Calcul de la dette de l'aggent
            dette_employe = DetteEmploye.objects.filter(employe=employe.id).last()
            periode_dette = []
            nb_periodes = 0
            for periode in dette_employe.periodes_couverture.split(";"):
                nombre = periode.split(",")
                periode_dette.append((int(nombre[0]),int(nombre[1])))
                nb_periodes += 1    
                  
            for m,a in periode_dette:
                if int(mois) == int(m) and int(annee) == int(a):
                    dette_periode = round(dette_employe.montant / nb_periodes,2)
            #Fin calcul de la dette de l'agent et attribution 
            
            avancesursal = dette_periode if 'dette_periode' in locals() and dette_employe.avance_sur_salaire == 1 else 0
            pret = dette_periode if 'dette_periode' in locals() and dette_employe.pret == 1 else 0
            
            netapayer = (float(salbrut) + float(sal_jrs_maladie) + float(sal_heure_supp) + float(prime) + float(transport) + float(communication) + float(logement) + float(allocation_fam) + float(sal_anciennete)) - (float(cnss) + float(ipr) + float(avancesursal)+float(pret))
            mois = mois
            annee = annee
            
            rem = Remuneration(
                id = remun.id if remun else None,
                employe = employe,
                saljr = saljr,
                joursprestes = joursprestes,
                salbrut = salbrut, 
                joursmaladie = joursmaladie,
                sal_jrs_maladie = sal_jrs_maladie,
                heure_supp = heure_supp,
                sal_heure_supp = sal_heure_supp,
                prime = prime,
                transport = transport,
                communication = communication,
                logement = logement,
                allocation_fam = allocation_fam,
                sal_anciennete = sal_anciennete,
                ipr = ipr,
                cnss = cnss,
                onem = onem,
                inpp = inpp,
                pret = pret,
                avancesursal = avancesursal,
                netapayer = netapayer,
                mois = mois,
                annee = annee,
            )
            if remun.paid == False:
                rem.save()
            # envoyer_mail_paiement(mois, annee, employe)
    
    # --------------------------------------------------PAR EMPLOYE ------------
       
    if by_employee:
        print("ID EMPL",id_emp)
        for employe in Employe.objects.filter(id=id_emp):
            remun = Remuneration.objects.filter(mois=mois, annee=annee,employe=employe).last()
            employe = employe
            saljr = employe.categorie.salbase / 30
            joursprestes = joursprestes if 'joursprestes' in locals() else remun.joursprestes if remun is not None else 0
            salbrut = float(joursprestes) * float(saljr)
            joursmaladie = joursmaladie if 'joursmaladie' in locals() else remun.joursmaladie if remun is not None else 0
            sal_jrs_maladie = joursmaladie * saljr
            heure_supp = heure_supp if 'heure_supp' in locals() else remun.heure_supp if remun is not None else 0
            sal_heure_supp = heure_supp * (saljr/24)
            prime = prime if 'prime' in locals() else remun.prime if remun is not None else 0
            transport = transport if 'transport' in locals() else remun.transport if remun is not None else 0
            communication = communication if 'communication' in locals() else remun.communication if remun is not None else 0
            logement = logement if 'logement' in locals() else remun.logement if remun is not None else 0
            allocation_fam = allocation_fam if 'allocation_fam' in locals() else remun.allocation_fam if remun is not None else 0
            sal_anciennete = sal_anciennete if 'sal_anciennete' in locals() else remun.sal_anciennete if remun is not None else 0
            ipr = ipr if 'ipr' in locals() else remun.ipr if remun is not None else 0
            cnss = cnss if 'cnss' in locals() else remun.cnss  if remun is not None else 0
            onem = onem if 'onem' in locals() else remun.onem  if remun is not None else 0
            inpp = inpp if 'inpp' in locals() else remun.inpp  if remun is not None else 0
            
            #Calcul de la dette de l'aggent
            dette_employe = DetteEmploye.objects.filter(employe=employe.id).last()
            periode_dette = []
            nb_periodes = 0
            for periode in dette_employe.periodes_couverture.split(";"):
                nombre = periode.split(",")
                periode_dette.append((int(nombre[0]),int(nombre[1])))
                nb_periodes += 1    
                  
            for m,a in periode_dette:
                if int(mois) == int(m) and int(annee) == int(a):
                    dette_periode = round(dette_employe.montant / nb_periodes,2)
            #Fin calcul de la dette de l'agent et attribution 
            
            avancesursal = dette_periode if 'dette_periode' in locals() and dette_employe.avance_sur_salaire == 1 else 0
            pret = dette_periode if 'dette_periode' in locals() and dette_employe.pret == 1 else 0
            
            netapayer = (float(salbrut) + float(sal_jrs_maladie) + float(sal_heure_supp) + float(prime) + float(transport) + float(communication) + float(logement) + float(allocation_fam) + float(sal_anciennete)) - (float(cnss) + float(ipr) + float(avancesursal)+float(pret))
            mois = mois
            annee = annee
            
            rem = Remuneration(
                id = remun.id if remun else None,
                employe = employe,
                saljr = saljr,
                joursprestes = joursprestes,
                salbrut = salbrut, 
                joursmaladie = joursmaladie,
                sal_jrs_maladie = sal_jrs_maladie,
                heure_supp = heure_supp,
                sal_heure_supp = sal_heure_supp,
                prime = prime,
                transport = transport,
                communication = communication,
                logement = logement,
                allocation_fam = allocation_fam,
                sal_anciennete = sal_anciennete,
                ipr = ipr,
                cnss = cnss,
                onem = onem,
                inpp = inpp,
                pret = pret,
                avancesursal = avancesursal,
                netapayer = netapayer,
                mois = mois,
                annee = annee,
            )
            if remun.paid == False:
                rem.save()
            # envoyer_mail_paiement(mois, annee, employe)

    return JsonResponse({"msg":"Effectuée"})

def rapports_reception(req):
    today = datetime.now().date()
    #Journalier
    rapp1 = Paiement.objects.annotate(date_jr = TruncDate('datejr')).filter(date_jr = today).values('extra','occupation__client__nom','occupation__client__postnom','occupation__entreprise__nom','occupation__chambre__numero','mode__designation','occupation__id').annotate(mtn=Sum('montant'))
    checkouts = Checkout.objects.all()
    
    for c in checkouts:
        print(f"{c.datejr}: {c.checkin.client.nom}, chambre {c.checkin.chambre.numero}, Total: {c.checkin.prixnuitee*c.nuitees}, Accom: {c.montant_accom}, Extra: {c.montant_extra}, Dette: {c.credit}")
        
    
    # ------------------------------------------------------- PERIODIQUE ----------------------------------
    #Periodique
    date1 = req.GET.get("date1")
    date2 = req.GET.get("date2")
    if date1 and date2:
        from datetime import date 
        d1 = date.fromisoformat(date1)
        d2 = date.fromisoformat(date2)
    else:
        from datetime import timedelta
        today = datetime.now().date()
        d1 = today # - timedelta(days=30)
        d2 = today
    rapp2 = Paiement.objects.annotate(date_jr = TruncDate('datejr')).filter(date_jr__range=(d1,d2)).values(
        'date_jr','extra','occupation__client__nom','occupation__client__postnom','occupation__entreprise__nom',
        'occupation__chambre__numero','mode__designation','occupation__id').annotate(total_mtn=Sum('montant')).order_by('-date_jr')
    resultats = {}
    for p in rapp2:
        date_jr = p['date_jr']
        id_ci = p['occupation__id']
        if date_jr not in resultats:
            resultats[date_jr]={
                'total_acc':0.0,
                'total_extra':0.0,
                'total_gen':0.0,
            }
        if id_ci not in resultats[date_jr]:
            resultats[date_jr][id_ci] = {
                'id_ci':p['occupation__id'],
                'nom_cli':f"{p['occupation__client__nom']} {p['occupation__client__postnom']}",
                'chambre':p['occupation__chambre__numero'],
                'entreprise':p['occupation__entreprise__nom'],
                'accommodation':0,
                'extra':0,
                'total_mtn':0,
                'mode':p['mode__designation'],
            }
        if p['extra']==0:
            resultats[date_jr][id_ci]['accommodation'] += p['total_mtn']
        else:
            resultats[date_jr][id_ci]['extra'] += p['total_mtn']
            
        resultats[date_jr][id_ci]['total_mtn'] += p['total_mtn']
        
        resultats[date_jr]['total_acc'] += resultats[date_jr][id_ci]['accommodation']
        resultats[date_jr]['total_extra'] += resultats[date_jr][id_ci]['extra']
        resultats[date_jr]['total_gen'] = resultats[date_jr]['total_acc'] + resultats[date_jr]['total_extra']
            
    donnees = {
        'titre':'Rapports de la réception',
        'checkins':Enregistrer.objects.filter(still_in = 1),
        'paiements_periodique':resultats,
        'date1':d1,
        'date2':d2,
        'checkouts':checkouts,
    }
    return render(req, "riviera/rapports_reception.html", donnees)


def rapports_ress_hum(req):
    empl_ = req.GET.get("empl_category") if req.GET.get("empl_category") is not None else "all"
    
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
        employes = Employe.objects.all().order_by('nom')
    if by_service:
        employes = Employe.objects.filter(service=id_ser).order_by('nom')
    if by_departement:
        employes = Employe.objects.filter(service__departement=id_dep).order_by('nom')
    if by_employee:
        employes = Employe.objects.filter(id=id_emp).order_by('nom')
 
    donnees = {
        'titre':'Informations sur le salaire des employés',
        'employes':employes,
        'services':Service.objects.all().order_by('designation'),
        'departements':Departement.objects.all().order_by('designation'),
        'categories':Categorie_employe.objects.all().order_by('code'),
        'id_emp':id_emp if 'id_emp' in locals() else id_dep if 'id_dep' in locals() else id_ser if 'id_ser' in locals() else "all",
        'category':'E' if 'id_emp' in locals() else 'D' if 'id_dep' in locals() else 'S' if 'id_ser' in locals() else "all",
    }
    return render(req, "riviera/rapports_ress_hum.html", donnees)

def suivie_creances(req):
    checkouts = Checkout.objects.filter(credit=1)
    donnees = {
        'titre':'Suivie des nos créanciers',
        'creanciers':Checkout.objects.filter(credit=1),
        'pdvs':PointVente.objects.all(),
        'autres':AutreRevenu.objects.all(),
        'dettes_factures':PaiementFacture.objects.filter(occupation__isnull=False),
    }
    return render(req, "riviera/suivie_creances.html", donnees)