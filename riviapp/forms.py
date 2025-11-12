from django.contrib.auth.forms import UserCreationForm # type: ignore
from django.contrib.auth import get_user_model # type: ignore
from django import forms # type: ignore

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
    ('REC','Réceptionniste'),
    ('PDV','Serveur'),
    ('FIN','Financier'),
    ('MAG','Magasinier'),
    ('HKP','Chargé d\'entretien'),
    ('RHM','Resp. Ress. Humaines'),
    # ('CUI','Cuisine'),
    ('GER','Gérant'),
    ('ADM','Administrateur'),
]
ROLE = [
    ('SUP','Superviseur'),
    ('VIC','Vice-Superviseur'),
    ('ORD','Ordinaire'),
    ('INV','Invité'), #Lire seulement les rapports
]

class UserForm(UserCreationForm): 
    first_name = forms.CharField(
        label='Prénom',
        strip=False,
        widget=forms.TextInput(attrs={'class':'form-control form-control-lg col-md-11'})
    )
    last_name = forms.CharField(
        label='Nom de famille',
        strip=False,
        widget=forms.TextInput(attrs={'class':'form-control form-control-lg col-md-11'})
    )
    sexe = forms.ChoiceField(
        label='Sexe',
        choices=SEXE,
        widget=forms.Select(attrs={'class':'form-control form-control-lg col-md-11'})
    )
    nationalite = forms.ChoiceField(
        label='Nationalité',
        choices=NATIONALITE,
        widget=forms.Select(attrs={'class':'form-control form-control-lg col-md-11'})
    )
    tel = forms.CharField(
        label='Téléphone',
        strip=False,
        widget=forms.TextInput(attrs={'class':'form-control form-control-lg col-11'})
    )
    adresse = forms.CharField(
        label='Adresse de résidence',
        strip=False,
        widget=forms.TextInput(attrs={'class':'form-control form-control-lg col-11'})
    )
    affectation = forms.ChoiceField(
        label='Poste de travail',
        choices=AFFECTATION,
        widget=forms.Select(attrs={'class':'form-control form-control-lg col-11'})
    )
    role = forms.ChoiceField( 
        label='Role et Fonction',
        choices=ROLE,
        widget=forms.Select(attrs={'class':'form-control form-control-lg col-11'})
    )
    username = forms.CharField(
        label='Nom d\'utilisateur',
        strip=False,
        widget=forms.TextInput(attrs={'class':'form-control form-control-lg col-11'})
    )
    password1 = forms.CharField(
        label='Mot de passe',
        strip=False,
        widget=forms.PasswordInput(attrs={'class':'form-control form-control-lg col-11'})
    )
    
    password2 = forms.CharField(
        label='Confirmer le mot de passe',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete':'new-password','class':'form-control form-control-lg col-11'})
    )
    class Meta:
        model = get_user_model()
        fields = ['first_name','last_name','affectation','username','password1','password2','role','sexe','nationalite','tel','adresse']
        
        
class Change_Password_UserForm(UserCreationForm): 
    username = forms.CharField(
        label='Nom d\'utilisateur',
        strip=False,
        widget=forms.TextInput(attrs={'class':'form-control form-control-sm col-12'})
    )
    password1 = forms.CharField(
        label='Ancien mot de passe',
        strip=False,
        widget=forms.PasswordInput(attrs={'class':'form-control form-control-sm col-12'})
    )
    
    password2 = forms.CharField(
        label='Nouveau mot de passe',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete':'new-password','class':'form-control form-control-sm col-12'})
    )
    password3 = forms.CharField(
        label='Confirmer le mot de passe',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete':'new-password','class':'form-control form-control-sm col-12'})
    )
    class Meta:
        model = get_user_model()
        fields = ['username','password1','password2']
        
