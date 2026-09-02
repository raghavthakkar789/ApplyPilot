import hmac

from applypilot.core.security import hash_token, token_is_well_formed

CSRF_HEADER = "X-ApplyPilot-CSRF"


def csrf_matches(raw_token: str, stored_hash: str) -> bool:
    return token_is_well_formed(raw_token) and hmac.compare_digest(
        hash_token(raw_token), stored_hash
    )
