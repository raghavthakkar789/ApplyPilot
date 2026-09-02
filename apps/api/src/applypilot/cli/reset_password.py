import argparse
import getpass

from applypilot.core.security import PasswordPolicyError
from applypilot.repositories.database import SessionFactory
from applypilot.services.password_recovery_service import PasswordRecoveryService


def build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        prog="applypilot-reset-password",
        description="Reset the local ApplyPilot owner password and revoke all sessions.",
    )


def main() -> int:
    build_parser().parse_args()
    password = getpass.getpass("New owner password: ")
    confirmation = getpass.getpass("Confirm new owner password: ")
    try:
        with SessionFactory() as database:
            PasswordRecoveryService(database).reset(password, confirmation)
    except (PasswordPolicyError, ValueError):
        print("Password recovery could not be completed.")
        return 1
    print("Owner password reset. All existing sessions were revoked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
