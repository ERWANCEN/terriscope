"""Admin Django : pour contrôler à la main les données importées (http://localhost:8000/admin/)."""

from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin

from .models import Departement, Domaine1, Domaine2, Domaine3, Equipement, Region


@admin.register(Region, Departement, Domaine1, Domaine2, Domaine3)
class ReferentielAdmin(admin.ModelAdmin):
    search_fields = ["libelle"]


@admin.register(Equipement)
class EquipementAdmin(GISModelAdmin):          # GISModelAdmin affiche le point sur une mini-carte
    list_display = ["nom", "ville", "domaine3", "departement"]
    list_filter = ["departement"]
    search_fields = ["nom", "ville", "siret"]
    list_select_related = ["domaine3", "departement"]   # évite une requête SQL par ligne
    raw_id_fields = ["domaine3"]                         # pas de liste déroulante géante
