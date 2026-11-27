"""
Routes de TerriScope.

Les ViewSets des applications (bpe, prospection) sont déclarés sur le router ci-dessous.
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from bpe.views import DomaineListView, EquipementViewSet, VilleListView

# Le router génère automatiquement les URL d'un ViewSet (liste, détail, création…)
router = DefaultRouter()
router.register("equipements", EquipementViewSet, basename="equipement")

urlpatterns = [
    path("admin/", admin.site.urls),
    # Vues simples (hors router)
    path("api/domaines/", DomaineListView.as_view(), name="domaines"),
    path("api/villes/", VilleListView.as_view(), name="villes"),
    path("api/", include(router.urls)),
    # Documentation de l'API
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
