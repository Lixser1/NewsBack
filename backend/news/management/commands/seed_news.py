"""Создаёт демонстрационные новости. Команду можно запускать повторно."""

from django.core.management.base import BaseCommand

from accounts.models import Role
from news.models import News

SEED_NEWS = [
    {
        "title": "Расписание консультаций перед сессией",
        "body": (
            "Консультации по алгоритмам проходят по средам в 17:00, аудитория 312.\n"
            "Приходите с вопросами по разбору сложности и доказательствам."
        ),
        "author_role": Role.TEACHER,
    },
    {
        "title": "Первая лабораторная: сортировки",
        "body": (
            "Нужно реализовать быструю и пирамидальную сортировки, замерить время "
            "на массивах разного размера и оформить короткий отчёт.\n"
            "Дедлайн — через две недели."
        ),
        "author_role": Role.TEACHER,
    },
    {
        "title": "Собрали команду на разбор задач",
        "body": (
            "Ищем двоих человек для совместного разбора задач на графы. "
            "Пишите в чат группы, встречаемся в библиотеке."
        ),
        "author_role": Role.STUDENT,
    },
    {
        "title": "Конспект по динамическому программированию",
        "body": (
            "Выложил свои записи с лекции по ДП: задачи о кузнечике, рюкзаке и НВП. "
            "Буду рад, если поможете дополнить примерами кода."
        ),
        "author_role": Role.STUDENT,
    },
]


class Command(BaseCommand):
    help = "Создаёт демонстрационные новости, если их ещё нет"

    def handle(self, *args, **options):
        created = 0
        for item in SEED_NEWS:
            _, is_new = News.objects.get_or_create(
                title=item["title"],
                defaults={
                    "body": item["body"],
                    "author_role": item["author_role"],
                },
            )
            created += int(is_new)
        self.stdout.write(self.style.SUCCESS(f"Добавлено новостей: {created}"))
