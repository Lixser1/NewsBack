from django.contrib.auth.models import User
from django.db import models


class Role(models.TextChoices):
    TEACHER = "teacher", "Преподаватель"
    STUDENT = "student", "Студент"


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="пользователь",
    )
    role = models.CharField("роль", max_length=10, choices=Role.choices)

    class Meta:
        verbose_name = "профиль"
        verbose_name_plural = "профили"

    def __str__(self) -> str:
        return f"{self.user.username} ({self.get_role_display()})"
