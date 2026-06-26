"""Edit, background, branding, upscale, upload, and segment resources."""

from __future__ import annotations

import io
import os
from typing import IO, List, Optional, Union

from .._transport import _Transport
from ..models import Job, SegmentItem, SegmentResult, UploadResult


class EditResource:
    def __init__(self, transport: _Transport):
        self._t = transport

    def image(
        self,
        *,
        prompt: str,
        input_image: Optional[Union[str, List[str]]] = None,
        mode: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        seed: int = -1,
        output_format: str = "webp",
        num_inference_steps: Optional[int] = None,
        guidance_scale: Optional[float] = None,
        refine_strength: Optional[float] = None,
        faster_inference: bool = True,
        cfg_norm_strength: Optional[float] = None,
        product_saturation: Optional[float] = None,
        mask_segment: Optional[str] = None,
        mask_feather_px: Optional[int] = None,
        palette: Optional[List[str]] = None,
        negative_prompt: Optional[str] = None,
        profile_id: Optional[str] = None,
        callback_url: Optional[str] = None,
        wait: bool = True,
    ) -> Job:
        """Edit an existing image with a natural-language instruction.

        Pass one image URL for single-image editing, or a list of two URLs for
        multi-image editing (e.g. person + clothing for try-on).

        Args:
            prompt: Editing instruction.
            input_image: Source image URL, or list of URLs for multi-image editing.
            mode: Processing mode — ``'anime'`` converts to anime style.
            width: Output width in pixels (max 2048). Defaults to source image width.
            height: Output height in pixels (max 2048). Defaults to source image height.
            seed: Reproducibility seed (-1 for random).
            output_format: ``'webp'`` (default), ``'jpeg'``, or ``'png'``.
            num_inference_steps: Diffusion steps (1–100).
            guidance_scale: Classifier-free guidance scale (0.0–20.0).
            refine_strength: Refinement pass strength (0.0–1.0).
                             Values of 0.15–0.30 improve skin and texture without changing composition.
            faster_inference: ``True`` (default) uses a distilled model for 8-step inference.
                              ``False`` runs full 20-step inference for higher quality.
            cfg_norm_strength: CFG normalisation strength (0.0–1.0). Reduces colour saturation
                               from high guidance. Try 0.7–0.9 if colours look oversaturated.
            product_saturation: Desaturate the product / reference image before editing (0.0–2.0).
                                Values below 1.0 reduce colour shift. Omit to use server default.
            mask_segment: Segment label to use as edit mask — only this region is taken from the
                          edited output; everything else is composited from the original.
                          Pass any label from the fixed vocabulary (see ``ip.segment.image()``),
                          or a region alias: ``'clothing'``, ``'person'``, ``'background'``.
            mask_feather_px: Gaussian blur radius in pixels for the mask edge (0–64). Default 8.
            palette: Brand colour palette as hex codes e.g. ``['#FF5733']``.
            negative_prompt: Things to avoid in the output.
            profile_id: Identity profile ID — applies the profile's prompt template and settings.
            callback_url: Webhook URL. We POST a ``WebhookEvent`` on completion.
            wait: Poll until complete if True.
        """
        body: dict = {
            "prompt": prompt,
            "seed": seed,
            "output_format": output_format,
            "faster_inference": faster_inference,
        }
        if input_image is not None:
            body["input_image"] = input_image
        if mode:
            body["mode"] = mode
        if width is not None:
            body["width"] = width
        if height is not None:
            body["height"] = height
        if num_inference_steps is not None:
            body["num_inference_steps"] = num_inference_steps
        if guidance_scale is not None:
            body["guidance_scale"] = guidance_scale
        if refine_strength is not None:
            body["refine_strength"] = refine_strength
        if cfg_norm_strength is not None:
            body["cfg_norm_strength"] = cfg_norm_strength
        if product_saturation is not None:
            body["product_saturation"] = product_saturation
        if mask_segment:
            body["mask_segment"] = mask_segment
        if mask_feather_px is not None:
            body["mask_feather_px"] = mask_feather_px
        if palette:
            body["palette"] = palette
        if negative_prompt:
            body["negative_prompt"] = negative_prompt
        if profile_id:
            body["profile_id"] = profile_id
        if callback_url:
            body["callback_url"] = callback_url
        endpoint = "edit/image/v1"
        return self._t.submit_and_poll(endpoint, body) if wait else self._t.submit(endpoint, body)


