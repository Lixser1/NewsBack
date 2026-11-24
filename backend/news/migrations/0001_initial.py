# Generated for the initial News model.

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="News",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=200, verbose_name="заголовок")),
                ("body", models.TextField(verbose_name="текст")),
                (
                    "author_role",
                    models.CharField(
                        choices=[("teacher", "Преподаватель"), ("student", "Студент")],
                        max_length=10,
                        verbose_name="автор",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="создано"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="обновлено"),
                ),
            ],
            options={
                "verbose_name": "новость",
                "verbose_name_plural": "новости",
                "ordering": ["-created_at", "-id"],
            },
        ),
    ]
