from django.db import models
from django.contrib.auth.models import AbstractUser

MODULE = [
    ('REC','Réception'),
    ('PDV','Point de Vente'),
    ('FIN','Finance et Comptabilité'),
    ('MAG','Magasin et Stock'),
    ('HKP','House Keeping'),
    ('RHM','Ressources Humaines'),
    ('IAT','Intellicence Articficielle'),
]
class Module(models.Model):
    affectation = models.CharField(max_length=30, choices=MODULE, unique=True)
    is_avalable = models.BooleanField(default=True)
    
    def get_affectation_display(self):
        return dict(AFFECTATION).get(self.affectation, self.affectation)

class Configuration(models.Model):
    name = models.CharField(max_length=15)

#Pour night audit
class Account(models.Model):
    account_date_room = models.DateField()
    account_date_pos = models.DateField()


# ------------------------------------------------------------------  
NATIONALITE = [
    ('Congolaise','Congolaise'),
    ('Rwandaise','Rwandaise'),
    ('Burundaise','Burundaise'),
    ('Kenyane','Kenyane'),
    ('Ugandaise','Ugandaise'),
    ('Zambienne','Zambienne'),
    ('Angolaise','Angolaise'),
    ('Autre','Autre'),
]

SEXE = [
    ('M','Masculin'),
    ('F','Féminin'),
]
AFFECTATION = [
    ('REC','Réception'),
    ('PDV','Point de Vente'),
    ('FIN','Finance et Comptabilité'),
    ('MAG','Magasin et Stock'),
    ('HKP','House Keeping'),
    ('GAR','Garde et Sécurité'),
    ('RHM','Ressources Humaines'),
    ('INF','Informatique'),
    ('CUI','Cuisine'),
    ('GER','Gérance'),
]
ROLE = [
    ('SUP','Superviseur'),
    ('VIC','Vice-Superviseur'),
    ('ORD','Ordinaire'),
    ('INV','Invité'), #Lire seulement les rapports
]

class Utilisateur(AbstractUser):
    affectation = models.CharField(max_length=30, choices=AFFECTATION)
    role = models.CharField(max_length=30, choices=ROLE)
    sexe=models.CharField(max_length=30, choices=SEXE)
    nationalite=models.CharField(max_length=30, null=True, choices=NATIONALITE)
    tel=models.CharField(max_length=30)
    adresse=models.CharField(max_length=30)
    
    def get_affectation_display(self):
        return dict(AFFECTATION).get(self.affectation, self.affectation)
    def get_role_display(self):
        return dict(ROLE).get(self.role,self.role)
# ------------------------------------------------------------------  
class Operateur(models.Model):
    designation = models.CharField(max_length=255)
    p_caisse = models.BooleanField(default=False)
    
class Caisse(models.Model):
    date = models.DateTimeField(auto_now=True)
    mouvement = models.FloatField()
    libelle = models.CharField(max_length=50)
    operateur = models.ForeignKey(Operateur, on_delete=models.CASCADE)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
# ---------------------------------------------------------------------------
class Client(models.Model):
    nom=models.CharField(max_length=30)
    postnom=models.CharField(max_length=30)
    sexe=models.CharField(max_length=12)
    nationalite=models.CharField(max_length=5)
    tel=models.CharField(max_length=20)
    mail=models.CharField(max_length=30)
    profession=models.CharField(max_length=30)
    adresse_serv=models.CharField(max_length=30)
    adresse_rdc=models.CharField(max_length=30)
    lieu_nais=models.CharField(max_length=30)
    date_nais=models.CharField(max_length=30)
# ------------------------------------------------------------------  
class Entreprise(models.Model):
    nom=models.CharField(max_length=30)
    adresse=models.CharField(max_length=30)
    activite=models.CharField(max_length=30)
    notre_relation=models.CharField(max_length=20)
# ------------------------------------------------------------------    
class Categorie(models.Model):
    designation = models.CharField(max_length=255)
    prix = models.FloatField()
    paxmax = models.IntegerField()
