from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import DatabaseError

from applypilot.models.candidate_fact import (
    CandidateFactConfirmation,
    CandidateFactVersion,
)
from applypilot.models.security_event import SecurityEvent
from applypilot.repositories.database import SessionFactory
from applypilot.schemas.candidate_fact import FactEditRequest
from applypilot.services.candidate_fact_service import CandidateFactService
from tests.auth_helpers import ORIGIN, client, initialize, reset_auth_database


@pytest.fixture(autouse=True)
def clean_database() -> None:
    reset_auth_database()


def csrf_headers(test_client: object) -> dict[str, str]:
    token = test_client.cookies.get("applypilot_csrf")  # type: ignore[attr-defined]
    assert token
    return {**ORIGIN, "X-ApplyPilot-CSRF": token}


def fact_payload(value: str = "Python", scope: str = "*") -> dict[str, object]:
    return {
        "fact_type": "skill",
        "semantic_key": "skill.python",
        "scope": scope,
        "value": value,
        "source_type": "owner_entry",
        "sensitivity": "standard",
        "reconfirmation_policy": "days_90",
    }


def test_authentication_and_csrf_are_required() -> None:
    with client() as anonymous:
        assert anonymous.get("/api/candidate-facts").status_code == 401
    with client() as owner:
        initialize(owner)
        assert owner.post("/api/candidate-facts", json=fact_payload()).status_code == 403
        assert owner.put("/api/profile", json={}).status_code == 403


def test_profile_read_is_side_effect_free_and_update_is_structured() -> None:
    with client() as owner:
        initialize(owner)
        empty = owner.get("/api/profile")
        assert empty.status_code == 200
        assert empty.json()["created_at"] is None
        updated = owner.put(
            "/api/profile",
            headers=csrf_headers(owner),
            json={"identity": {"preferred_name": "Sample Candidate"}},
        )
        assert updated.status_code == 200
        assert updated.json()["sections"]["identity"]["preferred_name"] == "Sample Candidate"


def test_new_fact_is_unverified_and_explicit_confirmation_verifies() -> None:
    with client() as owner:
        initialize(owner)
        created = owner.post(
            "/api/candidate-facts", headers=csrf_headers(owner), json=fact_payload()
        )
        assert created.status_code == 201
        version = created.json()["current_version"]
        assert version["lifecycle_state"] == "unverified"
        verified = owner.post(
            f"/api/candidate-facts/versions/{version['id']}/verify",
            headers=csrf_headers(owner),
        )
        assert verified.status_code == 200
        assert verified.json()["lifecycle_state"] == "verified"
        assert verified.json()["confirmation_due_at"] is not None
        with SessionFactory() as database:
            assert database.scalar(select(CandidateFactConfirmation)) is not None


def test_edit_creates_immutable_unverified_history() -> None:
    with client() as owner:
        initialize(owner)
        created = owner.post(
            "/api/candidate-facts", headers=csrf_headers(owner), json=fact_payload()
        ).json()
        identity_id = created["identity_id"]
        original_id = created["current_version"]["id"]
        owner.post(
            f"/api/candidate-facts/versions/{original_id}/verify", headers=csrf_headers(owner)
        )
        edited_payload = {**fact_payload("Python and SQL"), "reason": "Added a distinct skill"}
        edited = owner.post(
            f"/api/candidate-facts/{identity_id}/versions",
            headers=csrf_headers(owner),
            json=edited_payload,
        )
        assert edited.status_code == 200
        detail = owner.get(f"/api/candidate-facts/{identity_id}").json()
        assert [item["version_number"] for item in detail["versions"]] == [2, 1]
        assert detail["versions"][0]["lifecycle_state"] == "unverified"
        assert detail["versions"][1]["value"] == "Python"
        with SessionFactory.begin() as database:
            with pytest.raises(DatabaseError):
                database.execute(
                    text(
                        "UPDATE candidate_fact_versions "
                        "SET typed_value = '\"changed\"' WHERE id = :id"
                    ),
                    {"id": original_id},
                )


def test_revocation_is_reasoned_and_cannot_be_verified() -> None:
    with client() as owner:
        initialize(owner)
        version = owner.post(
            "/api/candidate-facts", headers=csrf_headers(owner), json=fact_payload()
        ).json()["current_version"]
        revoked = owner.post(
            f"/api/candidate-facts/versions/{version['id']}/revoke",
            headers=csrf_headers(owner),
            json={"reason": "No longer accurate"},
        )
        assert revoked.json()["lifecycle_state"] == "revoked"
        assert (
            owner.post(
                f"/api/candidate-facts/versions/{version['id']}/verify",
                headers=csrf_headers(owner),
            ).status_code
            == 409
        )


