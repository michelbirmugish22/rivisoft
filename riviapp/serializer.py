from rest_framework import serializers
from riviapp.models import *

class ClientSerial(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'
        
class CategorieSerial(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = '__all__'
    

