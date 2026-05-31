"""Identity namespace: faceswap, lock, replace, voice_clone, profiles, instamodel, tryon."""

from __future__ import annotations

from typing import List, Optional

from .._transport import _Transport
from ..models import Job


class IdentityResource:
    def __init__(self, transport: _Transport):
        self._t = transport

    def faceswap(
        self,
        *,
        source: str,
        target: str,
        upscale: float = 1.5,
        restore_weight: float = 0.5,
        profile_id: Optional[str] = None,
        callback_url: Optional[str] = None,
        wait: bool = True,
    ) -> Job:
        """Swap the face from source onto the target image.

        Args:
            source: Public URL of the face to swap in.
            target: Public URL of the image to swap onto.
            upscale: Output upscale factor (1.0–4.0).
            restore_weight: Face restoration strength (0.0–1.0).
            profile_id: Optional identity profile ID.
            callback_url: Webhook URL. We POST a ``WebhookEvent`` on completion.
            wait: Poll until complete if True.
        """
        body: dict = {
            "source": source,
            "target": target,
            "upscale": upscale,
            "restore_weight": restore_weight,
        }
        if profile_id:
            body["profile_id"] = profile_id
        if callback_url:
            body["callback_url"] = callback_url
        endpoint = "identity/faceswap/image/v1"
        return self._t.submit_and_poll(endpoint, body) if wait else self._t.submit(endpoint, body)

    def lock(
        self,
        *,
        input_image: str,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        seed: int = -1,
        profile_id: Optional[str] = None,
        callback_url: Optional[str] = None,
        wait: bool = True,
    ) -> Job:
        """Preserve a person's identity while generating a new scene.

        Args:
            input_image: Reference photo URL (face to preserve).
            prompt: Description of the new scene.
            width: Output width in pixels (max 2048).
            height: Output height in pixels (max 2048).
            seed: Reproducibility seed (-1 for random).
            profile_id: Optional identity profile ID.
            callback_url: Webhook URL. We POST a ``WebhookEvent`` on completion.
            wait: Poll until complete if True.
        """
        body: dict = {
            "input_image": input_image,
            "prompt": prompt,
            "width": width,
            "height": height,
            "seed": seed,
        }
        if profile_id:
            body["profile_id"] = profile_id
        if callback_url:
            body["callback_url"] = callback_url
        endpoint = "identity/lock/image/v1"
        return self._t.submit_and_poll(endpoint, body) if wait else self._t.submit(endpoint, body)

    def replace(
        self,
        *,
        input_image: str,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        seed: int = -1,
        profile_id: Optional[str] = None,
        callback_url: Optional[str] = None,
        wait: bool = True,
    ) -> Job:
        """Replace the person/model in an image while preserving the background.

        Args:
            input_image: Public URL of the source image.
            prompt: Description of the replacement identity / model.
            width: Output width in pixels (max 2048).
            height: Output height in pixels (max 2048).
            seed: Reproducibility seed (-1 for random).
            profile_id: Optional identity profile ID.
            callback_url: Webhook URL. We POST a ``WebhookEvent`` on completion.
            wait: Poll until complete if True.
        """
        body: dict = {
            "input_image": input_image,
            "prompt": prompt,
            "width": width,
            "height": height,
            "seed": seed,
        }
        if profile_id:
            body["profile_id"] = profile_id
        if callback_url:
            body["callback_url"] = callback_url
        endpoint = "identity/replace/image/v1"
        return self._t.submit_and_poll(endpoint, body) if wait else self._t.submit(endpoint, body)

    def voice_clone(
        self,
        *,
        text: str,
        reference_voice_url: str,
        language_id: str = "en",
        max_new_tokens: int = 256,
        exaggeration: float = 0.5,
        apply_watermark: bool = True,
        callback_url: Optional[str] = None,
        wait: bool = True,
    ) -> Job:
        """Clone a voice and synthesise speech.

        Args:
            text: Text to speak.
            reference_voice_url: Public URL of the reference voice sample (WAV/MP3).
            language_id: Language code e.g. ``'en'``, ``'es'``.
            max_new_tokens: Max tokens to generate (max 1024).
            exaggeration: Voice expressiveness (0.0–1.0).
            apply_watermark: Apply audio watermark.
            callback_url: Webhook URL. We POST a ``WebhookEvent`` on completion.
            wait: Poll until complete if True.
        """
        body: dict = {
            "text": text,
            "reference_voice_url": reference_voice_url,
            "language_id": language_id,
            "max_new_tokens": max_new_tokens,
            "exaggeration": exaggeration,
            "apply_watermark": apply_watermark,
        }
        if callback_url:
            body["callback_url"] = callback_url
        endpoint = "identity/voice/clone/v1"
        return self._t.submit_and_poll(endpoint, body) if wait else self._t.submit(endpoint, body)

    def instamodel(
        self,
        *,
        face_image: str,
        prompt: str,
        width: int = 768,
        height: int = 1024,
        seed: Optional[int] = None,
        profile_id: Optional[str] = None,
        callback_url: Optional[str] = None,
        wait: bool = True,
    ) -> Job:
        """Generate a consistent AI influencer / model image.

        Args:
            face_image: Public URL of the reference face image.
            prompt: Description of the desired scene / outfit.
            width: Output width in pixels (default 768).
            height: Output height in pixels (default 1024).
            seed: Reproducibility seed (None for random).
            profile_id: Optional identity profile ID.
            callback_url: Webhook URL. We POST a ``WebhookEvent`` on completion.
            wait: Poll until complete if True.
        """
        body: dict = {
            "input_face": face_image,
            "prompt": prompt,
            "width": width,
            "height": height,
        }
        if seed is not None:
            body["seed"] = seed
        if profile_id:
            body["profile_id"] = profile_id
        if callback_url:
            body["callback_url"] = callback_url
        endpoint = "creator/instamodel/image/v1"
        return self._t.submit_and_poll(endpoint, body) if wait else self._t.submit(endpoint, body)

    def tryon(
        self,
        *,
        person_image: str,
        clothing_image: str,
        gender: str = "woman",
        width: int = 832,
        height: int = 1248,
        seed: int = -1,
        output_format: str = "webp",
        profile_id: Optional[str] = None,
        callback_url: Optional[str] = None,
        wait: bool = True,
    ) -> Job:
        """Virtual try-on — dress a person in a clothing item.

        The person's face, pose, and body are preserved; only the clothing is
        replaced with the item from ``clothing_image``.

        Args:
            person_image: Public URL of the person / model photo.
            clothing_image: Public URL of the clothing item to try on.
            gender: ``'woman'`` (default) or ``'man'``.
            width: Output width in pixels (recommended 832).
            height: Output height in pixels (recommended 1248).
            seed: Reproducibility seed (-1 for random).
            output_format: ``'webp'`` (default), ``'jpeg'``, or ``'png'``.
            profile_id: Optional identity profile ID.
            callback_url: Webhook URL. We POST a ``WebhookEvent`` on completion.
            wait: Poll until complete if True.
        """
        body: dict = {
            "person_image": person_image,
            "clothing_image": clothing_image,
            "gender": gender,
            "width": width,
            "height": height,
            "seed": seed,
            "output_format": output_format,
        }
        if profile_id:
            body["profile_id"] = profile_id
        if callback_url:
            body["callback_url"] = callback_url
        endpoint = "creator/tryon/image/v1"
        return self._t.submit_and_poll(endpoint, body) if wait else self._t.submit(endpoint, body)

    # ── Profiles ──────────────────────────────────────────────────────────────

    def create_profile(
        self,
        *,
        name: str,
        tags: Optional[List[str]] = None,
        description: Optional[str] = None,
        prompt_template: Optional[str] = None,
        prompt_template_mode: str = "suffix",
        negative_prompt: Optional[str] = None,
        cfg_scale: Optional[float] = None,
        steps: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        output_format: Optional[str] = None,
        seed_strategy: str = "random",
        fixed_seed: Optional[int] = None,
    ) -> dict:
        """Create an identity profile.

        Args:
            name: Profile display name.
            tags: Optional list of tags for organisation.
            description: Optional description.
            prompt_template: Jinja2 template. Use ``{{ user_prompt }}`` as the placeholder
                             for the caller's prompt. Example:
                             ``'{{ user_prompt }}, Caucasian woman, late 20s, blue eyes'``.
            prompt_template_mode: ``'suffix'`` (default) — template appended after caller's
                                  prompt. ``'prefix'`` — template prepended before.
            negative_prompt: Default negative prompt applied to all jobs using this profile.
            cfg_scale: Default guidance scale override.
            steps: Default number of inference steps.
            width: Default output width in pixels.
            height: Default output height in pixels.
            output_format: Default output format (``'webp'``, ``'jpeg'``, ``'png'``).
            seed_strategy: ``'random'`` (default), ``'fixed'``, or ``'user'``.
            fixed_seed: Seed value used when ``seed_strategy='fixed'``.

        Returns:
            Raw profile dict containing ``profile_id``, ``name``, ``adapter_snapshot``, etc.
        """
        body: dict = {"name": name, "seed_strategy": seed_strategy, "prompt_template_mode": prompt_template_mode}
        if tags:
            body["tags"] = tags
        if description:
            body["description"] = description
        if prompt_template:
            body["prompt_template"] = prompt_template
        if negative_prompt:
            body["negative_prompt"] = negative_prompt
        if cfg_scale is not None:
            body["cfg_scale"] = cfg_scale
        if steps is not None:
            body["steps"] = steps
        if width is not None:
            body["width"] = width
        if height is not None:
            body["height"] = height
        if output_format:
            body["output_format"] = output_format
        if fixed_seed is not None:
            body["fixed_seed"] = fixed_seed
        return self._t.post("/profiles/v1", body)

    def get_profile(self, profile_id: str) -> dict:
        """Fetch a single identity profile by ID."""
        return self._t.get(f"/profiles/v1/{profile_id}")

    def list_profiles(self) -> dict:
        """List all identity profiles for the authenticated user."""
        return self._t.get("/profiles/v1")

    def delete_profile(self, profile_id: str) -> None:
        """Delete an identity profile."""
        url = f"/profiles/v1/{profile_id}"
        resp = self._t._session.delete(f"{self._t._base_url}{url}", timeout=self._t._timeout)
        if not resp.ok and resp.status_code != 204:
            self._t._handle(resp)
