"""
Unit tests for the local demo application.
"""

from demo_app.app import create_app, validate_contact_form


def test_health_endpoint_returns_ok():
    app = create_app()
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_home_page_exposes_demo_navigation_links():
    app = create_app()
    client = app.test_client()

    response = client.get("/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "QA Demo Target" in html
    assert "Redirect Link" in html
    assert "Contact Form" in html


def test_status_code_detail_returns_configured_status():
    app = create_app()
    client = app.test_client()

    response = client.get("/status-codes/500")

    assert response.status_code == 500
    assert "server error 500" in response.get_data(as_text=True)


def test_contact_form_validation_reports_required_fields():
    errors = validate_contact_form(
        {
            "name": "",
            "email": "",
            "message": "",
        }
    )

    assert errors == {
        "name": "Name is required.",
        "email": "Email is required.",
        "message": "Message is required.",
    }


def test_contact_form_accepts_valid_submission():
    app = create_app()
    client = app.test_client()

    response = client.post(
        "/contact",
        data={
            "name": "Ada Lovelace",
            "email": "ada@example.com",
            "message": "This is a valid automation message.",
        },
    )
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Contact Submitted" in html
    assert "Ada Lovelace" in html
