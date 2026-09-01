import json
import urllib.request


def main() -> None:
    with urllib.request.urlopen("http://127.0.0.1:8000/api/health/live", timeout=2) as response:  # noqa: S310
        payload = json.load(response)
    if payload != {"status": "ok"}:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
