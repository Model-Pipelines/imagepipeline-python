# imagepipeline

**On-model imagery for fast brands.**

ImagePipeline is the image AI API for fashion and ecommerce. Turn flat-lays into on-model shots, run virtual try-on, and relight backgrounds — from one API. No studio, no photoshoot.

[imagepipeline.io](https://www.imagepipeline.io) · [Book a demo](https://cal.com/imagepipeline/30min) · [Docs](https://docs.imagepipeline.io)

---

## Installation

```bash
pip install imagepipeline
```

Requires Python 3.9+ and a free API key from [imagepipeline.io](https://www.imagepipeline.io).

---

## Quick start

```python
from imagepipeline import ImagePipeline

ip = ImagePipeline("ip_live_xxxxxxxxxxxx")

# Turn a flat-lay into an on-model shot
result = ip.generate.image(
    prompt="fashion model wearing the product, white studio background, editorial lighting"
)
print(result.url)
```

---

## Core use cases

### Virtual try-on

Dress a real person in any clothing item. Pass the model photo and the product image — ImagePipeline handles the compositing.

```python
result = ip.identity.tryon(
    person_image="https://cdn.example.com/model.jpg",
    clothing_image="https://cdn.example.com/shirt.jpg",
    gender="woman",
)
print(result.url)
```

### Background replacement

Swap a flat studio background for any scene. The subject is automatically isolated — no masking required.

```python
result = ip.background.change(
    input_image="https://cdn.example.com/product-shot.jpg",
    prompt="minimal white marble surface, soft natural light",
)
print(result.url)
```

### On-model image generation

Generate consistent AI models with your brand's look and feel using identity profiles.

```python
# Create a reusable brand model profile
profile = ip.identity.create_profile(
    name="Campaign Model",
    prompt_template="{{ user_prompt }}, Caucasian woman, late 20s, blue eyes, studio lighting",
    seed_strategy="fixed",
    fixed_seed=42,
)

# Generate on-model imagery with consistent identity
result = ip.generate.image(
    prompt="wearing a navy linen blazer, white background",
    profile_id=profile["profile_id"],
)
print(result.url)
```

### Image editing

Edit product images with natural-language instructions.

```python
result = ip.edit.image(
    input_image="https://cdn.example.com/product.jpg",
    prompt="remove the wrinkles from the fabric, keep everything else identical",
)
print(result.url)
```

### Upload & edit

Upload local assets and use them directly in any editing workflow.

```python
# Upload a flat-lay image
upload = ip.upload.image("flat-lay.jpg")

# Then use it as an edit input
result = ip.edit.image(
    input_image=[upload.url, "https://cdn.example.com/model.jpg"],
    prompt="put the model in the flat-lay clothing",
    mask_segment="upper-clothes",
)
print(result.url)
```

### Targeted editing with segmentation

Use segment detection to edit only the clothing — face, hair, and background stay pixel-perfect.

```python
# Optional: preview what segments exist in the image
seg = ip.segment.image("https://cdn.example.com/model.jpg")
for s in seg.segments:
    print(s.label, "→", s.display)
# upper-clothes → Top / Shirt
# pants         → Pants

# Edit only the detected segment
result = ip.edit.image(
    input_image=["https://cdn.example.com/model.jpg", "https://cdn.example.com/new-shirt.jpg"],
    prompt="dress the model in the shirt from image 2",
    mask_segment="upper-clothes",   # face, background, pants unchanged
)
print(result.url)
```

---

## Async & webhooks

All methods default to `wait=True` (blocks until the job completes). For high-throughput pipelines:

```python
# Fire-and-forget — returns immediately
job = ip.generate.image(prompt="...", wait=False)
print(job.job_id)

# Poll manually when ready
completed = ip._transport.poll("generate/image/v1", job.job_id)
print(completed.url)

# Or use a webhook — we POST a WebhookEvent to your URL on completion
job = ip.identity.tryon(
    person_image="https://...",
    clothing_image="https://...",
    callback_url="https://yourserver.com/hooks/imagepipeline",
    wait=False,
)
```

---

## Error handling

```python
from imagepipeline.exceptions import (
    AuthenticationError,
    RateLimitError,
    JobFailedError,
    JobTimeoutError,
    APIError,
)

try:
    result = ip.generate.image(prompt="...")
except AuthenticationError:
    print("Invalid API key — get one at imagepipeline.io")
except RateLimitError as e:
    print(f"Rate limited — retry after {e.retry_after}s")
except JobFailedError as e:
    print(f"Job {e.job_id} failed: {e.reason}")
except JobTimeoutError as e:
    print(f"Timed out after {e.timeout}s")
except APIError as e:
    print(f"HTTP {e.status_code}")
```

---

## API reference

| Resource | Method | Description |
|---|---|---|
| `ip.generate` | `.image(prompt, ...)` | Text-to-image generation |
| `ip.generate` | `.video(input_image, ...)` | Image-to-video |
| `ip.generate` | `.speech(text, ...)` | Text-to-speech |
| `ip.generate` | `.generate_3d(image_path, ...)` | Image-to-3D mesh |
| `ip.edit` | `.image(prompt, input_image, ...)` | Instruction-based image editing |
| `ip.background` | `.change(input_image, prompt, ...)` | Background replacement |
| `ip.upscale` | `.image(input_image, ...)` | AI image enhancement |
| `ip.branding` | `.logo(prompt, ...)` | Branded image generation |
| `ip.upload` | `.image(file)` | Upload an image, receive a URL |
| `ip.segment` | `.image(image_url)` | Detect segments for targeted editing |
| `ip.identity` | `.tryon(person_image, clothing_image, ...)` | Virtual try-on |
| `ip.identity` | `.faceswap(source, target, ...)` | Face swap |
| `ip.identity` | `.lock(input_image, prompt, ...)` | Identity-locked generation |
| `ip.identity` | `.replace(input_image, prompt, ...)` | Person/model replacement |
| `ip.identity` | `.instamodel(face_image, prompt, ...)` | Consistent AI model imagery |
| `ip.identity` | `.voice_clone(text, reference_voice_url, ...)` | Voice cloning |
| `ip.identity` | `.create_profile(name, ...)` | Create a reusable identity profile |
| `ip.identity` | `.list_profiles()` | List identity profiles |
| `ip.identity` | `.get_profile(profile_id)` | Fetch a profile |
| `ip.identity` | `.delete_profile(profile_id)` | Delete a profile |

---

## Requirements

- Python 3.9+
- `requests`

## License

MIT — see [LICENSE](LICENSE).

---

[imagepipeline.io](https://www.imagepipeline.io) · [Book a demo](https://cal.com/imagepipeline/30min) · [Docs](https://docs.imagepipeline.io)
