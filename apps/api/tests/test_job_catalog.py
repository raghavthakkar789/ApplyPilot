from unittest.mock import AsyncMock, patch

import pytest

from applypilot.adapters.jobs.ashby import AshbyAdapter
from applypilot.adapters.jobs.base import AdapterError
from applypilot.adapters.jobs.greenhouse import GreenhouseAdapter
from applypilot.adapters.jobs.lever import LeverAdapter
from applypilot.adapters.jobs.remotive import RemotiveAdapter
from applypilot.domain.jobs.job import SourceJob
from tests.auth_helpers import ORIGIN, client, initialize, reset_auth_database


@pytest.fixture(autouse=True)
def clean_database() -> None:
    reset_auth_database()


def csrf_headers(owner: object) -> dict[str, str]:
    token = owner.cookies.get("applypilot_csrf")  # type: ignore[attr-defined]
    assert token
    return {**ORIGIN, "X-ApplyPilot-CSRF": token}


def test_manual_entry_requires_authentication_csrf_and_origin_and_never_fetches() -> None:
    payload = {
        "title": "Synthetic Engineer",
        "employer": "Example Labs",
        "description": "Safe text",
        "source_url": "https://example.test/jobs/1",
    }
    with client() as anonymous:
        assert anonymous.post("/api/manual-jobs", json=payload).status_code == 401
    with client() as owner:
        initialize(owner)
        assert owner.post("/api/manual-jobs", json=payload).status_code == 403
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as external_get:
            created = owner.post("/api/manual-jobs", headers=csrf_headers(owner), json=payload)
        assert created.status_code == 201
        external_get.assert_not_called()
        body = created.json()
        assert body["freshness_state"] == "manually_entered"
        assert (
            body["sources"][0]["attribution"]
            == "Manually entered — source not automatically verified"
        )
        assert body["match_status"] == "not_evaluated"


def test_manual_entry_strips_active_html_and_rejects_unsafe_urls() -> None:
    with client() as owner:
        initialize(owner)
        headers = csrf_headers(owner)
        created = owner.post(
            "/api/manual-jobs",
            headers=headers,
            json={
                "title": "Role",
                "employer": "Example",
                "description": "<script>bad()</script><p>Useful</p>",
            },
        )
        assert created.status_code == 201
        assert created.json()["description"] == "Useful"
        assert (
            owner.post(
                "/api/manual-jobs",
                headers=headers,
                json={"title": "Role", "employer": "Example", "source_url": "file:///etc/passwd"},
            ).status_code
            == 422
        )


def test_official_adapter_contracts_and_attribution() -> None:
    greenhouse = GreenhouseAdapter().parse(
        {
            "jobs": [
                {
                    "id": 1,
                    "title": "Engineer",
                    "absolute_url": "https://boards.greenhouse.io/example/jobs/1",
                    "location": {"name": "Remote"},
                    "content": "<p>Build</p>",
                }
            ]
        },
        "Example",
    )
    lever = LeverAdapter().parse(
        [
            {
                "id": "l1",
                "text": "Engineer",
                "hostedUrl": "https://jobs.lever.co/example/l1",
                "applyUrl": "https://jobs.lever.co/example/l1/apply",
                "descriptionPlain": "Build",
                "categories": {"location": "Remote"},
            }
        ],
        "Example",
    )
    ashby = AshbyAdapter().parse(
        {
            "apiVersion": "1",
            "jobs": [
                {
                    "id": "a1",
                    "title": "Engineer",
                    "jobUrl": "https://jobs.ashbyhq.com/example/a1",
                    "applyUrl": "https://jobs.ashbyhq.com/example/a1/application",
                    "isListed": True,
                }
            ],
        },
        "Example",
    )
    remotive = RemotiveAdapter().parse(
        {
            "jobs": [
                {
                    "id": 1,
                    "title": "Engineer",
                    "company_name": "Example",
                    "url": "https://remotive.com/remote-jobs/software-dev/engineer-1",
                    "description": "Build",
                }
            ]
        },
        "Remotive",
    )
    assert [items[0].attribution for items in (greenhouse, lever, ashby, remotive)] == [
        "Source: Greenhouse",
        "Source: Lever",
        "Source: Ashby",
        "Source: Remotive",
    ]
    assert all(
        "<" not in items[0].description_text for items in (greenhouse, lever, ashby, remotive)
    )


