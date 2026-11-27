from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from prospection.views import ImplantationViewSet, MeView, RegisterView

router = DefaultRouter()
router.register("implantations", ImplantationViewSet, basename="implantation")

urlpatterns = [
    path("auth/token/", obtain_auth_token, name="auth-token"),
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/me/", MeView.as_view(), name="auth-me"),
    path("", include(router.urls)),
]