class BackgroundResource:
    def __init__(self, transport: _Transport):
        self._t = transport

    def change(
        self,
        *,
        input_image: str,
        prompt: str,
        subject_description: str,
        use_segmentation: bool = True,
        tone_correction: Optional[float] = None,
        has_text: Optional[bool] = None,
        palette: Optional[List[str]] = None,
        num_inference_steps: Optional[int] = None,
        true_cfg_scale: Optional[float] = None,
        faster_inference: Optional[bool] = None,
        harmonize_strength: Optional[float] = None,
        seed: int = -1,
        output_format: str = "webp",
        callback_url: Optional[str] = None,
        wait: bool = True,
    ) -> Job:
        """Replace the background of an image while preserving the subject.

        The subject (person, product, etc.) is automatically segmented and
        composited from the original image — no quality loss on the subject.

        Args:
            input_image: Public URL of the source image.
            prompt: Description of the new background or scene.
            subject_description: Short description of the main subject to preserve —
                                 e.g. ``'person'``, ``'glass bottle'``, ``'sneakers'``.
                                 Helps the segmentation model identify what to keep.
            use_segmentation: Isolate the subject and composite it back over the new
                              background (default True). Preserves subject edges cleanly.
            tone_correction: Colour correction strength (0.0–1.0). Blends the generated
                             background colour toward the original to reduce drift.
            has_text: Whether the image contains visible text/labels. Set ``False`` to
                      skip text detection and save ~2–3 s. Omit to auto-detect.
            palette: Brand colour palette as hex codes blended into the background.
            num_inference_steps: Diffusion steps (default 8).
            true_cfg_scale: CFG scale (default 4.0).
            faster_inference: Enable faster inference mode (default True).
            harmonize_strength: Lighting harmonization strength (0.0–1.0). Shifts the
                                subject's low-frequency lighting to match the generated
                                background. ``0.7`` is a good starting point. Omit to disable.
            seed: Reproducibility seed (-1 for random).
            output_format: ``'webp'`` (default), ``'jpeg'``, or ``'png'``.
            callback_url: Webhook URL. We POST a ``WebhookEvent`` on completion.
            wait: Poll until complete if True.
        """
        body: dict = {
            "input_image": input_image,
            "prompt": prompt,
            "subject_description": subject_description,
            "use_segmentation": use_segmentation,
            "seed": seed,
            "output_format": output_format,
        }
        if tone_correction is not None:
            body["tone_correction"] = tone_correction
        if has_text is not None:
            body["has_text"] = has_text
        if palette:
            body["palette"] = palette
        if num_inference_steps is not None:
            body["num_inference_steps"] = num_inference_steps
        if true_cfg_scale is not None:
            body["true_cfg_scale"] = true_cfg_scale
        if faster_inference is not None:
            body["faster_inference"] = faster_inference
        if harmonize_strength is not None:
            body["harmonize_strength"] = harmonize_strength
        if callback_url:
            body["callback_url"] = callback_url
        endpoint = "background/change/image/v1"
        return self._t.submit_and_poll(endpoint, body) if wait else self._t.submit(endpoint, body)

    def remove(
        self,
        *,
        input_image: str,
        recolor: Optional[str] = None,
        drop_shadow: bool = False,
        shadow_opacity: float = 0.38,
        shadow_blur: float = 0.018,
        shadow_dy: float = 0.022,
        shadow_dx: float = 0.004,
        output_format: str = "png",
        callback_url: Optional[str] = None,
        wait: bool = True,
    ) -> Job:
        """Remove the background from an image.

        Always returns a transparent PNG cutout (``job.cutout_url``). When
        ``recolor`` is provided, also returns a flat-background composite
        (``job.url`` / ``job.result_url``).

        Args:
            input_image: Public URL of the image to process.
            recolor: Hex colour for the new background, e.g. ``'#FFFFFF'`` or ``'F0F0F0'``.
                     When omitted only the transparent cutout is returned.
            drop_shadow: Add a soft drop shadow beneath the subject before compositing.
                         Requires ``recolor``.
            shadow_opacity: Shadow darkness (0.0–1.0, default 0.38).
            shadow_blur: Blur radius as a fraction of image width (default 0.018).
            shadow_dy: Vertical shadow offset as a fraction of image height (default 0.022).
            shadow_dx: Horizontal shadow offset as a fraction of image width (default 0.004).
            output_format: Output format for composited result — ``'png'`` (default), ``'webp'``, or ``'jpeg'``.
            callback_url: Webhook URL. We POST a ``WebhookEvent`` on completion.
            wait: Poll until complete if True.

        Returns:
            :class:`Job` with ``cutout_url`` set (transparent PNG) and ``result_url`` set
            when ``recolor`` was provided.
        """
        body: dict = {
            "input_image": input_image,
            "drop_shadow": drop_shadow,
            "output_format": output_format,
        }
        if recolor:
            body["recolor"] = recolor
        if drop_shadow:
            body["shadow_opacity"] = shadow_opacity
            body["shadow_blur"] = shadow_blur
            body["shadow_dy"] = shadow_dy
            body["shadow_dx"] = shadow_dx
        if callback_url:
            body["callback_url"] = callback_url
        endpoint = "background/remove/image/v1"
        return self._t.submit_and_poll(endpoint, body) if wait else self._t.submit(endpoint, body)