# ------------------------------------------------------------------
class Bloc(models.Model):
    designation = models.CharField(max_length=255)
    nbchamax = models.IntegerField()
# ------------------------------------------------------------------
class Chambre(models.Model):
    numero = models.CharField(max_length=6)
    statut = models.CharField(max_length=20) #Vaccante, Occupée, Sale, Bloquée, Hors service
    etage = models.CharField(max_length=20)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    bloc = models.ForeignKey(Bloc, on_delete=models.CASCADE)
# ------------------------------------------------------------------ 
class ImageChambre(models.Model):
    designation = models.CharField(max_length=30)
    image = models.ImageField(upload_to='images/chambres/')
    description = models.CharField(max_length=50)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)
# ------------------------------------------------------------------
class Statut_chambre(models.Model):
    datejr = models.DateTimeField(auto_now=True)
    chambre = models.ForeignKey(Chambre, on_delete=models.CASCADE)
    reservee = models.BooleanField(default=False)
    bloquee = models.BooleanField(default=False)
    hors_service = models.BooleanField(default=False)
    echeance = models.DateField()
    raison = models.TextField(max_length=30)
# ------------------------------------------------------------------
class Piece_indentite(models.Model):
    designation = models.CharField(max_length=30)
    numero = models.CharField(max_length=30)
    date_livre = models.DateField()
    date_expire = models.DateField()
    lieu_livre = models.CharField(max_length=30)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
