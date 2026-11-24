from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from .models import News
from .serializers import NewsSerializer


def health(request):
    return JsonResponse({"status": "ok"})


class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsSerializer

    def _author_role(self) -> str:
        profile = getattr(self.request.user, "profile", None)
        if profile is None:
            raise PermissionDenied("У пользователя не настроена роль.")
        return profile.role

    def perform_create(self, serializer):
        serializer.save(author_role=self._author_role())
