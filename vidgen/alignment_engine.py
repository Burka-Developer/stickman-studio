"""
StickFilm AI Studio Pro - Alignment Engine
Speech-to-text alignment, dynamic visual shot segmentation (2.0s - 3.5s),
and millisecond word-level timestamps for karaoke captioning.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple


class AlignmentEngine:
    """
    Handles script-to-audio synchronization, shot chunking,
    word-level timecoding, and subtitle formatting (ASS / SRT).
    """

    def __init__(
        self,
        min_shot_duration: float = 1.8,
        max_shot_duration: float = 3.8,
        target_shot_duration: float = 2.6
    ):
        self.min_shot_duration = min_shot_duration
        self.max_shot_duration = max_shot_duration
        self.target_shot_duration = target_shot_duration

    def align_and_chunk(
        self,
        script_text: str,
        total_audio_duration: float,
        raw_word_boundaries: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Aligns script text against audio duration or raw word events,
        then segments into dynamic visual shots (2.0s - 3.5s target).
        """
        script_text = script_text.strip()
        if not script_text:
            return {"total_duration": total_audio_duration, "shots": [], "words": []}

        # 1. Clean script into words and punctuation
        words = self._extract_clean_words(script_text)
        if not words:
            return {"total_duration": total_audio_duration, "shots": [], "words": []}

        # 2. Build or refine word-level timestamps
        timed_words = self._resolve_word_timestamps(
            words=words,
            total_duration=total_audio_duration,
            raw_boundaries=raw_word_boundaries
        )

        # 3. Segment into visual shots based on speech cadence & punctuation
        shots = self._segment_shots(timed_words, total_audio_duration)

        return {
            "total_duration": round(total_audio_duration, 3),
            "shot_count": len(shots),
            "shots": shots,
            "words": timed_words
        }

    def _extract_clean_words(self, script_text: str) -> List[Dict[str, Any]]:
        """
        Extracts words while preserving trailing punctuation for pause estimation.
        """
        raw_tokens = script_text.split()
        words = []
        for i, token in enumerate(raw_tokens):
            clean = re.sub(r'^[^\w\u0900-\u097F]+|[^\w\u0900-\u097F]+$', '', token)
            has_comma = bool(re.search(r'[,;:\-—]', token))
            has_period = bool(re.search(r'[.!?।]', token))
            words.append({
                "index": i,
                "text": token,
                "clean": clean if clean else token,
                "has_comma": has_comma,
                "has_period": has_period,
                "char_length": max(1, len(clean or token))
            })
        return words

    def _resolve_word_timestamps(
        self,
        words: List[Dict[str, Any]],
        total_duration: float,
        raw_boundaries: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Computes accurate start/end timestamps for each word.
        If raw boundaries from Edge-TTS exist, map them. Otherwise, compute
        weighted acoustic proportional distribution with pause inflation.
        """
        if raw_boundaries and len(raw_boundaries) >= len(words) * 0.7:
            # Map raw boundaries matching word count
            timed_words = []
            rb_len = len(raw_boundaries)
            for i, w in enumerate(words):
                rb_idx = min(i, rb_len - 1)
                rb = raw_boundaries[rb_idx]
                start = float(rb.get("start", 0.0))
                end = float(rb.get("end", start + 0.3))
                # Ensure monotonicity
                if timed_words and start < timed_words[-1]["end"]:
                    start = timed_words[-1]["end"]
                if end <= start:
                    end = start + 0.25
                timed_words.append({
                    "word": w["text"],
                    "clean": w["clean"],
                    "start": round(start, 3),
                    "end": round(min(total_duration, end), 3),
                    "duration": round(max(0.08, end - start), 3),
                    "has_comma": w["has_comma"],
                    "has_period": w["has_period"]
                })
            # Adjust final word to end cleanly near total_duration
            if timed_words and timed_words[-1]["end"] < total_duration * 0.95:
                timed_words[-1]["end"] = round(total_duration, 3)
                timed_words[-1]["duration"] = round(timed_words[-1]["end"] - timed_words[-1]["start"], 3)
            return timed_words

        # Weighted proportional distribution
        weights = []
        for w in words:
            # Syllable / char weight
            wt = w["char_length"] * 1.0
            if w["has_comma"]:
                wt += 3.5  # comma pause weight
            elif w["has_period"]:
                wt += 6.0  # sentence terminal pause weight
            weights.append(wt)

        total_weight = sum(weights) if weights else 1.0
        time_per_weight = max(0.01, total_duration / total_weight)

        curr_time = 0.0
        timed_words = []
        for i, w in enumerate(words):
            wt = weights[i]
            dur = max(0.12, wt * time_per_weight)
            # Add pause cushion
            pause = 0.0
            if w["has_comma"]:
                pause = min(0.25, dur * 0.2)
            elif w["has_period"]:
                pause = min(0.45, dur * 0.3)

            w_start = curr_time
            w_end = min(total_duration, curr_time + (dur - pause))
            if w_end <= w_start:
                w_end = w_start + 0.1
            curr_time += dur

            timed_words.append({
                "word": w["text"],
                "clean": w["clean"],
                "start": round(w_start, 3),
                "end": round(w_end, 3),
                "duration": round(w_end - w_start, 3),
                "has_comma": w["has_comma"],
                "has_period": w["has_period"]
            })

        # Ensure last word reaches total_duration
        if timed_words:
            timed_words[-1]["end"] = round(total_duration, 3)
            timed_words[-1]["duration"] = round(timed_words[-1]["end"] - timed_words[-1]["start"], 3)

        return timed_words

    def _segment_shots(
        self,
        timed_words: List[Dict[str, Any]],
        total_duration: float
    ) -> List[Dict[str, Any]]:
        """
        Segments timed words into dynamic visual shots averaging 2.0s - 3.5s.
        Splits at sentence breaks (. ! ?) or clause pauses (, ; -) when duration allows.
        """
        shots: List[Dict[str, Any]] = []
        if not timed_words:
            return shots

        current_words: List[Dict[str, Any]] = []
        shot_id = 1

        for i, w in enumerate(timed_words):
            current_words.append(w)
            shot_start = current_words[0]["start"]
            shot_end = w["end"]
            curr_dur = shot_end - shot_start

            is_last_word = (i == len(timed_words) - 1)
            is_period = w.get("has_period", False)
            is_comma = w.get("has_comma", False)

            # Decision to split shot:
            should_split = False

            if is_last_word:
                should_split = True
            elif curr_dur >= self.max_shot_duration:
                # Force split if exceeded maximum shot duration
                should_split = True
            elif curr_dur >= self.min_shot_duration and is_period:
                # Natural sentence boundary
                should_split = True
            elif curr_dur >= self.target_shot_duration and is_comma:
                # Clause boundary
                should_split = True

            if should_split:
                text_content = " ".join([cw["word"] for cw in current_words])
                shots.append({
                    "shot_id": shot_id,
                    "index": shot_id - 1,
                    "start_time": round(shot_start, 3),
                    "end_time": round(shot_end, 3),
                    "duration": round(max(0.5, shot_end - shot_start), 3),
                    "text": text_content,
                    "words": current_words[:]
                })
                shot_id += 1
                current_words = []

        # If any trailing words remained
        if current_words:
            if shots:
                # Merge into last shot if too short
                shots[-1]["words"].extend(current_words)
                shots[-1]["end_time"] = round(current_words[-1]["end"], 3)
                shots[-1]["duration"] = round(shots[-1]["end_time"] - shots[-1]["start_time"], 3)
                shots[-1]["text"] = " ".join([cw["word"] for cw in shots[-1]["words"]])
            else:
                shots.append({
                    "shot_id": 1,
                    "index": 0,
                    "start_time": round(current_words[0]["start"], 3),
                    "end_time": round(current_words[-1]["end"], 3),
                    "duration": round(current_words[-1]["end"] - current_words[0]["start"], 3),
                    "text": " ".join([cw["word"] for cw in current_words]),
                    "words": current_words
                })

        # Final pass: adjust shot transitions so there are zero dead gaps between consecutive visual shots
        for s_idx in range(len(shots) - 1):
            shots[s_idx]["end_time"] = shots[s_idx + 1]["start_time"]
            shots[s_idx]["duration"] = round(shots[s_idx]["end_time"] - shots[s_idx]["start_time"], 3)

        if shots:
            shots[-1]["end_time"] = round(total_duration, 3)
            shots[-1]["duration"] = round(shots[-1]["end_time"] - shots[-1]["start_time"], 3)

        return shots

    def generate_srt(self, shots: List[Dict[str, Any]]) -> str:
        """Generates standard SRT subtitles for video players."""
        lines = []
        for i, s in enumerate(shots, start=1):
            start_str = self._format_srt_time(s["start_time"])
            end_str = self._format_srt_time(s["end_time"])
            lines.append(f"{i}\n{start_str} --> {end_str}\n{s['text']}\n")
        return "\n".join(lines)

    def generate_karaoke_ass(
        self,
        shots: List[Dict[str, Any]],
        preset_style: str = "Word Highlight",
        video_width: int = 1920,
        video_height: int = 1080
    ) -> str:
        """
        Generates Advanced SubStation Alpha (.ass) format with dynamic karaoke animations
        and high-CTR YouTube typography.
        Presets: 'Word Highlight', 'Bold Comic', 'Karaoke Fill', 'Simple Green', 'Boxed', 'One Word Pop', 'Simple', 'Off'
        """
        if preset_style.lower() == "off":
            return ""

        # ASS Colors in &HAABBGGRR format
        # Gold highlight: &H002EB8F5 (RGB #f5b82e)
        # White: &H00FFFFFF
        # Green: &H0081B910 (RGB #10b981)
        # Black outline: &H00000000

        font_name = "Arial Black"
        font_size = 54 if video_height >= 1080 else 32
        margin_v = int(video_height * 0.12)  # bottom 12%

        primary_color = "&H00FFFFFF"
        highlight_color = "&H002EB8F5"  # Gold
        outline_color = "&H00000000"
        back_color = "&H80000000"
        bold = 1

        if preset_style == "Simple Green":
            primary_color = "&H00FFFFFF"
            highlight_color = "&H0081B910"
        elif preset_style == "Bold Comic":
            font_size = int(font_size * 1.15)
            highlight_color = "&H0000D0FF"  # Vivid yellow/orange
        elif preset_style == "Boxed":
            back_color = "&H00000000"

        header = f"""[Script Info]
Title: StickFilm AI Studio Pro Karaoke
ScriptType: v4.00+
PlayResX: {video_width}
PlayResY: {video_height}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size},{primary_color},{highlight_color},{outline_color},{back_color},{bold},0,0,0,100,100,1,0,1,4,2,2,40,40,{margin_v},1
Style: Highlight,{font_name},{font_size},{highlight_color},{primary_color},{outline_color},{back_color},{bold},0,0,0,100,100,1,0,1,4,2,2,40,40,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        dialogues = []

        if preset_style == "One Word Pop":
            # Display single word popping up in center screen
            for shot in shots:
                for w in shot.get("words", []):
                    s_time = self._format_ass_time(w["start"])
                    e_time = self._format_ass_time(w["end"])
                    dialogues.append(
                        f"Dialogue: 0,{s_time},{e_time},Highlight,,0,0,{int(video_height * 0.45)},,{{\\b1\\fscx115\\fscy115}}{w['word']}"
                    )
        else:
            # Word Highlight or Karaoke Fill across phrase
            for shot in shots:
                words = shot.get("words", [])
                if not words:
                    continue

                # For Word Highlight: render individual dialogues per active word so current word is gold
                for current_idx, active_word in enumerate(words):
                    w_start = self._format_ass_time(active_word["start"])
                    w_end = self._format_ass_time(active_word["end"])

                    formatted_words = []
                    for idx, w in enumerate(words):
                        if idx == current_idx:
                            # Highlighted active word in gold
                            formatted_words.append(f"{{\\c{highlight_color}\\b1}}{w['word']}{{\\c{primary_color}}}")
                        else:
                            formatted_words.append(w["word"])

                    phrase_str = " ".join(formatted_words)
                    dialogues.append(f"Dialogue: 0,{w_start},{w_end},Default,,0,0,{margin_v},,{phrase_str}")

        return header + "\n".join(dialogues) + "\n"

    def _format_srt_time(self, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int(round((seconds - int(seconds)) * 1000))
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def _format_ass_time(self, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centis = int(round((seconds - int(seconds)) * 100))
        if centis >= 100:
            centis = 99
        return f"{hours:01d}:{minutes:02d}:{secs:02d}.{centis:02d}"

    def save_timestamps(self, alignment_result: Dict[str, Any], output_path: str):
        """Save timestamps result to JSON file."""
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(alignment_result, f, indent=2, ensure_ascii=False)
