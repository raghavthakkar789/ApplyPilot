from datetime import datetime, timedelta

from applypilot.domain.candidate_fact import ReconfirmationPolicy


def confirmation_due_at(policy: str, confirmed_at: datetime | None) -> datetime | None:
    if confirmed_at is None:
        return None
    if policy == ReconfirmationPolicy.DAYS_90:
        return confirmed_at + timedelta(days=90)
    if policy == ReconfirmationPolicy.DAYS_30:
        return confirmed_at + timedelta(days=30)
    return None


def usable_without_application(policy: str, confirmed_at: datetime | None, now: datetime) -> bool:
    if policy in {
        ReconfirmationPolicy.PER_APPLICATION,
        ReconfirmationPolicy.PER_DESTINATION_ATTEMPT,
    }:
        return False
    due = confirmation_due_at(policy, confirmed_at)
    return due is None or now < due
