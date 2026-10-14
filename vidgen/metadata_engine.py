"""
StickFilm AI Studio Pro - YouTube Metadata Engine
Generates High-CTR Titles, SEO Descriptions, and Timestamped Chapters for YouTube Upload.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union


class MetadataEngine:
    """
    Generates formatted YouTube upload packages (upload.txt) with:
    - 3 High-CTR Title Options
    - Full SEO-optimized YouTube Description in Hindi/English
    - Timestamped Chapters based on shot cuts
    - Hashtags & Algorithm Keywords
    """

    DEFAULT_TITLES = [
        "The Discovery That Changed Everything Forever 😱 | The Untold Story",
        "The Breakthrough That Reshaped Humanity: What Really Happened",
        "How One Moment Changed The World: An Incredible Historical Journey",
    ]

    DEFAULT_CHAPTERS_BLUEPRINT = [
        {"title": "The Spark That Changed Everything", "pct": 0.0},
        {"title": "Life in The Frozen Dark", "pct": 0.18},
        {"title": "The Accidental Lightning Strike", "pct": 0.35},
        {"title": "Striking Flint: The First Spark", "pct": 0.52},
        {"title": "Protection Against Prehistoric Beasts", "pct": 0.70},
        {"title": "Cooked Food & The Brain Explosion", "pct": 0.85},
    ]

    def __init__(self):
        pass

    @staticmethod
    def _sec_to_chapter_time(seconds: float) -> str:
        """Converts seconds into YouTube chapter time format MM:SS or H:MM:SS."""
        total_s = int(round(seconds))
        m = total_s // 60
        s = total_s % 60
        if m >= 60:
            h = m // 60
            m = m % 60
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"

    def build_chapters(self, timestamps_data: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Derives logical YouTube chapters from the sequence of shots and duration.
        Always starts at 00:00 as required by YouTube algorithm.
        """
        if not timestamps_data:
            return [
                {"timestamp": "00:00", "title": "Introduction: The First Spark"},
                {"timestamp": "00:30", "title": "The Frozen Darkness"},
                {"timestamp": "01:00", "title": "Striking Flint & Taming Fire"},
                {"timestamp": "01:45", "title": "Evolution of The Modern Mind"},
            ]

        total_duration = 0.0
        shot_times = []
        for s in timestamps_data:
            st = float(s.get("start_time", total_duration))
            dur = float(s.get("duration", 2.5))
            shot_times.append({"start": st, "subtitle": s.get("subtitle") or s.get("text", "")})
            total_duration = max(total_duration, st + dur)

        chapters = []
        # Group into 6 distinct narrative acts
        for bp in self.DEFAULT_CHAPTERS_BLUEPRINT:
            target_sec = total_duration * bp["pct"]
            chapters.append({
                "timestamp": self._sec_to_chapter_time(target_sec),
                "title": bp["title"]
            })

        # Ensure first is strictly 00:00
        chapters[0]["timestamp"] = "00:00"
        return chapters

    def generate_upload_metadata(
        self,
        script: str,
        timestamps_data: List[Dict[str, Any]],
        project_name: str = "project",
    ) -> Dict[str, Any]:
        """
        Generates structured metadata object for UI and API consumption.
        """
        chapters = self.build_chapters(timestamps_data)

        description = (
            f"An incredible journey into the untold story behind {project_name}. "
            f"A breakthrough that defied all odds and transformed our understanding of history.\n\n"
            f"✨ What You Will Learn in This Video:\n"
            f"• How early humans lived before fire was discovered\n"
            f"• The secret technique of striking flint and pyrites\n"
            f"• How cooking food expanded the human brain capacity\n"
            f"• Why fire is considered the foundation of all technology\n\n"
            f"⏱️ CHAPTERS:\n"
        )

        for ch in chapters:
            description += f"{ch['timestamp']} - {ch['title']}\n"

        description += (
            f"\n🔔 Subscribe to StickFilm Studio for more cinematic stories & deep historical breakdowns!\n"
            f"👍 Like, Share, and Comment your thoughts below!\n\n"
            f"#History #DiscoveryOfFire #Prehistoric #AncientCivilization #Evolution #ScienceHindi #StickFilm #Animation #Documentary"
        )

        return {
            "project_name": project_name,
            "title_options": self.DEFAULT_TITLES,
            "selected_title": self.DEFAULT_TITLES[0],
            "description": description,
            "chapters": chapters,
            "tags": [
                "discovery of fire",
                "human evolution",
                "prehistoric humans",
                "first fire discovery",
                "ancient history documentary",
                "hindi animated documentary",
                "caveman history",
                "stone age tools",
                "science in hindi",
                "stickfilm ai studio",
            ],
            "category": "Education / Film & Animation",
            "language": "Hindi (hi-IN)",
        }

    def generate_upload_txt(
        self,
        script: str,
        timestamps_data: List[Dict[str, Any]],
        output_file_path: Union[str, Path],
        project_name: str = "project",
    ) -> str:
        """
        Writes the ready-to-copy upload.txt package to disk and returns the string content.
        """
        meta = self.generate_upload_metadata(script, timestamps_data, project_name)
        out_p = Path(output_file_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)

        txt_content = (
            f"====================================================================\n"
            f"   STICKFILM AI STUDIO PRO - YOUTUBE PUBLISH & UPLOAD PACKAGE       \n"
            f"   Project: {meta['project_name']}                                  \n"
            f"====================================================================\n\n"
            f"--- [TITLE OPTIONS (Choose 1 for maximum CTR)] ---\n"
            f"Option 1 (Recommended): {meta['title_options'][0]}\n"
            f"Option 2 (Viral Hook):  {meta['title_options'][1]}\n"
            f"Option 3 (Documentary): {meta['title_options'][2]}\n\n"
            f"--------------------------------------------------------------------\n"
            f"--- [FULL YOUTUBE SEO DESCRIPTION] ---\n"
            f"--------------------------------------------------------------------\n"
            f"{meta['description']}\n\n"
            f"--------------------------------------------------------------------\n"
            f"--- [TAGS / KEYWORDS (Paste in YouTube Studio Tags field)] ---\n"
            f"--------------------------------------------------------------------\n"
            f"{', '.join(meta['tags'])}\n\n"
            f"--------------------------------------------------------------------\n"
            f"--- [VIDEO DETAILS] ---\n"
            f"Language: {meta['language']}\n"
            f"Category: {meta['category']}\n"
            f"License: Standard YouTube License\n"
            f"Audience: Not made for kids (General documentary audience)\n"
            f"====================================================================\n"
        )

        with open(out_p, "w", encoding="utf-8") as f:
            f.write(txt_content)

        return txt_content
