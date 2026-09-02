from datetime import datetime
from typing import Any

from applypilot.adapters.jobs.base import AdapterError, JobAdapter
from applypilot.domain.jobs.job import SourceJob
from applypilot.domain.jobs.normalization import safe_external_url, safe_text


class RemotiveAdapter(JobAdapter):
    provider = "remotive"

    def url(self, identifier: str | None) -> str:
        if identifier is not None:
            raise AdapterError("Remotive does not accept a board identifier.")
        return "https://remotive.com/api/remote-jobs"

    def parse(self, payload: Any, employer: str) -> list[SourceJob]:
        if not isinstance(payload, dict) or not isinstance(payload.get("jobs"), list):
            raise AdapterError("Malformed Remotive response.")
        result = []
        for j in payload["jobs"]:
            if not isinstance(j, dict) or not j.get("id") or not j.get("url"):
                continue
            published = None
            try:
                published = datetime.fromisoformat(
                    str(j.get("publication_date", "")).replace("Z", "+00:00")
                )
            except ValueError:
                pass
            result.append(
                SourceJob(
                    str(j["id"]),
                    str(j.get("title") or "Untitled role"),
                    str(j.get("company_name") or employer),
                    safe_external_url(j["url"]) or "",
                    safe_external_url(j["url"]),
                    safe_text(str(j.get("description") or "")),
                    str(j.get("candidate_required_location") or "") or None,
                    "remote",
                    str(j.get("job_type") or "") or None,
                    published,
                    None,
                    "Source: Remotive",
                    j,
                )
            )
        return result
