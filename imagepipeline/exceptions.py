"""Exceptions raised by the ImagePipeline SDK."""

from __future__ import annotations


class ImagePipelineError(Exception):
    """Base exception for all SDK errors."""


class AuthenticationError(ImagePipelineError):
    """API key is missing or invalid (401)."""


class RateLimitError(ImagePipelineError):
    """Rate limit exceeded (429). Retry after the indicated delay."""

    def __init__(self, message: str, retry_after: int = 60):
        super().__init__(message)
        self.retry_after = retry_after


class JobFailedError(ImagePipelineError):
    """The submitted job completed with status 'failed'."""

    def __init__(self, job_id: str, reason: str | None = None):
        super().__init__(f"Job {job_id} failed: {reason or 'unknown error'}")
        self.job_id = job_id
        self.reason = reason


class JobTimeoutError(ImagePipelineError):
    """Polling timed out before the job completed."""

    def __init__(self, job_id: str, timeout: int):
        super().__init__(f"Job {job_id} did not complete within {timeout}s")
        self.job_id = job_id
        self.timeout = timeout


class APIError(ImagePipelineError):
    """Unexpected HTTP error from the API."""

    def __init__(self, status_code: int, message: str, error_code: str | None = None):
        super().__init__(f"HTTP {status_code}: {message}")
        self.status_code = status_code
        # Stable machine-readable code from the API body, e.g. "INVALID_PARAMETERS",
        # "INSUFFICIENT_BALANCE", "NOT_FOUND". None if the body had no error_code.
        self.error_code = error_code
