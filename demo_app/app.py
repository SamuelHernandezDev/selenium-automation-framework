"""
Deterministic local web app used as a Selenium automation target.
"""

from __future__ import annotations

from dataclasses import dataclass
from email.utils import parseaddr

from flask import Flask, redirect, render_template, request, url_for


@dataclass(frozen=True)
class ContactSubmission:
    """
    Sanitized contact form submission.
    """

    name: str
    email: str
    message: str


def create_app() -> Flask:
    """
    Create the demo Flask application.
    """

    app = Flask(__name__)

    @app.get("/")
    def home():
        return render_template("home.html")

    @app.get("/redirect")
    def redirect_page():
        return render_template("redirect.html")

    @app.get("/redirect/target")
    def redirect_target():
        return redirect(url_for("status_codes"))

    @app.get("/status-codes")
    def status_codes():
        codes = [
            "200",
            "301",
            "404",
            "500",
        ]

        return render_template(
            "status_codes.html",
            codes=codes,
        )

    @app.get("/status-codes/<code>")
    def status_code_detail(code: str):
        messages = {
            "200": "This page represents a successful 200 response.",
            "301": "This page represents a 301 redirect scenario.",
            "404": "This page represents a not found 404 response.",
            "500": "This page represents a server error 500 response.",
        }

        status = int(code) if code in messages else 404

        return (
            render_template(
                "status_detail.html",
                code=code,
                message=messages.get(
                    code,
                    "The requested status code is not configured.",
                ),
            ),
            status,
        )

    @app.route(
        "/contact",
        methods=[
            "GET",
            "POST",
        ],
    )
    def contact():
        errors = {}
        values = {
            "name": "",
            "email": "",
            "message": "",
        }

        if request.method == "POST":
            values = {
                "name": request.form.get("name", "").strip(),
                "email": request.form.get("email", "").strip(),
                "message": request.form.get("message", "").strip(),
            }
            errors = validate_contact_form(values)

            if not errors:
                submission = ContactSubmission(**values)

                return render_template(
                    "form_success.html",
                    submission=submission,
                )

        return render_template(
            "contact.html",
            errors=errors,
            values=values,
        )

    @app.get("/health")
    def health():
        return {
            "status": "ok",
            "service": "qa-demo-target",
        }

    return app


def validate_contact_form(values: dict[str, str]) -> dict[str, str]:
    """
    Validate contact form values and return field-level errors.
    """

    errors = {}

    if not values["name"]:
        errors["name"] = "Name is required."
    elif len(values["name"]) > 60:
        errors["name"] = "Name must be 60 characters or fewer."

    if not values["email"]:
        errors["email"] = "Email is required."
    elif not is_valid_email(values["email"]):
        errors["email"] = "Enter a valid email address."

    if not values["message"]:
        errors["message"] = "Message is required."
    elif len(values["message"]) < 10:
        errors["message"] = "Message must be at least 10 characters."
    elif len(values["message"]) > 500:
        errors["message"] = "Message must be 500 characters or fewer."

    return errors


def is_valid_email(value: str) -> bool:
    """
    Return whether a value looks like a valid email address.
    """

    _, address = parseaddr(value)

    return (
        "@" in address
        and "." in address.rsplit("@", maxsplit=1)[-1]
    )


app = create_app()


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
    )
