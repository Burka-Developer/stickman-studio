"""
StickFilm AI Studio Pro - Prompt Engine
Action-first iconic cinematic prompt generation tailored to 8+ visual art styles,
character turnaround references, and dynamic camera angles.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Any


# Preset Art Style Formulas
STYLE_PRESETS: Dict[str, Dict[str, Any]] = {
    "3D Animated (Pixar / DreamWorks CGI Style)": {
        "key": "3d_pixar",
        "style_prefix": "3D Pixar DreamWorks CGI animation style, highly expressive stylized character, subsurface scattering, octane render, soft cinematic rim lighting, 8k resolution, vibrant rich colors, whimsical cinematic charm",
        "lighting": "warm golden rim light, soft volumetric ambient fill, expressive eye catchlights",
        "negative": "photorealistic human, live action, flat 2d, sketch, grainy, watermark, text, lowres, deformed, bad anatomy",
    },
    "2D Stickman (Moronomy Flat Vector)": {
        "key": "2d_stickman_moronomy",
        "style_prefix": "iconic 2D Moronomy flat vector animation style, minimalist bold clean black ink line stickman character with expressive oversized round white eyes and comedic body posture, solid minimalist color blocking, crisp modern vector art, clean white or vibrant flat pastel background",
        "lighting": "flat high-contrast studio vector lighting, no gradients, sharp silhouettes",
        "negative": "3d render, realistic skin, photographic, complex shadows, muddy colors, text, watermark, signature",
    },
    "Realistic / Cinematic Documentary": {
        "key": "cinematic_documentary",
        "style_prefix": "cinematic 35mm film still, National Geographic documentary cinematography, Panavision anamorphic lens, shallow depth of field, photorealistic textures, atmospheric haze, authentic historical realism",
        "lighting": "natural overcast daylight, dramatic directional chiaroscuro, natural golden hour dust motes",
        "negative": "cartoon, 3d render, anime, over-saturated, CGI, plastic skin, drawing, watermark, subtitles, text",
    },
    "Playful Stick Figure Cartoon": {
        "key": "playful_stickman",
        "style_prefix": "playful animated stick figure cartoon, vibrant doodles, cheerful hand-drawn clean outlines, humorous animated physics, bright energetic colors, YouTube animated explainer aesthetic",
        "lighting": "bright upbeat studio lighting, cheerful highlights",
        "negative": "dark horror, realistic anatomy, gritty texture, blur, text, watermark",
    },
    "Colorful Prehistoric": {
        "key": "colorful_prehistoric",
        "style_prefix": "vibrant prehistoric primeval world, lush giant jungle ferns, glowing prehistoric flora, dramatic smoking volcanoes in distance, colorful stylized dinosaurs and ancient creatures, epic high adventure art style",
        "lighting": "dramatic prehistoric sunrise, amber crepuscular rays piercing misty canopy, glowing lava reflections",
        "negative": "modern buildings, cars, smartphones, modern clothing, text, watermark, blurry",
    },
    "Finance Vector Storyboard": {
        "key": "finance_vector",
        "style_prefix": "sleek modern fintech infographic illustration, isometric clean storyboard art, minimalist geometric business figures, glowing green profit arrows, dark navy and neon emerald palette, crisp corporate vector aesthetic",
        "lighting": "futuristic neon edge highlights, clean soft studio backlight",
        "negative": "messy sketch, hand-drawn, dirty textures, photograph, text, watermark, low quality",
    },
    "Vox Collage (Vox board)": {
        "key": "vox_collage",
        "style_prefix": "Vox style mixed-media motion collage, cutout archival photographs blended with bold papercraft textures, risograph halftone grain, striking editorial collage, punchy graphic shapes and vintage elements",
        "lighting": "high contrast graphic editorial lighting, drop shadows between paper layers",
        "negative": "smooth 3d cgi, airbrushed, generic anime, 3d render, text, watermark, blurry",
    },
    "Retro Space Collage (Vox board)": {
        "key": "retro_space_collage",
        "style_prefix": "retro 1960s space race collage, vintage NASA photography mixed with cosmic geometric cutouts, analog screen print texture, cyan and magenta duotone accents, cosmic nebula papercraft",
        "lighting": "stark lunar sunlight and deep space starfield glow",
        "negative": "contemporary modern digital art, smooth cgi, text, watermark, signature",
    },
}

# Dynamic Camera Staging Presets
CAMERA_STAGINGS: List[Dict[str, str]] = [
    {"type": "wide establishing", "desc": "epic wide establishing shot, panoramic composition revealing environmental scale and atmospheric depth"},
    {"type": "medium action", "desc": "dynamic medium action shot, waist-up composition focusing on intense physical motion and immediate body language"},
    {"type": "dramatic low angle", "desc": "dramatic low angle hero perspective looking up, towering monumental scale, powerful visual impact"},
    {"type": "close-up macro", "desc": "cinematic close-up portrait, focusing on detailed emotional expression, hyper-focused eyes and micro-reactions"},
    {"type": "drone aerial", "desc": "high-angle drone aerial view looking down at the unfolding scene, sweeping kinetic overview"},
    {"type": "over the shoulder", "desc": "cinematic over-the-shoulder perspective, framing the subject looking toward the looming destination"},
]


class PromptEngine:
    """
    Synthesizes action-first iconic scene prompts for video generation.
    """

    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        self.api_keys = api_keys or {}

    def set_api_keys(self, keys: Dict[str, str]):
        self.api_keys.update(keys)

    def generate_shot_prompt(
        self,
        shot_text: str,
        shot_index: int,
        total_shots: int,
        visual_style: str = "3D Animated (Pixar / DreamWorks CGI Style)",
        character_ref: str = "Iconic Stickman Hero with expressive large round white eyes",
        world_setting: str = "",
        aspect_ratio: str = "16:9",
        camera_motion: str = "Mix of all"
    ) -> Dict[str, Any]:
        """
        Creates an action-first iconic prompt for a single shot chunk.
        """
        # Resolve style details
        style_info = self._resolve_style_info(visual_style)
        style_prefix = style_info["style_prefix"]
        lighting_style = style_info["lighting"]
        negative_prompt = style_info["negative"]

        # Action-First subject extraction
        action_phrase = self._extract_action_phrase(shot_text)

        # Select dynamic camera staging based on index
        camera_stage = CAMERA_STAGINGS[shot_index % len(CAMERA_STAGINGS)]

        # Determine world setting
        setting_clause = world_setting.strip()
        if not setting_clause:
            setting_clause = "atmospheric environment matching narrative theme, richly detailed backdrop"

        # Clean character reference inclusion (strip filenames like .png and underscores)
        raw_char = character_ref.strip() if character_ref else "main stickman character"
        char_clean = re.sub(r'\.(png|jpg|jpeg|webp)$', '', Path(raw_char).name, flags=re.I).replace('_', ' ').replace('-', ' ').strip()
        if not char_clean or char_clean.isdigit():
            char_clean = "main stickman protagonist"

        # Action-First composition:
        prompt_parts = [
            f"{action_phrase}",
            f"featuring {char_clean}",
            f"{camera_stage['desc']}",
            f"{setting_clause}",
            f"{lighting_style}",
            f"{style_prefix}",
            f"masterpiece visual, 8k resolution, cinematic 16:9 framing"
        ]

        full_prompt = ", ".join(prompt_parts)

        return {
            "shot_index": shot_index,
            "shot_number": shot_index + 1,
            "script_text": shot_text,
            "prompt": full_prompt,
            "action_core": action_phrase,
            "camera_staging": camera_stage["type"],
            "negative_prompt": negative_prompt,
            "visual_style": visual_style,
            "aspect_ratio": aspect_ratio,
        }

    def generate_all_prompts(
        self,
        shots: List[Dict[str, Any]],
        visual_style: str = "3D Animated (Pixar / DreamWorks CGI Style)",
        character_ref: str = "Iconic Stickman Hero with expressive large round white eyes",
        world_setting: str = "",
        aspect_ratio: str = "16:9",
        camera_motion: str = "Mix of all"
    ) -> List[Dict[str, Any]]:
        """
        Synthesizes visual prompts for an entire sequence of script shots.
        """
        prompts = []
        total = len(shots)
        for i, s in enumerate(shots):
            text = s.get("text", "")
            shot_prompt_data = self.generate_shot_prompt(
                shot_text=text,
                shot_index=i,
                total_shots=total,
                visual_style=visual_style,
                character_ref=character_ref,
                world_setting=world_setting,
                aspect_ratio=aspect_ratio,
                camera_motion=camera_motion
            )
            # Merge with shot timing info
            shot_prompt_data["shot_id"] = s.get("shot_id", i + 1)
            shot_prompt_data["start_time"] = s.get("start_time", 0.0)
            shot_prompt_data["end_time"] = s.get("end_time", 0.0)
            shot_prompt_data["duration"] = s.get("duration", 0.0)
            prompts.append(shot_prompt_data)
        return prompts

    def generate_style_samples(
        self,
        style_name: str,
        reference_notes: str = "",
        aspect_ratio: str = "16:9"
    ) -> Dict[str, Any]:
        """
        Generates 8 sample prompt concepts and a style breakdown formula
        for the 'New category' style creator modal.
        """
        clean_name = style_name.strip() or "Custom Artistic Style"
        
        # Style formula breakdown
        formula = {
            "style_name": clean_name,
            "lineage": "Signature Custom Aesthetic",
            "primary_medium": "Mixed Stylized Rendering with Precision Inking",
            "palette": "Vibrant Obsidian & Sunburst Gold (#f5b82e) with cinematic ambient grading",
            "texture_profile": "Crisp anti-aliased geometry with subtle tactile surface grain",
            "lighting_setup": "Directional key light with dramatic volumetric rim highlights",
            "camera_rule": "Dynamic angular staging with high kinetic readability",
            "prompt_keywords": [
                f"{clean_name} visual aesthetic",
                "cinematic framing",
                "masterpiece illustration",
                "clean expressive silhouettes",
                "8k visual fidelity"
            ]
        }

        # 8 distinct shot archetypes for visual consistency evaluation
        archetypes = [
            ("Character Turnaround (Front)", "Full body frontal hero stance against neutral studio backdrop, clear proportions and costume details"),
            ("Character Turnaround (3/4 Profile)", "Three-quarter dynamic pose showing depth, silhouette curvature, and expressive head angle"),
            ("Heroic Action Pose", "High-energy leap or dynamic sprint with motion distortion lines and physical momentum"),
            ("Close-Up Facial Emotion", "Dramatic close-up framing highlighting intense focus, glowing expressive eyes, and emotional tension"),
            ("Epic Environment Establishing", "Wide scenic vista showing the expansive world architecture, atmospheric weather, and horizon"),
            ("Duo Interaction / Conflict", "Two characters in an engaging dialogue or tense standoff with cinematic depth-of-field separation"),
            ("Night Atmosphere / Lighting", "Nocturnal scene illuminated by glowing lanterns, neon embers, or celestial moonlight reflections"),
            ("Climactic Hero Moment", "Low-angle heroic silhouette standing at the mountain precipice, triumphant golden hour wind effect"),
        ]

        samples = []
        for idx, (title, desc) in enumerate(archetypes, start=1):
            sample_prompt = (
                f"{clean_name} style, {desc}, {reference_notes}. "
                f"Flawless composition, bold iconic character design, professional studio quality, "
                f"volumetric lighting, aspect ratio {aspect_ratio}"
            )
            samples.append({
                "sample_id": idx,
                "title": title,
                "description": desc,
                "prompt": sample_prompt,
                "aspect_ratio": aspect_ratio,
                "image_filename": f"sample_{idx}.png",
            })

        return {
            "style_name": clean_name,
            "formula": formula,
            "samples": samples
        }

    def _resolve_style_info(self, visual_style: str) -> Dict[str, Any]:
        """Looks up or synthesizes style preset parameters."""
        for key, preset in STYLE_PRESETS.items():
            if visual_style.lower() in key.lower() or key.lower() in visual_style.lower():
                return preset

        # Default fallback or custom style parser
        return {
            "key": "custom_style",
            "style_prefix": f"{visual_style} aesthetic, highly detailed masterpiece, expressive stylized composition, 8k resolution, cinematic atmosphere",
            "lighting": "dramatic cinematic lighting with balanced ambient fill and striking rim highlights",
            "negative": "blurry, low quality, distorted, extra limbs, bad anatomy, text, watermark, signature, duplicate, cropped",
        }

    def _extract_action_phrase(self, text: str) -> str:
        """
        Extracts the active dynamic core of the script chunk.
        Produces vivid, scene-specific cinematic visual action descriptions.
        """
        raw = text.strip()
        if not raw:
            return "cinematic heroic character standing alert in atmospheric world"

        low = raw.lower()

        # Semantic scene archetypes for richer image generation
        if any(k in low for k in ["winter", "cold", "snow", "freez", "ice", "blizzard", "ठंड", "बर्फ"]):
            return "braving a ferocious sub-zero blizzard storm with biting howling winds and frozen snowdrifts"
        elif any(k in low for k in ["fire", "spark", "flame", "ember", "smoke", "चिंगारी", "आग", "दावानल"]):
            return "discovering a roaring golden fire ember bursting into bright warm flames"
        elif any(k in low for k in ["cave", "shelter", "गुफा", "अंधेरे", "dark", "pitch-black"]):
            return "seeking desperate refuge inside a shadowy ancient stone cave under flickering torchlight"
        elif any(k in low for k in ["beast", "predator", "tiger", "saber", "mammoth", "animal", "खूंखार", "जानवर"]):
            return "confronting fierce primeval wild beasts pacing with glowing eyes in the twilight shadows"
        elif any(k in low for k in ["lightning", "storm", "thunder", "बिजली", "तूफान"]):
            return "witnessing a colossal blinding fork of lightning tearing through dark stormy skies"
        elif any(k in low for k in ["brain", "mind", "evolution", "thought", "दिमाग", "सोच"]):
            return "symbolic cinematic shot of human mind evolution awakening with glowing sparks of ingenuity"
        elif any(k in low for k in ["food", "meat", "cook", "feast", "खाना", "पका"]):
            return "gathering around a crackling hearth sharing the first cooked nourishing meal"
        elif any(k in low for k in ["flint", "stone", "tool", "strike", "पत्थर"]):
            return "vigorously striking twin flints together generating a shower of golden ignition sparks"

        # Strip conversational fillers
        cleaned = re.sub(
            r'^(imagine|think about|what if|you see|there is no|outside|inside|so|and then|because|in fact|but then|suddenly)\s+',
            '', raw, flags=re.I
        ).strip()
        cleaned = re.sub(r'[^\w\s\-,]', ' ', cleaned).strip()
        words = cleaned.split()

        # Varied cinematic action verbs
        actions = [
            "heroic visual of", "dramatic cinematic scene of", "kinetic action shot depicting",
            "atmospheric panorama showcasing", "expressive close-up capturing", "powerful composition showing"
        ]
        chosen_action = actions[abs(hash(raw)) % len(actions)]
        core_text = " ".join(words[:14])
        return f"{chosen_action} {core_text}"

    def save_prompts(self, prompts: List[Dict[str, Any]], output_path: str):
        """Save prompt sequence to JSON file."""
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(prompts, f, indent=2, ensure_ascii=False)
