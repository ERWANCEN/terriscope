from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from prospection.models import Implantation

User = get_user_model()


class ImplantationSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Implantation
        geo_field = "geom"
        # proprietaire est volontairement absent : il est fixé côté serveur dans la vue
        fields = ["id", "titre", "domaine3", "commentaire", "cree_le", "modifie_le"]
        read_only_fields = ["id", "cree_le", "modifie_le"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "password"]

    def create(self, validated_data):
        # create_user chiffre automatiquement le mot de passe en base
        return User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
        )