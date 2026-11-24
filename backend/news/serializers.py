from rest_framework import serializers

from .models import News


def nonempty(label: str):
    def validator(value: str) -> str:
        value = value.strip()
        if not value:
            raise serializers.ValidationError(f"{label} не может быть пустым.")
        return value

    return staticmethod(validator)


class NewsSerializer(serializers.ModelSerializer):
    author_role_display = serializers.CharField(
        source="get_author_role_display", read_only=True
    )

    class Meta:
        model = News
        fields = [
            "id",
            "title",
            "body",
            "author_role",
            "author_role_display",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["author_role", "created_at", "updated_at"]
        extra_kwargs = {
            "title": {"allow_blank": True},
            "body": {"allow_blank": True},
        }

    validate_title = nonempty("Заголовок")
    validate_body = nonempty("Текст новости")
