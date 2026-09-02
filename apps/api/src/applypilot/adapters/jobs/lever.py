from typing import Any
from urllib.parse import quote

from applypilot.adapters.jobs.base import AdapterError, JobAdapter
from applypilot.domain.jobs.job import SourceJob
from applypilot.domain.jobs.normalization import safe_external_url, safe_text


class LeverAdapter(JobAdapter):
    provider = "lever"

    def url(self, identifier: str | None) -> str:
        if not identifier or not identifier.replace("-", "").isalnum():
            raise AdapterError("Invalid Lever site identifier.")
        return f"https://api.lever.co/v0/postings/{quote(identifier)}?mode=json&limit=100&skip=0"

    def urls(self, identifier: str | None) -> list[str]:
        first = self.url(identifier)
        return [first.replace("skip=0", f"skip={offset}") for offset in range(0, 500, 100)]

    def parse(self, payload: Any, employer: str) -> list[SourceJob]:
        if not isinstance(payload, list):
            raise AdapterError("Malformed Lever response.")
        result = []
        for j in payload:
            if (
                not isinstance(j, dict)
                or not j.get("id")
                or not j.get("text")
                or not j.get("hostedUrl")
            ):
                continue
            raw_categories = j.get("categories")
            categories: dict[str, Any] = raw_categories if isinstance(raw_categories, dict) else {}
            result.append(
                SourceJob(
                    str(j["id"]),
                    str(j["text"]),
                    employer,
                    safe_external_url(j["hostedUrl"]) or "",
                    safe_external_url(j.get("applyUrl")),
                    safe_text(str(j.get("descriptionPlain") or j.get("description") or "")),
                    str(categories.get("location") or "") or None,
                    str(j.get("workplaceType") or "") or None,
                    str(categories.get("commitment") or "") or None,
                    None,
                    None,
                    "Source: Lever",
                    j,
                )
            )
        return result
