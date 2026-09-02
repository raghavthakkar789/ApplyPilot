from typing import Any
from urllib.parse import quote

from applypilot.adapters.jobs.base import AdapterError, JobAdapter
from applypilot.domain.jobs.job import SourceJob
from applypilot.domain.jobs.normalization import safe_external_url, safe_text


class AshbyAdapter(JobAdapter):
    provider = "ashby"

    def url(self, identifier: str | None) -> str:
        if not identifier or not identifier.replace("-", "").isalnum():
            raise AdapterError("Invalid Ashby board identifier.")
        return f"https://api.ashbyhq.com/posting-api/job-board/{quote(identifier)}?includeCompensation=true"

    def parse(self, payload: Any, employer: str) -> list[SourceJob]:
        if not isinstance(payload, dict) or not isinstance(payload.get("jobs"), list):
            raise AdapterError("Malformed Ashby response.")
        result = []
        for j in payload["jobs"]:
            if not isinstance(j, dict) or j.get("isListed") is False or not j.get("jobUrl"):
                continue
            record_id = str(j.get("id") or j["jobUrl"].rstrip("/").rsplit("/", 1)[-1])
            result.append(
                SourceJob(
                    record_id,
                    str(j.get("title") or "Untitled role"),
                    employer,
                    safe_external_url(j["jobUrl"]) or "",
                    safe_external_url(j.get("applyUrl")),
                    safe_text(str(j.get("descriptionPlain") or j.get("descriptionHtml") or "")),
                    str(j.get("location") or "") or None,
                    str(j.get("workplaceType") or "") or None,
                    str(j.get("employmentType") or "") or None,
                    None,
                    None,
                    "Source: Ashby",
                    j,
                )
            )
        return result
