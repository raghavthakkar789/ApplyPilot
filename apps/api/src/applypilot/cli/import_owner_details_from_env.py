import argparse
import os

from applypilot.repositories.database import SessionFactory
from applypilot.services.owner_details_import_service import (
    OwnerDetailsImportError,
    OwnerDetailsImportService,
    mask_email,
    mask_name,
    normalize_email,
    normalize_name,
)

GENERIC_FAILURE = "Owner details import could not be completed."


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="applypilot-import-owner-details",
        description=(
            "One-time local-shell import of owner name and email into PostgreSQL. "
            "Does not read or import a password."
        ),
    )
    parser.add_argument("--name", help="Owner name. Overrides USER_NAME when provided.")
    parser.add_argument("--email", help="Owner email. Overrides USER_EMAIL when provided.")
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirm the masked import without an interactive prompt.",
    )
    return parser


def _read_optional_env(name: str) -> str | None:
    value = os.environ.get(name)
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _resolve_text(argument: str | None, env_name: str, prompt: str) -> str:
    if argument is not None and argument.strip():
        return argument
    env_value = _read_optional_env(env_name)
    if env_value is not None:
        return env_value
    try:
        typed = input(prompt).strip()
    except EOFError as error:
        raise OwnerDetailsImportError(GENERIC_FAILURE) from error
    if not typed:
        raise OwnerDetailsImportError(GENERIC_FAILURE)
    return typed


def _confirm(masked_name: str, masked_email: str, assumed: bool) -> bool:
    print("Import owner details into PostgreSQL as unverified facts?")
    print(f"  name:  {masked_name}")
    print(f"  email: {masked_email}")
    if assumed:
        return True
    try:
        answer = input("Type yes to continue: ").strip().casefold()
    except EOFError:
        return False
    return answer == "yes"


def main() -> int:
    arguments = build_parser().parse_args()
    try:
        name = _resolve_text(arguments.name, "USER_NAME", "Owner name: ")
        email = _resolve_text(arguments.email, "USER_EMAIL", "Owner email: ")
        normalized_name = normalize_name(name)
        normalized_email = normalize_email(email)
        if not _confirm(
            mask_name(normalized_name), mask_email(normalized_email), arguments.yes
        ):
            print("Import cancelled.")
            return 1
        with SessionFactory() as database:
            imported = OwnerDetailsImportService(database).import_details(
                normalized_name, normalized_email
            )
    except OwnerDetailsImportError as error:
        print(str(error) if str(error) else GENERIC_FAILURE)
        return 1
    except Exception:
        print(GENERIC_FAILURE)
        return 1
    print(
        "Imported unverified owner details. "
        f"Masked confirmation: name {imported['name']}, email {imported['email']}. "
        "Verify them in Evidence. Remove USER_NAME and USER_EMAIL from .env."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
