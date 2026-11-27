"""Vues publiques du référentiel BPE : carte, fiche, arbre des domaines, villes."""

from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics, serializers, viewsets
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import EquipementFilter, InBBoxLimiteFilter
from .models import Domaine1, Domaine2, Domaine3, Equipement
from .serializers import Domaine1Serializer, EquipementCarteSerializer, EquipementDetailSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Équipements d'une zone (GeoJSON)",
        parameters=[
            OpenApiParameter(
                "in_bbox", str, required=True,
                description="Zone visible : minLon,minLat,maxLon,maxLat (1° × 1° maximum). "
                            "Ex. 0.66,47.37,0.72,47.41 (Tours)",
            ),
        ],
    ),
    retrieve=extend_schema(summary="Fiche complète d'un équipement"),
)
class EquipementViewSet(viewsets.ReadOnlyModelViewSet):
    filter_backends = [DjangoFilterBackend, InBBoxLimiteFilter]
    filterset_class = EquipementFilter
    bbox_filter_field = "geom"           # champ utilisé par InBBoxFilter
    pagination_class = None              # le front découpe déjà en petites tuiles

    def get_queryset(self):
        if self.action == "retrieve":
            # Fiche : on charge les domaines et le département en une seule requête (jointures)
            return Equipement.objects.select_related("domaine3__domaine2__domaine1", "departement")
        # Carte : seulement les colonnes affichées. Le code domaine3 est la clé étrangère
        # elle-même (colonne domaine3_code), donc aucune jointure n'est nécessaire.
        return Equipement.objects.only("id", "nom", "geom", "domaine3")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return EquipementDetailSerializer
        return EquipementCarteSerializer

    def list(self, request, *args, **kwargs):
        # Jamais toute la région d'un coup : la zone visible est obligatoire
        if "in_bbox" not in request.query_params:
            raise ParseError("Le paramètre in_bbox est obligatoire (minLon,minLat,maxLon,maxLat).")
        return super().list(request, *args, **kwargs)


@extend_schema(summary="Arbre des domaines : domaine1 > domaine2 > domaine3")
class DomaineListView(generics.ListAPIView):
    serializer_class = Domaine1Serializer
    pagination_class = None

    def get_queryset(self):
        # 3 requêtes au total (une par niveau) au lieu d'une par domaine, triées par code
        return Domaine1.objects.order_by("code").prefetch_related(
            Prefetch("enfants", queryset=Domaine2.objects.order_by("code")),
            Prefetch("enfants__enfants", queryset=Domaine3.objects.order_by("code")),
        )


class VilleListView(APIView):
    LIMITE_RECHERCHE = 20

    @extend_schema(
        summary="Villes (autocomplétion)",
        parameters=[
            OpenApiParameter("search", str, description="Début ou partie du nom, ex. tou. "
                                                        "Sans ce paramètre : toutes les villes."),
        ],
        responses=serializers.ListSerializer(child=serializers.CharField()),   # liste de noms
    )
    def get(self, request):
        villes = Equipement.objects.values_list("ville", flat=True).distinct().order_by("ville")
        recherche = request.query_params.get("search", "").strip()
        if recherche:
            villes = villes.filter(ville__icontains=recherche)[: self.LIMITE_RECHERCHE]
        return Response(list(villes))
