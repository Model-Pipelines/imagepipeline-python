"""Unit tests for the ImagePipeline Python SDK.

Run with:  pytest tests/
"""
from __future__ import annotations

import pytest
import responses as resp_lib

from imagepipeline import ImagePipeline
from imagepipeline.exceptions import (
    AuthenticationError,
    JobFailedError,
    JobTimeoutError,
    RateLimitError,
)
from imagepipeline.models import JobStatus

BASE = "https://api.imagepipeline.io"


@pytest.fixture
def ip():
    return ImagePipeline("ip_live_testkey")


# ── helpers ──────────────────────────────────────────────────────────────────

def _queued(job_id: str = "job_001") -> dict:
    return {"job_id": job_id, "status": "queued"}


def _completed(job_id: str = "job_001") -> dict:
    return {"job_id": job_id, "status": "completed", "result_url": "https://cdn.example.com/out.png"}


def _failed(job_id: str = "job_001") -> dict:
    return {"job_id": job_id, "status": "failed", "error": "CUDA out of memory"}


# ── generate.image ────────────────────────────────────────────────────────────

@resp_lib.activate
def test_generate_image_wait(ip):
    resp_lib.add(resp_lib.POST, f"{BASE}/generate/image/v1", json=_queued())
    resp_lib.add(resp_lib.GET, f"{BASE}/generate/image/v1/status/job_001", json=_completed())

    result = ip.generate.image(prompt="sunset over tokyo")
    assert result.job_id == "job_001"
    assert result.status == JobStatus.COMPLETED
    assert result.url == "https://cdn.example.com/out.png"


@resp_lib.activate
def test_generate_image_no_wait(ip):
    resp_lib.add(resp_lib.POST, f"{BASE}/generate/image/v1", json=_queued())

    job = ip.generate.image(prompt="sunset over tokyo", wait=False)
    assert job.job_id == "job_001"
    assert job.status == JobStatus.QUEUED
    assert job.url is None


@resp_lib.activate
def test_generate_image_with_callback(ip):
    resp_lib.add(resp_lib.POST, f"{BASE}/generate/image/v1", json=_queued())

    job = ip.generate.image(
        prompt="sunset over tokyo",
        callback_url="https://example.com/hook",
        wait=False,
    )
    assert job.job_id == "job_001"
    # Verify callback_url was sent in the request body
    assert resp_lib.calls[0].request.body is not None
    import json
    body = json.loads(resp_lib.calls[0].request.body)
    assert body["callback_url"] == "https://example.com/hook"


# ── generate.video ────────────────────────────────────────────────────────────

@resp_lib.activate
def test_generate_video(ip):
    resp_lib.add(resp_lib.POST, f"{BASE}/generate/video/v1", json={"job_id": "v_001", "status": "queued"})
    resp_lib.add(resp_lib.GET, f"{BASE}/generate/video/v1/status/v_001",
                 json={"job_id": "v_001", "status": "completed", "result_url": "https://cdn.example.com/v.mp4"})

    result = ip.generate.video(input_image="https://example.com/frame.jpg")
    assert result.url == "https://cdn.example.com/v.mp4"


# ── identity.faceswap ─────────────────────────────────────────────────────────

@resp_lib.activate
def test_faceswap_sends_profile_id_top_level(ip):
    resp_lib.add(resp_lib.POST, f"{BASE}/identity/faceswap/image/v1", json=_queued("fs_001"))
    resp_lib.add(resp_lib.GET, f"{BASE}/identity/faceswap/image/v1/status/fs_001", json=_completed("fs_001"))

    ip.identity.faceswap(
        source="https://example.com/face.jpg",
        target="https://example.com/scene.jpg",
        profile_id="prof_abc",
    )
    import json
    body = json.loads(resp_lib.calls[0].request.body)
    # profile_id must be top-level, NOT inside payload
    assert body.get("profile_id") == "prof_abc"
    assert "profile_id" not in body.get("payload", {})


# ── identity.voice_clone ──────────────────────────────────────────────────────

@resp_lib.activate
def test_voice_clone(ip):
    resp_lib.add(resp_lib.POST, f"{BASE}/identity/voice/clone/v1",
                 json={"job_id": "vc_001", "status": "queued"})
    resp_lib.add(resp_lib.GET, f"{BASE}/identity/voice/clone/v1/status/vc_001",
                 json={"job_id": "vc_001", "status": "completed", "result_url": "https://cdn.example.com/audio.mp3"})

    result = ip.identity.voice_clone(
        text="Hello from ImagePipeline",
        reference_voice_url="https://example.com/voice.mp3",
    )
    assert result.url == "https://cdn.example.com/audio.mp3"


# ── error handling ────────────────────────────────────────────────────────────

@resp_lib.activate
def test_auth_error(ip):
    resp_lib.add(resp_lib.POST, f"{BASE}/generate/image/v1", status=401, json={"detail": "Unauthorized"})

    with pytest.raises(AuthenticationError):
        ip.generate.image(prompt="test")


@resp_lib.activate
def test_rate_limit_error(ip):
    resp_lib.add(
        resp_lib.POST, f"{BASE}/generate/image/v1", status=429,
        json={"detail": "Rate limit exceeded"},
        headers={"Retry-After": "30"},
    )
    with pytest.raises(RateLimitError) as exc_info:
        ip.generate.image(prompt="test")
    assert exc_info.value.retry_after == 30


@resp_lib.activate
def test_job_failed_error(ip):
    resp_lib.add(resp_lib.POST, f"{BASE}/generate/image/v1", json=_queued())
    resp_lib.add(resp_lib.GET, f"{BASE}/generate/image/v1/status/job_001", json=_failed())

    with pytest.raises(JobFailedError) as exc_info:
        ip.generate.image(prompt="test")
    assert exc_info.value.job_id == "job_001"
    assert "CUDA" in exc_info.value.reason


def test_job_timeout(ip, monkeypatch):
    """Timeout error is raised when polling exceeds the timeout."""
    import time

    call_count = 0

    def fake_get(path: str) -> dict:
        nonlocal call_count
        call_count += 1
        return {"job_id": "job_001", "status": "processing"}

    monkeypatch.setattr(ip._transport, "get", fake_get)

    # Mock time.monotonic to advance faster than poll_interval
    start = [0.0]
    def fake_monotonic():
        start[0] += 10
        return start[0]

    monkeypatch.setattr(time, "monotonic", fake_monotonic)
    monkeypatch.setattr(time, "sleep", lambda _: None)

    with pytest.raises(JobTimeoutError):
        ip._transport.poll("generate/image/v1", "job_001", poll_interval=1, timeout=5)


# ── profiles ─────────────────────────────────────────────────────────────────

@resp_lib.activate
def test_create_profile(ip):
    resp_lib.add(resp_lib.POST, f"{BASE}/profiles/v1",
                 json={"profile_id": "prof_001", "name": "Alex"})

    profile = ip.identity.create_profile(name="Alex", tags=["fashion"])
    assert profile["profile_id"] == "prof_001"


@resp_lib.activate
def test_list_profiles(ip):
    resp_lib.add(resp_lib.GET, f"{BASE}/profiles/v1",
                 json={"profiles": [], "total": 0})

    result = ip.identity.list_profiles()
    assert "profiles" in result


@resp_lib.activate
def test_delete_profile(ip):
    resp_lib.add(resp_lib.DELETE, f"{BASE}/profiles/v1/prof_001", status=204)

    ip.identity.delete_profile("prof_001")  # should not raise
