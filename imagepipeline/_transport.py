"""Low-level HTTP transport shared by all resource classes."""

from __future__ import annotations

import time
from typing import Any, Dict, IO, Optional

import requests as _requests

from .exceptions import (
    APIError,
    AuthenticationError,
    JobFailedError,
    JobTimeoutError,
    RateLimitError,
)
from .models import Job, JobStatus

_DEFAULT_BASE_URL = "https://api.imagepipeline.io"
_DEFAULT_POLL_INTERVAL = 3  # seconds
_DEFAULT_TIMEOUT = 300  # seconds
_SDK_VERSION = "0.3.0"


class _Transport:
    """Wraps requests.Session with auth headers and error handling."""

    def __init__(self, api_key: str, base_url: str, timeout: int):
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._session = _requests.Session()
        self._session.headers.update({
            "X-API-Key": api_key,
            "Content-Type": "application/json",
            "User-Agent": f"imagepipeline-python/{_SDK_VERSION}",
        })

    def post(self, path: str, body: dict) -> dict:
        url = f"{self._base_url}{path}"
        resp = self._session.post(url, json=body, timeout=self._timeout)
        return self._handle(resp)

    def get(self, path: str) -> dict:
        url = f"{self._base_url}{path}"
        resp = self._session.get(url, timeout=self._timeout)
        return self._handle(resp)

    def post_file(self, path: str, file_obj: IO[bytes], filename: str, content_type: str) -> dict:
        """POST multipart/form-data — used by the upload endpoint."""
        url = f"{self._base_url}{path}"
        # Remove Content-Type so requests sets multipart boundary automatically
        headers = {k: v for k, v in self._session.headers.items() if k.lower() != "content-type"}
        resp = self._session.post(
            url,
            files={"file": (filename, file_obj, content_type)},
            headers=headers,
            timeout=self._timeout,
        )
        return self._handle(resp)

    def _handle(self, resp: _requests.Response) -> dict:
        if resp.status_code == 401:
            raise AuthenticationError("Invalid or missing API key.")
        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", 60))
            raise RateLimitError("Rate limit exceeded.", retry_after=retry_after)
        if resp.status_code == 204:
            return {}
        if not resp.ok:
            try:
                detail = resp.json().get("detail") or resp.text
            except Exception:
                detail = resp.text
            raise APIError(resp.status_code, detail)
        return resp.json()

    def submit_and_poll(
        self,
        endpoint: str,
        body: dict,
        poll_interval: int = _DEFAULT_POLL_INTERVAL,
        timeout: int = _DEFAULT_TIMEOUT,
    ) -> Job:
        """POST to endpoint, then poll /status/{job_id} until done."""
        data = self.post(f"/{endpoint}", body)
        job_id = data["job_id"]
        return self.poll(endpoint, job_id, poll_interval=poll_interval, timeout=timeout)

    def submit(self, endpoint: str, body: dict) -> Job:
        """POST to endpoint and return immediately without polling."""
        data = self.post(f"/{endpoint}", body)
        return Job(
            job_id=data["job_id"],
            status=JobStatus(data.get("status", "queued")),
            endpoint=endpoint,
        )

    def poll(
        self,
        endpoint: str,
        job_id: str,
        poll_interval: int = _DEFAULT_POLL_INTERVAL,
        timeout: int = _DEFAULT_TIMEOUT,
    ) -> Job:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            data = self.get(f"/{endpoint}/status/{job_id}")
            status = JobStatus(data.get("status", "queued"))
            if status == JobStatus.COMPLETED:
                return Job._from_status_response(data, endpoint)
            if status == JobStatus.FAILED:
                raise JobFailedError(job_id, data.get("error"))
            time.sleep(poll_interval)
        raise JobTimeoutError(job_id, timeout)
