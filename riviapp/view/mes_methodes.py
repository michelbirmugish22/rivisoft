from django.forms.models import model_to_dict
    
def model_vers_dict(objects):
    objs_dicts = {"obj": {}}
    for obj in objects:
        blocs_dict = model_to_dict(obj)
        objs_dicts["obj"][str(obj.id)] = blocs_dict
    return objs_dicts

# def model_vers_dict(objects):
    """
La fonction `model_vers_dict` convertit une liste d'objets modèles en un dictionnaire où chaque objet
 est représenté par son ID et les valeurs de champ correspondantes.

 :param objets : le paramètre `objects` dans la fonction `model_vers_dict` devrait être une liste
 d'instances de modèle. Ces instances de modèle sont des objets qui représentent des lignes dans une table de base de données,
 généralement défini à l'aide de l'ORM (Object-Relational Mapping) de Django
 :return : La fonction `model_vers_dict` prend une liste d'objets en entrée, convertit chaque objet en
 un dictionnaire utilisant la fonction `model_to_dict`, et stocke ces dictionnaires dans un nouveau dictionnaire
 avec l'ID de l'objet comme clé. Enfin, il renvoie un dictionnaire contenant tous les convertis
 objets avec leurs identifiants comme clés.
    """
    # objs_dicts = {"obj": {}}
    # for obj in objects:
    #     blocs_dict = model_to_dict(obj, fields=[field.name for field in obj._meta.fields])
    #     objs_dicts["obj"][str(obj.id)] = blocs_dict
    # return objs_dicts
