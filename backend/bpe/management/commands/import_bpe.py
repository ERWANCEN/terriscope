import pyarrow.parquet as pq
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.db import transaction

from bpe.models import Departement, Domaine1, Domaine2, Domaine3, Equipement, Region

# Libellés absents du fichier parquet (écrits en dur pour la région 24)
REGIONS = {"24": "Centre-Val de Loire"}
DEPTS = {
    "18": "Cher",
    "28": "Eure-et-Loir",
    "36": "Indre",
    "37": "Indre-et-Loire",
    "41": "Loir-et-Cher",
    "45": "Loiret",
}
DOM_COLS = [
    "domaine1_code",
    "domaine1_libelle",
    "domaine2_code",
    "domaine2_libelle",
    "domaine3_code",
    "domaine3_libelle",
]


class Command(BaseCommand):
    help = "Importe les équipements BPE 2025 d'une région depuis le fichier parquet"

    def add_arguments(self, parser):
        parser.add_argument("--file", default="/data/bpe25_clean.parquet")
        parser.add_argument("--region", default="24")

    @transaction.atomic
    def handle(self, *args, file, region, **options):
        region = str(region)

        # 1. Extraction : toute la classification des domaines, puis équipements de la région
        dom = pq.read_table(file, columns=DOM_COLS).to_pandas().drop_duplicates()
        dom = dom.dropna(subset=["domaine1_code", "domaine2_code", "domaine3_code"]).fillna("")

        df = pq.read_table(file, filters=[("region", "=", region)]).to_pandas()

        # 2. Nettoyage : lignes géolocalisées uniquement, valeurs vides en "" et renommage
        df = df.dropna(subset=["lon", "lat"]).fillna("")
        df = df.rename(columns={"_id": "uuid", "SIRET": "siret"})

        # 3. Chargement des référentiels dans l'ordre des clés étrangères (idempotent)
        Region.objects.bulk_create(
            [Region(id_region=k, libelle=v) for k, v in REGIONS.items()],
            ignore_conflicts=True,
        )
        Departement.objects.bulk_create(
            [Departement(id_dept=k, libelle=v, region_id=region) for k, v in DEPTS.items()],
            ignore_conflicts=True,
        )

        d1 = dom.drop_duplicates("domaine1_code")
        Domaine1.objects.bulk_create(
            [Domaine1(code=str(r.domaine1_code)[:1], libelle=str(r.domaine1_libelle)[:255]) for r in d1.itertuples()],
            ignore_conflicts=True,
        )

        d2 = dom.drop_duplicates("domaine2_code")
        Domaine2.objects.bulk_create(
            [
                Domaine2(
                    code=str(r.domaine2_code)[:2],
                    domaine1_id=str(r.domaine1_code)[:1],
                    libelle=str(r.domaine2_libelle)[:255],
                )
                for r in d2.itertuples()
            ],
            ignore_conflicts=True,
        )

        d3 = dom.drop_duplicates("domaine3_code")
        Domaine3.objects.bulk_create(
            [
                Domaine3(
                    code=str(r.domaine3_code)[:4],
                    domaine2_id=str(r.domaine2_code)[:2],
                    libelle=str(r.domaine3_libelle)[:255],
                )
                for r in d3.itertuples()
            ],
            ignore_conflicts=True,
        )

        # 4. Purge et rechargement des équipements uniquement (préserve les liens vers Domaine3)
        Equipement.objects.all().delete()
        Equipement.objects.bulk_create(
            (
                Equipement(
                    id=r.uuid,
                    nom=str(r.nom)[:255],
                    adresse=str(r.adresse)[:255],
                    codepostal=str(r.codepostal)[:5],
                    ville=str(r.ville)[:255],
                    siret=str(r.siret)[:14],
                    departement_id=str(r.dept)[:3],
                    domaine3_id=str(r.domaine3_code)[:4],
                    geom=Point(float(r.lon), float(r.lat), srid=4326),
                )
                for r in df.itertuples()
            ),
            batch_size=5000,
        )

        self.stdout.write(self.style.SUCCESS(f"{Equipement.objects.count()} équipements importés"))