"""
Reusable data table checks.
"""

from __future__ import annotations

from time import perf_counter
from typing import Callable
from urllib.parse import urljoin

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from core.evidence_collector import EvidenceCollector
from core.result import CheckResult, Severity


TICKETS_PATH = "/tickets"
EXPECTED_HEADERS = [
    "ID",
    "Title",
    "Status",
    "Priority",
    "Owner",
]
PRIORITY_ORDER = [
    "Critical",
    "High",
    "Medium",
    "Low",
]


def check_ticket_table_renders(
    driver,
    base_url: str,
    *,
    evidence_collector: EvidenceCollector | None = None,
) -> CheckResult:
    """
    Verify the tickets table renders expected headers and rows.
    """

    check_name = "data.ticket_table_renders"
    collector = evidence_collector or EvidenceCollector()
    start = perf_counter()

    try:
        driver.get(_tickets_url(base_url))
        _wait_for_element(driver, "tickets-table")

        headers = [
            element.text.strip()
            for element in driver.find_elements(By.CSS_SELECTOR, "#tickets-table th")
        ]
        row_count = len(_visible_rows(driver))
        count_text = driver.find_element(By.ID, "ticket-count").text.strip()
        evidence = [
            collector.browser_state(
                driver,
                label=f"{check_name}_state",
            )
        ]

        if headers == EXPECTED_HEADERS and row_count == 4 and count_text == "4 tickets shown":
            result = CheckResult.passed(
                check_name,
                "Ticket table renders expected headers and initial rows.",
                expected=f"{EXPECTED_HEADERS}; 4 rows",
                actual=f"{headers}; {row_count} rows",
                evidence=evidence,
                tags=["data", "table", "smoke"],
                metadata={
                    "row_count": row_count,
                    "headers": headers,
                },
            )
        else:
            result = CheckResult.failed(
                check_name,
                "Ticket table initial state does not match expectations.",
                severity=Severity.HIGH,
                expected=f"{EXPECTED_HEADERS}; 4 rows; 4 tickets shown",
                actual=f"{headers}; {row_count} rows; {count_text}",
                evidence=evidence + collector.failure_bundle(driver, check_name),
                tags=["data", "table", "smoke"],
                metadata={
                    "row_count": row_count,
                    "headers": headers,
                    "count_text": count_text,
                },
            )

        result.duration_ms = _duration_ms(start)
        return result

    except Exception as exc:
        return _unexpected_error(driver, collector, check_name, exc, start)


def check_ticket_search_and_status_filter(
    driver,
    base_url: str,
    *,
    evidence_collector: EvidenceCollector | None = None,
) -> CheckResult:
    """
    Verify search and status filters narrow the visible ticket rows.
    """

    check_name = "data.ticket_search_and_status_filter"
    collector = evidence_collector or EvidenceCollector()
    start = perf_counter()

    try:
        driver.get(_tickets_url(base_url))
        _wait_for_element(driver, "tickets-table")

        search = driver.find_element(By.ID, "ticket-search")
        search.send_keys("password")
        _wait_for_ticket_count(driver, "1 ticket shown")

        searched_ids = _visible_ticket_ids(driver)

        search.clear()
        Select(driver.find_element(By.ID, "status-filter")).select_by_visible_text("Open")
        _wait_for_ticket_count(driver, "2 tickets shown")

        filtered_ids = _visible_ticket_ids(driver)
        evidence = [
            collector.browser_state(
                driver,
                label=f"{check_name}_state",
            )
        ]

        if searched_ids == ["QA-104"] and filtered_ids == ["QA-101", "QA-104"]:
            result = CheckResult.passed(
                check_name,
                "Ticket search and status filter return expected rows.",
                expected="Search password -> QA-104; Open filter -> QA-101, QA-104",
                actual=f"search={searched_ids}; filter={filtered_ids}",
                evidence=evidence,
                tags=["data", "table", "filtering"],
                metadata={
                    "searched_ids": searched_ids,
                    "filtered_ids": filtered_ids,
                },
            )
        else:
            result = CheckResult.failed(
                check_name,
                "Ticket search or status filtering returned unexpected rows.",
                severity=Severity.MEDIUM,
                expected="Search password -> QA-104; Open filter -> QA-101, QA-104",
                actual=f"search={searched_ids}; filter={filtered_ids}",
                evidence=evidence + collector.failure_bundle(driver, check_name),
                tags=["data", "table", "filtering"],
                metadata={
                    "searched_ids": searched_ids,
                    "filtered_ids": filtered_ids,
                },
            )

        result.duration_ms = _duration_ms(start)
        return result

    except Exception as exc:
        return _unexpected_error(driver, collector, check_name, exc, start)


