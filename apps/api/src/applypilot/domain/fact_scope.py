def scopes_overlap(left: str | None, right: str | None) -> bool:
    return left in {None, "*"} or right in {None, "*"} or left == right
