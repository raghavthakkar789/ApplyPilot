import asyncio
from abc import ABC, abstractmethod
from typing import Any

import httpx

from applypilot.domain.jobs.job import SourceJob


class AdapterError(RuntimeError):
    pass


def retry_after(value: str | None) -> float:
    try:
        return min(max(float(value or "0.25"), 0.0), 2.0)
    except ValueError:
        return 0.25


class JobAdapter(ABC):
    provider: str
    adapter_version = "1"
    maximum_response_bytes = 5 * 1024 * 1024
    maximum_records = 500

    @abstractmethod
    def url(self, identifier: str | None) -> str: ...

    @abstractmethod
    def parse(self, payload: Any, employer: str) -> list[SourceJob]: ...

    def urls(self, identifier: str | None) -> list[str]:
        return [self.url(identifier)]

    async def retrieve(self, identifier: str | None, employer: str) -> list[SourceJob]:
        timeout = httpx.Timeout(10, connect=3)
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=False) as client:
            jobs: list[SourceJob] = []
            for url in self.urls(identifier):
                for attempt in range(3):
                    response = await client.get(url, headers={"Accept": "application/json"})
                    if response.status_code == 429 or response.status_code >= 500:
                        if attempt == 2:
                            raise AdapterError("The source is temporarily unavailable.")
                        retry = retry_after(response.headers.get("Retry-After"))
                        await asyncio.sleep(retry + 0.05 * attempt)
                        continue
                    if 300 <= response.status_code < 400:
                        raise AdapterError("The source redirected outside its approved endpoint.")
                    response.raise_for_status()
                    if "application/json" not in response.headers.get("content-type", ""):
                        raise AdapterError("The source returned an unexpected content type.")
                    if len(response.content) > self.maximum_response_bytes:
                        raise AdapterError("The source response exceeded its safety limit.")
                    page = self.parse(response.json(), employer)
                    jobs.extend(page)
                    break
                if not page or len(jobs) >= self.maximum_records:
                    break
            return jobs[: self.maximum_records]
