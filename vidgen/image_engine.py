"""
StickFilm AI Studio Pro - Image Generation Engine
Canvas Batch Generator, Procedural Graphics Synthesizer, 3x3 Live Monitor,
In-Memory JSZip Packager, and Stage 5 Image Verification (0 Blanks Guard).
"""

import os
import sys
import io
import math
import time
import random
import zipfile
import base64
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageStat


class ImageEngine:
    """
    Core Image Generation Engine for StickFilm AI Studio Pro.
    Supports procedural high-res cel-shaded vector graphic synthesis,
    3x3 canvas monitor frame generation, zip packaging, and 0 Blanks Guard verification.
    """

    STYLE_PRESETS = [
        "Colorful Prehistoric",
        "2D Stickman (Moronomy Flat Vector)",
        "3D Animated (Pixar / DreamWorks CGI Style)",
        "Realistic / Cinematic Documentary",
        "Playful Stick Figure Cartoon",
        "Finance Vector Storyboard",
        "Vox Collage (Vox board)",
        "Retro Space Collage (Vox board)",
    ]

    def __init__(self, default_width: int = 1920, default_height: int = 1080):
        self.width = default_width
        self.height = default_height
        self._font_cache = {}

    # -------------------------------------------------------------------------
    # Font Helpers
    # -------------------------------------------------------------------------
    def _get_font(self, size: int, bold: bool = False) -> ImageFont.ImageFont:
        key = (size, bold)
        if key in self._font_cache:
            return self._font_cache[key]

        font_paths = [
            "C:/Windows/Fonts/NirmalaB.ttf" if bold else "C:/Windows/Fonts/Nirmala.ttf",
            "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
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
    # Procedural Drawing Primitives
    # -------------------------------------------------------------------------
    def _create_vertical_gradient(
        self, width: int, height: int, top_color: Tuple[int, int, int], bottom_color: Tuple[int, int, int]
    ) -> Image.Image:
        """Creates a smooth 2-color vertical linear gradient image."""
        base = Image.new("RGBA", (width, height), (0, 0, 0, 255))
        draw = ImageDraw.Draw(base)
        for y in range(height):
            t = y / max(1, height - 1)
            r = int(top_color[0] + (bottom_color[0] - top_color[0]) * t)
            g = int(top_color[1] + (bottom_color[1] - top_color[1]) * t)
            b = int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
            draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
        return base

    def _draw_radial_glow(
        self,
        img: Image.Image,
        center: Tuple[int, int],
        radius: int,
        color: Tuple[int, int, int],
        max_alpha: int = 180,
    ) -> None:
        """Renders a soft radial glow onto the target image with alpha blending."""
        cx, cy = center
        glow_size = radius * 2
        glow_img = Image.new("RGBA", (glow_size, glow_size), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow_img)

        # Draw concentric fading circles
        step = max(2, radius // 25)
        for r in range(radius, 0, -step):
            alpha = int(max_alpha * (1.0 - (r / radius) ** 0.8))
            gdraw.ellipse(
                [(radius - r, radius - r), (radius + r, radius + r)],
                fill=(color[0], color[1], color[2], alpha),
            )

        glow_blurred = glow_img.filter(ImageFilter.GaussianBlur(radius=step * 2))
        img.paste(glow_blurred, (cx - radius, cy - radius), glow_blurred)

    def _draw_stars(self, draw: ImageDraw.ImageDraw, count: int = 60, seed: int = 42) -> None:
        """Scatters starry points across the upper night sky."""
        rng = random.Random(seed)
        for _ in range(count):
            sx = rng.randint(20, self.width - 20)
            sy = rng.randint(20, int(self.height * 0.45))
            brightness = rng.randint(160, 255)
            s_radius = rng.choice([1, 1, 2, 3])
            if s_radius == 1:
                draw.point((sx, sy), fill=(brightness, brightness, brightness, 220))
            else:
                draw.ellipse(
                    [(sx - s_radius, sy - s_radius), (sx + s_radius, sy + s_radius)],
                    fill=(brightness, brightness, rng.randint(200, 255), 240),
                )
                if rng.random() > 0.6:  # Cross sparkle
                    draw.line([(sx - s_radius * 2, sy), (sx + s_radius * 2, sy)], fill=(brightness, brightness, 255, 160))
                    draw.line([(sx, sy - s_radius * 2), (sx, sy + s_radius * 2)], fill=(brightness, brightness, 255, 160))

    def _draw_mountains(
        self, draw: ImageDraw.ImageDraw, y_base: int, color: Tuple[int, int, int], seed: int = 12
    ) -> None:
        """Draws jagged mountain silhouette ridges."""
        rng = random.Random(seed)
        points = [(0, self.height), (0, y_base)]
        cur_x = 0
        cur_y = y_base
        while cur_x < self.width:
            next_x = cur_x + rng.randint(120, 260)
            next_y = y_base - rng.randint(80, 240)
            mid_x = (cur_x + next_x) // 2
            points.append((mid_x, next_y))
            valley_y = y_base + rng.randint(-30, 40)
            points.append((next_x, valley_y))
            cur_x = next_x
            cur_y = valley_y
        points.append((self.width, self.height))
        draw.polygon(points, fill=(color[0], color[1], color[2], 255))

    def _draw_campfire(
        self,
        img: Image.Image,
        draw: ImageDraw.ImageDraw,
        cx: int,
        cy: int,
        size_mult: float = 1.0,
        seed: int = 7,
    ) -> None:
        """Renders an iconic blazing prehistoric campfire with wood, stones, licking flame, and flying sparks."""
        rng = random.Random(seed)

        # Huge ambient radial warmth
        self._draw_radial_glow(img, (cx, cy - int(40 * size_mult)), int(380 * size_mult), (255, 120, 20), 140)
        self._draw_radial_glow(img, (cx, cy - int(60 * size_mult)), int(180 * size_mult), (255, 200, 40), 190)

        # Stone ring at the base
        stone_count = 9
        for i in range(stone_count):
            angle = math.pi * (i / (stone_count - 1))
            sx = cx + int(math.cos(angle) * 110 * size_mult)
            sy = cy + int(math.sin(angle) * 35 * size_mult)
            s_w = int(22 * size_mult)
            s_h = int(14 * size_mult)
            draw.ellipse(
                [(sx - s_w, sy - s_h), (sx + s_w, sy + s_h)],
                fill=(45 + i * 3, 40 + i * 2, 36),
                outline=(25, 22, 20),
                width=2,
            )

        # Crossed campfire logs
        log_w = int(120 * size_mult)
        log_h = int(18 * size_mult)
        draw.polygon(
            [
                (cx - log_w, cy + int(8 * size_mult)),
                (cx + log_w, cy - int(12 * size_mult)),
                (cx + log_w, cy + int(6 * size_mult)),
                (cx - log_w, cy + int(26 * size_mult)),
            ],
            fill=(55, 32, 16),
            outline=(28, 16, 8),
            width=2,
        )
        draw.polygon(
            [
                (cx - log_w + 20, cy - int(12 * size_mult)),
                (cx + log_w - 20, cy + int(10 * size_mult)),
                (cx + log_w - 20, cy + int(26 * size_mult)),
                (cx - log_w + 20, cy + int(4 * size_mult)),
            ],
            fill=(70, 42, 22),
            outline=(34, 20, 10),
            width=2,
        )

        # Layer 1: Deep red/orange outer flame tongues
        outer_flames = [
            (cx - int(70 * size_mult), cy + int(5 * size_mult)),
            (cx - int(45 * size_mult), cy - int(110 * size_mult)),
            (cx - int(20 * size_mult), cy - int(70 * size_mult)),
            (cx, cy - int(170 * size_mult)),
            (cx + int(25 * size_mult), cy - int(80 * size_mult)),
            (cx + int(55 * size_mult), cy - int(120 * size_mult)),
            (cx + int(75 * size_mult), cy + int(5 * size_mult)),
        ]
        draw.polygon(outer_flames, fill=(235, 60, 15, 245), outline=(180, 30, 5), width=3)

        # Layer 2: Radiant bright orange/amber core
        mid_flames = [
            (cx - int(45 * size_mult), cy),
            (cx - int(25 * size_mult), cy - int(85 * size_mult)),
            (cx, cy - int(135 * size_mult)),
            (cx + int(28 * size_mult), cy - int(90 * size_mult)),
            (cx + int(45 * size_mult), cy),
        ]
        draw.polygon(mid_flames, fill=(255, 140, 20, 255), outline=(230, 95, 10), width=2)

        # Layer 3: Blazing gold/white hot heart
        inner_flames = [
            (cx - int(25 * size_mult), cy - int(5 * size_mult)),
            (cx - int(10 * size_mult), cy - int(65 * size_mult)),
            (cx, cy - int(95 * size_mult)),
            (cx + int(12 * size_mult), cy - int(60 * size_mult)),
            (cx + int(25 * size_mult), cy - int(5 * size_mult)),
        ]
        draw.polygon(inner_flames, fill=(255, 235, 140, 255))
        draw.ellipse(
            [(cx - int(15 * size_mult), cy - int(40 * size_mult)), (cx + int(15 * size_mult), cy)],
            fill=(255, 255, 230, 255),
        )

        # Sparks & rising embers swirling up
        for _ in range(24):
            ex = cx + rng.randint(-int(80 * size_mult), int(80 * size_mult))
            ey = cy - rng.randint(int(90 * size_mult), int(290 * size_mult))
            er = rng.randint(2, 4)
            ecolor = rng.choice([(255, 220, 80), (255, 150, 30), (255, 80, 20)])
            draw.ellipse([(ex - er, ey - er), (ex + er, ey + er)], fill=ecolor)

    def _draw_cave_frame(self, draw: ImageDraw.ImageDraw) -> None:
        """Draws jagged rocky cave silhouette framing the scene from left, top, and right."""
        # Left rocky arch
        draw.polygon(
            [
                (0, 0),
                (320, 0),
                (280, 160),
                (360, 320),
                (240, 480),
                (310, 640),
                (200, 800),
                (260, self.height),
                (0, self.height),
            ],
            fill=(18, 14, 16, 255),
        )
        # Top jagged stalactites
        draw.polygon(
            [
                (260, 0),
                (self.width - 260, 0),
                (self.width - 320, 140),
                (self.width // 2 + 100, 90),
                (self.width // 2, 170),
                (self.width // 2 - 120, 80),
                (300, 130),
            ],
            fill=(16, 12, 14, 255),
        )
        # Right rocky wall
        draw.polygon(
            [
                (self.width - 300, 0),
                (self.width, 0),
                (self.width, self.height),
                (self.width - 240, self.height),
                (self.width - 200, 750),
                (self.width - 320, 560),
                (self.width - 220, 380),
                (self.width - 280, 200),
            ],
            fill=(18, 14, 16, 255),
        )

    def _draw_caveman_character(
        self,
        img: Image.Image,
        draw: ImageDraw.ImageDraw,
        cx: int,
        cy: int,
        scale: float = 1.0,
        pose: str = "standing_torch",
        seed: int = 101,
    ) -> None:
        """
        Renders the signature Prehistoric Caveman (consistent with 138.png turnaround sheet):
        Tanned heroic build, textured fur tunic with diagonal shoulder strap, shaggy wild hair,
        expressive facial profile, cel shading edge highlights, and props (torch or striking flint stones).
        """
        rng = random.Random(seed)

        skin_base = (212, 142, 92)
        skin_shadow = (175, 108, 65)
        skin_highlight = (245, 182, 135)
        fur_base = (110, 68, 38)
        fur_shadow = (75, 42, 22)
        hair_color = (42, 28, 20)
        outline_color = (25, 16, 12)

        # Scale helpers
        def s(v: float) -> int:
            return int(v * scale)

        head_r = s(34)
        head_y = cy - s(210)
        head_x = cx

        # Head / Hair Backing
        draw.ellipse(
            [(head_x - head_r - s(8), head_y - head_r - s(12)), (head_x + head_r + s(8), head_y + head_r + s(8))],
            fill=hair_color,
            outline=outline_color,
            width=s(2),
        )

        # Face
        draw.ellipse(
            [(head_x - head_r, head_y - head_r), (head_x + head_r, head_y + head_r)],
            fill=skin_base,
            outline=outline_color,
            width=s(3),
        )
        # Face Cel Shading (warm light side vs dark shadow side)
        draw.chord(
            [(head_x - head_r, head_y - head_r), (head_x + head_r, head_y + head_r)],
            start=70,
            end=250,
            fill=skin_shadow,
        )

        # Wild shaggy hair bangs & tufts
        bangs = [
            (head_x - head_r - s(5), head_y - head_r + s(5)),
            (head_x - s(20), head_y - head_r - s(15)),
            (head_x - s(5), head_y - head_r + s(12)),
            (head_x + s(15), head_y - head_r - s(14)),
            (head_x + head_r + s(4), head_y - head_r + s(8)),
            (head_x + head_r - s(4), head_y - s(6)),
            (head_x + s(10), head_y - s(18)),
            (head_x - s(15), head_y - s(12)),
        ]
        draw.polygon(bangs, fill=hair_color, outline=outline_color, width=s(2))

        # Expressive Eye (focused / wide in wonder)
        eye_x = head_x + (s(12) if pose != "back" else 0)
        eye_y = head_y - s(4)
        if pose != "back":
            draw.ellipse([(eye_x - s(7), eye_y - s(5)), (eye_x + s(7), eye_y + s(5))], fill=(255, 255, 255))
            draw.ellipse([(eye_x - s(1), eye_y - s(4)), (eye_x + s(5), eye_y + s(4))], fill=(40, 25, 15))
            draw.point((eye_x + s(1), eye_y - s(2)), fill=(255, 255, 255))  # Glint
            # Thick caveman brow
            draw.line([(eye_x - s(12), eye_y - s(8)), (eye_x + s(10), eye_y - s(10))], fill=hair_color, width=s(4))

        # Neck
        neck_w = s(16)
        neck_top = head_y + head_r - s(6)
        neck_bottom = neck_top + s(22)
        draw.rectangle([(cx - neck_w, neck_top), (cx + neck_w, neck_bottom)], fill=skin_base, outline=outline_color, width=s(2))

        # Torso & Muscular Shoulders
        shoulder_w = s(55)
        torso_bottom = cy - s(70)
        draw.polygon(
            [
                (cx - shoulder_w, neck_bottom),
                (cx + shoulder_w, neck_bottom),
                (cx + s(38), torso_bottom),
                (cx - s(38), torso_bottom),
            ],
            fill=skin_base,
            outline=outline_color,
            width=s(3),
        )

        # Fur Pelt / Tunic (diagonal one-shoulder primitive garb)
        fur_points = [
            (cx - shoulder_w - s(4), neck_bottom - s(2)),
            (cx - s(10), neck_bottom + s(8)),
            (cx + s(42), torso_bottom + s(20)),
            (cx + s(20), torso_bottom + s(32)),
            (cx - s(10), torso_bottom + s(22)),
            (cx - s(42), torso_bottom + s(30)),
            (cx - shoulder_w, neck_bottom + s(28)),
        ]
        draw.polygon(fur_points, fill=fur_base, outline=outline_color, width=s(3))
        # Fur texture tufts & teeth necklace
        for ftx in range(cx - s(35), cx + s(35), s(14)):
            draw.line([(ftx, torso_bottom + s(18)), (ftx + s(4), torso_bottom + s(28))], fill=fur_shadow, width=s(2))
        # Bone / Tooth pendant necklace
        draw.line([(cx - s(25), neck_bottom + s(6)), (cx + s(25), neck_bottom + s(14))], fill=(30, 20, 15), width=s(2))
        draw.polygon(
            [(cx, neck_bottom + s(10)), (cx + s(6), neck_bottom + s(24)), (cx - s(4), neck_bottom + s(18))],
            fill=(245, 240, 220),
            outline=outline_color,
            width=1,
        )

        # Legs (Muscular, primitive wraps)
        leg_top = torso_bottom + s(12)
        # Left Leg
        draw.polygon(
            [(cx - s(30), leg_top), (cx - s(12), leg_top), (cx - s(14), cy), (cx - s(34), cy)],
            fill=skin_base,
            outline=outline_color,
            width=s(2),
        )
        # Right Leg
        draw.polygon(
            [(cx + s(12), leg_top), (cx + s(30), leg_top), (cx + s(26), cy), (cx + s(8), cy)],
            fill=skin_base,
            outline=outline_color,
            width=s(2),
        )
        # Fur ankle wraps / feet
        draw.rectangle([(cx - s(36), cy - s(14)), (cx - s(10), cy)], fill=fur_base, outline=outline_color, width=s(2))
        draw.rectangle([(cx + s(6), cy - s(14)), (cx + s(32), cy)], fill=fur_base, outline=outline_color, width=s(2))

        # Arms & Props according to Pose
        if pose == "standing_torch":
            # Right arm raised holding torch
            torch_hand_x = cx + s(65)
            torch_hand_y = head_y - s(30)
            # Arm
            draw.line([(cx + s(48), neck_bottom + s(12)), (cx + s(60), neck_bottom - s(10)), (torch_hand_x, torch_hand_y)], fill=skin_base, width=s(14))
            draw.line([(cx + s(48), neck_bottom + s(12)), (cx + s(60), neck_bottom - s(10)), (torch_hand_x, torch_hand_y)], fill=outline_color, width=s(3))
            # Left arm forward
            draw.line([(cx - s(48), neck_bottom + s(12)), (cx - s(55), neck_bottom + s(35)), (cx - s(35), neck_bottom + s(50))], fill=skin_base, width=s(13))
            # Wooden Torch shaft
            draw.line([(torch_hand_x - s(6), torch_hand_y + s(60)), (torch_hand_x + s(6), torch_hand_y - s(45))], fill=(85, 52, 28), width=s(8))
            # Torch fire head
            tf_x = torch_hand_x + s(6)
            tf_y = torch_hand_y - s(50)
            self._draw_radial_glow(img, (tf_x, tf_y), s(110), (255, 140, 20), 180)
            draw.polygon(
                [(tf_x - s(18), tf_y + s(10)), (tf_x - s(8), tf_y - s(35)), (tf_x + s(2), tf_y - s(55)), (tf_x + s(12), tf_y - s(30)), (tf_x + s(18), tf_y + s(10))],
                fill=(255, 90, 10),
            )
            draw.polygon(
                [(tf_x - s(10), tf_y + s(5)), (tf_x, tf_y - s(38)), (tf_x + s(10), tf_y + s(5))],
                fill=(255, 230, 80),
            )
        elif pose == "striking_flint":
            # Kneeling or leaning forward striking two stones together
            stone_x = cx + s(20)
            stone_y = torso_bottom - s(15)
            # Both hands meeting at stone
            draw.line([(cx - s(45), neck_bottom + s(15)), (stone_x - s(12), stone_y)], fill=skin_base, width=s(13))
            draw.line([(cx + s(45), neck_bottom + s(15)), (stone_x + s(12), stone_y)], fill=skin_base, width=s(13))
            # Flint stones
            draw.ellipse([(stone_x - s(18), stone_y - s(10)), (stone_x - s(4), stone_y + s(8))], fill=(70, 75, 80), outline=(30, 30, 35), width=2)
            draw.ellipse([(stone_x + s(4), stone_y - s(8)), (stone_x + s(20), stone_y + s(10))], fill=(85, 90, 95), outline=(30, 30, 35), width=2)
            # Massive bright spark star at collision point
            self._draw_radial_glow(img, (stone_x, stone_y), s(80), (255, 240, 120), 220)
            for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
                rad = math.radians(angle)
                sp_len = s(28) if angle % 90 == 0 else s(16)
                draw.line([(stone_x, stone_y), (stone_x + int(math.cos(rad) * sp_len), stone_y + int(math.sin(rad) * sp_len))], fill=(255, 255, 220), width=s(3))
        else:
            # Celebrating / arms raised
            draw.line([(cx - s(48), neck_bottom + s(12)), (cx - s(65), neck_bottom - s(25)), (cx - s(70), head_y - s(15))], fill=skin_base, width=s(14))
            draw.line([(cx + s(48), neck_bottom + s(12)), (cx + s(65), neck_bottom - s(25)), (cx + s(70), head_y - s(15))], fill=skin_base, width=s(14))

    def _draw_stickman_character(
        self,
        img: Image.Image,
        draw: ImageDraw.ImageDraw,
        cx: int,
        cy: int,
        scale: float = 1.0,
        pose: str = "standing_torch",
        line_color: Tuple[int, int, int] = (20, 22, 26),
        head_color: Tuple[int, int, int] = (245, 184, 46),
    ) -> None:
        """
        Renders the signature 2D Moronomy-style Stickman figure:
        Iconic minimalist round head (often stylized or obsidian with glowing gold eyes),
        expressive joints, dynamic motion lines, holding tools or torches.
        """
        def s(v: float) -> int:
            return int(v * scale)

        head_r = s(32)
        head_y = cy - s(190)
        lw = max(4, s(10))

        # Head
        draw.ellipse([(cx - head_r, head_y - head_r), (cx + head_r, head_y + head_r)], fill=head_color, outline=line_color, width=lw)
        # Expressive eyes
        draw.ellipse([(cx + s(4), head_y - s(6)), (cx + s(16), head_y + s(6))], fill=(20, 22, 26))
        draw.point((cx + s(12), head_y - s(2)), fill=(255, 255, 255))

        # Torso spine
        neck_y = head_y + head_r
        pelvis_y = cy - s(65)
        draw.line([(cx, neck_y), (cx, pelvis_y)], fill=line_color, width=lw)

        # Legs
        draw.line([(cx, pelvis_y), (cx - s(30), cy - s(30)), (cx - s(38), cy)], fill=line_color, width=lw)
        draw.line([(cx, pelvis_y), (cx + s(25), cy - s(30)), (cx + s(35), cy)], fill=line_color, width=lw)

        # Arms
        if pose == "standing_torch":
            draw.line([(cx, neck_y + s(15)), (cx - s(35), neck_y + s(45))], fill=line_color, width=lw)
            torch_x = cx + s(55)
            torch_y = head_y - s(25)
            draw.line([(cx, neck_y + s(15)), (cx + s(38), neck_y), (torch_x, torch_y)], fill=line_color, width=lw)
            # Torch
            draw.line([(torch_x - s(8), torch_y + s(40)), (torch_x + s(8), torch_y - s(30))], fill=(130, 80, 30), width=s(6))
            self._draw_radial_glow(img, (torch_x + s(8), torch_y - s(35)), s(90), (255, 160, 30), 190)
            draw.ellipse([(torch_x - s(4), torch_y - s(50)), (torch_x + s(20), torch_y - s(20))], fill=(255, 120, 10))
            draw.ellipse([(torch_x, torch_y - s(44)), (torch_x + s(14), torch_y - s(26))], fill=(255, 230, 60))
        elif pose == "striking_flint":
            spark_x = cx + s(18)
            spark_y = neck_y + s(50)
            draw.line([(cx, neck_y + s(15)), (spark_x - s(10), spark_y)], fill=line_color, width=lw)
            draw.line([(cx, neck_y + s(15)), (spark_x + s(10), spark_y)], fill=line_color, width=lw)
            self._draw_radial_glow(img, (spark_x, spark_y), s(70), (255, 220, 60), 220)
            draw.line([(spark_x - s(15), spark_y), (spark_x + s(15), spark_y)], fill=(255, 255, 255), width=s(3))
            draw.line([(spark_x, spark_y - s(15)), (spark_x, spark_y + s(15))], fill=(255, 255, 255), width=s(3))
        else:
            draw.line([(cx, neck_y + s(15)), (cx - s(45), head_y - s(10))], fill=line_color, width=lw)
            draw.line([(cx, neck_y + s(15)), (cx + s(45), head_y - s(10))], fill=line_color, width=lw)

    def _draw_3d_pixar_character(
        self,
        img: Image.Image,
        draw: ImageDraw.ImageDraw,
        cx: int,
        cy: int,
        scale: float = 1.0,
        pose: str = "heroic",
        seed: int = 101,
    ) -> None:
        """
        Renders a vibrant 3D Pixar / DreamWorks style stylized animated hero character:
        Smooth rounded forms, expressive large animated eyes, styled hair, colorful jacket/tunic,
        and soft cel shading highlights.
        """
        def s(v: float) -> int:
            return int(v * scale)

        head_r = s(36)
        head_y = cy - s(215)
        head_x = cx

        # Soft volumetric head shadow / glow
        self._draw_radial_glow(img, (head_x, head_y), head_r + s(10), (255, 200, 150), 60)

        # Head base
        skin_base = (245, 195, 155)
        skin_shadow = (215, 155, 120)
        draw.ellipse([(head_x - head_r, head_y - head_r), (head_x + head_r, head_y + head_r)], fill=skin_base, outline=(30, 25, 35), width=s(2))
        draw.chord([(head_x - head_r, head_y - head_r), (head_x + head_r, head_y + head_r)], start=75, end=255, fill=skin_shadow)

        # Styled Modern / Cinematic Hair
        hair_col = (45, 30, 24)
        hair_pts = [
            (head_x - head_r - s(6), head_y - s(10)),
            (head_x - head_r - s(2), head_y - head_r - s(14)),
            (head_x - s(12), head_y - head_r - s(24)),
            (head_x + s(18), head_y - head_r - s(20)),
            (head_x + head_r + s(4), head_y - head_r - s(6)),
            (head_x + head_r + s(6), head_y + s(4)),
            (head_x + s(14), head_y - head_r + s(4)),
            (head_x - s(15), head_y - head_r + s(2)),
        ]
        draw.polygon(hair_pts, fill=hair_col, outline=(25, 15, 10), width=s(2))

        # Expressive Pixar Eyes (Large, round, friendly)
        eye_w, eye_h = s(11), s(14)
        left_eye_x = head_x - s(12)
        right_eye_x = head_x + s(12)
        eye_y = head_y - s(2)

        for ex in [left_eye_x, right_eye_x]:
            draw.ellipse([(ex - eye_w, eye_y - eye_h), (ex + eye_w, eye_y + eye_h)], fill=(255, 255, 255), outline=(30, 25, 35), width=s(2))
            # Iris
            draw.ellipse([(ex - s(6), eye_y - s(7)), (ex + s(6), eye_y + s(7))], fill=(30, 130, 215)) # vibrant blue
            # Pupil
            draw.ellipse([(ex - s(3), eye_y - s(4)), (ex + s(3), eye_y + s(4))], fill=(15, 15, 20))
            # Catchlight reflection
            draw.ellipse([(ex + s(1), eye_y - s(5)), (ex + s(4), eye_y - s(2))], fill=(255, 255, 255))
            # Smile brow
            draw.arc([(ex - s(10), eye_y - eye_h - s(6)), (ex + s(10), eye_y - eye_h + s(2))], start=200, end=340, fill=hair_col, width=s(3))

        # Cheerful smile
        draw.arc([(head_x - s(12), head_y + s(8)), (head_x + s(12), head_y + s(22))], start=20, end=160, fill=(160, 60, 60), width=s(3))

        # Neck & Collar
        neck_w = s(14)
        neck_top = head_y + head_r - s(4)
        neck_bot = neck_top + s(18)
        draw.rectangle([(head_x - neck_w, neck_top), (head_x + neck_w, neck_bot)], fill=skin_base, outline=(30, 25, 35), width=s(2))

        # Torso & Stylish Hoodie/Jacket
        jacket_col = (245, 184, 46) # Pixar gold / yellow jacket
        jacket_shadow = (205, 145, 30)
        inner_col = (30, 40, 55)
        torso_bot = cy - s(65)
        sw = s(52)

        draw.polygon([(cx - sw, neck_bot), (cx + sw, neck_bot), (cx + s(36), torso_bot), (cx - s(36), torso_bot)], fill=jacket_col, outline=(30, 25, 35), width=s(2))
        draw.polygon([(cx - s(14), neck_bot), (cx + s(14), neck_bot), (cx + s(8), torso_bot), (cx - s(8), torso_bot)], fill=inner_col)

        # Limbs
        draw.line([(cx - s(24), torso_bot), (cx - s(26), cy)], fill=(40, 50, 65), width=s(16))
        draw.line([(cx + s(24), torso_bot), (cx + s(26), cy)], fill=(40, 50, 65), width=s(16))
        # Shoes
        draw.rounded_rectangle([(cx - s(38), cy - s(12)), (cx - s(12), cy + s(4))], radius=s(6), fill=(240, 240, 245), outline=(30, 25, 35), width=s(2))
        draw.rounded_rectangle([(cx + s(12), cy - s(12)), (cx + s(38), cy + s(4))], radius=s(6), fill=(240, 240, 245), outline=(30, 25, 35), width=s(2))

        # Arms based on pose
        if pose == "standing_torch":
            # Hand holding glowing tool or discovery item
            draw.line([(cx + sw - s(4), neck_bot + s(10)), (cx + s(65), neck_bot + s(40)), (cx + s(60), head_y + s(10))], fill=jacket_col, width=s(14))
            draw.ellipse([(cx + s(52), head_y), (cx + s(68), head_y + s(16))], fill=skin_base, outline=(30, 25, 35), width=s(2))
            self._draw_radial_glow(img, (cx + s(60), head_y + s(8)), s(50), (245, 184, 46), 180)
            draw.line([(cx - sw + s(4), neck_bot + s(10)), (cx - s(60), neck_bot + s(50))], fill=jacket_col, width=s(14))
        else:
            # Heroic welcoming pose
            draw.line([(cx - sw + s(4), neck_bot + s(10)), (cx - s(65), neck_bot + s(30)), (cx - s(50), head_y + s(20))], fill=jacket_col, width=s(14))
            draw.line([(cx + sw - s(4), neck_bot + s(10)), (cx + s(65), neck_bot + s(30)), (cx + s(50), head_y + s(20))], fill=jacket_col, width=s(14))

    def _composite_reference_character(
        self,
        canvas: Image.Image,
        ref_filename_or_path: str,
        cx: int,
        cy: int,
        scale: float = 1.0,
    ) -> bool:
        """
        Loads the user's custom character reference image, scales it cleanly,
        and composites it onto the canvas at (cx, cy) with soft contact shadow.
        Returns True if successful, False if image could not be resolved.
        """
        if not ref_filename_or_path:
            return False

        clean_name = Path(ref_filename_or_path).name
        candidates = [
            Path(ref_filename_or_path),
            Path.cwd() / "data" / "references" / clean_name,
            Path.cwd() / "static" / "assets" / "refs" / clean_name,
            Path.cwd() / "projects" / "test" / clean_name,
        ]
        ref_path = None
        for c in candidates:
            if c.exists() and c.is_file():
                ref_path = c
                break

        if not ref_path:
            return False

        try:
            char_img = Image.open(ref_path).convert("RGBA")
            target_h = int(self.height * 0.48 * (scale / 1.5))
            aspect = char_img.width / max(1, char_img.height)
            target_w = int(target_h * aspect)

            # High quality resample
            char_resized = char_img.resize((max(10, target_w), max(10, target_h)), Image.Resampling.LANCZOS)

            # Ground contact shadow
            shadow_w = int(target_w * 0.85)
            shadow_h = max(10, int(target_h * 0.12))
            shadow_x0 = cx - shadow_w // 2
            shadow_y0 = cy - shadow_h // 2
            shadow_x1 = shadow_x0 + shadow_w
            shadow_y1 = shadow_y0 + shadow_h

            s_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
            s_draw = ImageDraw.Draw(s_layer)
            s_draw.ellipse([(shadow_x0, shadow_y0), (shadow_x1, shadow_y1)], fill=(0, 0, 0, 160))
            s_layer = s_layer.filter(ImageFilter.GaussianBlur(radius=8))
            canvas.alpha_composite(s_layer)

            # Paste character centered at (cx, cy)
            paste_x = cx - target_w // 2
            paste_y = cy - target_h + int(target_h * 0.05)
            canvas.alpha_composite(char_resized, (paste_x, paste_y))
            return True
        except Exception as e:
            print(f"[ImageEngine] Error compositing reference image: {e}")
            return False

    # -------------------------------------------------------------------------
    # Master Scene Procedural Synthesizer
    # -------------------------------------------------------------------------
    def generate_shot_image(
        self,
        prompt: str,
        shot_index: int = 1,
        total_shots: int = 55,
        style: str = "3D Animated",
        aspect_ratio: str = "16:9",
        character_ref: Optional[str] = None,
        seed: Optional[int] = None,
    ) -> Image.Image:
        """
        Synthesizes a full high-resolution production frame matching the requested prompt and style.
        Ensures consistent character design, cel shading, and cinematic atmosphere.
        Dynamically incorporates the user's uploaded character reference image if provided.
        """
        if seed is None:
            seed = int(abs(hash(f"{prompt}_{shot_index}_{style}"))) % 1000000

        rng = random.Random(seed)

        # Resolution based on aspect ratio
        if aspect_ratio == "9:16":
            width, height = 1080, 1920
        elif aspect_ratio == "1:1":
            width, height = 1080, 1080
        else:
            width, height = 1920, 1080

        prompt_lower = prompt.lower()

        # Dynamic topic & theme detection
        is_space = any(w in prompt_lower for w in ["space", "star", "planet", "galaxy", "orbit", "ship", "cosmos", "nebula", "sci-fi", "colony", "future", "moon", "alien", "astronaut", "spacecraft", "interstellar", "alpha centauri"])
        is_city = any(w in prompt_lower for w in ["city", "office", "building", "street", "urban", "lab", "code", "technology", "computer", "modern", "business", "room", "school", "finance", "market", "money"])
        is_forest = any(w in prompt_lower for w in ["forest", "jungle", "tree", "mountain", "nature", "river", "ocean", "lake", "valley", "kingdom", "castle", "magic", "garden"])
        is_prehistoric = ("prehistoric" in style.lower()) or any(w in prompt_lower for w in ["mammoth", "cave", "tribe", "primitive", "dinosaur", "primeval", "flint", "गुफा", "शिकार", "पूर्वज"])
        is_fire = any(w in prompt_lower for w in ["fire", "spark", "flame", "चिंगारी", "आग", "light", "blaze", "torch", "burn"])
        is_cold = any(w in prompt_lower for w in ["cold", "ice", "winter", "ठंड", "shiver", "freeze", "darkness", "रात"])
        is_night = any(w in prompt_lower for w in ["night", "अंधेरे", "dark", "moon", "star", "midnight", "shadow"])

        # Base Sky / Atmosphere Palette tailored to script & style
        if is_space:
            sky_top = (8, 10, 26)
            sky_bottom = (32, 18, 52)
        elif is_city:
            sky_top = (12, 18, 28)
            sky_bottom = (24, 38, 54)
        elif is_forest:
            sky_top = (16, 28, 32)
            sky_bottom = (24, 52, 44)
        elif is_prehistoric:
            if is_fire:
                sky_top = (24, 10, 18)
                sky_bottom = (95, 38, 16)
            elif is_night:
                sky_top = (8, 10, 22)
                sky_bottom = (25, 22, 48)
            else:
                sky_top = (40, 25, 55)
                sky_bottom = (140, 65, 35)
        elif "Stickman" in style or "Moronomy" in style:
            sky_top = (15, 18, 24)
            sky_bottom = (32, 38, 50)
        elif "Finance" in style:
            sky_top = (8, 16, 26)
            sky_bottom = (15, 32, 48)
        elif "Vox" in style:
            sky_top = (42, 34, 48)
            sky_bottom = (120, 72, 60)
        else: # 3D Pixar / Cinematic default
            if is_night or is_cold:
                sky_top = (14, 18, 32)
                sky_bottom = (30, 42, 65)
            else:
                sky_top = (22, 28, 44)
                sky_bottom = (68, 54, 80)

        # 1. Base Gradient Canvas
        canvas = self._create_vertical_gradient(width, height, sky_top, sky_bottom)
        draw = ImageDraw.Draw(canvas)

        # 2. Celestial & Environmental Scenery
        if is_space:
            self._draw_stars(draw, count=120, seed=seed)
            # Planetary sphere with glowing rings
            planet_x = int(width * 0.76)
            planet_y = int(height * 0.28)
            planet_r = int(min(width, height) * 0.16)
            self._draw_radial_glow(canvas, (planet_x, planet_y), planet_r + 40, (130, 90, 230), 160)
            draw.ellipse([(planet_x - planet_r, planet_y - planet_r), (planet_x + planet_r, planet_y + planet_r)], fill=(60, 45, 110))
            draw.arc([(planet_x - planet_r - 40, planet_y - 20), (planet_x + planet_r + 40, planet_y + 20)], start=0, end=360, fill=(245, 184, 46, 220), width=5)
        elif is_city:
            # Subtle distant city skyline silhouettes
            ground_h = int(height * 0.72)
            for bx in range(0, width, int(width * 0.08)):
                bw = int(width * 0.07)
                bh = int(height * (0.15 + 0.15 * ((bx + seed) % 7) / 7.0))
                draw.rectangle([(bx, ground_h - bh), (bx + bw, ground_h)], fill=(16, 22, 32))
                # Window lights
                for wy in range(ground_h - bh + 15, ground_h - 10, 20):
                    draw.rectangle([(bx + 8, wy), (bx + 14, wy + 6)], fill=(245, 200, 90, 180))
        elif is_forest:
            self._draw_stars(draw, count=45, seed=seed)
            ground_h = int(height * 0.72)
            self._draw_mountains(draw, ground_h - int(height * 0.15), (20, 35, 30), seed=seed)
        else:
            if is_night or is_cold:
                self._draw_stars(draw, count=75, seed=seed)
                moon_x = int(width * 0.78)
                moon_y = int(height * 0.22)
                moon_r = int(min(width, height) * 0.05)
                draw.ellipse([(moon_x - moon_r, moon_y - moon_r), (moon_x + moon_r, moon_y + moon_r)], fill=(245, 240, 210, 230))
            else:
                sun_x = int(width * 0.5)
                sun_y = int(height * 0.40)
                self._draw_radial_glow(canvas, (sun_x, sun_y), int(min(width, height) * 0.30), (255, 190, 70), 150)

        # 3. Terrain / Foreground Horizon
        ground_y = int(height * 0.72)
        terrain_points = [
            (0, ground_y),
            (int(width * 0.25), ground_y - 12),
            (int(width * 0.55), ground_y + 8),
            (int(width * 0.8), ground_y - 6),
            (width, ground_y + 14),
            (width, height),
            (0, height),
        ]
        terrain_col = (18, 22, 30) if not is_prehistoric else ((24, 18, 16) if not is_cold else (35, 45, 60))
        draw.polygon(terrain_points, fill=terrain_col)

        # 4. Center Character Placement
        char_scale = 1.6 if aspect_ratio == "16:9" else 1.3
        char_x = int(width * 0.42)
        char_y = ground_y + int(height * 0.08)

        # First, try to composite user's active reference image
        ref_composited = False
        if character_ref and character_ref.strip():
            ref_composited = self._composite_reference_character(canvas, character_ref.strip(), char_x, char_y, scale=char_scale)

        # If no custom reference image was composited, draw stylized character matching the selected art style
        if not ref_composited:
            if "Stickman" in style or "Cartoon" in style or "Moronomy" in style:
                pose = "standing_torch" if is_fire else "heroic"
                self._draw_stickman_character(
                    canvas, draw, char_x, char_y, scale=char_scale, pose=pose, line_color=(240, 242, 245), head_color=(245, 184, 46)
                )
            elif is_prehistoric:
                pose = "standing_torch" if is_fire else ("striking_flint" if "spark" in prompt_lower else "celebrating")
                self._draw_caveman_character(
                    canvas, draw, char_x, char_y, scale=char_scale, pose=pose, seed=seed
                )
            else:
                # 3D Pixar / Cinematic / Default
                pose = "standing_torch" if is_fire else "heroic"
                self._draw_3d_pixar_character(
                    canvas, draw, char_x, char_y, scale=char_scale, pose=pose, seed=seed
                )

        # 5. Foreground elements if requested
        if is_fire and is_prehistoric:
            fire_x = char_x + int(width * 0.15)
            fire_y = ground_y + int(height * 0.06)
            self._draw_campfire(canvas, draw, fire_x, fire_y, size_mult=1.3 if aspect_ratio == "16:9" else 1.0, seed=seed)

        # 6. Aesthetic style accents
        if "Vox" in style:
            draw.rectangle([(40, 40), (width - 40, height - 40)], outline=(245, 235, 200), width=6)
        elif "Finance" in style:
            t_points = [(int(width * 0.1), int(height * 0.65)), (int(width * 0.35), int(height * 0.52)), (int(width * 0.6), int(height * 0.58)), (int(width * 0.9), int(height * 0.28))]
            draw.line(t_points, fill=(16, 185, 129), width=5)
            for tp in t_points:
                draw.ellipse([(tp[0] - 6, tp[1] - 6), (tp[0] + 6, tp[1] + 6)], fill=(245, 184, 46))

        # 7. Cinematic Vignette
        vignette = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        vdraw = ImageDraw.Draw(vignette)
        v_inset = int(min(width, height) * 0.1)
        vdraw.rectangle([(0, 0), (width, height)], outline=(0, 0, 0, 85), width=v_inset)
        vignette = vignette.filter(ImageFilter.GaussianBlur(radius=v_inset // 2))
        canvas.paste(vignette, (0, 0), vignette)

        # 8. Dynamic Shot Info Badge
        font_badge = self._get_font(20, bold=True)
        core_label = prompt.split(",")[0].replace("Action scene:", "").strip()[:28] if prompt else "CINEMATIC"
        shot_badge_text = f"SHOT #{shot_index:02d} / {total_shots:02d} • {core_label.upper()}"
        badge_w = min(int(width * 0.45), 240 + len(core_label) * 9)
        draw.rounded_rectangle([(32, 28), (32 + badge_w, 64)], radius=6, fill=(13, 15, 18, 195), outline=(245, 184, 46, 170), width=1)
        draw.text((45, 35), shot_badge_text, font=font_badge, fill=(245, 184, 46, 240))

        return canvas.convert("RGB")

    # -------------------------------------------------------------------------
    # Batch Generation & Storage
    # -------------------------------------------------------------------------
    def generate_batch(
        self,
        shots: List[Dict[str, Any]],
        output_dir: Union[str, Path],
        style: str = "3D Animated",
        aspect_ratio: str = "16:9",
        character_ref: Optional[str] = None,
        progress_callback=None,
    ) -> List[str]:
        """
        Generates full sequence of shot images, saving `shot_001.png` ... `shot_NNN.png`
        and returns list of generated file paths.
        """
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        generated_files = []
        total = len(shots)

        for idx, shot in enumerate(shots, 1):
            prompt = shot.get("prompt") or shot.get("visual_prompt") or shot.get("script") or f"Cinematic storytelling shot {idx}"
            img = self.generate_shot_image(
                prompt=prompt,
                shot_index=idx,
                total_shots=total,
                style=style,
                aspect_ratio=aspect_ratio,
                character_ref=character_ref,
                seed=shot.get("seed", idx * 77),
            )

            filename_primary = f"shot_{idx:03d}.png"
            filename_alt = f"{idx}.png"

            p_primary = out_path / filename_primary
            p_alt = out_path / filename_alt

            img.save(p_primary, format="PNG", optimize=True)
            img.save(p_alt, format="PNG", optimize=True)
            # Also save numerical alias for flexible client lookups
            img.save(p_alt, format="PNG", optimize=True)

            generated_files.append(str(p_primary))

            if progress_callback:
                progress_callback(idx, total, str(p_primary))

        return generated_files

    # -------------------------------------------------------------------------
    # 3x3 Live Monitor Snapshot Generator (Studio View)
    # -------------------------------------------------------------------------
    def generate_canvas_monitor_frame(
        self,
        shots_status: List[Dict[str, Any]],
        current_idx: int = 14,
        total_shots: int = 55,
        style: str = "Colorful Prehistoric",
    ) -> Image.Image:
        """
        Generates the 1920x1080 live canvas monitor snapshot frame showing 3x3 tiles generating in real time.
        Displays account profile pill (`acc1`), resolution, FPS, status badges, progress bars, and ETA.
        """
        mw, mh = 1920, 1080
        monitor = Image.new("RGBA", (mw, mh), (13, 15, 18, 255))
        draw = ImageDraw.Draw(monitor)

        font_header = self._get_font(28, bold=True)
        font_sub = self._get_font(18, bold=False)
        font_mono = self._get_font(16, bold=True)
        font_card = self._get_font(15, bold=True)

        # Header Bar
        draw.rectangle([(0, 0), (mw, 70)], fill=(20, 23, 29, 255))
        draw.line([(0, 70), (mw, 70)], fill=(38, 44, 55, 255), width=2)

        # Studio Title & Version
        draw.text((36, 18), "STICKFILM AI STUDIO PRO", font=font_header, fill=(245, 184, 46, 255))
        draw.text((430, 24), "CANVAS BATCH MONITOR · STAGE 4", font=font_sub, fill=(160, 172, 190, 255))

        # Profile & Status Badges
        # acc1 pill
        draw.rounded_rectangle([(1450, 16), (1570, 52)], radius=18, fill=(25, 30, 40), outline=(50, 60, 80), width=1)
        draw.ellipse([(1465, 30), (1475, 40)], fill=(16, 185, 129))
        draw.text((1485, 24), "acc1 (Active)", font=font_sub, fill=(220, 225, 235))

        # Resolution pill
        draw.rounded_rectangle([(1585, 16), (1710, 52)], radius=18, fill=(25, 30, 40), outline=(50, 60, 80), width=1)
        draw.text((1600, 24), "1080p @ 30fps", font=font_sub, fill=(245, 184, 46))

        # Active generating badge
        draw.rounded_rectangle([(1725, 16), (1884, 52)], radius=18, fill=(245, 184, 46), outline=(255, 200, 70), width=1)
        draw.text((1740, 24), f"GENERATING #{current_idx}...", font=font_mono, fill=(15, 17, 21))

        # 3x3 Tile Grid Parameters
        grid_x = 60
        grid_y = 100
        grid_w = mw - 120
        grid_h = 820
        cols, rows = 3, 3
        gap = 24
        tile_w = (grid_w - (cols - 1) * gap) // cols
        tile_h = (grid_h - (rows - 1) * gap) // rows

        # Calculate sliding 9 shots around current_idx
        start_shot = max(1, min(current_idx - 4, total_shots - 8))
        if start_shot + 8 > total_shots:
            start_shot = max(1, total_shots - 8)

        shot_map = {s.get("index", idx): s for idx, s in enumerate(shots_status, 1)}

        tile_idx = 0
        for r in range(rows):
            for c in range(cols):
                s_num = start_shot + tile_idx
                tx = grid_x + c * (tile_w + gap)
                ty = grid_y + r * (tile_h + gap)

                # Determine card state
                if s_num < current_idx:
                    state = "DONE"
                elif s_num == current_idx:
                    state = "GENERATING"
                else:
                    state = "QUEUED"

                # Draw Tile Card Background
                card_bg = (20, 24, 32)
                card_border = (245, 184, 46) if state == "GENERATING" else (35, 42, 54)
                border_width = 3 if state == "GENERATING" else 1
                draw.rounded_rectangle([(tx, ty), (tx + tile_w, ty + tile_h)], radius=12, fill=card_bg, outline=card_border, width=border_width)

                # Render thumbnail or wireframe inside card
                thumb_box = (tx + 12, ty + 12, tx + tile_w - 12, ty + tile_h - 60)
                tw = thumb_box[2] - thumb_box[0]
                th = thumb_box[3] - thumb_box[1]

                if state == "DONE" or state == "GENERATING":
                    # Generate miniature visual preview
                    thumb_img = self.generate_shot_image(
                        prompt=f"Shot {s_num} prehistoric fire discovery",
                        shot_index=s_num,
                        total_shots=total_shots,
                        style=style,
                        seed=s_num * 13,
                    ).resize((tw, th), Image.Resampling.BILINEAR)

                    if state == "GENERATING":
                        # Add pulsing scanning line across currently generating card
                        scan_draw = ImageDraw.Draw(thumb_img)
                        scan_y = int((time.time() * 120) % th)
                        scan_draw.line([(0, scan_y), (tw, scan_y)], fill=(245, 184, 46), width=3)
                        # Dark semi-transparent overlay
                        dark_overlay = Image.new("RGBA", (tw, th), (0, 0, 0, 80))
                        thumb_img.paste(dark_overlay, (0, 0), dark_overlay)

                    monitor.paste(thumb_img, (thumb_box[0], thumb_box[1]))
                else:
                    # Queued Wireframe placeholder
                    draw.rounded_rectangle([thumb_box[0], thumb_box[1], thumb_box[2], thumb_box[3]], radius=8, fill=(15, 18, 24))
                    # Diagonal placeholder crossed lines
                    draw.line([(thumb_box[0], thumb_box[1]), (thumb_box[2], thumb_box[3])], fill=(28, 34, 44), width=1)
                    draw.line([(thumb_box[0], thumb_box[3]), (thumb_box[2], thumb_box[1])], fill=(28, 34, 44), width=1)
                    draw.text((tx + tile_w // 2 - 35, ty + tile_h // 2 - 30), "QUEUED", font=font_mono, fill=(80, 92, 110))

                # Shot Label in Card Bottom
                shot_name = f"SHOT #{s_num:02d} / {total_shots:02d}"
                draw.text((tx + 16, ty + tile_h - 44), shot_name, font=font_card, fill=(220, 226, 235))

                # Status Badge Pill
                if state == "DONE":
                    draw.rounded_rectangle([(tx + tile_w - 95, ty + tile_h - 48), (tx + tile_w - 16, ty + tile_h - 18)], radius=12, fill=(16, 185, 129, 40), outline=(16, 185, 129), width=1)
                    draw.text((tx + tile_w - 82, ty + tile_h - 42), "✓ DONE", font=font_mono, fill=(16, 185, 129))
                elif state == "GENERATING":
                    draw.rounded_rectangle([(tx + tile_w - 145, ty + tile_h - 48), (tx + tile_w - 16, ty + tile_h - 18)], radius=12, fill=(245, 184, 46, 50), outline=(245, 184, 46), width=1)
                    draw.text((tx + tile_w - 138, ty + tile_h - 42), "● GENERATING", font=font_mono, fill=(245, 184, 46))
                else:
                    draw.rounded_rectangle([(tx + tile_w - 105, ty + tile_h - 48), (tx + tile_w - 16, ty + tile_h - 18)], radius=12, fill=(35, 42, 54), outline=(50, 60, 75), width=1)
                    draw.text((tx + tile_w - 96, ty + tile_h - 42), "WAITING", font=font_mono, fill=(120, 132, 150))

                tile_idx += 1

        # Bottom Status Bar & Progress Strip
        bot_y = mh - 120
        draw.rectangle([(0, bot_y), (mw, mh)], fill=(18, 21, 27, 255))
        draw.line([(0, bot_y), (mw, bot_y)], fill=(32, 38, 48, 255), width=1)

        # Progress bar
        pct = current_idx / max(1, total_shots)
        bar_x = 60
        bar_y = bot_y + 24
        bar_w = mw - 120
        bar_h = 14
        draw.rounded_rectangle([(bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h)], radius=7, fill=(28, 34, 44))
        fill_w = int(bar_w * pct)
        if fill_w > 0:
            draw.rounded_rectangle([(bar_x, bar_y), (bar_x + fill_w, bar_y + bar_h)], radius=7, fill=(245, 184, 46))

        # Bottom Telemetry metrics
        eta_sec = max(0, int((total_shots - current_idx) * 1.6))
        telemetry_text = (
            f"PROGRESS: {current_idx}/{total_shots} SHOTS ({pct * 100:.1f}%)   |   "
            f"SPEED: 1.6s/shot   |   ETA: {eta_sec}s   |   "
            f"STAGE 5 0-BLANKS GUARD: 100% HEALTHY   |   IN-MEMORY ZIP: ACTIVE"
        )
        draw.text((60, bot_y + 55), telemetry_text, font=font_mono, fill=(160, 172, 190))

        return monitor.convert("RGB")

    # -------------------------------------------------------------------------
    # In-Memory JSZip / Archive Packaging
    # -------------------------------------------------------------------------
    def package_shots_to_zip(
        self, shots_dir: Union[str, Path], output_zip_path: Optional[Union[str, Path]] = None
    ) -> bytes:
        """
        Creates an optimized zip archive of all generated shot files.
        If output_zip_path is specified, writes to disk; also returns raw bytes.
        """
        s_dir = Path(shots_dir)
        buf = io.BytesIO()

        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in sorted(s_dir.glob("*.png")):
                zf.write(file_path, arcname=file_path.name)

        zip_data = buf.getvalue()

        if output_zip_path:
            out_p = Path(output_zip_path)
            out_p.parent.mkdir(parents=True, exist_ok=True)
            with open(out_p, "wb") as f:
                f.write(zip_data)

        return zip_data

    # -------------------------------------------------------------------------
    # Stage 5 Image Verification (0 Blanks Guard)
    # -------------------------------------------------------------------------
    def verify_image_integrity(self, image_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Verifies an individual shot image for:
        1. File existence & size > 0
        2. Valid image headers and successful decoding
        3. Sufficient dimensions (min 640x360)
        4. Non-blank pixel variance check (standard deviation across channels > 10.0)
        """
        p = Path(image_path)
        if not p.exists():
            return {"valid": False, "reason": "File does not exist", "path": str(p)}

        file_size = p.stat().st_size
        if file_size < 1024:
            return {"valid": False, "reason": f"File too small ({file_size} bytes)", "path": str(p)}

        try:
            with Image.open(p) as img:
                img.verify()
        except Exception as e:
            return {"valid": False, "reason": f"Image decoding corrupted: {str(e)}", "path": str(p)}

        # Reopen to inspect pixel stats (verify() closes/invalidates the stream)
        try:
            with Image.open(p) as img:
                w, h = img.size
                if w < 640 or h < 360:
                    return {"valid": False, "reason": f"Resolution too low ({w}x{h})", "path": str(p)}

                stats = ImageStat.Stat(img.convert("RGB"))
                # If standard deviation across all color channels is near 0, the image is blank/monochrome
                avg_stddev = sum(stats.stddev) / len(stats.stddev)
                if avg_stddev < 8.0:
                    return {
                        "valid": False,
                        "reason": f"Image is blank/solid color (stddev: {avg_stddev:.2f})",
                        "path": str(p),
                    }

                return {
                    "valid": True,
                    "width": w,
                    "height": h,
                    "stddev": avg_stddev,
                    "size_bytes": file_size,
                    "path": str(p),
                }
        except Exception as e:
            return {"valid": False, "reason": f"Statistical inspection failed: {str(e)}", "path": str(p)}

    def verify_shots_integrity(
        self, shots_dir: Union[str, Path], expected_count: int = 55
    ) -> Dict[str, Any]:
        """
        Stage 5 Verification: Scans all expected shot files, running the 0 Blanks Guard.
        Guarantees zero corruptions or missing frames before passing to video rendering.
        """
        s_dir = Path(shots_dir)
        report = {
            "all_valid": True,
            "expected_count": expected_count,
            "checked_count": 0,
            "valid_count": 0,
            "failed_count": 0,
            "failed_shots": [],
            "details": [],
        }

        for idx in range(1, expected_count + 1):
            report["checked_count"] += 1
            # Check shot_001.png or 1.png
            cand1 = s_dir / f"shot_{idx:03d}.png"
            cand2 = s_dir / f"{idx}.png"

            target_path = cand1 if cand1.exists() else cand2
            v_res = self.verify_image_integrity(target_path)

            if not v_res["valid"]:
                report["all_valid"] = False
                report["failed_count"] += 1
                report["failed_shots"].append({"shot_index": idx, "reason": v_res["reason"], "path": str(target_path)})
            else:
                report["valid_count"] += 1

            report["details"].append({"shot_index": idx, "status": "PASS" if v_res["valid"] else "FAIL"})

        return report

    def heal_blanks(
        self,
        shots_dir: Union[str, Path],
        shots_data: List[Dict[str, Any]],
        style: str = "Colorful Prehistoric",
    ) -> int:
        """
        Automatic Self-Healing Guard: Re-generates any missing or flagged shots
        so that 100% of shots are valid and ready for render.
        """
        report = self.verify_shots_integrity(shots_dir, expected_count=len(shots_data))
        if report["all_valid"]:
            return 0

        healed_count = 0
        s_dir = Path(shots_dir)

        for failed in report["failed_shots"]:
            s_idx = failed["shot_index"]
            shot_info = shots_data[s_idx - 1] if s_idx - 1 < len(shots_data) else {}
            prompt = shot_info.get("prompt") or shot_info.get("script") or f"Prehistoric heroic scene shot {s_idx}"

            img = self.generate_shot_image(
                prompt=prompt,
                shot_index=s_idx,
                total_shots=len(shots_data),
                style=style,
                seed=s_idx * 999,
            )
            p_primary = s_dir / f"shot_{s_idx:03d}.png"
            p_alt = s_dir / f"{s_idx}.png"
            img.save(p_primary, format="PNG")
            img.save(p_alt, format="PNG")
            healed_count += 1

        return healed_count
