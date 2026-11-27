from django.contrib.gis import admin

from prospection.models import Implantation


@admin.register(Implantation)
class ImplantationAdmin(admin.GISModelAdmin):
    list_display = ("id", "titre", "proprietaire", "domaine3", "cree_le")
    list_filter = ("proprietaire",)
    search_fields = ("titre", "commentaire")