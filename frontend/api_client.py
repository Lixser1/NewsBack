from typing import Any

import requests


class ApiError(Exception):
    """Ошибка обращения к backend API."""

    def __init__(
        self,
        message: str,
        status: int | None = None,
        errors: dict[str, list[str]] | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.status = status
        self.errors = errors or {}


class ApiClient:
    def __init__(
        self,
        base_url: str,
        timeout: float = 5.0,
        token: str | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.token = token

    def with_token(self, token: str | None) -> "ApiClient":
        """Возвращает клиент для одного запроса с токеном пользователя."""
        return ApiClient(self.base_url, self.timeout, token)

    def _request(self, method: str, path: str, **kwargs) -> Any:
        url = f"{self.base_url}{path}"
        headers = dict(kwargs.pop("headers", None) or {})
        if self.token:
            headers["Authorization"] = f"Token {self.token}"

        try:
            response = requests.request(
                method,
                url,
                timeout=self.timeout,
                headers=headers,
                **kwargs,
            )
        except requests.RequestException as exc:
            raise ApiError(
                "Сервис данных недоступен. Попробуйте обновить страницу позже."
            ) from exc

        if response.status_code >= 400:
            raise self._build_error(response)
        if response.status_code == 204 or not response.content:
            return None
        try:
            return response.json()
        except ValueError as exc:
            raise ApiError("Сервис данных вернул неожиданный ответ.") from exc

    @staticmethod
    def _build_error(response: requests.Response) -> ApiError:
        try:
            payload = response.json()
        except ValueError:
            payload = {}

        errors: dict[str, list[str]] = {}
        detail = ""
        if isinstance(payload, dict):
            errors = {
                key: value
                for key, value in payload.items()
                if key != "detail" and isinstance(value, list)
            }
            detail = str(payload.get("detail") or "")

        if response.status_code == 401:
            message = detail or "Неверный логин или пароль."
        elif response.status_code == 403:
            message = detail or "Недостаточно прав."
        elif response.status_code == 404:
            message = "Новость не найдена."
        elif response.status_code >= 500:
            message = "Сервис данных временно недоступен."
        elif errors:
            message = "Проверьте заполнение формы."
        elif detail:
            message = detail
        else:
            message = "Не удалось выполнить запрос."

        return ApiError(message, status=response.status_code, errors=errors)

    def register(self, data: dict) -> dict:
        return self._request("POST", "/api/auth/register/", json=data)

    def login(self, username: str, password: str) -> dict:
        return self._request(
            "POST",
            "/api/auth/login/",
            json={"username": username, "password": password},
        )

    def logout(self) -> None:
        self._request("POST", "/api/auth/logout/")

    def me(self) -> dict:
        return self._request("GET", "/api/auth/me/")

    def list_news(self) -> list[dict]:
        return self._request("GET", "/api/news/")

    def get_news(self, news_id: int) -> dict:
        return self._request("GET", f"/api/news/{news_id}/")

    def create_news(self, data: dict) -> dict:
        return self._request("POST", "/api/news/", json=data)

    def update_news(self, news_id: int, data: dict) -> dict:
        return self._request("PUT", f"/api/news/{news_id}/", json=data)

    def delete_news(self, news_id: int) -> None:
        self._request("DELETE", f"/api/news/{news_id}/")
