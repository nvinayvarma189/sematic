# Standard library
import base64
import typing
from urllib.parse import urlunsplit, urlencode, urlsplit

# Third-party
import sqlalchemy
import flask

# Glow
from glow.api.app import glow_api
from glow.db.db import db
from glow.db.models.run import Run


DEFAULT_LIMIT = 20


@glow_api.route("/api/v1/runs", methods=["GET"])
def list_runs_endpoint() -> flask.Response:
    request_args = flask.request.args

    limit: int = int(request_args.get("limit", DEFAULT_LIMIT))
    if limit < 1:
        raise Exception("limit must be greater than 0")

    cursor: typing.Optional[str] = None
    decoded_cursor: typing.Optional[str] = None
    if "cursor" in request_args:
        cursor = request_args["cursor"]
        try:
            decoded_cursor = base64.urlsafe_b64decode(bytes(cursor, "utf-8")).decode(
                "utf-8"
            )
        except Exception:
            raise Exception("invalid cursor")

    with db().get_session() as session:
        query = session.query(Run).order_by(sqlalchemy.desc(Run.created_at))

        if decoded_cursor is not None:
            query = query.filter(
                sqlalchemy.text(
                    "(runs.created_at || '_' || runs.id) < '{}'".format(
                        # "CONCAT(runs.created_at, '_', runs.id) < '{}'".format(
                        decoded_cursor
                    )
                )
            )
        runs: typing.List[Run] = query.limit(limit).all()
        after_cursor_count: int = query.count()

    current_url_params: typing.Dict[str, str] = dict(limit=str(limit))
    if cursor is not None:
        current_url_params["cursor"] = cursor

    scheme, netloc, path, _, fragment = urlsplit(flask.request.url)
    current_page_url = urlunsplit(
        (scheme, netloc, path, urlencode(current_url_params), fragment)
    )

    next_page_url: typing.Optional[str] = None
    next_cursor: typing.Optional[str] = None

    if runs and after_cursor_count > limit:
        next_url_params: typing.Dict[str, str] = dict(limit=str(limit))
        next_cursor = _make_cursor("{}_{}".format(runs[-1].created_at, runs[-1].id))
        next_url_params["cursor"] = next_cursor
        next_page_url = urlunsplit(
            (scheme, netloc, path, urlencode(next_url_params), fragment)
        )

    content = [run.to_json_encodable() for run in runs]

    payload = dict(
        current_page_url=current_page_url,
        next_page_url=next_page_url,
        limit=limit,
        next_cursor=next_cursor,
        after_cursor_count=after_cursor_count,
        content=content,
    )

    return flask.jsonify(payload)


def _make_cursor(key: str) -> str:
    return base64.urlsafe_b64encode(bytes(key, "utf-8")).decode("utf-8")