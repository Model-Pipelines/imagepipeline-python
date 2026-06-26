"""Generate namespace: image, video, speech, 3d."""

from __future__ import annotations

from typing import List, Optional

from .._transport import _Transport
from ..models import Job


class GenerateResource:
    def __init__(self, transport: _Transport):
        self._t = transport

    def image(
        self,
        *,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        seed: int = -1,
        output_format: str = "webp",
        num_inference_steps: Optional[int] = None,
        guidance_scale: Optional[float] = None,
        enhance_prompt: bool = False,
        logo_url: Optional[str] = None,
        profile_id: Optional[str] = None,
        callback_url: Optional[str] = None,
        wait: bool = True,
    ) -> Job:
        """Generate an image from a text prompt.

        Args:
            prompt: Text description of the image to generate.
            width: Output width in pixels (max 1024).
            height: Output height in pixels (max 1024).
            seed: Reproducibility seed (-1 for random).
            output_format: ``'webp'`` (default), ``'jpeg'``, or ``'png'``.
            num_inference_steps: Diffusion steps (default 8). Higher = slower but sharper.
            guidance_scale: CFG scale. Leave unset to use the model default (0.0).
            enhance_prompt: Run the prompt through a lightweight AI enhancer before generation.
                            Expands terse prompts into detailed visual descriptions. Adds ~1–2 s.
            logo_url: Public URL of your company logo (PNG/WebP). Stamped at bottom-right at 50% opacity.
            profile_id: Identity profile ID — applies the profile's prompt template and quality settings.
            callback_url: Webhook URL. We POST a ``WebhookEvent`` on completion.
            wait: If True (default), poll until complete and return a finished Job.
                  If False, return immediately with a QUEUED Job.
        """
        body: dict = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "seed": seed,
            "output_format": output_format,
            "enhance_prompt": enhance_prompt,
        }
        if num_inference_steps is not None:
            body["num_inference_steps"] = num_inference_steps
        if guidance_scale is not None:
            body["guidance_scale"] = guidance_scale
        if logo_url:
            body["logo_url"] = logo_url
        if profile_id:
            body["profile_id"] = profile_id
        if callback_url:
            body["callback_url"] = callback_url
        endpoint = "generate/image/v1"
        return self._t.submit_and_poll(endpoint, body) if wait else self._t.submit(endpoint, body)

    def video(
        self,
        *,
        input_image: str,
        prompt: str = "make this image come alive, cinematic motion, smooth animation",
        width: int = 896,
        height: int = 512,
        duration_seconds: float = 2.0,
        seed: int = 42,
        callback_url: Optional[str] = None,
        wait: bool = True,
    ) -> Job:
        """Generate a short video from an input image (image-to-video).

        Args:
            input_image: Public URL of the image to animate.
            prompt: Animation style description.
            width: Output width in pixels (max 1536, divisible by 32).
            height: Output height in pixels (max 1536, divisible by 32).
            duration_seconds: Video length in seconds (0.1–10.0).
            seed: Reproducibility seed.
            callback_url: Webhook URL. We POST a ``WebhookEvent`` on completion.
            wait: Poll until complete if True.
        """
        body: dict = {
            "input_image": input_image,
            "prompt": prompt,
            "width": width,
            "height": height,
            "duration_seconds": duration_seconds,
            "seed": seed,
        }
        if callback_url:
            body["callback_url"] = callback_url
        endpoint = "generate/video/v1"
        return self._t.submit_and_poll(endpoint, body) if wait else self._t.submit(endpoint, body)

    def speech(
        self,
        *,
        text: str,
        language_id: str = "en",
        target_voice_path: Optional[str] = None,
        max_new_tokens: int = 256,
        exaggeration: float = 0.5,
        apply_watermark: bool = True,
        callback_url: Optional[str] = None,
        wait: bool = True,
    ) -> Job:
        """Convert text to speech.

        Args:
            text: Text to synthesise (max 5000 chars).
            language_id: Language code e.g. ``'en'``, ``'es'``, ``'fr'``.
            target_voice_path: URL of a reference voice sample for voice cloning.
            max_new_tokens: Maximum tokens to generate (max 1024).
            exaggeration: Voice expressiveness (0.0–1.0).
            apply_watermark: Apply audio watermark.
            callback_url: Webhook URL. We POST a ``WebhookEvent`` on completion.
            wait: Poll until complete if True.
        """
        body: dict = {
            "text": text,
            "language_id": language_id,
            "max_new_tokens": max_new_tokens,
            "exaggeration": exaggeration,
            "apply_watermark": apply_watermark,
        }
        if target_voice_path:
            body["target_voice_path"] = target_voice_path
        if callback_url:
            body["callback_url"] = callback_url
        endpoint = "generate/speech/v1"
        return self._t.submit_and_poll(endpoint, body) if wait else self._t.submit(endpoint, body)

    def generate_3d(
        self,
        *,
        image_path: str,
        mode: str = "generate_and_paint",
        mesh_save_name: Optional[str] = None,
        painted_save_name: Optional[str] = None,
        auto_unload: bool = True,
        callback_url: Optional[str] = None,
        wait: bool = True,
    ) -> Job:
        """Convert an image to a 3D mesh (Pro plan required).

        Args:
            image_path: Public URL of the image to convert.
            mode: ``'generate'`` | ``'paint'`` | ``'generate_and_paint'``.
            mesh_save_name: Optional filename for the output mesh.
            painted_save_name: Optional filename for the textured mesh.
            auto_unload: Unload model from GPU after generation.
            callback_url: Webhook URL. We POST a ``WebhookEvent`` on completion.
            wait: Poll until complete if True.
        """
        body: dict = {
            "image_path": image_path,
            "mode": mode,
            "auto_unload": auto_unload,
        }
        if mesh_save_name:
            body["mesh_save_name"] = mesh_save_name
        if painted_save_name:
            body["painted_save_name"] = painted_save_name
        if callback_url:
            body["callback_url"] = callback_url
        endpoint = "generate/3d/v1"
        return self._t.submit_and_poll(endpoint, body) if wait else self._t.submit(endpoint, body)
