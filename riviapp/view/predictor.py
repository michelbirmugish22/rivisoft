from datetime import datetime
import os
from django.shortcuts import redirect,HttpResponse, render # type: ignore
from django.http import JsonResponse # type: ignore
import joblib
import pandas as pd 
from num2words import num2words # type: ignore

def index(req):
    if req.method == "POST":
        # Charger le modèle avec un chemin absolu
        model = joblib.load('./savedModels/Sales_predictor_new_riviera_hotel.pkl')
        # Weekend, Mois, Jours, Jour_Semaine, Saison, 
        Plats = int(req.POST.get("Plats"))
        Type_Plat = int(req.POST.get("Type_Plat"))
        Point_de_Vente = int(req.POST.get("Point_de_Vente"))
        Jour_Ferie = int(req.POST.get("Jour_Ferie"))
        Evenement_Special = int(req.POST.get("Evenement_Special"))        
        Date_pred = datetime.strptime(req.POST.get("Date_pred"), '%Y-%m-%d').date()
        
        jour = Date_pred.day
        mois = Date_pred.month 
        jour_semaine  = Date_pred.weekday()
        weekend = 1 if jour_semaine >= 5 else 0  #True si jour_semaine est 5,6 ou 7
        def obtenir_saison(mois):
            if mois >= 1 and mois <4 :
                return 1
            if mois >= 4 and mois <7 :
                return 2
            if mois >= 7 and mois <10 :
                return 3
            if mois >= 10 and mois <13 :
                return 4
            
        saison = obtenir_saison(mois)
        # print(f"Mois: {mois}")
        # print(f"Jour: {jour}")
        # print(f"Jour de la semaine: {jour_semaine}")
        # print(f"Weekend: {weekend}")
        # print(f"Saison: {saison}")
            
        data = {
            "Plats": [Plats],
            "Type_Plat": [Type_Plat],
            "Point_de_Vente": [Point_de_Vente],
            "Weekend": [weekend],
            "Mois": [mois],
            "Jours": [jour],
            "Jour_Semaine": [jour_semaine],
            "Saison": [saison],
            "Jour_Ferie": [Jour_Ferie],
            "Evenement_Special": [Evenement_Special] 
        }
        new_datas = pd.DataFrame(data)
        prediction = model.predict(new_datas)
        # print("Pred : ", prediction[0])
        return JsonResponse({'prediction': f"Pour la date du {Date_pred.strftime("%d/%m/%Y")}, vous allez réaliser les ventes de «{round(prediction[0],1)}$»  ✔️ </br> <i class=\"display-6\">({num2words(round(prediction[0],2), lang="fr")} dollars.)</i> "})

    return HttpResponse("PREDICTOR MODEL")