class BrandingResource:
    def __init__(self, transport: _Transport):
        self._t = transport

    def logo(
        self,
        *,
        input_image: str,
        logo_url: str,
        position: str = "bottom_right",
        output_format: str = "webp",
        callback_url: Optional[str] = None,
        wait: bool = True,
    ) -> Job:
        """Stamp your company logo onto an existing image.

        Downloads ``input_image``, overlays ``logo_url`` at the chosen corner
        at a small pixel size and 50% opacity. Pure image compositing — no GPU
        required, typically completes in 1–2 s.

        Args:
            input_image: Public URL of the base image to stamp the logo onto.
            logo_url: Public URL of your logo (PNG with transparency recommended).
            position: Corner placement — ``'bottom_right'`` (default), ``'bottom_left'``,
                      ``'top_right'``, or ``'top_left'``.
            output_format: ``'webp'`` (default), ``'jpeg'``, or ``'png'``.
            callback_url: Webhook URL. We POST a ``WebhookEvent`` on completion.
            wait: Poll until complete if True.
        """
        body: dict = {
            "input_image": input_image,
            "logo_url": logo_url,
            "position": position,
            "output_format": output_format,
        }
        if callback_url:
            body["callback_url"] = callback_url
        endpoint = "branding/logo/image/v1"
        return self._t.submit_and_poll(endpoint, body) if wait else self._t.submit(endpoint, body)

    def template(
        self,
        *,
        input_image: str,
        background_prompt: str = "clean professional studio background",
        palette_mode: str = "similar",
        subject_description: Optional[str] = None,
        logo_url: Optional[str] = None,
        position: str = "bottom_right",
        output_format: str = "webp",
        seed: int = -1,
        callback_url: Optional[str] = None,
        wait: bool = True,
    ) -> Job:
        """Brand Scene Composer — derive a palette from your photo and generate a matching background.

        Automatically extracts the dominant clothing/accessory colours from
        ``input_image``, transforms them by ``palette_mode``, and drives a
        background swap. Optionally stamps your logo at a chosen corner.

        Args:
            input_image: Public URL of your model or product photo. The brand palette
                         is extracted from the clothing and accessories automatically.
            background_prompt: Describe the background scene, e.g. ``'urban rooftop at dusk'``.
                               The derived palette colours are automatically injected.
            palette_mode: How the background palette relates to the outfit colours:
                          ``'similar'`` (same hue family, harmonious),
                          ``'complementary'`` (opposite on the colour wheel),
                          or ``'radical'`` (triadic shift, bold and eye-catching).
            subject_description: Short description of the subject to preserve, e.g. ``'woman in red dress'``.
            logo_url: Public URL of your logo (PNG with transparency). Stamped at ``position`` after generation.
            position: Corner for the logo stamp — ``'bottom_right'`` (default), ``'bottom_left'``,
                      ``'top_right'``, or ``'top_left'``.
            output_format: ``'webp'`` (default), ``'jpeg'``, or ``'png'``.
            seed: Reproducibility seed (-1 for random).
            callback_url: Webhook URL. We POST a ``WebhookEvent`` on completion.
            wait: Poll until complete if True.
        """
        body: dict = {
            "input_image": input_image,
            "background_prompt": background_prompt,
            "palette_mode": palette_mode,
            "position": position,
            "output_format": output_format,
            "seed": seed,
        }
        if subject_description:
            body["subject_description"] = subject_description
        if logo_url:
            body["logo_url"] = logo_url
        if callback_url:
            body["callback_url"] = callback_url
        endpoint = "branding/template/image/v1"
        return self._t.submit_and_poll(endpoint, body) if wait else self._t.submit(endpoint, body)


