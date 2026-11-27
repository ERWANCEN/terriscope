"""
Référentiel BPE 2025 (lecture seule) : 6 tables, noms repris du schéma du sujet.

Ordre des clés étrangères pour l'import : regions > depts, domaine1 > domaine2 > domaine3, puis bpe.
"""

from django.contrib.gis.db import models


class Region(models.Model):
    id_region = models.CharField(max_length=3, primary_key=True)
    libelle = models.CharField(max_length=255)

    class Meta:
        db_table = "regions"

    def __str__(self):
        return f"{self.id_region} {self.libelle}"


class Departement(models.Model):
    id_dept = models.CharField(max_length=3, primary_key=True)
    region = models.ForeignKey(Region, on_delete=models.PROTECT, db_column="id_region")
    libelle = models.CharField(max_length=255)

    class Meta:
        db_table = "depts"

    def __str__(self):
        return f"{self.id_dept} {self.libelle}"


class Domaine1(models.Model):
    code = models.CharField(max_length=1, primary_key=True)       # ex. "F"
    libelle = models.CharField(max_length=255)

    class Meta:
        db_table = "domaine1"

    def __str__(self):
        return f"{self.code} {self.libelle}"


class Domaine2(models.Model):
    code = models.CharField(max_length=2, primary_key=True)       # ex. "F3"
    domaine1 = models.ForeignKey(Domaine1, on_delete=models.PROTECT,
                                 db_column="domaine1_code", related_name="enfants")
    libelle = models.CharField(max_length=255)

    class Meta:
        db_table = "domaine2"

    def __str__(self):
        return f"{self.code} {self.libelle}"


class Domaine3(models.Model):
    code = models.CharField(max_length=4, primary_key=True)       # ex. "F307"
    domaine2 = models.ForeignKey(Domaine2, on_delete=models.PROTECT,
                                 db_column="domaine2_code", related_name="enfants")
    libelle = models.CharField(max_length=255)

    class Meta:
        db_table = "domaine3"

    def __str__(self):
        return f"{self.code} {self.libelle}"


class Equipement(models.Model):
    id = models.UUIDField(primary_key=True)                       # colonne _id du parquet
    domaine3 = models.ForeignKey(Domaine3, on_delete=models.PROTECT, db_column="domaine3_code")
    # Le schéma du sujet montre id_dept et dept : fusionnés en une seule clé étrangère
    departement = models.ForeignKey(Departement, on_delete=models.PROTECT, db_column="id_dept")
    nom = models.CharField(max_length=255, blank=True)
    adresse = models.CharField(max_length=255, blank=True)
    codepostal = models.CharField(max_length=5, blank=True)
    ville = models.CharField(max_length=255, db_index=True)       # index pour le filtre par ville
    siret = models.CharField(max_length=14, blank=True)
    geom = models.PointField(srid=4326)                           # Point(lon, lat), index GiST automatique

    class Meta:
        db_table = "bpe"

    def __str__(self):
        return self.nom or str(self.id)
