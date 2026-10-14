"""
StickFilm AI Studio Pro - Video Renderer Engine
Master FFmpeg Video Renderer with Dynamic Camera Motions,
Animated Subtitle Overlay Engine (7 Styles), Audio Ducking & Muxing.
"""

import os
import sys
import json
import math
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union

from PIL import Image


class VideoRenderer:
    """
    Master 1080p Full HD Video Renderer for StickFilm AI Studio Pro.
    Integrates dynamic camera motions, word-highlighted karaoke captions,
    and ducked audio-video muxing.
    """

    CAPTION_STYLES = [
        "Word Highlight",
        "Bold Comic",
        "Simple Green",
        "Karaoke Fill",
        "Boxed",
        "One Word Pop",
        "Simple",
    ]

    CAMERA_MOTIONS = [
        "Ken Burns",
        "Slow zoom in",
        "Slow zoom out",
        "Pan left",
        "Pan right",
        "Drone rise",
        "Crash zoom",
        "No motion",
        "Mix of all",
    ]

    def __init__(self, ffmpeg_bin: str = "ffmpeg"):
        self.ffmpeg_bin = ffmpeg_bin
        self._verify_ffmpeg()

    def _verify_ffmpeg(self) -> bool:
        """Verifies if ffmpeg is accessible in the system path."""
        try:
            res = subprocess.run([self.ffmpeg_bin, "-version"], capture_output=True, text=True)
            return res.returncode == 0
        except Exception:
            return False

    # -------------------------------------------------------------------------
    # Timecode Helpers
    # -------------------------------------------------------------------------
    @staticmethod
    def _sec_to_ass_time(seconds: float) -> str:
        """Converts floating point seconds to ASS timestamp format: H:MM:SS.cs"""
        total_cs = int(round(seconds * 100))
        cs = total_cs % 100
        total_s = total_cs // 100
        s = total_s % 60
        total_m = total_s // 60
        m = total_m % 60
        h = total_m // 60
        return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

    # -------------------------------------------------------------------------
    # Subtitle Overlay Generator (7 Caption Styles)
    # -------------------------------------------------------------------------
    def generate_ass_subtitles(
        self,
        timestamps_data: List[Dict[str, Any]],
        output_ass_path: Union[str, Path],
        caption_style: str = "Word Highlight",
        aspect_ratio: str = "16:9",
    ) -> Path:
        """
        Generates an Advanced SubStation Alpha (.ass) subtitle file supporting all 7 caption styles:
        - Word Highlight: Active word highlighted in bold gold (&H002EB8F5&)
        - Bold Comic: Comic font with heavy black outline and bright yellow fill (&H0000E6FF&)
        - Simple Green: Crisp minimalist green (&H0081B910&)
        - Karaoke Fill: Color wipe across active words
        - Boxed: Dark rounded container (&H400F1118&) behind subtitle
        - One Word Pop: Large centered single word pop
        - Simple: Standard clean white text with drop shadow
        """
        out_p = Path(output_ass_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)

        res_x = 1080 if aspect_ratio == "9:16" else 1920
        res_y = 1920 if aspect_ratio == "9:16" else 1080
        font_name = "Nirmala UI"

        # Style definition parameters
        font_size = 56 if aspect_ratio == "16:9" else 68
        bold_flag = 1
        border_style = 1  # 1 = outline + shadow, 3 = opaque box
        outline_size = 3
        shadow_size = 2
        margin_v = 75 if aspect_ratio == "16:9" else 220
        alignment = 2  # 2 = bottom-center, 5 = middle-center

        # Color codes in ASS BGR format (&HAABBGGRR&)
        gold_color = "&H002EB8F5&"       # #f5b82e
        white_color = "&H00FFFFFF&"      # #ffffff
        yellow_color = "&H0000E6FF&"     # #ffe600
        green_color = "&H0081B910&"      # #10b981
        black_color = "&H00000000&"      # #000000
        box_bg_color = "&H50120F0D&"     # Dark obsidian semi-transparent box
        shadow_color = "&H80000000&"

        pri_color = white_color
        sec_color = gold_color

        if caption_style == "Bold Comic":
            font_size = 64 if aspect_ratio == "16:9" else 76
            pri_color = yellow_color
            sec_color = white_color
            outline_size = 5
            shadow_size = 3
        elif caption_style == "Simple Green":
            pri_color = green_color
            sec_color = white_color
            outline_size = 2
            shadow_size = 1
        elif caption_style == "Boxed":
            border_style = 3
            outline_size = 12
            shadow_size = 0
            pri_color = white_color
            sec_color = gold_color
            shadow_color = box_bg_color
        elif caption_style == "One Word Pop":
            font_size = 78 if aspect_ratio == "16:9" else 92
            alignment = 5  # center
            pri_color = gold_color
            outline_size = 4
            shadow_size = 3
        elif caption_style == "Simple":
            outline_size = 2
            shadow_size = 1
            pri_color = white_color

        ass_header = f"""[Script Info]
Title: StickFilm AI Studio Pro Subtitles
ScriptType: v4.00+
PlayResX: {res_x}
PlayResY: {res_y}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: MainStyle,{font_name},{font_size},{pri_color},{sec_color},{black_color},{shadow_color},{bold_flag},0,0,0,100,100,0,0,{border_style},{outline_size},{shadow_size},{alignment},40,40,{margin_v},1
Style: PopStyle,{font_name},{font_size + 16},{gold_color},{white_color},{black_color},{shadow_color},1,0,0,0,105,105,0,0,1,5,3,5,40,40,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        dialogue_lines = []

        for item in timestamps_data:
            start_s = float(item.get("start_time", 0.0))
            end_s = float(item.get("end_time", start_s + float(item.get("duration", 2.5))))
            if end_s <= start_s:
                end_s = start_s + 2.0

            text = str(item.get("subtitle") or item.get("text") or item.get("script") or "").strip()
            if not text:
                continue

            words = text.split()
            if not words:
                continue

            # Word-level breakdown
            word_timestamps = item.get("words", [])
            total_duration = end_s - start_s
            num_words = len(words)

            if caption_style == "One Word Pop":
                # Single word pop sequentially
                word_dur = total_duration / max(1, num_words)
                for w_i, word in enumerate(words):
                    w_start = start_s + w_i * word_dur
                    w_end = min(end_s, w_start + word_dur)
                    t_start = self._sec_to_ass_time(w_start)
                    t_end = self._sec_to_ass_time(w_end)
                    dialogue_lines.append(
                        f"Dialogue: 0,{t_start},{t_end},PopStyle,,0,0,0,,{word}"
                    )
            elif caption_style in ["Word Highlight", "Karaoke Fill"]:
                # Generates active karaoke word highlighted in bold gold
                word_dur = total_duration / max(1, num_words)
                for w_i in range(num_words):
                    w_start = start_s + w_i * word_dur
                    w_end = min(end_s, w_start + word_dur)
                    t_start = self._sec_to_ass_time(w_start)
                    t_end = self._sec_to_ass_time(w_end)

                    highlighted_tokens = []
                    for k_idx, kw in enumerate(words):
                        if k_idx == w_i:
                            # Highlight active word with gold override
                            highlighted_tokens.append(f"{{\\c{gold_color}\\b1}}{kw}{{\\c{white_color}\\b0}}")
                        else:
                            highlighted_tokens.append(kw)

                    display_str = " ".join(highlighted_tokens)
                    dialogue_lines.append(
                        f"Dialogue: 0,{t_start},{t_end},MainStyle,,0,0,0,,{display_str}"
                    )
            elif caption_style == "Bold Comic":
                # Comic styling, uppercase punch with yellow fill
                t_start = self._sec_to_ass_time(start_s)
                t_end = self._sec_to_ass_time(end_s)
                dialogue_lines.append(
                    f"Dialogue: 0,{t_start},{t_end},MainStyle,,0,0,0,,{{\\c{yellow_color}}}{text.upper()}"
                )
            elif caption_style == "Simple Green":
                t_start = self._sec_to_ass_time(start_s)
                t_end = self._sec_to_ass_time(end_s)
                dialogue_lines.append(
                    f"Dialogue: 0,{t_start},{t_end},MainStyle,,0,0,0,,{{\\c{green_color}}}{text}"
                )
            else:
                # Simple or Boxed
                t_start = self._sec_to_ass_time(start_s)
                t_end = self._sec_to_ass_time(end_s)
                dialogue_lines.append(
                    f"Dialogue: 0,{t_start},{t_end},MainStyle,,0,0,0,,{text}"
                )

        full_ass = ass_header + "\n".join(dialogue_lines) + "\n"
        with open(out_p, "w", encoding="utf-8") as f:
            f.write(full_ass)

        return out_p

    # -------------------------------------------------------------------------
    # Camera Motion Filter Builder
    # -------------------------------------------------------------------------
    @staticmethod
    def get_camera_motion_filter(
        motion: str,
        duration_sec: float,
        width: int = 1920,
        height: int = 1080,
        fps: int = 30,
        shot_index: int = 1,
    ) -> str:
        """
        Builds the FFmpeg zoompan filter expression for the specified camera motion:
        - Ken Burns: Slow zoom in + drift
        - Slow zoom in: Centered zoom in
        - Slow zoom out: Centered zoom out
        - Pan left / right: Horizontal tracking
        - Drone rise: Vertical ascent
        - Crash zoom: Dynamic punch
        - No motion: Static hold
        """
        total_frames = int(max(1, duration_sec * fps))

        if motion == "Mix of all":
            styles = ["Ken Burns", "Slow zoom in", "Pan right", "Slow zoom out", "Drone rise", "Pan left", "Crash zoom"]
            motion = styles[(shot_index - 1) % len(styles)]

        if motion == "Slow zoom in":
            # Zooms from 1.0 to 1.15 centered
            step = 0.15 / max(1, total_frames)
            return f"zoompan=z='min(zoom+{step:.5f},1.15)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"

        elif motion == "Slow zoom out":
            # Zooms from 1.15 down to 1.0 centered
            step = 0.15 / max(1, total_frames)
            return f"zoompan=z='if(lte(zoom,1.0),1.15,max(1.001,zoom-{step:.5f}))':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"

        elif motion == "Pan left":
            # Pan from right towards left with subtle 1.12 zoom
            return f"zoompan=z=1.12:d={total_frames}:x='(1-on/{total_frames})*(iw-iw/zoom)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"

        elif motion == "Pan right":
            # Pan from left towards right with subtle 1.12 zoom
            return f"zoompan=z=1.12:d={total_frames}:x='(on/{total_frames})*(iw-iw/zoom)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"

        elif motion == "Drone rise":
            # Vertical pan upwards from bottom with gentle zoom
            return f"zoompan=z='min(zoom+0.0005,1.10)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='(1-on/{total_frames})*(ih-ih/zoom)':s={width}x{height}:fps={fps}"

        elif motion == "Crash zoom":
            # Fast punch zoom in first 15 frames, then holds
            return f"zoompan=z='min(1.0+on*0.015,1.25)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"

        elif motion == "No motion":
            return f"scale={width}:{height},fps={fps}"

        else:
            # Default: Ken Burns (Slow zoom + gentle drift)
            step = 0.14 / max(1, total_frames)
            return f"zoompan=z='min(zoom+{step:.5f},1.14)':d={total_frames}:x='(on/{total_frames})*(iw-iw/zoom)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"

    # -------------------------------------------------------------------------
    # Audio Sync & Music Ducking
    # -------------------------------------------------------------------------
    def mix_audio_with_ducking(
        self,
        voiceover_path: Union[str, Path],
        bg_music_path: Optional[Union[str, Path]],
        output_audio_path: Union[str, Path],
        duration_sec: float,
        duck_volume: float = 0.18,
    ) -> Path:
        """
        Mixes voiceover narration with background music.
        Background music is ducked (reduced to ~18% volume) so voiceover is crisp and clear.
        """
        out_p = Path(output_audio_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        v_p = Path(voiceover_path)

        if not v_p.exists() or v_p.stat().st_size == 0:
            # Generate clean silent audio track
            cmd = [
                self.ffmpeg_bin, "-y",
                "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo",
                "-t", str(duration_sec),
                "-c:a", "aac", "-b:a", "192k",
                str(out_p)
            ]
            subprocess.run(cmd, capture_output=True, check=True)
            return out_p

        if not bg_music_path or not Path(bg_music_path).exists():
            # Only voiceover needed, copy / re-encode
            shutil.copy2(v_p, out_p)
            return out_p

        # Mux voiceover and ducked background music using FFmpeg amix filter
        bg_p = Path(bg_music_path)
        cmd = [
            self.ffmpeg_bin, "-y",
            "-i", str(v_p),
            "-stream_loop", "-1", "-i", str(bg_p),
            "-filter_complex",
            f"[0:a]volume=1.0[voice];[1:a]volume={duck_volume},afade=t=out:st={max(0, duration_sec - 3)}:d=3[music];[voice][music]amix=inputs=2:duration=first:dropout_transition=2[aout]",
            "-map", "[aout]",
            "-c:a", "aac", "-b:a", "320k",
            str(out_p)
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            # Fallback to voiceover if mix fails
            shutil.copy2(v_p, out_p)

        return out_p

    # -------------------------------------------------------------------------
    # Master Video Rendering Pipeline
    # -------------------------------------------------------------------------
    def render_master_video(
        self,
        project_dir: Union[str, Path],
        output_mp4_path: Union[str, Path],
        motion: str = "Ken Burns",
        caption_style: str = "Word Highlight",
        aspect_ratio: str = "16:9",
        fps: int = 30,
        progress_callback=None,
    ) -> Path:
        """
        Executes Full HD master rendering:
        1. Compiles shot images with animated camera motion.
        2. Overlays synchronized karaoke subtitles with active word highlight.
        3. Muxes voiceover narration with ducked background music.
        """
        proj_dir = Path(project_dir)
        out_mp4 = Path(output_mp4_path)
        out_mp4.parent.mkdir(parents=True, exist_ok=True)

        shots_dir = proj_dir / "shots"
        timestamps_file = proj_dir / "timestamps.json"
        voiceover_file = proj_dir / "voiceover.mp3"
        bg_music_file = proj_dir / "bg_music.mp3"

        width = 1080 if aspect_ratio == "9:16" else 1920
        height = 1920 if aspect_ratio == "9:16" else 1080

        # Load timestamps data
        timestamps = []
        if timestamps_file.exists():
            with open(timestamps_file, "r", encoding="utf-8") as f:
                timestamps = json.load(f)

        if not timestamps:
            raise ValueError(f"Timestamps file {timestamps_file} is empty or missing.")

        total_shots = len(timestamps)

        # Temporary work folder for render segments
        tmp_dir = proj_dir / ".render_tmp"
        tmp_dir.mkdir(parents=True, exist_ok=True)

        # 1. Render camera motion video clips for each shot
        clip_paths = []
        total_duration = 0.0

        for idx, shot in enumerate(timestamps, 1):
            s_dur = float(shot.get("duration", 2.5))
            if s_dur <= 0.2:
                s_dur = 2.5
            total_duration += s_dur

            # Locate shot image
            cand1 = shots_dir / f"shot_{idx:03d}.png"
            cand2 = shots_dir / f"{idx}.png"
            img_path = cand1 if cand1.exists() else cand2

            if not img_path.exists():
                raise FileNotFoundError(f"Missing shot image for shot #{idx}: {cand1}")

            clip_out = tmp_dir / f"clip_{idx:03d}.mp4"
            motion_filter = self.get_camera_motion_filter(
                motion=motion,
                duration_sec=s_dur,
                width=width,
                height=height,
                fps=fps,
                shot_index=idx,
            )

            # Generate individual shot clip
            cmd_clip = [
                self.ffmpeg_bin, "-y",
                "-loop", "1", "-i", str(img_path),
                "-t", f"{s_dur:.3f}",
                "-vf", motion_filter,
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "ultrafast",
                str(clip_out)
            ]
            res = subprocess.run(cmd_clip, capture_output=True, text=True)
            if res.returncode != 0:
                raise RuntimeError(f"FFmpeg failed rendering clip {idx}: {res.stderr}")

            clip_paths.append(clip_out)
            if progress_callback:
                progress_callback("clips", idx, total_shots)

        # 2. Concat all shot clips together
        concat_list_file = tmp_dir / "concat_list.txt"
        with open(concat_list_file, "w", encoding="utf-8") as f:
            for cp in clip_paths:
                f.write(f"file '{cp.name}'\n")

        raw_visual_video = tmp_dir / "raw_visual.mp4"
        cmd_concat = [
            self.ffmpeg_bin, "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_list_file),
            "-c", "copy",
            str(raw_visual_video)
        ]
        res_cat = subprocess.run(cmd_concat, capture_output=True, text=True)
        if res_cat.returncode != 0:
            raise RuntimeError(f"FFmpeg concat failed: {res_cat.stderr}")

        # 3. Generate ASS Subtitles
        ass_path = tmp_dir / "subtitles.ass"
        self.generate_ass_subtitles(
            timestamps_data=timestamps,
            output_ass_path=ass_path,
            caption_style=caption_style,
            aspect_ratio=aspect_ratio,
        )

        # 4. Mix Voiceover + Ducked Background Music
        final_audio_path = tmp_dir / "final_audio.aac"
        self.mix_audio_with_ducking(
            voiceover_path=voiceover_file,
            bg_music_path=bg_music_file if bg_music_file.exists() else None,
            output_audio_path=final_audio_path,
            duration_sec=total_duration,
        )

        # 5. Burn in ASS Subtitles and Mux Final Audio into 1080p Master MP4
        # Windows path escaping for libass filter: forward slashes and escaped colon
        ass_filter_path = str(ass_path).replace("\\", "/").replace(":", "\\:")
        video_filters = f"ass='{ass_filter_path}'" if caption_style != "Off" else "null"

        cmd_master = [
            self.ffmpeg_bin, "-y",
            "-i", str(raw_visual_video),
            "-i", str(final_audio_path),
            "-vf", video_filters,
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "18",
            "-c:a", "aac", "-b:a", "320k",
            "-shortest",
            str(out_mp4)
        ]
        res_master = subprocess.run(cmd_master, capture_output=True, text=True)
        if res_master.returncode != 0:
            # If libass font path had issues, fallback to render without ass filter
            cmd_fallback = [
                self.ffmpeg_bin, "-y",
                "-i", str(raw_visual_video),
                "-i", str(final_audio_path),
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast",
                "-c:a", "aac", "-b:a", "320k",
                "-shortest",
                str(out_mp4)
            ]
            subprocess.run(cmd_fallback, capture_output=True, check=True)

        # Cleanup temporary files
        try:
            shutil.rmtree(tmp_dir, ignore_errors=True)
        except Exception:
            pass

        return out_mp4
