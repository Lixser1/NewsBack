# СтудНовости

Учебное веб-приложение: новостная доска с двумя ролями — преподаватель и студент.
Flask рендерит HTML-страницы, Django отвечает за данные и REST API, SQLite хранит новости,
всё запускается в Docker.

## Как устроено

```
Браузер ──HTTP──> frontend (Flask + Jinja2, :5000) ──HTTP/JSON──> backend (Django + DRF, :8000)
                                                                        │
                                                                      SQLite
```

- `backend/` — Django-проект. Приложение `accounts` отвечает за регистрацию,
  вход и токены, приложение `news` — за CRUD новостей через Django REST Framework,
  миграции и наполнение демо-данными при старте контейнера.
- `frontend/` — Flask-приложение. Формы входа и регистрации, все страницы,
  шапка и подвал, обращение к API через `requests`. В базу напрямую не ходит.
- `docker-compose.yml` — два контейнера. Файл SQLite лежит в именованном volume
  и виден только backend'у.

## Запуск в Docker

```bash
cp .env.example .env      # секреты можно оставить учебными
docker compose up --build
```

Приложение: <http://localhost:5000>

Первый запуск создаёт базу, применяет миграции и добавляет 4 демонстрационные новости.
Команда наполнения идемпотентна: повторный запуск не создаёт дубликатов.

Чтобы войти, откройте <http://localhost:5000/register>, создайте аккаунт и выберите
роль. После регистрации вход выполняется по логину и паролю на `/login`.

Остановить: `docker compose down`. Удалить и данные: `docker compose down -v`.

## Запуск без Docker

Нужны два терминала и два виртуальных окружения.

Backend:

```bash
cd backend
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_news
python manage.py runserver 8000
```

Frontend:

```bash
cd frontend
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
API_BASE_URL=http://127.0.0.1:8000 FLASK_SECRET_KEY=dev flask --app app run --port 5000
```

Открыть <http://127.0.0.1:5000>.

## Страницы

| Маршрут | Назначение |
|---|---|
| `GET/POST /login` | вход по логину и паролю |
| `GET/POST /register` | регистрация с выбором роли |
| `POST /logout` | выход |
| `GET /news` | список новостей с автором и датой |
| `GET /news/<id>` | полный текст новости |
| `GET /news/new` | форма создания |
| `GET /news/<id>/edit` | форма редактирования |
| `POST /news/<id>/delete` | удаление |

Страницы `/news*` доступны только после входа: без токена происходит
редирект на `/login`.

## API

| Метод | Путь | Доступ |
|---|---|---|
| `POST` | `/api/auth/register/` | без токена |
| `POST` | `/api/auth/login/` | без токена |
| `POST` | `/api/auth/logout/` | токен |
| `GET` | `/api/auth/me/` | токен |
| `GET` | `/api/news/` | токен |
| `POST` | `/api/news/` | токен |
| `GET` | `/api/news/<id>/` | токен |
| `PUT` / `PATCH` | `/api/news/<id>/` | токен |
| `DELETE` | `/api/news/<id>/` | токен |
| `GET` | `/api/health/` | без токена |

Поля новости: `id`, `title`, `body`, `author_role` (`teacher` / `student`),
`author_role_display`, `created_at`, `updated_at`.

`author_role` теперь только для чтения: при создании Django сам берёт роль из
профиля авторизованного пользователя, а при редактировании автор сохраняется.
Подставить чужую роль через JSON нельзя. Пустые заголовок и текст отклоняются
с кодом 400.

Авторизация устроена так: Flask отправляет логин и пароль в
`/api/auth/login/`, получает токен DRF и хранит его в подписанной сессии.
Каждый следующий запрос к API идёт с заголовком `Authorization: Token ...`.

## Особенности учебного варианта

- Пользователи хранятся в стандартной таблице Django, пароли хэшируются.
  Роль лежит в связанном профиле `accounts.Profile`.
- Токен DRF передаётся через подписанную cookie сессии Flask. Для учебного
  проекта этого достаточно; в продакшене лучше серверное хранилище сессий.
- Ограничений на редактирование и удаление нет: любой вошедший может менять любую новость.
- SQLite выбран для простоты. Для реальной нагрузки стоит взять PostgreSQL;
  менять нужно только `DATABASES` в `backend/config/settings.py` и добавить сервис в compose.

## Полезные команды

```bash
# логи контейнеров
docker compose logs -f backend

# миграции вручную внутри контейнера
docker compose exec backend python manage.py migrate

# консоль Django
docker compose exec backend python manage.py shell
```
