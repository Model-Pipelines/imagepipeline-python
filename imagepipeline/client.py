"""Top-level ImagePipeline client."""

from __future__ import annotations

from ._transport import _Transport
from .resources import (
    BackgroundResource,
    BrandingResource,
    EditResource,
    GenerateResource,
    IdentityResource,
    SegmentResource,
    UploadResource,
    UpscaleResource,
)

_DEFAULT_BASE_URL = "https://api.imagepipeline.io"


class ImagePipeline:
    """Client for the ImagePipeline API.

    Usage::

        from imagepipeline import ImagePipeline

        ip = ImagePipeline("ip_live_xxxxxxxxxxxx")

        # Generate an image
        result = ip.generate.image(prompt="sunset over tokyo", width=1024, height=1024)
        print(result.url)

        # Upload a local file, then edit it
        upload = ip.upload.image("product.png")
        job = ip.edit.image(
            input_image=[person_url, upload.url],
            prompt="dress the person in the product from image 2",
            mask_segment="upper-clothes",
        )

        # Virtual try-on
        result = ip.identity.tryon(
            person_image="https://.../person.jpg",
            clothing_image="https://.../shirt.jpg",
            gender="woman",
        )

        # Segment an image to find label names
        seg = ip.segment.image("https://.../person.jpg")
        print(seg.segments)   # [SegmentItem(label='upper-clothes', display='Top / Shirt'), ...]

        # Background change (subject is automatically preserved)
        result = ip.background.change(
            input_image="https://.../photo.jpg",
            prompt="tropical beach at sunset",
        )

        # Manage identity profiles
        profile = ip.identity.create_profile(
            name="Brand Model",
            prompt_template="{{ user_prompt }}, Caucasian woman, 20s, blue eyes",
            seed_strategy="fixed",
            fixed_seed=42,
        )
        print(profile["profile_id"])

    Args:
        api_key: Your API key (starts with ``ip_live_``).
        base_url: Override the API base URL (useful for staging environments).
        timeout: HTTP request timeout in seconds.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: int = 30,
    ):
        self._transport = _Transport(api_key=api_key, base_url=base_url, timeout=timeout)

        self.generate = GenerateResource(self._transport)
        self.identity = IdentityResource(self._transport)
        self.edit = EditResource(self._transport)
        self.background = BackgroundResource(self._transport)
        self.branding = BrandingResource(self._transport)
        self.upscale = UpscaleResource(self._transport)
        self.upload = UploadResource(self._transport)
        self.segment = SegmentResource(self._transport)

    def account(self) -> dict:
        """Fetch the current account: plan, remaining balance, and the operations this
        API key is allowed to use. Useful as a preflight check before expensive calls."""
        return self._transport.get("/v1/user/details")
