from enum import StrEnum


class FactState(StrEnum):
    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    STALE = "stale"
    CONFLICTED = "conflicted"
    REVOKED = "revoked"


class Sensitivity(StrEnum):
    STANDARD = "standard"
    PRIVATE = "private"
    ELIGIBILITY = "eligibility"
    HIGHLY_SENSITIVE = "highly_sensitive"


class ReconfirmationPolicy(StrEnum):
    STABLE = "stable"
    DAYS_90 = "days_90"
    DAYS_30 = "days_30"
    PER_APPLICATION = "per_application"
    PER_DESTINATION_ATTEMPT = "per_destination_attempt"


PROTECTED_FACT_TYPES = {
    "age",
    "caste",
    "citizenship",
    "disability",
    "ethnicity",
    "gender",
    "nationality",
    "religion",
    "veteran_status",
}
