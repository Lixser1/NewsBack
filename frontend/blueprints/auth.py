from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from api_client import ApiError

auth_bp = Blueprint("auth", __name__)

PUBLIC_ENDPOINTS = {"index", "auth.login", "auth.register", "static"}


def _api():
    return current_app.extensions["api"].with_token(session.get("token"))


def _safe_next() -> str:
    next_url = request.values.get("next") or ""
    if not next_url.startswith("/") or next_url.startswith("//"):
        return url_for("news.list_news")
    return next_url


def _login_session(payload: dict) -> None:
    session.clear()
    session["token"] = payload["token"]
    session["username"] = payload["username"]
    session["role"] = payload["role"]
    session["role_label"] = payload["role_label"]


@auth_bp.before_app_request
def require_role():
    endpoint = request.endpoint or ""
    if endpoint in PUBLIC_ENDPOINTS or endpoint.startswith("static"):
        return None
    if not session.get("token") or not session.get("role"):
        return redirect(url_for("auth.login", next=request.path))
    return None


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    next_url = _safe_next()

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        if not username or not password:
            flash("Введите логин и пароль.", "error")
            return (
                render_template("login.html", next_url=next_url, username=username),
                400,
            )

        try:
            payload = _api().login(username, password)
        except ApiError as exc:
            status = 401 if exc.status in (400, 401) else 502
            flash(str(exc), "error")
            return (
                render_template("login.html", next_url=next_url, username=username),
                status,
            )

        _login_session(payload)
        flash(
            f"Вы вошли как {payload['role_label'].lower()}.",
            "success",
        )
        return redirect(next_url)

    if session.get("token"):
        return redirect(url_for("news.list_news"))
    return render_template("login.html", next_url=next_url, username="")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    next_url = _safe_next()
    form = {"username": "", "email": "", "role": ""}
    errors: dict[str, list[str]] = {}

    if request.method == "POST":
        form = {
            "username": (request.form.get("username") or "").strip(),
            "email": (request.form.get("email") or "").strip(),
            "role": (request.form.get("role") or "").strip(),
        }
        password = request.form.get("password") or ""
        password_confirm = request.form.get("password_confirm") or ""

        if password != password_confirm:
            errors = {"password_confirm": ["Пароли не совпадают."]}
            return (
                render_template(
                    "register.html",
                    next_url=next_url,
                    form=form,
                    errors=errors,
                    message=None,
                ),
                400,
            )

        try:
            payload = _api().register(
                {
                    **form,
                    "password": password,
                    "password_confirm": password_confirm,
                }
            )
        except ApiError as exc:
            status = 400 if exc.status == 400 else 502
            return (
                render_template(
                    "register.html",
                    next_url=next_url,
                    form=form,
                    errors=exc.errors,
                    message=None if exc.errors else str(exc),
                ),
                status,
            )

        _login_session(payload)
        flash("Аккаунт создан, вы вошли в систему.", "success")
        return redirect(next_url)

    return render_template(
        "register.html",
        next_url=next_url,
        form=form,
        errors=errors,
        message=None,
    )


@auth_bp.post("/logout")
def logout():
    if session.get("token"):
        try:
            _api().logout()
        except ApiError:
            pass
    session.clear()
    flash("Вы вышли из аккаунта.", "success")
    return redirect(url_for("auth.login"))
