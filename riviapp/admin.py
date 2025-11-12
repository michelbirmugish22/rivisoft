from django.contrib import admin
from .models import *

class ModulesAdmin(admin.ModelAdmin):
    list_display = ('get_affectation_display', 'is_avalable')

    def get_affectation_display(self, obj):
        return dict(AFFECTATION).get(obj.affectation, obj.affectation)
    get_affectation_display.short_description = 'Modules'

admin.site.register(Module, ModulesAdmin)


# Register your models here.
admin.site.register(Utilisateur)

class OperateurAdmin(admin.ModelAdmin):
    list_display = ('designation','p_caissse')

admin.site.register(Operateur)
admin.site.register(Configuration)