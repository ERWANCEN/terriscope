from django.conf import settings
from django.contrib.gis.db import models


class Implantation(models.Model):
    # Chaque implantation appartient à un utilisateur unique (isolation des données privées)
    proprietaire = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="implantations",
    )
    titre = models.CharField(max_length=255)
    # Seul lien avec le référentiel BPE : le type de commerce envisagé (jamais un équipement)
    domaine3 = models.ForeignKey(
        "bpe.Domaine3",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    commentaire = models.TextField(blank=True)
    geom = models.PointField(srid=4326)  # Point(lon, lat), système GPS WGS 84
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.titre} ({self.proprietaire})"