"""
StickFilm AI Studio Pro - Thumbnail Engine
High-CTR Viral YouTube Thumbnail Generator with High-Contrast Cinematic Scenes,
Volumetric Lighting, and Bold Stylized Badge Typography.
"""

import os
import sys
import math
import random
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance


class ThumbnailEngine:
    """
    Generates 4 high-CTR viral YouTube thumbnail options:
    1. "THE SECRET TRUTH"
    2. "WHO MADE IT FIRST?"
    3. "HOW WE SURVIVED"
    4. "CAN YOU SURVIVE?"
    """

    THUMBNAIL_PRESETS = [
        {
            "id": 1,
            "title": "THE SECRET TRUTH",
            "tag": "HIDDEN HISTORY",
            "theme": "secret",
            "badge_color": (245, 184, 46),      # Gold
            "tag_color": (239, 68, 68),         # Crimson Red
            "text_color": (255, 255, 255),
            "filename": "thumb_1",
        },
        {
            "id": 2,
            "title": "WHO MADE IT FIRST?",
            "tag": "1,000,000 BC",
            "theme": "mystery",
            "badge_color": (6, 182, 212),       # Cyan
            "tag_color": (245, 184, 46),        # Gold
            "text_color": (255, 255, 255),
            "filename": "thumb_2",
        },
        {
            "id": 3,
            "title": "HOW WE SURVIVED",
            "tag": "TRUE STORY",
            "theme": "survival",
            "badge_color": (249, 115, 22),      # Orange
            "tag_color": (16, 185, 129),        # Emerald Green
            "text_color": (255, 255, 255),
            "filename": "thumb_3",
        },
        {
            "id": 4,
            "title": "CAN YOU SURVIVE?",
            "tag": "EXTREME TEST",
            "theme": "danger",
            "badge_color": (239, 68, 68),       # Red
            "tag_color": (245, 184, 46),        # Gold
            "text_color": (255, 255, 255),
            "filename": "thumb_4",
        },
    ]

    def __init__(self, width: int = 1280, height: int = 720):
        self.width = width
        self.height = height
        self._font_cache = {}

    def _get_font(self, size: int, bold: bool = True) -> ImageFont.ImageFont:
        key = (size, bold)
        if key in self._font_cache:
            return self._font_cache[key]

        font_paths = [
            "C:/Windows/Fonts/impact.ttf",
            "C:/Windows/Fonts/ariblk.ttf",
            "C:/Windows/Fonts/segoeuib.ttf",
            "C:/Windows/Fonts/NirmalaB.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
        ]
        font = None
        for fp in font_paths:
            if os.path.exists(fp):
                try:
                    font = ImageFont.truetype(fp, size)
                    break
                except Exception:
                    continue

        if font is None:
            font = ImageFont.load_default()

        self._font_cache[key] = font
        return font

    # -------------------------------------------------------------------------
    # Visual Base Renderers for Thumbnails
    # -------------------------------------------------------------------------
    def _draw_cinematic_base(self, theme: str) -> Image.Image:
        """Creates high-contrast, atmospheric base scenes tailored for viral curiosity."""
        img = Image.new("RGBA", (self.width, self.height), (12, 10, 16, 255))
        draw = ImageDraw.Draw(img)

        if theme == "secret":
            # Dark cave with intense golden firelight radiating from center-right
            for y in range(self.height):
                t = y / self.height
                r = int(18 + 40 * t)
                g = int(10 + 15 * t)
                b = int(14 + 10 * t)
                draw.line([(0, y), (self.width, y)], fill=(r, g, b, 255))

            # Giant fire glow at right
            glow = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
            gdraw = ImageDraw.Draw(glow)
            cx, cy = int(self.width * 0.75), int(self.height * 0.65)
            for r in range(450, 0, -15):
                alpha = int(180 * (1.0 - (r / 450) ** 0.8))
                gdraw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill=(255, 120, 20, alpha))
            img.paste(glow, (0, 0), glow)

            # Caveman silhouette staring in shock
            char_x = int(self.width * 0.68)
            char_y = int(self.height * 0.75)
            draw.ellipse([(char_x - 70, char_y - 280), (char_x + 70, char_y - 140)], fill=(20, 15, 18))
            draw.polygon([(char_x - 110, char_y - 140), (char_x + 110, char_y - 140), (char_x + 80, char_y + 40), (char_x - 80, char_y + 40)], fill=(20, 15, 18))
            # Glowing flame reflections
            draw.arc([(char_x - 72, char_y - 282), (char_x + 72, char_y - 138)], start=300, end=70, fill=(255, 180, 40), width=6)

        elif theme == "mystery":
            # Cosmic dark night with giant glowing prehistoric torch
            for y in range(self.height):
                t = y / self.height
                draw.line([(0, y), (self.width, y)], fill=(int(8 + 15 * t), int(12 + 25 * t), int(28 + 35 * t), 255))

            # Starry night
            rng = random.Random(88)
            for _ in range(80):
                sx, sy = rng.randint(20, self.width - 20), rng.randint(20, int(self.height * 0.6))
                draw.ellipse([(sx - 2, sy - 2), (sx + 2, sy + 2)], fill=(255, 255, 255, 220))

            # Mammoth silhouette on cliff
            mam_x = int(self.width * 0.76)
            mam_y = int(self.height * 0.58)
            draw.ellipse([(mam_x - 120, mam_y - 80), (mam_x + 120, mam_y + 60)], fill=(10, 14, 22))
            draw.line([(mam_x - 100, mam_y), (mam_x - 160, mam_y + 80)], fill=(10, 14, 22), width=24)
            draw.arc([(mam_x - 170, mam_y - 40), (mam_x - 80, mam_y + 70)], start=60, end=240, fill=(240, 230, 200), width=8)

            # Primitive torch in foreground
            tx = int(self.width * 0.45)
            ty = int(self.height * 0.62)
            draw.line([(tx, ty + 180), (tx, ty)], fill=(80, 48, 24), width=20)
            # Huge blue-gold fire burst
            draw.ellipse([(tx - 65, ty - 90), (tx + 65, ty + 20)], fill=(255, 140, 20))
            draw.ellipse([(tx - 35, ty - 70), (tx + 35, ty)], fill=(255, 235, 100))

        elif theme == "survival":
            # Harsh cold blizzard with warm tribe sanctuary
            for y in range(self.height):
                t = y / self.height
                draw.line([(0, y), (self.width, y)], fill=(int(18 + 30 * t), int(28 + 35 * t), int(48 + 45 * t), 255))

            # Snowy mountain peaks
            draw.polygon([(0, self.height), (int(self.width * 0.3), int(self.height * 0.35)), (int(self.width * 0.6), self.height)], fill=(210, 225, 245))
            draw.polygon([(int(self.width * 0.4), self.height), (int(self.width * 0.75), int(self.height * 0.3)), (self.width, self.height)], fill=(185, 205, 235))

            # Heroic tribe group with torches on mountain ridge
            ridge_y = int(self.height * 0.68)
            draw.polygon([(0, ridge_y), (self.width, ridge_y - 40), (self.width, self.height), (0, self.height)], fill=(22, 28, 38))
            for i, offset in enumerate([-90, -30, 40, 100]):
                px = int(self.width * 0.68) + offset
                draw.ellipse([(px - 22, ridge_y - 120), (px + 22, ridge_y - 75)], fill=(12, 14, 20))
                draw.polygon([(px - 35, ridge_y - 75), (px + 35, ridge_y - 75), (px + 25, ridge_y), (px - 25, ridge_y)], fill=(12, 14, 20))
                # Torch fire
                draw.ellipse([(px + 18, ridge_y - 150), (px + 38, ridge_y - 110)], fill=(255, 120, 20))

        else:  # danger
            # Blood red / intense firestorm atmosphere
            for y in range(self.height):
                t = y / self.height
                draw.line([(0, y), (self.width, y)], fill=(int(35 + 45 * t), int(10 + 15 * t), int(10 + 10 * t), 255))

            # Extreme fire vortex
            cx, cy = int(self.width * 0.65), int(self.height * 0.5)
            for r in range(400, 0, -20):
                alpha = int(190 * (1.0 - (r / 400) ** 0.7))
                draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill=(255, int(70 + 120 * (r / 400)), 15, alpha))

            # Dramatic close-up silhouette of eyes / intense face
            draw.ellipse([(cx - 140, cy - 80), (cx - 30, cy + 10)], fill=(255, 255, 255))
            draw.ellipse([(cx + 30, cy - 80), (cx + 140, cy + 10)], fill=(255, 255, 255))
            draw.ellipse([(cx - 95, cy - 55), (cx - 55, cy - 15)], fill=(255, 80, 10))
            draw.ellipse([(cx + 55, cy - 55), (cx + 95, cy - 15)], fill=(255, 80, 10))

        return img

    # -------------------------------------------------------------------------
    # High-CTR Stylized Badge Overlay
    # -------------------------------------------------------------------------
    def _draw_viral_badge(
        self,
        img: Image.Image,
        title: str,
        tag: str,
        badge_color: Tuple[int, int, int],
        tag_color: Tuple[int, int, int],
    ) -> None:
        """
        Renders a high-impact, high-CTR YouTube thumbnail typography badge:
        Angled pill, heavy drop shadow, thick black outlines, and vibrant text colors.
        """
        draw = ImageDraw.Draw(img)
        font_title = self._get_font(76, bold=True)
        font_tag = self._get_font(28, bold=True)

        # 1. Category Tag Pill (Top)
        tag_text = tag.upper()
        tag_bbox = draw.textbbox((0, 0), tag_text, font=font_tag)
        tag_w = tag_bbox[2] - tag_bbox[0]
        tag_h = tag_bbox[3] - tag_bbox[1]

        px = 64
        py = 70
        tag_pad_x = 24
        tag_pad_y = 10
        draw.rounded_rectangle(
            [(px, py), (px + tag_w + tag_pad_x * 2, py + tag_h + tag_pad_y * 2)],
            radius=12,
            fill=tag_color,
            outline=(255, 255, 255),
            width=3,
        )
        draw.text((px + tag_pad_x, py + tag_pad_y - 2), tag_text, font=font_tag, fill=(15, 17, 21))

        # 2. Main Title Typography with Multiple Contrast Layers
        title_y = py + tag_h + tag_pad_y * 2 + 25
        title_lines = title.split()

        # Group into 2 punchy lines if long
        if len(title_lines) >= 3:
            mid = len(title_lines) // 2 + (len(title_lines) % 2)
            lines = [" ".join(title_lines[:mid]), " ".join(title_lines[mid:])]
        else:
            lines = [" ".join(title_lines)]

        cur_y = title_y
        for line in lines:
            # Measure line
            l_bbox = draw.textbbox((0, 0), line, font=font_title)
            lw = l_bbox[2] - l_bbox[0]
            lh = l_bbox[3] - l_bbox[1]

            # Background Dark Container Badge for extreme readability
            b_pad_x = 28
            b_pad_y = 14
            # Heavy black drop shadow for the container
            draw.rounded_rectangle(
                [(px + 6, cur_y + 8), (px + lw + b_pad_x * 2 + 6, cur_y + lh + b_pad_y * 2 + 8)],
                radius=14,
                fill=(0, 0, 0, 220),
            )
            # Main container
            draw.rounded_rectangle(
                [(px, cur_y), (px + lw + b_pad_x * 2, cur_y + lh + b_pad_y * 2)],
                radius=14,
                fill=(13, 15, 20, 245),
                outline=badge_color,
                width=4,
            )

            # Heavy Text Outlines
            tx = px + b_pad_x
            ty = cur_y + b_pad_y - 4
            outline_range = 5
            for ox in range(-outline_range, outline_range + 1):
                for oy in range(-outline_range, outline_range + 1):
                    if ox * ox + oy * oy <= outline_range * outline_range:
                        draw.text((tx + ox, ty + oy), line, font=font_title, fill=(0, 0, 0))

            # Text Fill
            draw.text((tx, ty), line, font=font_title, fill=badge_color)

            cur_y += lh + b_pad_y * 2 + 18

    # -------------------------------------------------------------------------
    # Public Generation API
    # -------------------------------------------------------------------------
    def generate_thumbnail(
        self,
        preset_id: int = 1,
        base_image: Optional[Image.Image] = None,
    ) -> Image.Image:
        """Generates a single viral thumbnail based on one of the 4 presets."""
        preset = next((p for p in self.THUMBNAIL_PRESETS if p["id"] == preset_id), self.THUMBNAIL_PRESETS[0])

        if base_image:
            # Resize and boost saturation / contrast for cinematic punch
            thumb = base_image.convert("RGBA").resize((self.width, self.height), Image.Resampling.LANCZOS)
            thumb = ImageEnhance.Contrast(thumb).enhance(1.25)
            thumb = ImageEnhance.Color(thumb).enhance(1.20)
        else:
            thumb = self._draw_cinematic_base(preset["theme"])

        self._draw_viral_badge(
            img=thumb,
            title=preset["title"],
            tag=preset["tag"],
            badge_color=preset["badge_color"],
            tag_color=preset["tag_color"],
        )

        return thumb.convert("RGB")

    def generate_thumbnail_set(
        self,
        output_dir: Union[str, Path],
        base_images: Optional[List[Image.Image]] = None,
    ) -> List[str]:
        """
        Generates the complete set of 4 viral YouTube thumbnails, saving them in `output_dir/`.
        Returns list of generated file paths.
        """
        out_p = Path(output_dir)
        out_p.mkdir(parents=True, exist_ok=True)

        generated_paths = []
        for idx, preset in enumerate(self.THUMBNAIL_PRESETS):
            base_img = base_images[idx] if base_images and idx < len(base_images) else None
            thumb = self.generate_thumbnail(preset_id=preset["id"], base_image=base_img)

            # Save high-res JPG and PNG
            jpg_path = out_p / f"{preset['filename']}.jpg"
            png_path = out_p / f"{preset['filename']}.png"

            thumb.save(jpg_path, format="JPEG", quality=95, optimize=True)
            thumb.save(png_path, format="PNG", optimize=True)

            generated_paths.append(str(jpg_path))

        return generated_paths