# ------------------------------------------------------------------
class Enregistrer(models.Model):
    datejr = models.DateTimeField(auto_now=True)
    datearr = models.DateTimeField()
    datesor = models.DateTimeField()
    provenance = models.CharField(max_length=30)
    destination = models.CharField(max_length=30)
    prixnuitee=models.FloatField()
    avance=models.FloatField()
    nbpax=models.IntegerField()
    nbjrs = models.IntegerField(default=1)
    still_in = models.BooleanField(default=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    chambre = models.ForeignKey(Chambre, on_delete=models.CASCADE)
# ------------------------------------------------------------------
class Checkout(models.Model):
    datejr = models.DateTimeField(auto_now=True)
    checkin = models.ForeignKey(Enregistrer, on_delete=models.CASCADE)
    datesor = models.DateTimeField()
    nuitees = models.IntegerField()
    montant_extra = models.FloatField()
    montant_accom = models.FloatField()
    credit = models.BooleanField()
    client = models.ForeignKey(Enregistrer, null=True, on_delete=models.CASCADE, related_name="dette_transfert_chambre")
    entreprise = models.ForeignKey(Entreprise, null=True, on_delete=models.CASCADE)
    

class Reservation(models.Model):
    datejr = models.DateTimeField(auto_now=True)
    mode = models.CharField(max_length=10) #En ligne, Contact Whatsapp, autre à préciser
    prixvalide = models.FloatField()
    datearrivee = models.DateField()
    datesortie = models.DateField()
    nbadultes = models.IntegerField()
    nbenfants = models.IntegerField()
    nbchambre = models.IntegerField()
    autresinfos = models.TextField()
    etat_rsv = models.CharField(max_length=10)#Encours, Confirme, chechin, annuler
    raison_annul = models.CharField(max_length=30, default="")
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    entreprise = models.ForeignKey(Entreprise, null=True, on_delete=models.CASCADE)
# ------------------------------------------------------------------
class Paiement(models.Model):
    datejr = models.DateTimeField(auto_now=True)
    montant = models.FloatField()
    mode = models.ForeignKey(Operateur, on_delete=models.CASCADE) #M-Pesa, Airtel money, Visa ou Cash
    libelle = models.CharField(max_length=20, default='')
    extra = models.BooleanField(default=False)
    reste = models.FloatField()
    occupation = models.ForeignKey(Enregistrer, null=True, on_delete=models.CASCADE)
    reservation = models.ForeignKey(Reservation,null=True, on_delete=models.CASCADE)
# ------------------------------------------------------------------
class Departement(models.Model):
    designation = models.CharField(max_length=30)
# ------------------------------------------------------------------
class Service(models.Model):
    designation = models.CharField(max_length=30)
    departement = models.ForeignKey(Departement, on_delete=models.CASCADE)
# ------------------------------------------------------------------
class Categorie_employe(models.Model):
    designation = models.CharField(max_length=30)
    code = models.CharField(max_length=5, unique=True)
    salbase = models.FloatField()
# ------------------------------------------------------------------
class Employe(models.Model):
    nom = models.TextField(max_length=20)
    postnom = models.TextField(max_length=20)
    sexe = models.TextField(max_length=2)
    etat_civil = models.TextField(max_length=5)
    nb_enfant = models.IntegerField()
    date_naiss = models.DateField()
    date_engage = models.DateField() #Pour calculer son ancienneté
    mail = models.EmailField(unique=True)
    adresse = models.TextField(max_length=30)
    tel = models.CharField(max_length=30)
    niveau_etu = models.CharField(max_length=30)
    fonction = models.CharField(max_length=30)
    nationalite = models.CharField(max_length=20)
    categorie = models.ForeignKey(Categorie_employe, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    dossier = models.FileField(upload_to='dossiers_agents/')
# ------------------------------------------------------------------
class PointVente (models.Model):
   designation = models.CharField(max_length=30)
# ------------------------------------------------------------------
class GroupeMenu(models.Model):
    designation = models.CharField(max_length=30, default='Dinner')
# ------------------------------------------------------------------
class MenuRestau(models.Model):
    typem = models.CharField(max_length=20) #Boisson ou nourriture
    prix = models.FloatField()
    designation = models.CharField(max_length=40)
    commentaire = models.CharField(max_length=200)
    datecreation = models.DateField(auto_now=True)
    datefin = models.DateField()
    groupe = models.ForeignKey(GroupeMenu, default=1, on_delete=models.CASCADE)
    urlimage = models.ImageField(upload_to='images/menurestaurant/', default='')
# ------------------------------------------------------------------  
class CommandeVente(models.Model):
    datev = models.DateField()
    etat = models.CharField(max_length=20) #Commandée, Facturée, Annulée, PAYEE
    typev = models.CharField(max_length=20)
    total = models.IntegerField()
    caissier = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    pointvente = models.ForeignKey(PointVente, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
# ------------------------------------------------------------------   
class PaiementFacture(models.Model):
    date = models.DateTimeField(auto_now=True)
    montant = models.FloatField()
    mode = models.CharField(max_length=20)
    numero = models.CharField(max_length=30, null=True)
    occupation = models.ForeignKey(Enregistrer, null=True, on_delete=models.CASCADE)
    vente = models.ForeignKey(CommandeVente, on_delete=models.CASCADE)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
# ------------------------------------------------------------------
class LigneCommandeVente(models.Model):
    qte = models.FloatField()
    compliment = models.CharField(max_length=30)
    menu = models.ForeignKey(MenuRestau, on_delete=models.CASCADE)
    commandevente = models.ForeignKey(CommandeVente, on_delete=models.CASCADE)
# ------------------------------------------------------------------ 
class Fournisseur(models.Model):
    nom=models.CharField(max_length=30)
    postnom=models.CharField(max_length=30)
    tel=models.CharField(max_length=20)
    mail=models.CharField(max_length=30)
    adresse_serv=models.CharField(max_length=30)
    type_ese = models.CharField(max_length=30)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
# ------------------------------------------------------------------ 
class Stock(models.Model):
    designation = models.CharField(max_length=30)
    datemodif = models.DateTimeField(auto_now=True)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
# ------------------------------------------------------------------     
class Groupe_article(models.Model):
    designation = models.CharField(max_length=30)
    datemodif = models.DateTimeField(auto_now=True)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
# ------------------------------------------------------------------   
class Article(models.Model):
    designation = models.CharField(max_length=30)
    qte = models.FloatField()
    prixu = models.FloatField()
    last_pachat = models.FloatField()
    datemodif = models.DateTimeField(auto_now=True)
    unitmsr = models.CharField(max_length=5)
    groupe = models.ForeignKey(Groupe_article, on_delete=models.CASCADE)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
# ------------------------------------------------------------------   
class Autorisation(models.Model):
    valide = models.BooleanField(default=False)
    remarque = models.CharField(max_length=30)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)  
# ------------------------------------------------------------------           
class CommandeAchat(models.Model):    
    datea = models.DateTimeField(auto_now=True)
    date_stockage = models.DateTimeField(null=True)
    typea = models.CharField(max_length=30) #CREDIT ou à CASH
    etat = models.CharField(max_length=15) #TERMINE, ENCOURS
    total = models.FloatField()
    remarque = models.CharField(max_length=50)
    autorisation1 = models.ForeignKey(Autorisation, null=True, on_delete=models.CASCADE)  
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE)
    utilisateur = models.ForeignKey(Utilisateur, null=True, on_delete=models.CASCADE)
# ------------------------------------------------------------------     
class LigneCommandeAchat(models.Model):
    qte = models.FloatField()
    prix = models.FloatField()
    model = models.CharField(max_length=50)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    commandeachat = models.ForeignKey(CommandeAchat, on_delete=models.CASCADE)
# ------------------------------------------------------------------    
class CommandeStock(models.Model):
    datec = models.DateTimeField(auto_now=True)
    date_livraison = models.DateTimeField(null=True)
    etat = models.CharField(max_length=15) #Livré, en cours
    total = models.FloatField()
    remarque = models.CharField(max_length=50)
    autorisation1 = models.ForeignKey(Autorisation, null=True, on_delete=models.CASCADE)   
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
# ------------------------------------------------------------------     
class LigneCommandeStock(models.Model):
    qte = models.FloatField()
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    commandestock = models.ForeignKey(CommandeStock, on_delete=models.CASCADE)
# ------------------------------------------------------------------        
class Remuneration(models.Model):
    dater = models.DateTimeField(auto_now=True)
    saljr = models.FloatField()
    joursprestes = models.IntegerField()
    salbrut = models.FloatField()
    joursmaladie = models.IntegerField()
    sal_jrs_maladie = models.FloatField()
    heure_supp = models.FloatField()
    sal_heure_supp = models.FloatField()
    prime = models.FloatField()
    transport = models.FloatField()
    communication = models.FloatField()
    logement = models.FloatField()
    allocation_fam = models.FloatField()
    sal_anciennete = models.FloatField()
    ipr = models.FloatField()
    cnss = models.FloatField()
    onem = models.FloatField()
    inpp = models.FloatField()
    pret = models.FloatField()
    avancesursal = models.FloatField()
    netapayer = models.FloatField()
    mois = models.IntegerField()
    annee = models.IntegerField()
    
    date_paid = models.DateTimeField(null=True)
    paid = models.BooleanField(default=False)
    
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE)
# ------------------------------------------------------------------     
class DetteEmploye(models.Model):
    montant = models.FloatField()
    motif = models.CharField(max_length=50)
    dated = models.DateTimeField(auto_now=True)
    avance_sur_salaire = models.BooleanField(default=False)
    pret = models.BooleanField(default=False)
    periodes_couverture = models.CharField(max_length=30)
    reste = models.FloatField()
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE)
# ------------------------------------------------------------------     
class AutreRevenu(models.Model):
    designation = models.CharField(max_length=30)
