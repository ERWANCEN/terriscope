"""Filtres de l'endpoint carte : ?in_bbox=…&domaine1=…&domaine2=…&domaine3=…&ville=…"""

import django_filters
from rest_framework.exceptions import ParseError
from rest_framework_gis.filters import InBBoxFilter

from .models import Equipement

# Taille maximale de la zone demandée, en degrés (garde-fou contre « toute la région d'un coup »)
TAILLE_BBOX_MAX = 1.0


class CharInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    """Accepte plusieurs valeurs séparées par des virgules : ?ville=Tours,Blois"""


class EquipementFilter(django_filters.FilterSet):
    # Les niveaux 1 et 2 passent par les relations : bpe > domaine3 > domaine2 > domaine1
    domaine1 = CharInFilter(field_name="domaine3__domaine2__domaine1", lookup_expr="in",
                            help_text="Codes domaine1 séparés par des virgules, ex. F,A")
    domaine2 = CharInFilter(field_name="domaine3__domaine2", lookup_expr="in",
                            help_text="Codes domaine2 séparés par des virgules, ex. F3,A1")
    domaine3 = CharInFilter(field_name="domaine3", lookup_expr="in",
                            help_text="Codes domaine3 séparés par des virgules, ex. F307,F303")
    ville = CharInFilter(field_name="ville", lookup_expr="in",
                         help_text="Villes séparées par des virgules, ex. Tours,Blois")

    class Meta:
        model = Equipement
        fields = []          # tous les filtres sont déclarés ci-dessus


class InBBoxLimiteFilter(InBBoxFilter):
    """Filtre ?in_bbox=minLon,minLat,maxLon,maxLat, en refusant les zones trop grandes."""

    def get_filter_bbox(self, request):
        bbox = super().get_filter_bbox(request)      # None si le paramètre est absent
        if bbox is not None:
            min_lon, min_lat, max_lon, max_lat = bbox.extent
            if max_lon - min_lon > TAILLE_BBOX_MAX or max_lat - min_lat > TAILLE_BBOX_MAX:
                raise ParseError(f"Zone trop grande : {TAILLE_BBOX_MAX}° × {TAILLE_BBOX_MAX}° maximum.")
        return bbox
