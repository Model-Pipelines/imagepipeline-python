"""Core data models for the ImagePipeline SDK."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class JobStatus(str, Enum):
    QUEUED = "queued"
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Job:
    """Represents a submitted or completed job."""

    job_id: str
    status: JobStatus
    endpoint: str
    result_url: Optional[str] = None
    error: Optional[str] = None

    # Progress
    progress: Optional[int] = None
    result_mime_type: Optional[str] = None

    # Timing
    queue_wait_seconds: Optional[float] = None
    inference_time_seconds: Optional[float] = None
    total_elapsed_seconds: Optional[float] = None
    estimated_time_seconds: Optional[int] = None
    processing_time_seconds: Optional[float] = None

    # Queue position (enterprise plans)
    queue_position: Optional[int] = None
    queue_metrics: Optional[Dict[str, Any]] = None
    queue_metrics_hint: Optional[str] = None

    # Failure info
    failure_reason_code: Optional[str] = None
    retryable: Optional[bool] = None
    warnings: Optional[List[str]] = None
    prompt_hash: Optional[str] = None

    # Billing
    cost_usd: Optional[float] = None
    balance_remaining_usd: Optional[float] = None

    # Background removal specific
    cutout_url: Optional[str] = None

    @property
    def url(self) -> Optional[str]:
        """Alias for result_url."""
        return self.result_url

    @classmethod
    def _from_status_response(cls, data: dict, endpoint: str) -> "Job":
        return cls(
            job_id=data.get("job_id", ""),
            status=JobStatus(data.get("status", "queued")),
            endpoint=endpoint,
            result_url=data.get("result_url"),
            error=data.get("error"),
            progress=data.get("progress"),
            result_mime_type=data.get("result_mime_type"),
            queue_wait_seconds=data.get("queue_wait_seconds"),
            inference_time_seconds=data.get("inference_time_seconds"),
            total_elapsed_seconds=data.get("total_elapsed_seconds"),
            estimated_time_seconds=data.get("estimated_time_seconds"),
            processing_time_seconds=data.get("processing_time_seconds"),
            queue_position=data.get("queue_position"),
            queue_metrics=data.get("queue_metrics"),
            queue_metrics_hint=data.get("queue_metrics_hint"),
            failure_reason_code=data.get("failure_reason_code"),
            retryable=data.get("retryable"),
            warnings=data.get("warnings"),
            prompt_hash=data.get("prompt_hash"),
            cost_usd=data.get("cost_usd"),
            balance_remaining_usd=data.get("balance_remaining_usd"),
            cutout_url=data.get("cutout_url"),
        )


@dataclass
class UploadResult:
    """Result of a file upload."""
    url: str
    filename: str
    content_type: str
    size_bytes: int


@dataclass
class SegmentItem:
    """A single detected segment from segmentation."""
    label: str
    display: str


@dataclass
class SegmentResult:
    """Result of image segmentation."""
    preview_url: str
    segments: List[SegmentItem]
