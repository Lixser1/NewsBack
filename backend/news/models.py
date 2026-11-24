from django.db import models

from accounts.models import Role


class News(models.Model):
    title = models.CharField("заголовок", max_length=200)
    body = models.TextField("текст")
    author_role = models.CharField("автор", max_length=10, choices=Role.choices)
    created_at = models.DateTimeField("создано", auto_now_add=True)
    updated_at = models.DateTimeField("обновлено", auto_now=True)

    class Meta:
        verbose_name = "новость"
        verbose_name_plural = "новости"
        ordering = ["-created_at", "-id"]

    def __str__(self) -> str:
        return self.title