def check_ticket_priority_sort(
    driver,
    base_url: str,
    *,
    evidence_collector: EvidenceCollector | None = None,
) -> CheckResult:
    """
    Verify priority sorting orders visible rows by severity.
    """

    check_name = "data.ticket_priority_sort"
    collector = evidence_collector or EvidenceCollector()
    start = perf_counter()

    try:
        driver.get(_tickets_url(base_url))
        _wait_for_element(driver, "tickets-table")
        driver.find_element(By.ID, "sort-priority").click()
        _wait_for_first_ticket(driver, "QA-104")

        priorities = [
            row.find_elements(By.TAG_NAME, "td")[3].text.strip()
            for row in _visible_rows(driver)
        ]
        sorted_ids = _visible_ticket_ids(driver)
        evidence = [
            collector.browser_state(
                driver,
                label=f"{check_name}_state",
            )
        ]

        if priorities == PRIORITY_ORDER and sorted_ids[0] == "QA-104":
            result = CheckResult.passed(
                check_name,
                "Ticket priority sort orders rows from highest to lowest risk.",
                expected=str(PRIORITY_ORDER),
                actual=str(priorities),
                evidence=evidence,
                tags=["data", "table", "sorting", "risk"],
                metadata={
                    "sorted_ids": sorted_ids,
                    "priorities": priorities,
                },
            )
        else:
            result = CheckResult.failed(
                check_name,
                "Ticket priority sort did not order rows by expected risk.",
                severity=Severity.MEDIUM,
                expected=str(PRIORITY_ORDER),
                actual=str(priorities),
                evidence=evidence + collector.failure_bundle(driver, check_name),
                tags=["data", "table", "sorting", "risk"],
                metadata={
                    "sorted_ids": sorted_ids,
                    "priorities": priorities,
                },
            )

        result.duration_ms = _duration_ms(start)
        return result

    except Exception as exc:
        return _unexpected_error(driver, collector, check_name, exc, start)


def _tickets_url(base_url: str) -> str:
    """
    Return the tickets page URL for a base URL.
    """

    return urljoin(
        base_url,
        TICKETS_PATH,
    )


def _visible_rows(driver):
    """
    Return visible ticket table rows.
    """

    return [
        row
        for row in driver.find_elements(By.CSS_SELECTOR, "[data-ticket-row]")
        if row.is_displayed()
    ]


def _visible_ticket_ids(driver) -> list[str]:
    """
    Return IDs from visible ticket table rows.
    """

    return [
        row.find_elements(By.TAG_NAME, "td")[0].text.strip()
        for row in _visible_rows(driver)
    ]


def _wait_for_element(driver, element_id: str):
    """
    Wait until an element exists.
    """

    return WebDriverWait(
        driver,
        10,
    ).until(
        EC.presence_of_element_located(
            (By.ID, element_id)
        )
    )


def _wait_for_ticket_count(driver, expected_text: str):
    """
    Wait until the ticket count displays expected text.
    """

    return WebDriverWait(
        driver,
        10,
    ).until(
        EC.text_to_be_present_in_element(
            (By.ID, "ticket-count"),
            expected_text,
        )
    )


def _wait_for_first_ticket(driver, expected_id: str):
    """
    Wait until the first visible row has the expected ticket ID.
    """

    return WebDriverWait(
        driver,
        10,
    ).until(
        lambda current_driver: (
            _visible_ticket_ids(current_driver)
            and _visible_ticket_ids(current_driver)[0] == expected_id
        )
    )


def _unexpected_error(
    driver,
    collector: EvidenceCollector,
    check_name: str,
    exc: Exception,
    start: float,
) -> CheckResult:
    """
    Build a consistent unexpected-error result.
    """

    result = CheckResult.errored(
        check_name,
        "Unexpected error while executing data table check.",
        evidence=collector.failure_bundle(
            driver,
            check_name,
            exc,
        ),
        tags=["data", "runner"],
        error=repr(exc),
    )
    result.duration_ms = _duration_ms(start)

    return result


def _duration_ms(start: float) -> int:
    """
    Return elapsed milliseconds from a perf_counter start value.
    """

    return int(
        (perf_counter() - start) * 1000
    )


DATA_TABLE_CHECKS: dict[str, Callable[..., CheckResult]] = {
    "ticket_table_renders": check_ticket_table_renders,
    "ticket_search_and_status_filter": check_ticket_search_and_status_filter,
    "ticket_priority_sort": check_ticket_priority_sort,
}