def test_adapter_urls_are_fixed_and_identifiers_are_validated() -> None:
    assert GreenhouseAdapter().url("example").startswith("https://boards-api.greenhouse.io/")
    assert LeverAdapter().url("example").startswith("https://api.lever.co/")
    assert AshbyAdapter().url("example").startswith("https://api.ashbyhq.com/")
    assert RemotiveAdapter().url(None) == "https://remotive.com/api/remote-jobs"
    for adapter in (GreenhouseAdapter(), LeverAdapter(), AshbyAdapter()):
        with pytest.raises(AdapterError):
            adapter.url("../../internal")


def test_registry_validation_and_sync_use_only_adapter_contract() -> None:
    synthetic = SourceJob(
        "1",
        "Engineer",
        "Example Labs",
        "https://example.test/job/1",
        None,
        "Build",
        None,
        None,
        None,
        None,
        None,
        "Source: Greenhouse",
        {"id": 1},
    )
    with client() as owner:
        initialize(owner)
        headers = csrf_headers(owner)
        with patch(
            "applypilot.adapters.jobs.greenhouse.GreenhouseAdapter.retrieve",
            new=AsyncMock(return_value=[synthetic]),
        ):
            response = owner.post(
                "/api/source-registry",
                headers=headers,
                json={
                    "provider": "greenhouse",
                    "employer_name": "Example Labs",
                    "employer_domain": "example.test",
                    "board_identifier": "example",
                    "careers_url": "https://example.test/careers",
                    "verification_method": "owner reviewed careers page",
                },
            )
        assert response.status_code == 200
        assert response.json()["enabled"] is True


def test_registry_employer_mismatch_fails_closed() -> None:
    mismatched = SourceJob(
        "1",
        "Engineer",
        "Different Employer",
        "https://example.test/job/1",
        None,
        "Build",
        None,
        None,
        None,
        None,
        None,
        "Source: Greenhouse",
        {"id": 1},
    )
    with client() as owner:
        initialize(owner)
        with patch(
            "applypilot.adapters.jobs.greenhouse.GreenhouseAdapter.retrieve",
            new=AsyncMock(return_value=[mismatched]),
        ):
            response = owner.post(
                "/api/source-registry",
                headers=csrf_headers(owner),
                json={
                    "provider": "greenhouse",
                    "employer_name": "Example Labs",
                    "employer_domain": "example.test",
                    "board_identifier": "example",
                    "careers_url": "https://example.test/careers",
                    "verification_method": "owner reviewed careers page",
                },
            )
        assert response.status_code == 200
        assert response.json()["enabled"] is False
        assert response.json()["last_failure_category"] == "employer_mismatch"


def test_uncertain_duplicate_requires_owner_reason_and_preserves_both_jobs() -> None:
    payload = {
        "title": "Synthetic Engineer",
        "employer": "Example Labs",
        "location": "Remote",
        "description": "Different owner-supplied descriptions",
    }
    with client() as owner:
        initialize(owner)
        headers = csrf_headers(owner)
        first = owner.post("/api/manual-jobs", headers=headers, json=payload)
        second = owner.post("/api/manual-jobs", headers=headers, json=payload)
        assert first.status_code == second.status_code == 201
        candidates = owner.get("/api/job-deduplication").json()
        assert len(candidates) == 1
        assert candidates[0]["status"] == "pending"
        candidate_id = candidates[0]["id"]
        assert (
            owner.post(
                f"/api/job-deduplication/{candidate_id}/split",
                headers=headers,
                json={"reason": "Distinct owner records"},
            ).json()["status"]
            == "kept_separate"
        )
        assert len(owner.get("/api/jobs").json()["jobs"]) == 2
