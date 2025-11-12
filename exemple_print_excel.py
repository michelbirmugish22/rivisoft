import pandas as pd
import win32com.client as win32

# Étape 1 : Ajouter des données temporaires et imprimer la feuille
def imprimer_feuille_avec_donnees_temp(nom_fichier, nom_feuille, donnees_temp):
    # Initialiser l'application Excel
    excel = win32.gencache.EnsureDispatch('Excel.Application')
    excel.Visible = False

    # Ouvrir le classeur Excel existant
    workbook = excel.Workbooks.Open(nom_fichier)

    # Sélectionner la feuille de calcul
    worksheet = workbook.Sheets(nom_feuille)

    # Ajouter des données temporaires
    for idx, (col, val) in enumerate(donnees_temp.items(), start=1):
        worksheet.Cells(1, idx).Value = col  # Ajouter le nom de la colonne
        worksheet.Cells(2, idx).Value = val  # Ajouter la valeur temporaire

    # Imprimer la feuille de calcul
    worksheet.PrintOut()

    # Fermer le classeur sans sauvegarder
    workbook.Close(SaveChanges=False)
    # Quitter l'application Excel
    excel.Quit()

    print(f"Feuille {nom_feuille} imprimée avec succès avec des données temporaires.")

# Données temporaires à ajouter (exemple)
donnees_temp = {
    'Temp1': 'Valeur1',
    'Temp2': 'Valeur2',
    'Temp3': 'Valeur3'
}

# Utiliser la fonction avec le fichier existant
# nom_fichier = 'chemin_vers_votre_fichier.xlsx'
# Créer un fichier Excel et l'imprimer
nom_fichier = 'exemple_fichier.xlsx'
nom_fichier = "C:\\Users\\MICHKA\\Desktop\\DJ\\rivisoft\\"+nom_fichier
imprimer_feuille_avec_donnees_temp(nom_fichier, 'Feuil1', donnees_temp)



# creer_fichier_excel(nom_fichier)
# imprimer_feuille(nom_fichier, 'Feuille1')