# ------------------------------------------------------------------ 
class TarifAutreRevenu(models.Model):
    designation = models.CharField(max_length=30)
    prix = models.FloatField()
    autrerevenu = models.ForeignKey(AutreRevenu, on_delete=models.CASCADE)
# ------------------------------------------------------------------     
class Consommation(models.Model):
    datec = models.DateTimeField(auto_now=True)
    commentaire = models.CharField(max_length=30)
    total = models.FloatField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
# ------------------------------------------------------------------     
class LigneConsommation(models.Model):
    nbre = models.IntegerField()
    tarifautrerevenu = models.ForeignKey(TarifAutreRevenu, on_delete=models.CASCADE)
    consommation = models.ForeignKey(Consommation, on_delete=models.CASCADE)
# ------------------------------------------------------------------ 

    
    
# ------------------------------------------------------------------
# PAS ENCORE DANS LE DIAGRAMME DE CLASSES
# ------------------------------------------------------------------    
class Notification(models.Model):
    texte = models.CharField(max_length=40)
    typen = models.CharField(max_length=15) #Danger, Info
    daten = models.DateTimeField(auto_now=True)
# ------------------------------------------------------------------     
class Banquet(models.Model):
    designation = models.CharField(max_length=255)
    numero = models.CharField(max_length=20)
    image = models.ImageField(blank=True, upload_to='images/baquets/')
    bloc = models.ForeignKey(Bloc, on_delete=models.CASCADE) 
