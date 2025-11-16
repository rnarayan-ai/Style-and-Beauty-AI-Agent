import os
import uuid
from typing import List, Optional
import torch
from fastapi import APIRouter, BackgroundTasks, Form
from diffusers import StableDiffusionXLPipeline

router = APIRouter()

# ---------------- GLOBAL PIPELINE CACHE ----------------
pipe = None  # global pipeline object reused for all requests


def _select_device_and_dtype():
    if torch.cuda.is_available():
        return "cuda", torch.float16
    return "cpu", torch.float32


def _load_sdxl_pipeline():
    """Load the SDXL model only once and reuse it."""
    global pipe
    if pipe is not None:
        return pipe  # already loaded

    model_id = "stabilityai/stable-diffusion-xl-base-1.0"
    device, dtype = _select_device_and_dtype()
    print(f"Loading SDXL model on {device} with dtype {dtype}...")

    pipe = StableDiffusionXLPipeline.from_pretrained(
        model_id,
        torch_dtype=dtype,
        local_files_only=False,  # allow auto-download if missing
        use_safetensors=True,
        revision="fp16" if dtype == torch.float16 else None,
    ).to(device)

    # Optional optimizations
    if device == "cuda":
        pipe.enable_attention_slicing()
        try:
            pipe.enable_xformers_memory_efficient_attention()
        except Exception as e:
            print("⚠️ xformers not available:", e)

    print("✅ SDXL pipeline loaded and ready.")
    return pipe


def generate_sdxl_images(
    prompt: str,
    out_dir: str,
    num_images: int = 2,
    negative_prompt: Optional[str] = "blurry, low-quality, watermark",
    seed: Optional[int] = None,
) -> List[str]:
    """Generate `num_images` SDXL images for the given prompt."""
    os.makedirs(out_dir, exist_ok=True)
    print(f"Generating {num_images} images for: {prompt}")

    pipe = _load_sdxl_pipeline()  # load once, reuse later
    device = pipe.device
    saved_paths: List[str] = []

    for i in range(max(1, num_images)):
        gen = torch.Generator(device=device).manual_seed(seed + i if seed else torch.seed())
        result = pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=28,
            guidance_scale=7.5,
            generator=gen,
        )
        image = result.images[0]
        fname = f"sdxl_{uuid.uuid4().hex[:8]}_{i+1}.png"
        path = os.path.join(out_dir, fname)
        image.save(path)
        saved_paths.append(path)
        print(f"Saved → {path}")

    return saved_paths


# ---------------- FASTAPI ENDPOINT ----------------
@router.post("/sd_generate")
async def sd_generate(prompt: str = Form(...)):
    """Generate SDXL image(s) for a given text prompt."""
    print("Received prompt:", prompt)
    out_dir = "uploads/sdxl"
    saved_paths = generate_sdxl_images(prompt, out_dir, num_images=2)
    return {"status": "done", "files": saved_paths}


# ---------------- CLI SUPPORT ----------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--out", default="outputs/sdxl")
    parser.add_argument("--n", type=int, default=2)
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    paths = generate_sdxl_images(args.prompt, args.out, num_images=args.n, seed=args.seed)
    print("✅ Images saved:", paths)
