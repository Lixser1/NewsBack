from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import NewsViewSet, health

router = DefaultRouter()
router.register("news", NewsViewSet, basename="news")

urlpatterns = [
    path("health/", health, name="health"),
    path("", include(router.urls)),
]
