"""Transformation des équipements et des domaines en JSON / GeoJSON."""

from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from .models import Domaine1, Domaine2, Domaine3, Equipement


class EquipementCarteSerializer(GeoFeatureModelSerializer):
    """Point de la carte : GeoJSON léger (le front en charge des milliers)."""

    class Meta:
        model = Equipement
        geo_field = "geom"                       # devient la "geometry" de chaque Feature
        fields = ["id", "nom", "domaine3"]       # id sort au niveau de la Feature, le reste dans "properties"


class EquipementRechercheSerializer(serializers.ModelSerializer):
    longitude = serializers.FloatField(source="geom.x")
    latitude = serializers.FloatField(source="geom.y")

    class Meta:
        model = Equipement
        fields = ["id", "nom", "adresse", "codepostal", "ville", "longitude", "latitude"]


class EquipementDetailSerializer(EquipementRechercheSerializer):
    """Fiche complète d'un équipement, avec les libellés des 3 niveaux de domaine."""

    departement = serializers.CharField(source="departement.libelle")
    domaine1 = serializers.CharField(source="domaine3.domaine2.domaine1.libelle")
    domaine2 = serializers.CharField(source="domaine3.domaine2.libelle")
    domaine3 = serializers.CharField(source="domaine3.libelle")
    domaine3_code = serializers.CharField(source="domaine3.code")

    class Meta:
        model = Equipement
        fields = [
            "id", "nom", "adresse", "codepostal", "ville", "siret", "departement",
            "domaine1", "domaine2", "domaine3", "domaine3_code", "longitude", "latitude",
        ]


# --- Arbre des domaines pour le filtre : domaine1 > domaine2 > domaine3 ---

class Domaine3Serializer(serializers.ModelSerializer):
    class Meta:
        model = Domaine3
        fields = ["code", "libelle"]


class Domaine2Serializer(serializers.ModelSerializer):
    enfants = Domaine3Serializer(many=True)      # "enfants" = related_name défini dans models.py

    class Meta:
        model = Domaine2
        fields = ["code", "libelle", "enfants"]


class Domaine1Serializer(serializers.ModelSerializer):
    enfants = Domaine2Serializer(many=True)

    class Meta:
        model = Domaine1
        fields = ["code", "libelle", "enfants"]
