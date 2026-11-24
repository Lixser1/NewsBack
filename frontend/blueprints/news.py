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

news_bp = Blueprint("news", __name__, url_prefix="/news")


def _api():
    return current_app.extensions["api"].with_token(session.get("token"))


def _form_data() -> dict:
    return {
        "title": (request.form.get("title") or "").strip(),
        "body": (request.form.get("body") or "").strip(),
    }


def _render_error(exc: ApiError, status: int | None = None):
    if exc.status == 401:
        session.clear()
        flash("Сессия истекла, войдите заново.", "error")
        return redirect(url_for("auth.login", next=request.path))
    return render_template("error.html", message=str(exc)), status or 502


@news_bp.get("/")
def list_news():
    try:
        items = _api().list_news()
    except ApiError as exc:
        return _render_error(exc)
    return render_template("news/list.html", items=items)


@news_bp.get("/<int:news_id>")
def detail(news_id: int):
    try:
        item = _api().get_news(news_id)
    except ApiError as exc:
        return _render_error(exc, 404 if exc.status == 404 else None)
    return render_template("news/detail.html", item=item)


@news_bp.route("/new", methods=["GET", "POST"])
def create():
    form = {"title": "", "body": ""}
    if request.method == "POST":
        form = _form_data()
        try:
            item = _api().create_news(form)
        except ApiError as exc:
            status = 400 if exc.status == 400 else 502
            return (
                render_template(
                    "news/form.html",
                    mode="create",
                    form=form,
                    errors=exc.errors,
                    message=None if exc.errors else str(exc),
                    news_id=None,
                ),
                status,
            )
        flash("Новость опубликована.", "success")
        return redirect(url_for("news.detail", news_id=item["id"]))
    return render_template(
        "news/form.html", mode="create", form=form, errors={}, message=None, news_id=None
    )


@news_bp.route("/<int:news_id>/edit", methods=["GET", "POST"])
def edit(news_id: int):
    if request.method == "POST":
        form = _form_data()
        try:
            _api().update_news(news_id, form)
        except ApiError as exc:
            if exc.status == 404:
                return _render_error(exc, 404)
            status = 400 if exc.status == 400 else 502
            return (
                render_template(
                    "news/form.html",
                    mode="edit",
                    form=form,
                    errors=exc.errors,
                    message=None if exc.errors else str(exc),
                    news_id=news_id,
                ),
                status,
            )
        flash("Изменения сохранены.", "success")
        return redirect(url_for("news.detail", news_id=news_id))

    try:
        item = _api().get_news(news_id)
    except ApiError as exc:
        return _render_error(exc, 404 if exc.status == 404 else None)
    return render_template(
        "news/form.html", mode="edit", form=item, errors={}, message=None, news_id=news_id
    )


@news_bp.post("/<int:news_id>/delete")
def delete(news_id: int):
    try:
        _api().delete_news(news_id)
    except ApiError as exc:
        flash(str(exc), "error")
        return redirect(url_for("news.detail", news_id=news_id))
    flash("Новость удалена.", "success")
    return redirect(url_for("news.list_news"))
