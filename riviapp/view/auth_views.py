from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from riviapp.forms import UserForm, Change_Password_UserForm
from riviapp.models import Utilisateur
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from riviapp.view.mes_methodes import model_vers_dict
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

def connexion(request):
    username = None
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Le nom d\'utilisateur ou le mot de passe incorrect. Réessayer s\'il vous plait!!!')
    return render(request, 'riviera/authentification/login.html', {'username':username})

@login_required(login_url='login')
def deconnexion(request):
    messages.success(request, f'{request.user.first_name} {request.user.last_name} ! Vous avez été déconnecté ...')
    logout(request)
    
    return redirect('login')

@login_required(login_url='login')
def inscription(request):
    form = UserForm()
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'L\'utilisateur est enregistré avec succès.')
    if request.user.affectation != 'GER' and request.user.affectation != 'ADM' and request.user.is_staff != 1:
        return redirect('home')
    return render(request, 'riviera/authentification/register2.html', {'form':form,'users':Utilisateur.objects.all()})

@login_required(login_url='login')
def change_password(request):
    # form =  Change_Password_UserForm()
    if request.method == 'POST':
        print(f"Le nom d'utilisateur est : {request.user}")
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            print("FORM VALIDE")
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request,"Votre mot de passe a bien été modifié")
            return redirect('home')
        else:
            print("FORM NON VALIDE")
            messages.error(request, "Une erreur s'est produite !")
    form = PasswordChangeForm(request.user)
    return render(request, 'riviera/authentification/register.html', {'form':form,'users':Utilisateur.objects.all()})


@login_required(login_url='login')
def edit_user(request):
    if request.user.affectation != 'GER' and request.user.affectation != 'RHM' and request.user.is_staff != 1:
        return redirect('home')
    if request.POST.get('action') == 'EDIT':
        username = request.POST['username']
        user = Utilisateur.objects.get(username=username)
        user.first_name = request.POST.get('id_first_name')
        user.last_name = request.POST.get('id_last_name')
        user.affectation = request.POST.get('id_affectation')
        user.role = request.POST.get('id_role')
        user.sexe = request.POST.get('id_sexe')
        user.nationalite = request.POST.get('id_nationalite')
        user.adresse = request.POST.get('id_adresse')
        user.tel = request.POST.get('id_tel')
        user.save()
        
        messages.success(request, f"Les informations sur l'utilisateur { user.username} sont mises à jour avec succès.")
    else:
        print(request.POST['username'])
        username = request.POST['username']
        user = Utilisateur.objects.get(username=username)
        data = {
            'username':user.username,
            'first_name':user.first_name,
            'last_name':user.last_name,
            'sexe':user.sexe,
            'nationalite':user.nationalite,
            'tel':user.tel,
            'adresse':user.adresse,
            'affectation':user.affectation,
            'role':user.role,
            'password':user.password,
        }
        return JsonResponse({'user':data})
    return HttpResponse("vide")

@login_required(login_url='login')
def bloquer_user(request, username):
    if request.user.affectation != 'GER' and request.user.affectation != 'RHM' and request.user.is_staff != 1:
        return redirect('home')
    username = username
    user = Utilisateur.objects.get(username=username)
    if user.is_active == True:
        user.is_active = False
    else:
        user.is_active = True
    user.save()
    return redirect('signin')