from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers import LoginSerializer, ProfileSerializer, RegisterSerializer


def _auth_payload(user) -> dict:
    token, _ = Token.objects.get_or_create(user=user)
    return {"token": token.key, **ProfileSerializer(user.profile).data}


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return Response(_auth_payload(user), status=status.HTTP_201_CREATED)


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = authenticate(
        username=serializer.validated_data["username"].strip(),
        password=serializer.validated_data["password"],
    )
    if user is None:
        return Response(
            {"detail": "Неверный логин или пароль."},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    if not hasattr(user, "profile"):
        return Response(
            {"detail": "У пользователя не настроена роль."},
            status=status.HTTP_403_FORBIDDEN,
        )
    return Response(_auth_payload(user))


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    Token.objects.filter(user=request.user).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    profile = getattr(request.user, "profile", None)
    if profile is None:
        return Response(
            {"detail": "У пользователя не настроена роль."},
            status=status.HTTP_403_FORBIDDEN,
        )
    return Response(ProfileSerializer(profile).data)