def test_reconfirmation_policies_and_per_application_boundary() -> None:
    with client() as owner:
        initialize(owner)
        for policy, days in (("days_90", 90), ("days_30", 30)):
            payload = {
                **fact_payload(policy),
                "semantic_key": f"preference.{policy}",
                "reconfirmation_policy": policy,
            }
            version = owner.post(
                "/api/candidate-facts", headers=csrf_headers(owner), json=payload
            ).json()["current_version"]
            verified = owner.post(
                f"/api/candidate-facts/versions/{version['id']}/verify",
                headers=csrf_headers(owner),
            ).json()
            due = datetime.fromisoformat(verified["confirmation_due_at"])
            confirmed = datetime.fromisoformat(verified["owner_confirmed_at"])
            assert due - confirmed == timedelta(days=days)
        payload = {
            **fact_payload("declaration"),
            "semantic_key": "legal.declaration",
            "reconfirmation_policy": "per_application",
        }
        version = owner.post(
            "/api/candidate-facts", headers=csrf_headers(owner), json=payload
        ).json()["current_version"]
        assert (
            owner.post(
                f"/api/candidate-facts/versions/{version['id']}/verify",
                headers=csrf_headers(owner),
            ).status_code
            == 409
        )


def test_overlapping_incompatible_facts_conflict_and_owner_resolves() -> None:
    with client() as owner:
        initialize(owner)
        first = owner.post(
            "/api/candidate-facts",
            headers=csrf_headers(owner),
            json=fact_payload("Python", "work"),
        ).json()
        second = owner.post(
            "/api/candidate-facts",
            headers=csrf_headers(owner),
            json=fact_payload("Not Python", "*"),
        ).json()
        assert second["current_version"]["lifecycle_state"] == "conflicted"
        conflicts = owner.get("/api/candidate-fact-conflicts").json()["conflicts"]
        assert len(conflicts) == 1
        conflict_id = conflicts[0]["id"]
        detail = owner.get(f"/api/candidate-fact-conflicts/{conflict_id}").json()
        assert len(detail["members"]) == 2
        resolved = owner.post(
            f"/api/candidate-fact-conflicts/{conflict_id}/resolve",
            headers=csrf_headers(owner),
            json={
                "selected_version_id": first["current_version"]["id"],
                "reason": "Owner confirmed the scoped value",
            },
        )
        assert resolved.status_code == 204
        assert owner.get("/api/candidate-fact-conflicts").json()["conflicts"] == []


def test_non_overlapping_values_do_not_conflict_and_audits_are_redacted() -> None:
    with client() as owner:
        initialize(owner)
        owner.post(
            "/api/candidate-facts",
            headers=csrf_headers(owner),
            json=fact_payload("private-one", "employment-a"),
        )
        owner.post(
            "/api/candidate-facts",
            headers=csrf_headers(owner),
            json=fact_payload("private-two", "employment-b"),
        )
        assert owner.get("/api/candidate-fact-conflicts").json()["conflicts"] == []
        with SessionFactory() as database:
            events = list(database.scalars(select(SecurityEvent)))
            serialized = " ".join(str(event.metadata_json) for event in events)
            assert "private-one" not in serialized
            assert "private-two" not in serialized


def test_protected_trait_collection_is_rejected() -> None:
    with client() as owner:
        initialize(owner)
        payload = {**fact_payload("unknown"), "fact_type": "caste", "semantic_key": "caste"}
        assert (
            owner.post(
                "/api/candidate-facts", headers=csrf_headers(owner), json=payload
            ).status_code
            == 422
        )


def test_twenty_concurrent_version_attempts_keep_unique_ordered_versions() -> None:
    with client() as owner:
        initialize(owner)
        identity_id = owner.post(
            "/api/candidate-facts", headers=csrf_headers(owner), json=fact_payload()
        ).json()["identity_id"]

    def create_version(index: int) -> None:
        with SessionFactory() as database:
            CandidateFactService(database).edit(
                identity_id,
                FactEditRequest(
                    **fact_payload(f"Synthetic skill value {index}"),
                    reason=f"Concurrent synthetic edit {index}",
                ),
            )

    with ThreadPoolExecutor(max_workers=20) as executor:
        list(executor.map(create_version, range(20)))
    with SessionFactory() as database:
        versions = list(
            database.scalars(
                select(CandidateFactVersion)
                .where(CandidateFactVersion.fact_identity_id == identity_id)
                .order_by(CandidateFactVersion.version_number)
            )
        )
        assert [version.version_number for version in versions] == list(range(1, 22))
