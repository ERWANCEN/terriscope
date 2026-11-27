from rest_framework import generics, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from prospection.models import Implantation
from prospection.serializers import ImplantationSerializer, RegisterSerializer


class ImplantationViewSet(viewsets.ModelViewSet):
    serializer_class = ImplantationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Évite une erreur lors de la génération de la doc Swagger (utilisateur anonyme)
        if getattr(self, "swagger_fake_view", False):
            return Implantation.objects.none()
        # Isolation stricte : l'utilisateur connecté ne voit QUE ses propres points
        return Implantation.objects.filter(proprietaire=self.request.user)

    def perform_create(self, serializer):
        # Le propriétaire est toujours fixé côté serveur, jamais envoyé par le client
        serializer.save(proprietaire=self.request.user)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key}, status=status.HTTP_201_CREATED)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "id": request.user.id,
            "username": request.user.username,
        })