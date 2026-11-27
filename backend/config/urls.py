"""
Routes de TerriScope.

Les ViewSets des applications (bpe, prospection) seront déclarés sur le router ci-dessous.
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

# Le router génère automatiquement les URL d'un ViewSet (liste, détail, création…)
router = DefaultRouter()
# Exemple à venir : router.register("equipements", EquipementViewSet, basename="equipement")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    # Documentation de l'API
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
