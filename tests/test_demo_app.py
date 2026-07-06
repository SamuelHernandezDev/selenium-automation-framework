"""
Unit tests for the local demo application.
"""

from demo_app.app import (
    QA_TICKETS,
    create_app,
    validate_contact_form,
    validate_login_form,
)


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
    assert "Login Flow" in html
    assert "Ticket Table" in html


def test_status_code_detail_returns_configured_status():
    app = create_app()
    client = app.test_client()

    response = client.get("/status-codes/500")

    assert response.status_code == 500
    assert "server error 500" in response.get_data(as_text=True)


def test_tickets_page_renders_deterministic_ticket_table():
    app = create_app()
    client = app.test_client()

    response = client.get("/tickets")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "QA Tickets" in html
    assert "ticket-search" in html
    assert "status-filter" in html
    assert "sort-priority" in html
    assert len(QA_TICKETS) == 4
    assert "QA-104" in html
    assert "Password reset handles expired token" in html


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


def test_login_validation_reports_required_fields():
    errors = validate_login_form(
        {
            "email": "",
            "password": "",
        }
    )

    assert errors == {
        "email": "Email is required.",
        "password": "Password is required.",
    }


def test_invalid_login_shows_form_error():
    app = create_app()
    client = app.test_client()

    response = client.post(
        "/login",
        data={
            "email": "qa@example.com",
            "password": "wrong-password",
        },
    )
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Invalid email or password." in html


def test_valid_login_reaches_dashboard_and_logout_returns_to_login():
    app = create_app()
    client = app.test_client()

    login_response = client.post(
        "/login",
        data={
            "email": "qa@example.com",
            "password": "Password123",
        },
        follow_redirects=True,
    )
    login_html = login_response.get_data(as_text=True)

    assert login_response.status_code == 200
    assert "Dashboard" in login_html
    assert "qa@example.com" in login_html

    logout_response = client.get(
        "/logout",
        follow_redirects=True,
    )
    logout_html = logout_response.get_data(as_text=True)

    assert logout_response.status_code == 200
    assert "Login" in logout_html