class UpscaleResource:
    def __init__(self, transport: _Transport):
        self._t = transport

    def image(
        self,
        *,
        input_image: str,
        scale: int = 4,
        output_format: str = "webp",
        callback_url: Optional[str] = None,
        wait: bool = True,
    ) -> Job:
        """Enhance and upscale an image to higher resolution.

        Args:
            input_image: Public URL of the image to upscale / enhance.
            scale: Upscale factor — ``1`` (enhance-only), ``2``, ``3``, or ``4`` (default).
            output_format: ``'webp'`` (default), ``'jpeg'``, or ``'png'``.
            callback_url: Webhook URL. We POST a ``WebhookEvent`` on completion.
            wait: Poll until complete if True.
        """
        body: dict = {
            "input_image": input_image,
            "scale": scale,
            "output_format": output_format,
        }
        if callback_url:
            body["callback_url"] = callback_url
        endpoint = "upscale/image/v1"
        return self._t.submit_and_poll(endpoint, body) if wait else self._t.submit(endpoint, body)


class UploadResource:
    def __init__(self, transport: _Transport):
        self._t = transport

    def image(self, file: Union[str, IO[bytes]], *, filename: Optional[str] = None) -> UploadResult:
        """Upload an image to storage and receive a permanent URL.

        The returned URL can be passed directly to any endpoint that accepts
        ``input_image``, ``person_image``, ``clothing_image``, etc.

        Args:
            file: Either a local file path (str) or a file-like object opened in binary mode.
            filename: Override the filename sent to the server. Inferred from ``file`` if omitted.

        Returns:
            :class:`UploadResult` with ``url``, ``filename``, ``content_type``, ``size_bytes``.

        Example::

            result = ip.upload.image("product.png")
            job = ip.edit.image(prompt="...", input_image=result.url)
        """
        if isinstance(file, str):
            path = file
            fname = filename or os.path.basename(path)
            with open(path, "rb") as fh:
                data = fh.read()
            file_obj: IO[bytes] = io.BytesIO(data)
        else:
            file_obj = file
            fname = filename or getattr(file, "name", "upload.bin")

        ext = os.path.splitext(fname)[1].lower()
        _MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp", ".gif": "image/gif"}
        content_type = _MIME.get(ext, "application/octet-stream")

        raw = self._t.post_file("/upload/image/v1", file_obj, fname, content_type)
        return UploadResult(
            url=raw["url"],
            filename=raw["filename"],
            content_type=raw["content_type"],
            size_bytes=raw["size_bytes"],
        )


class SegmentResource:
    def __init__(self, transport: _Transport):
        self._t = transport

    def image(self, image_url: str) -> SegmentResult:
        """Detect clothing and body segments in an image.

        Returns a coloured preview overlay and the list of detected segment
        labels. Use the label values as ``mask_segment`` in
        :meth:`EditResource.image` to constrain an edit to that region.

        **Fixed label vocabulary** — always the same strings::

            upper-clothes  pants  skirt  dress  belt
            left-shoe  right-shoe  hat  bag  scarf
            hair  face  left-arm  right-arm  left-leg  right-leg  sunglasses

        Region aliases also accepted as ``mask_segment``:
        ``'clothing'`` · ``'person'`` · ``'background'``

        Args:
            image_url: Public URL of the image to segment.

        Returns:
            :class:`SegmentResult` with ``preview_url`` and ``segments`` list.

        Example::

            result = ip.segment.image("https://example.com/person.jpg")
            print(result.preview_url)          # coloured overlay
            for s in result.segments:
                print(s.label, s.display)      # e.g. "upper-clothes", "Top / Shirt"

            # Then use the chosen label in an edit:
            job = ip.edit.image(
                input_image=["https://.../person.jpg", "https://.../shirt.jpg"],
                prompt="dress the person in the shirt from image 2",
                mask_segment="upper-clothes",
            )
        """
        raw = self._t.post("/segment/image/v1", {"image_url": image_url})
        return SegmentResult(
            preview_url=raw["preview_url"],
            segments=[SegmentItem(label=s["label"], display=s["display"]) for s in raw["segments"]],
        )