# ------------------------------------------------------------------     
class Salle(Banquet):
    is_occupied = models.BooleanField(default=0)
    is_booked = models.BooleanField(default=0)
    is_blocked = models.BooleanField(default=0)
    capacite = models.IntegerField()
    prixoccup = models.FloatField() 
# ------------------------------------------------------------------     
class Boutique(Banquet):
    is_occupied = models.BooleanField(default=0)
    is_blocked = models.BooleanField(default=0)
    prixmensuel = models.FloatField()
# ------------------------------------------------------------------ 
class LocationBtq(models.Model):
    datejr = models.DateTimeField(auto_now=True)
    debut = models.DateField()    
    fin = models.DateField()   
    duree = models.IntegerField() 
    prixunit = models.FloatField()
    totverse = models.FloatField()
    reste = models.FloatField()
    commentaire = models.CharField(max_length=50)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    boutique = models.ForeignKey(Boutique, on_delete=models.CASCADE)
# ------------------------------------------------------------------ 
class ReservationSalle(models.Model):
    datejr = models.DateTimeField(auto_now=True)
    datedebut = models.DateField()    
    datefin = models.DateField()    
    debut = models.TimeField()   
    fin = models.TimeField()    
    duree = models.IntegerField() #Calculée auto
    prixunit = models.FloatField()
    totverse = models.FloatField()
    reste = models.FloatField()
    etatrsv = models.IntegerField(default=2) #Confirmé(0), Annulé(3), Occupé(1), Abouti(2)
    commentaire = models.CharField(max_length=50)
    entreprise = models.ForeignKey(Entreprise, null=True, on_delete=models.CASCADE)
    occupation = models.ForeignKey(Enregistrer, null=True, on_delete=models.CASCADE)
    salle = models.ForeignKey(Salle, on_delete=models.CASCADE)
# ------------------------------------------------------------------        
class VersementBq(models.Model):
    datejr = models.DateTimeField(auto_now=True)
    montant = models.FloatField()
    libelle = models.CharField(max_length=50)
    locationbq = models.ForeignKey(LocationBtq, on_delete=models.CASCADE)
# ------------------------------------------------------------------     
class VersementSalle(models.Model):
    datejr = models.DateTimeField(auto_now=True)
    montant = models.FloatField()
    libelle = models.CharField(max_length=50)
    facilitateur = models.CharField(max_length=50) #Le nom
    reservationsalle = models.ForeignKey(ReservationSalle, on_delete=models.CASCADE)
# ------------------------------------------------------------------     
class AutreDepense(models.Model):
    motif = models.CharField(max_length=30)
    libelle = models.CharField(max_length=30)
    montant = models.FloatField()
    dated = models.DateTimeField(auto_now=True)
    autorisation1 = models.ForeignKey(Autorisation, on_delete=models.CASCADE)   
    
    
# ------------------------------------------------------------------
# COMPTABILITE GENERALE
# ------------------------------------------------------------------ 
# class ExcerciceComptable(models.Model):
#     designation = models.CharField(max_length=10)
#     dated = models.DateField()
#     datef = models.DateField()
    
# class Compte(models.Model):
#     code = models.CharField(max_length=10)
#     designation = models.CharField(max_length=30)
#     typec = models.CharField(max_length=10) #Charge, Produit

# class Affectation(models.Model):
#     compte = models.ForeignKey(Compte, on_delete=models.CASCADE)
#     exercice = models.ForeignKey(ExcerciceComptable, on_delete=models.CASCADE)