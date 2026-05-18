"""
Module 7, Lesson 2: Multimodal Context
========================================
Images and documents add a new dimension to context engineering.
This lesson shows:
  1. Sending an image via URL (no file needed)
  2. Multiple images in one request
  3. Estimating image token cost before sending
  4. Combining text + image context for analysis

Run:
    python code/module7/lesson2_multimodal.py
"""

import os
import sys
import base64
import struct
import zlib
from anthropic import Anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from config import MODEL_FAST

load_dotenv()
client  = Anthropic()
console = Console()

# ── Public test images (no download needed — passed as URL) ──────────────
SAMPLE_IMAGES = {
    "chart":   "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Banana-Chocolate-Chip-Cookies-Recipe.jpg/640px-Banana-Chocolate-Chip-Cookies-Recipe.jpg",
    "diagram": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Wikipedia-logo-v2-en.svg/640px-Wikipedia-logo-v2-en.svg.png",
}


# ── Token cost estimation ────────────────────────────────────────────────
def estimate_image_tokens(width: int, height: int) -> int:
    """
    Anthropic's vision pricing: images are resized to fit within 1568 × 1568,
    then tiled into 85-token blocks. Approximation: ~1600 tokens for a
    1024×1024 image; scales roughly with pixel count.
    Reference: https://docs.anthropic.com/en/docs/build-with-claude/vision
    """
    scale = min(1568 / width, 1568 / height, 1.0)
    w, h  = int(width * scale), int(height * scale)
    tiles = ((w + 511) // 512) * ((h + 511) // 512)
    return tiles * 1500 + 2048  # base overhead


def create_synthetic_image_b64(color: tuple[int, int, int] = (70, 130, 180)) -> str:
    """Creates a tiny 4×4 solid-colour PNG in base64 — used when URL images aren't available."""
    def png_chunk(name, data):
        crc = zlib.crc32(name + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + name + data + struct.pack(">I", crc)

    w, h = 4, 4
    raw  = b""
    for _ in range(h):
        raw += b"\x00" + bytes(color) * w

    compressed = zlib.compress(raw)
    png = (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
        + png_chunk(b"IDAT", compressed)
        + png_chunk(b"IEND", b"")
    )
    return base64.b64encode(png).decode()


def ask_about_image_url(url: str, question: str) -> str:
    """Sends an image URL + question to Claude."""
    response = client.messages.create(
        model=MODEL_FAST,
        max_tokens=256,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {"type": "url", "url": url},
                },
                {"type": "text", "text": question},
            ],
        }],
    )
    return response.content[0].text


def ask_about_image_b64(b64_data: str, media_type: str, question: str) -> str:
    """Sends a base64-encoded image + question to Claude."""
    response = client.messages.create(
        model=MODEL_FAST,
        max_tokens=256,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type":       "base64",
                        "media_type": media_type,
                        "data":       b64_data,
                    },
                },
                {"type": "text", "text": question},
            ],
        }],
    )
    return response.content[0].text


def multi_image_comparison(url1: str, url2: str, question: str) -> str:
    """Sends two images in one request for comparison."""
    response = client.messages.create(
        model=MODEL_FAST,
        max_tokens=384,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "url", "url": url1}},
                {"type": "image", "source": {"type": "url", "url": url2}},
                {"type": "text", "text": question},
            ],
        }],
    )
    return response.content[0].text


if __name__ == "__main__":
    console.print("\n[bold]Module 7, Lesson 2 — Multimodal Context[/bold]\n")

    # ── Token cost table ─────────────────────────────────────────────────
    console.print(Rule("Image token cost estimates"))
    table = Table(show_lines=True)
    table.add_column("Size",     width=15)
    table.add_column("Tokens",   justify="right")
    table.add_column("Cost (Haiku @ $0.80/MTok)", justify="right")
    for w, h in [(256, 256), (512, 512), (1024, 768), (1920, 1080)]:
        tok  = estimate_image_tokens(w, h)
        cost = tok / 1_000_000 * 0.80
        table.add_row(f"{w}×{h}", f"~{tok:,}", f"~${cost:.5f}")
    console.print(table)
    console.print("[dim]Context engineering tip: resize images before sending to control cost.[/dim]\n")

    # ── Demo 1: single image via URL ─────────────────────────────────────
    console.print(Rule("Demo 1: Single image via URL"))
    try:
        url   = SAMPLE_IMAGES["chart"]
        answer = ask_about_image_url(url, "Describe what you see in this image in 2 sentences.")
        console.print(Panel(answer, title="Image description"))
    except Exception as e:
        console.print(f"[yellow]URL image skipped ({e}) — using synthetic fallback[/yellow]")
        img_b64 = create_synthetic_image_b64((70, 130, 180))
        answer  = ask_about_image_b64(img_b64, "image/png", "What colour is this image?")
        console.print(Panel(answer, title="Synthetic image response"))

    # ── Demo 2: base64 encoded image ─────────────────────────────────────
    console.print(Rule("Demo 2: Base64 encoded image"))
    img_b64 = create_synthetic_image_b64((220, 50, 50))   # red
    answer  = ask_about_image_b64(
        img_b64, "image/png",
        "Describe the dominant colour of this image and what it might represent."
    )
    console.print(Panel(answer, title="Base64 image response"))

    # ── Demo 3: text + image context window assembly ──────────────────────
    console.print(Rule("Demo 3: Text + image context (all 11 CWA layers still apply)"))
    console.print(
        "[dim]The image is Layer 8 (dynamic context). "
        "Layers 1-3 (system prompt) apply as normal.[/dim]\n"
    )
    response = client.messages.create(
        model=MODEL_FAST,
        max_tokens=256,
        system="You are an expert visual analyst. Be precise and concise.",
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": img_b64}},
                {"type": "text",  "text": "What emotion does this colour typically evoke in western cultures?"},
            ],
        }],
    )
    console.print(Panel(response.content[0].text, title="Text + image response"))

    console.print("\n[bold green]✓ Lesson 2 complete![/bold green]")
    console.print("Next: [italic]python code/module7/lesson3_future.py[/italic]\n")
