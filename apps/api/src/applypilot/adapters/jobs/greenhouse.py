from typing import Any
from urllib.parse import quote

from applypilot.adapters.jobs.base import AdapterError, JobAdapter
from applypilot.domain.jobs.job import SourceJob
from applypilot.domain.jobs.normalization import safe_external_url, safe_text


class GreenhouseAdapter(JobAdapter):
    provider = "greenhouse"

    def url(self, identifier: str | None) -> str:
        if not identifier or not identifier.replace("-", "").isalnum():
            raise AdapterError("Invalid Greenhouse board identifier.")
        return f"https://boards-api.greenhouse.io/v1/boards/{quote(identifier)}/jobs?content=true"

    def parse(self, payload: Any, employer: str) -> list[SourceJob]:
        if not isinstance(payload, dict) or not isinstance(payload.get("jobs"), list):
            raise AdapterError("Malformed Greenhouse response.")
        return [
            SourceJob(
                str(j["id"]),
                str(j["title"]),
                employer,
                safe_external_url(j["absolute_url"]) or "",
                safe_external_url(j["absolute_url"]),
                safe_text(str(j.get("content", ""))),
                str((j.get("location") or {}).get("name") or "") or None,
                None,
                None,
                None,
                None,
                "Source: Greenhouse",
                j,
            )
            for j in payload["jobs"]
            if isinstance(j, dict) and j.get("id") and j.get("title") and j.get("absolute_url")
        ]
