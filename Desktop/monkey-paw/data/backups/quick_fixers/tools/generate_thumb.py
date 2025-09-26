#!/usr/bin/env python3
"""
Professional YouTube thumbnail generator for automated content creation.

High-quality thumbnail generation with typography, branding, and aspect
ratio optimization for YouTube automation workflows.
"""

import json
import os
import sys
from typing import Union

from PIL import Image, ImageDraw, ImageFont
from PIL.Image import Image as PILImage


def load_font(size: int) -> Union[ImageFont.FreeTypeFont, ImageFont.ImageFont]:
    """
    Load professional typography with fallback handling.

    Args:
        size: Font size in pixels

    Returns:
        ImageFont object with professional typography
    """
    try:
        return ImageFont.truetype("assets/fonts/Inter-Bold.ttf", size)
    except (OSError, IOError):
        return ImageFont.load_default()


def generate_professional_thumbnail(
    output_path: str,
    aspect_ratio: str,
    title_json_path: str,
    background_image_path: str,
    avatar_image_path: str,
    palette_json_path: str,
) -> None:
    """
    Generate professional YouTube thumbnail with branding.

    Professional implementation for high-quality thumbnail generation
    with typography, color palettes, and aspect ratio optimization.

    Args:
        output_path: Output file path for generated thumbnail
        aspect_ratio: Target aspect ratio ("16x9", "9x16", "1x1")
        title_json_path: Path to title configuration JSON
        background_image_path: Path to background image
        avatar_image_path: Path to avatar/logo image
        palette_json_path: Path to color palette JSON

    Raises:
        FileNotFoundError: If required assets are missing
        ImageProcessingError: If image generation fails
    """
    # Professional color palette loading with fallback
    default_palette = ["#0a1c4a", "#2aa7ff"]
    if os.path.exists(palette_json_path):
        with open(palette_json_path, "r", encoding="utf-8") as palette_file:
            color_palette = json.load(palette_file)
    else:
        color_palette = default_palette

    # Professional dimension calculation based on aspect ratio
    dimensions_map = {"16x9": (1280, 720), "9x16": (1080, 1920), "1x1": (1080, 1080)}
    width, height = dimensions_map.get(aspect_ratio, (1280, 720))

    # Professional image composition
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    # Professional background processing
    background: PILImage = Image.open(background_image_path).convert("RGBA")
    background = background.resize((width, height))
    canvas.alpha_composite(background, (0, 0))

    # Professional avatar/logo integration
    if os.path.exists(avatar_image_path):
        avatar: PILImage = Image.open(avatar_image_path).convert("RGBA")
        avatar_width = int(width * 0.45)
        avatar_height = int(height * 0.6)
        avatar = avatar.resize((avatar_width, avatar_height))
        avatar_x = width - avatar.width - 10
        avatar_y = height - avatar.height
        canvas.alpha_composite(avatar, (avatar_x, avatar_y))

    # Professional title data processing
    with open(title_json_path, "r", encoding="utf-8") as title_file:
        title_data = json.load(title_file)

    draw = ImageDraw.Draw(canvas)

    # Professional branding bar
    header_height = int(height * 0.25)
    draw.rectangle((0, 0, width, header_height), fill=color_palette[0])

    # Professional typography layout
    kicker_font = load_font(int(height * 0.06))
    title_font = load_font(int(height * 0.12))

    kicker_text = title_data.get("kicker", "").upper()
    title_text = title_data.get("title", "")

    draw.text((20, 20), kicker_text, font=kicker_font, fill="white")
    draw.text((20, int(height * 0.1)), title_text, font=title_font, fill="white")

    # Professional image export with optimization
    final_image = canvas.convert("RGB")
    final_image.save(output_path, "JPEG", quality=92, optimize=True)
    print(f"Generated professional thumbnail: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 7:
        print("Usage: generate_thumb.py <output> <aspect> <title_json> <bg_img> <avatar_img> <palette_json>")
        sys.exit(1)

    (output_file, aspect, title_json, bg_image, avatar_image, palette_json) = sys.argv[1:7]

    generate_professional_thumbnail(output_file, aspect, title_json, bg_image, avatar_image, palette_json)
