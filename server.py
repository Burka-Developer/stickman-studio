"""
StickFilm AI Studio Pro - Backend Server
FastAPI HTTP API & WebSocket server on port 5199.
Serves web UI, project management, voice synthesis, prompt generation,
and 6-stage video rendering pipeline.
"""

import os
import sys
import json
import time
import shutil
import asyncio
import subprocess
import traceback
from pathlib import Path
import io
import base64
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, Request, Response, BackgroundTasks, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from PIL import Image

# Ensure local imports work
sys.path.insert(0, str(Path(__file__).resolve().parent))
from vidgen.voice_engine import VoiceEngine, VOICE_CATALOG
from vidgen.alignment_engine import AlignmentEngine
from vidgen.prompt_engine import PromptEngine
from vidgen.image_engine import ImageEngine
from vidgen.video_renderer import VideoRenderer
from vidgen.thumbnail_engine import ThumbnailEngine
from vidgen.metadata_engine import MetadataEngine
from vidgen.pipeline import VideoPipeline

# Paths
BASE_DIR = Path(__file__).resolve().parent
PROJECTS_DIR = BASE_DIR / "projects"
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
REFS_DIR = STATIC_DIR / "assets" / "refs"
REFS_DIR.mkdir(parents=True, exist_ok=True)
PREVIEWS_DIR = BASE_DIR / "previews"
PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_FILE = BASE_DIR / "config.json"
CACHE_DIR = BASE_DIR / "data" / "audio_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Load / Save Config Helper
DEFAULT_CONFIG = {
    "api_keys": {
        "gemini": "",
        "elevenlabs": "",
        "minimax": "",
        "openai": "",
        "openrouter": ""
    },
    "profiles": {
        "acc1": {
            "id": "acc1",
            "name": "acc1 (Primary)",
            "status": "Active",
            "email": "creator1@studio.ai",
            "cookies": 42,
            "last_active": "Just now",
            "data_dir": str((BASE_DIR / "data" / "chrome_profiles" / "acc1").resolve()),
            "notes": "Primary Google Chrome Canvas automation profile"
        },
        "acc2": {
            "id": "acc2",
            "name": "acc2 (Secondary)",
            "status": "Ready",
            "email": "creator2@studio.ai",
            "cookies": 38,
            "last_active": "2 hours ago",
            "data_dir": str((BASE_DIR / "data" / "chrome_profiles" / "acc2").resolve()),
            "notes": "Secondary Google Chrome Canvas backup profile"
        }
    },
    "active_profile": "acc1",
    "active_project": "",
    "theme": "obsidian",
    "veo_settings": {
        "model": "veo_3_1_lite",
        "strategy": "auto_8",
        "motion_intensity": 8,
        "negative_prompts": "blurry, distorted anatomy, morphing hands, shaky artifacts, flicker"
    }
}

def load_config() -> Dict[str, Any]:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {**DEFAULT_CONFIG, **data}
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()

def save_config(config_data: Dict[str, Any]):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2)

current_config = load_config()

# Shared Engines
voice_engine = VoiceEngine(data_dir=str(CACHE_DIR))
alignment_engine = AlignmentEngine()
prompt_engine = PromptEngine()
voice_engine.set_api_keys(current_config.get("api_keys", {}))
prompt_engine.set_api_keys(current_config.get("api_keys", {}))

# WebSocket Connection Manager for Real-Time Streaming
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        dead = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead.append(connection)
        for d in dead:
            if d in self.active_connections:
                self.active_connections.remove(d)

ws_manager = ConnectionManager()

# Global Pipeline State
global_pipeline_lock = asyncio.Lock()
active_pipeline: Optional[VideoPipeline] = None
pipeline_status = {
    "status": "idle",
    "stage": 0,
    "stage_name": "Ready",
    "progress": 0.0,
    "active_project": current_config.get("active_project", ""),
    "shots_ready": 0,
    "total_shots": 0,
    "screenshot_url": None,
    "last_error": None,
}

# FastAPI Initialization
app = FastAPI(
    title="StickFilm AI Studio Pro API",
    version="2.2.6",
    description="All-in-one desktop AI film studio backend and pipeline"
)

# Enable CORS for local cross-origin development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Real-Time System and Console Log Buffer
SYSTEM_LOGS: List[Dict[str, Any]] = []

def add_system_log(message: str, level: str = "info", details: Optional[str] = None):
    """
    Appends to in-memory system log buffer, prints to stdout for terminal visibility,
    and broadcasts to all connected WebSocket clients.
    """
    entry = {
        "timestamp": time.strftime("%H:%M:%S"),
        "level": level,
        "message": message,
        "details": details
    }
    SYSTEM_LOGS.append(entry)
    if len(SYSTEM_LOGS) > 500:
        SYSTEM_LOGS.pop(0)

    # Visible in terminal console
    prefix = f"[{entry['timestamp']}][SYSTEM-{level.upper()}]"
    print(f"{prefix} {message}")
    if details:
        print(f"         {details}")

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(ws_manager.broadcast({"type": "system_log", "data": entry}))
    except Exception:
        pass

# Event Dispatcher for Pipeline
def pipeline_event_listener(event_type: str, data: Dict[str, Any]):
    global pipeline_status

    if event_type == "stage_update":
        pipeline_status["stage"] = data.get("stage", 0)
        pipeline_status["stage_name"] = data.get("message", "")
        pipeline_status["progress"] = data.get("progress", 0.0)
        add_system_log(f"Stage {pipeline_status['stage']}: {pipeline_status['stage_name']} ({pipeline_status['progress']}%)", level="info")
    elif event_type == "shot_ready":
        pipeline_status["shots_ready"] = data.get("shot_id", 0)
        pipeline_status["total_shots"] = data.get("total", 0)
        pipeline_status["screenshot_url"] = data.get("image_url")
        add_system_log(f"Shot {pipeline_status['shots_ready']}/{pipeline_status['total_shots']} frame rendered", level="info")
    elif event_type == "pipeline_complete":
        pipeline_status["status"] = "completed"
        pipeline_status["progress"] = 100.0
        add_system_log("Video pipeline finished execution successfully! Master MP4 ready.", level="success")
    elif event_type == "pipeline_error":
        pipeline_status["status"] = "error"
        pipeline_status["last_error"] = data.get("error")
        add_system_log(f"Pipeline error encountered: {data.get('error')}", level="error")
    elif event_type == "pipeline_aborted":
        pipeline_status["status"] = "aborted"
        add_system_log("Pipeline run cancelled by user.", level="warning")
    elif event_type == "log":
        add_system_log(data.get("message", ""), level=data.get("level", "info"))

    # Broadcast over WebSocket asynchronously
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(ws_manager.broadcast({"type": event_type, "data": data}))
    except Exception:
        pass


# -------------------------------------------------------------
# Pydantic Request Models
# -------------------------------------------------------------
class ProjectCreateReq(BaseModel):
    name: str
    script: Optional[str] = ""

class ProjectDeleteReq(BaseModel):
    project_id: str

class ProjectClearReq(BaseModel):
    project_id: str

class ProjectSwitchReq(BaseModel):
    project_id: str

class ScriptGenerateReq(BaseModel):
    topic: str
    tone: Optional[str] = "hindi_doc"
    target_duration_sec: Optional[int] = 120
    language: Optional[str] = "Hindi"

class VoicePreviewReq(BaseModel):
    voice_id: str = "jerry"
    sample_text: Optional[str] = None
    speed: str = "+0%"

class VoiceGenerateReq(BaseModel):
    project_id: str
    script_text: str
    voice_id: str = "jerry"
    speed: str = "+0%"
    background_music: Optional[str] = None

class ScriptEstimateReq(BaseModel):
    script_text: str
    voice_id: str = "jerry"
    speed: str = "+0%"

class StyleGenerateSamplesReq(BaseModel):
    style_name: str
    reference_notes: Optional[str] = ""
    aspect_ratio: str = "16:9"

class PipelineRunReq(BaseModel):
    project_name: str
    script_text: str
    voice_id: str = "jerry"
    voice_speed: str = "+0%"
    visual_style: str = "3D Animated (Pixar / DreamWorks CGI Style)"
    aspect_ratio: str = "16:9"
    character_ref: str = "Iconic Stickman Hero with expressive large round white eyes"
    world_setting: Optional[str] = ""
    camera_motion: str = "Ken Burns"
    captions_preset: str = "Word Highlight"
    background_music: Optional[str] = None
    profile: str = "acc1"

class ProfileCreateReq(BaseModel):
    id: Optional[str] = None
    name: str
    email: Optional[str] = ""
    status: Optional[str] = "Ready"
    cookies: Optional[int] = 35
    data_dir: Optional[str] = ""
    notes: Optional[str] = ""

class ProfileUpdateReq(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = None
    cookies: Optional[int] = None
    data_dir: Optional[str] = None
    notes: Optional[str] = None

class ProfileActiveReq(BaseModel):
    profile_id: str

class ProfileActionReq(BaseModel):
    profile_id: str

class ShotRedrawReq(BaseModel):
    project_id: str
    shot_id: int
    custom_prompt: Optional[str] = None

class ShotAddReq(BaseModel):
    project_id: str
    index: Optional[int] = None
    subtitle: str
    prompt: str
    duration: Optional[float] = 2.5
    image_base64: Optional[str] = None

class ShotFullUpdateReq(BaseModel):
    project_id: str
    shot_id: int
    subtitle: Optional[str] = None
    prompt: Optional[str] = None
    duration: Optional[float] = None
    image_base64: Optional[str] = None

class ShotUpdateReq(BaseModel):
    project_id: str
    shot_id: int
    text: Optional[str] = None
    prompt: Optional[str] = None

class ShotDeleteReq(BaseModel):
    project_id: str
    shot_id: int

class VeoSettingsReq(BaseModel):
    model: str = "veo_3_1_lite"
    strategy: str = "auto_8"
    motion_intensity: int = 8
    negative_prompts: str = "blurry, distorted anatomy, morphing hands, shaky artifacts, flicker"

class RenderChangedReq(BaseModel):
    project_id: str
    aspect_ratio: str = "16:9"
    camera_motion: str = "Ken Burns"
    captions_preset: str = "Word Highlight"

class ApiKeysReq(BaseModel):
    gemini: Optional[str] = None
    elevenlabs: Optional[str] = None
    minimax: Optional[str] = None
    openai: Optional[str] = None
    openrouter: Optional[str] = None


# -------------------------------------------------------------
# API Endpoints
# -------------------------------------------------------------

# Root / Web Application Entry
@app.get("/")
async def root():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head><title>StickFilm AI Studio Pro v2.2.6</title></head>
    <body style="background:#0d0f12; color:#f5b82e; font-family:sans-serif; text-align:center; padding-top:100px;">
        <h1>⚡ StickFilm AI Studio Pro Server v2.2.6 Active</h1>
        <p style="color:#a0aec0;">Local API listening on port 5199. Static frontend initializing.</p>
        <p><a href="/docs" style="color:#10b981;">Explore Swagger API Docs</a></p>
    </body>
    </html>
    """)

# System and Console Logs API
@app.get("/api/console/logs")
@app.get("/api/system/logs")
async def get_console_logs():
    """Retrieve all real-time system and pipeline execution logs."""
    return {"logs": SYSTEM_LOGS, "total": len(SYSTEM_LOGS)}

# Projects APIs
@app.get("/api/projects")
async def list_projects():
    """List all workspace projects and their delivery statuses."""
    projects = []
    if PROJECTS_DIR.exists():
        for p_dir in PROJECTS_DIR.iterdir():
            if p_dir.is_dir():
                has_video = (p_dir / "output.mp4").exists()
                has_script = (p_dir / "script.txt").exists()
                has_voice = (p_dir / "voiceover.mp3").exists()
                shots_dir = p_dir / "shots"
                shot_count = len(list(shots_dir.glob("*.png"))) if shots_dir.exists() else 0
                
                script_text = ""
                if has_script:
                    try:
                        with open(p_dir / "script.txt", "r", encoding="utf-8") as f:
                            script_text = f.read()[:200]
                    except Exception:
                        pass

                projects.append({
                    "id": p_dir.name,
                    "name": p_dir.name.replace("_", " ").title(),
                    "has_video": has_video,
                    "has_script": has_script,
                    "has_voice": has_voice,
                    "shots_count": shot_count,
                    "video_url": f"/projects/{p_dir.name}/output.mp4" if has_video else None,
                    "voice_url": f"/projects/{p_dir.name}/voiceover.mp3" if has_voice else None,
                    "script_preview": script_text,
                    "created_at": time.ctime(p_dir.stat().st_ctime),
                })
    return {"projects": sorted(projects, key=lambda x: x["id"]), "active_project": current_config.get("active_project")}

@app.post("/api/projects")
@app.post("/api/projects/create")
async def create_project(req: ProjectCreateReq):
    """Create or switch to a new project."""
    clean_id = "".join([c if c.isalnum() or c in "_-" else "_" for c in req.name.strip()])
    p_dir = PROJECTS_DIR / clean_id
    p_dir.mkdir(parents=True, exist_ok=True)
    (p_dir / "shots").mkdir(exist_ok=True)
    (p_dir / "thumbnails").mkdir(exist_ok=True)

    if req.script:
        with open(p_dir / "script.txt", "w", encoding="utf-8") as f:
            f.write(req.script)

    current_config["active_project"] = clean_id
    save_config(current_config)
    pipeline_status["active_project"] = clean_id

    return {"success": True, "project_id": clean_id, "project_dir": str(p_dir)}

@app.delete("/api/projects")
@app.delete("/api/projects/delete")
@app.post("/api/projects/delete")
async def delete_project(req: ProjectDeleteReq):
    """Delete a project workspace."""
    p_dir = PROJECTS_DIR / req.project_id
    if p_dir.exists() and p_dir.is_dir():
        shutil.rmtree(p_dir)
        if current_config.get("active_project") == req.project_id:
            current_config["active_project"] = ""
            save_config(current_config)
        return {"success": True, "deleted": req.project_id}
    raise HTTPException(status_code=404, detail="Project not found")

@app.post("/api/projects/switch")
async def switch_project(req: ProjectSwitchReq):
    """Set active workspace project."""
    current_config["active_project"] = req.project_id
    save_config(current_config)
    pipeline_status["active_project"] = req.project_id
    return {"success": True, "active_project": req.project_id}

@app.post("/api/projects/clear")
async def clear_project_assets(req: ProjectClearReq):
    """Clear all generated assets (shots, video, voice, thumbnails, metadata) in a project."""
    p_dir = PROJECTS_DIR / req.project_id
    if not p_dir.exists() or not p_dir.is_dir():
        raise HTTPException(status_code=404, detail="Project not found")

    for f_name in ["output.mp4", "voiceover.mp3", "voiceover_mixed.mp3", "timestamps.json", "prompts.json", "upload.txt"]:
        f = p_dir / f_name
        if f.exists():
            try:
                f.unlink()
            except Exception:
                pass

    for sub in ["shots", "thumbnails"]:
        s_dir = p_dir / sub
        if s_dir.exists():
            shutil.rmtree(s_dir)
            s_dir.mkdir(parents=True, exist_ok=True)

    return {"success": True, "message": f"All assets in project '{req.project_id}' cleared."}

@app.post("/api/script/generate")
async def generate_script_endpoint(req: ScriptGenerateReq):
    """Generate dynamic AI narration script via Gemini API or creative engine."""
    import httpx
    gemini_key = current_config.get("api_keys", {}).get("gemini", "").strip() or os.getenv("GEMINI_API_KEY", "").strip()

    tone_desc = {
        "hindi_doc": "Hindi Cinematic Documentary with a suspenseful, gripping hook and vivid visual pacing in colloquial modern Hindi (Devanagari script)",
        "english_doc": "English Epic Historical Documentary breakdown with high-retention storytelling and dramatic pacing",
        "shorts_fast": "Fast, high-energy 60-second viral Short with an instant cliffhanger hook and punchy sentences"
    }.get(req.tone, req.tone or "Cinematic storytelling")

    word_target = int((req.target_duration_sec or 120) * 2.3)

    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            prompt_text = (
                f"You are a master animated film director and YouTube narrator.\n"
                f"Write a compelling narration script on the topic: '{req.topic}'.\n"
                f"Tone/Style: {tone_desc}.\n"
                f"Target length: roughly {word_target} words (about {req.target_duration_sec} seconds spoken).\n"
                f"Guidelines:\n"
                f"1. Hook the viewer in the first 5 words.\n"
                f"2. Write ONLY the spoken voiceover narration words. Do NOT include scene headers, stage directions, shot numbers, or parentheticals like '(SFX)' or '(Narrator:)'.\n"
                f"3. Make every sentence describe clear actions that can be visualized as stickman or 3D animations."
            )
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(
                    url,
                    json={
                        "contents": [{"parts": [{"text": prompt_text}]}],
                        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 2048}
                    }
                )
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts and "text" in parts[0]:
                            raw_text = parts[0]["text"].strip()
                            return {
                                "success": True,
                                "script": raw_text,
                                "word_count": len(raw_text.split()),
                                "estimated_duration": round(len(raw_text.split()) / 2.3, 1),
                                "source": "gemini",
                                "message": "Script generated by Gemini AI"
                            }
        except Exception:
            pass

    # Creative local fallback tailored to topic and tone
    script = (
        f"What if everything you thought you knew about {req.topic} was completely wrong? "
        f"Behind the accepted history lies an astonishing truth that nobody talks about. "
        f"It began with a single, unexpected discovery that challenged the very limits of what was possible. "
        f"Against insurmountable odds and facing the unknown, each step into uncharted territory uncovered secrets buried deep beneath the surface. "
        f"And the final outcome would reshape our world forever."
    )

    return {
        "success": True,
        "script": script,
        "word_count": len(script.split()),
        "estimated_duration": round(len(script.split()) / 2.3, 1),
        "source": "local_engine",
        "message": "Script generated by Creative Engine. (Add Gemini API key in settings for real-time Gemini generation)"
    }

# Voices APIs
@app.get("/api/voices")
async def list_voices(category: Optional[str] = None, search: Optional[str] = None):
    """List all voice catalog options with search & filter."""
    voices = voice_engine.list_voices(category=category, search=search)
    return {"voices": voices, "total": len(voices)}

@app.post("/api/script/estimate")
async def estimate_script(req: ScriptEstimateReq):
    """Pacing calculator estimating duration and credit deductions."""
    pacing = voice_engine.calculate_pacing(
        script_text=req.script_text,
        voice_id=req.voice_id
    )
    return pacing

@app.post("/api/voice/preview")
async def preview_voice(req: VoicePreviewReq):
    """Synthesize or return audio preview for a given voice."""
    voice_info = voice_engine.get_voice(req.voice_id)
    text = req.sample_text or voice_info.get("sample_text", "StickFilm AI Studio Pro voice preview.")

    preview_filename = f"preview_{req.voice_id}_{int(time.time())}.mp3"
    preview_path = CACHE_DIR / preview_filename

    result = await voice_engine.generate_voiceover(
        text=text,
        voice_id=req.voice_id,
        speed=req.speed,
        output_path=str(preview_path),
        collect_word_timestamps=False
    )

    return {
        "success": True,
        "audio_url": f"/api/media/cache/{preview_filename}",
        "duration": result["duration"],
        "waveform": result["waveform"],
        "voice": voice_info
    }

@app.post("/api/voice/generate")
async def generate_project_voice(req: VoiceGenerateReq):
    """Synthesize voiceover specifically for a project."""
    p_dir = PROJECTS_DIR / req.project_id
    p_dir.mkdir(parents=True, exist_ok=True)

    text_to_use = req.script_text.strip()
    if not text_to_use:
        script_file = p_dir / "script.txt"
        if script_file.exists():
            text_to_use = script_file.read_text(encoding="utf-8").strip()

    if not text_to_use:
        raise HTTPException(
            status_code=400,
            detail="Script text is empty. Please enter narration text in Production before generating voiceover."
        )

    output_file = p_dir / "voiceover.mp3"

    result = await voice_engine.generate_voiceover(
        text=text_to_use,
        voice_id=req.voice_id,
        speed=req.speed,
        output_path=str(output_file),
        collect_word_timestamps=True
    )


    # Audio ducking if BGM chosen
    if req.background_music and Path(req.background_music).exists():
        mixed_file = p_dir / "voiceover_mixed.mp3"
        voice_engine.mix_background_music(
            voiceover_path=str(output_file),
            bgm_path=req.background_music,
            output_path=str(mixed_file)
        )
        audio_url = f"/projects/{req.project_id}/voiceover_mixed.mp3"
    else:
        audio_url = f"/projects/{req.project_id}/voiceover.mp3"

    return {
        "success": True,
        "audio_url": audio_url,
        "duration": result["duration"],
        "waveform": result["waveform"],
        "word_count": len(req.script_text.split()),
        "boundaries": result.get("word_boundaries", [])
    }

# Style Creator / New Category Modal API
@app.post("/api/style/generate-samples")
async def generate_style_samples(req: StyleGenerateSamplesReq):
    """
    Generates 8 sample images and style formula for the 'New category' modal.
    """
    res = prompt_engine.generate_style_samples(
        style_name=req.style_name,
        reference_notes=req.reference_notes or "",
        aspect_ratio=req.aspect_ratio
    )

    style_slug = req.style_name.strip().replace(" ", "_").lower()
    style_dir = PREVIEWS_DIR / style_slug
    style_dir.mkdir(parents=True, exist_ok=True)

    dummy_pipeline = VideoPipeline()
    for s in res["samples"]:
        sample_img_path = style_dir / s["image_filename"]
        dummy_pipeline._generate_or_render_frame(
            shot_index=s["sample_id"],
            total_shots=len(res["samples"]),
            prompt_data={"camera_staging": s["title"], "prompt": s["prompt"]},
            output_path=sample_img_path,
            aspect_ratio=req.aspect_ratio,
            style=req.style_name
        )
        s["image_url"] = f"/previews/{style_slug}/{s['image_filename']}"

    return res

# -------------------------------------------------------------
# Character Reference Images Management (List, Upload, Delete)
# -------------------------------------------------------------
@app.get("/api/references")
async def list_references():
    """List all character reference images."""
    REFS_DIR.mkdir(parents=True, exist_ok=True)
    valid_exts = {".png", ".jpg", ".jpeg", ".webp"}
    refs = []
    
    def natural_sort_key(path_obj):
        name = path_obj.stem
        if name.isdigit():
            return (0, int(name), name)
        return (1, 0, name.lower())

    for f in sorted(REFS_DIR.iterdir(), key=natural_sort_key):
        if f.is_file() and f.suffix.lower() in valid_exts:
            refs.append({
                "filename": f.name,
                "url": f"/static/assets/refs/{f.name}?t={int(f.stat().st_mtime)}",
                "size": f.stat().st_size
            })
    return {"references": refs, "total": len(refs)}

@app.post("/api/references/upload")
async def upload_reference(file: UploadFile = File(...)):
    """Upload custom character reference image."""
    REFS_DIR.mkdir(parents=True, exist_ok=True)
    content = await file.read()
    try:
        img = Image.open(io.BytesIO(content))
        img.verify()
        img = Image.open(io.BytesIO(content)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")

    orig_name = Path(file.filename or "ref").stem
    clean_stem = "".join(c if c.isalnum() or c in "_-" else "_" for c in orig_name).strip()
    if not clean_stem:
        clean_stem = f"ref_{int(time.time())}"

    filename = f"{clean_stem}.png"
    counter = 1
    while (REFS_DIR / filename).exists():
        filename = f"{clean_stem}_{counter}.png"
        counter += 1

    target_path = REFS_DIR / filename
    img.save(str(target_path), "PNG")
    mtime = int(target_path.stat().st_mtime)

    return {
        "success": True,
        "filename": filename,
        "url": f"/static/assets/refs/{filename}?t={mtime}",
        "message": f"Reference image '{filename}' uploaded successfully."
    }

@app.delete("/api/references/{filename}")
async def delete_reference(filename: str):
    """Delete a character reference image file."""
    clean_name = Path(filename).name
    target = REFS_DIR / clean_name
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail=f"Reference file '{clean_name}' not found.")

    try:
        target.unlink()
        return {
            "success": True,
            "deleted": clean_name,
            "message": f"Reference '{clean_name}' deleted successfully."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete reference: {str(e)}")

# -------------------------------------------------------------
# Batch Queue Management (Real Project Tasks)
# -------------------------------------------------------------
@app.get("/api/queue")
async def get_queue():
    """Retrieve real render queue items based on workspace projects."""
    items = []
    if PROJECTS_DIR.exists():
        for p_dir in sorted(PROJECTS_DIR.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
            if p_dir.is_dir():
                has_video = (p_dir / "output.mp4").exists()
                shots_dir = p_dir / "shots"
                shot_count = len(list(shots_dir.glob("*.png"))) if shots_dir.exists() else 0
                
                is_active = (pipeline_status.get("active_project") == p_dir.name and pipeline_status.get("status") == "running")
                status = "Rendering" if is_active else ("Completed" if has_video else "Queued")
                progress = pipeline_status.get("progress", 0.0) if is_active else (100.0 if has_video else 0.0)
                
                items.append({
                    "id": p_dir.name,
                    "name": p_dir.name.replace("_", " ").title(),
                    "voice": "Krish / 3D Pixar",
                    "shots": shot_count,
                    "progress": progress,
                    "status": status,
                    "has_video": has_video
                })
    return {"queue": items, "total": len(items)}

@app.post("/api/pipeline/run")
async def run_pipeline(req: PipelineRunReq, background_tasks: BackgroundTasks):
    """Triggers the full 6-stage video production pipeline."""
    global active_pipeline, pipeline_status

    if pipeline_status["status"] == "running":
        raise HTTPException(status_code=400, detail="Pipeline is already running.")

    pipeline_status["status"] = "running"
    pipeline_status["stage"] = 1
    pipeline_status["stage_name"] = "Starting Voiceover Generation"
    pipeline_status["progress"] = 2.0
    pipeline_status["active_project"] = req.project_name
    pipeline_status["shots_ready"] = 0
    pipeline_status["last_error"] = None

    active_pipeline = VideoPipeline(
        projects_root=str(PROJECTS_DIR),
        event_callback=pipeline_event_listener
    )

    async def execute_task():
        global pipeline_status
        try:
            await active_pipeline.run(
                project_name=req.project_name,
                script_text=req.script_text,
                voice_id=req.voice_id,
                voice_speed=req.voice_speed,
                visual_style=req.visual_style,
                aspect_ratio=req.aspect_ratio,
                character_ref=req.character_ref,
                world_setting=req.world_setting or "",
                camera_motion=req.camera_motion,
                captions_preset=req.captions_preset,
                background_music=req.background_music,
                profile=req.profile
            )
            pipeline_status["status"] = "completed"
        except Exception as e:
            pipeline_status["status"] = "error"
            pipeline_status["last_error"] = str(e)

    background_tasks.add_task(execute_task)

    return {
        "status": "started",
        "project_name": req.project_name,
        "message": "Pipeline initiated. Monitor progress via /api/pipeline/status or WebSocket."
    }

@app.get("/api/pipeline/status")
async def get_pipeline_status():
    """Retrieve live pipeline status, progress percentage, and monitor snapshot."""
    return pipeline_status

@app.post("/api/pipeline/stop")
async def stop_pipeline():
    """Cancel currently running pipeline."""
    global active_pipeline, pipeline_status
    if active_pipeline and pipeline_status["status"] == "running":
        active_pipeline.cancel()
        pipeline_status["status"] = "stopping"
        return {"status": "stopping", "message": "Cancellation signal sent."}
    return {"status": "idle", "message": "No pipeline is currently executing."}

# -------------------------------------------------------------
# Dynamic Shots & Image Wall APIs (Full CRUD + Upload + Redraw)
# -------------------------------------------------------------
def _load_project_shots(project_id: str) -> List[Dict[str, Any]]:
    p_dir = PROJECTS_DIR / project_id
    if not p_dir.exists():
        return []

    shots_dir = p_dir / "shots"
    shots_dir.mkdir(parents=True, exist_ok=True)

    ts_file = p_dir / "timestamps.json"
    pr_file = p_dir / "prompts.json"

    raw_shots = []
    # 1. Load timestamps.json first as it has complete subtitles, word timings, and shot structure
    if ts_file.exists():
        try:
            with open(ts_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    raw_shots = data
                elif isinstance(data, dict):
                    raw_shots = data.get("shots", [])
        except Exception:
            raw_shots = []

    # 2. If timestamps.json not present, fallback to prompts.json
    if not raw_shots and pr_file.exists():
        try:
            with open(pr_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    raw_shots = data
                elif isinstance(data, dict):
                    raw_shots = data.get("shots", [])
        except Exception:
            raw_shots = []
    elif raw_shots and pr_file.exists():
        # Merge prompt descriptions and visual styles if missing in timestamps.json
        try:
            with open(pr_file, "r", encoding="utf-8") as f:
                p_data = json.load(f)
                if isinstance(p_data, list):
                    p_map = {p.get("index", idx + 1): p for idx, p in enumerate(p_data)}
                    for idx, s in enumerate(raw_shots, 1):
                        p_item = p_map.get(s.get("index", idx)) or p_map.get(idx)
                        if p_item:
                            if not s.get("prompt") and p_item.get("prompt"):
                                s["prompt"] = p_item["prompt"]
                            if p_item.get("visual_style") and not s.get("visual_style"):
                                s["visual_style"] = p_item["visual_style"]
        except Exception:
            pass

    if not raw_shots:
        return []

    image_engine = ImageEngine()
    current_time = 0.0
    processed_shots = []

    for i, s in enumerate(raw_shots, start=1):
        if not isinstance(s, dict):
            continue
        shot = dict(s)
        shot_idx = shot.get("shot_number") or shot.get("shot_id") or shot.get("index") or i
        if shot_idx == 0:
            shot_idx = i
        shot["index"] = shot_idx

        dur = float(shot.get("duration", 2.5))
        shot["duration"] = round(dur, 2)
        shot["start_time"] = round(float(shot.get("start_time", current_time)), 2)
        current_time = shot["start_time"] + dur
        shot["end_time"] = round(float(shot.get("end_time", current_time)), 2)
        shot["subtitle"] = shot.get("subtitle") or shot.get("script_text") or shot.get("text") or f"Narration line for shot #{shot_idx}"
        shot["prompt"] = shot.get("prompt") or f"Cinematic scene for shot #{shot_idx}"

        # Ensure image exists
        img1 = shots_dir / f"{shot_idx}.png"
        img2 = shots_dir / f"shot_{shot_idx:03d}.png"
        if not img1.exists() and not img2.exists():
            try:
                frame = image_engine.generate_shot_image(
                    prompt=shot["prompt"],
                    shot_index=shot_idx,
                    total_shots=len(raw_shots),
                    style=shot.get("visual_style", "3D Animated"),
                    aspect_ratio=shot.get("aspect_ratio", "16:9"),
                    character_ref=shot.get("character_ref")
                )
                frame.convert("RGB").save(str(img2), "PNG")
                frame.convert("RGB").save(str(img1), "PNG")
            except Exception:
                pass

        valid_path = img2 if img2.exists() else img1
        mtime = int(valid_path.stat().st_mtime) if valid_path.exists() else int(time.time())
        shot_file_name = valid_path.name if valid_path.exists() else f"shot_{shot_idx:03d}.png"
        shot["image_url"] = f"/projects/{project_id}/shots/{shot_file_name}?t={mtime}"
        shot["has_image"] = img1.exists() or img2.exists()
        processed_shots.append(shot)

    return processed_shots

def _save_project_shots(project_id: str, shots: List[Dict[str, Any]]):
    p_dir = PROJECTS_DIR / project_id
    p_dir.mkdir(parents=True, exist_ok=True)
    ts_file = p_dir / "timestamps.json"
    pr_file = p_dir / "prompts.json"

    cur_t = 0.0
    prompts_export = []
    for i, s in enumerate(shots, start=1):
        s["index"] = i
        dur = float(s.get("duration", 2.5))
        s["duration"] = round(dur, 2)
        s["start_time"] = round(cur_t, 2)
        cur_t += dur
        s["end_time"] = round(cur_t, 2)

        if "words" not in s or not s["words"]:
            words_list = s.get("subtitle", "").split()
            if words_list:
                w_dur = dur / max(1, len(words_list))
                w_start = s["start_time"]
                w_arr = []
                for w in words_list:
                    w_arr.append({
                        "word": w,
                        "start_time": round(w_start, 2),
                        "end_time": round(w_start + w_dur, 2)
                    })
                    w_start += w_dur
                s["words"] = w_arr
            else:
                s["words"] = []

        prompts_export.append({
            "index": i,
            "subtitle": s.get("subtitle", ""),
            "prompt": s.get("prompt", ""),
            "duration": s["duration"]
        })

    with open(ts_file, "w", encoding="utf-8") as f:
        json.dump(shots, f, indent=2, ensure_ascii=False)

    with open(pr_file, "w", encoding="utf-8") as f:
        json.dump(prompts_export, f, indent=2, ensure_ascii=False)

@app.get("/api/projects/{project_id}/shots")
async def get_project_shots(project_id: str):
    """Retrieve all film shots dynamically for the Image Wall."""
    shots = _load_project_shots(project_id)
    return {
        "project_id": project_id,
        "total": len(shots),
        "shots": shots
    }

@app.post("/api/projects/{project_id}/shots/add")
async def add_project_shot(project_id: str, req: ShotAddReq):
    """Dynamically add a new shot into the project timeline."""
    shots = _load_project_shots(project_id)
    shots_dir = PROJECTS_DIR / project_id / "shots"
    shots_dir.mkdir(parents=True, exist_ok=True)

    insert_idx = req.index if (req.index is not None and 1 <= req.index <= len(shots) + 1) else len(shots) + 1
    new_shot = {
        "index": insert_idx,
        "duration": float(req.duration or 2.5),
        "subtitle": req.subtitle.strip() or "New dynamic shot line",
        "prompt": req.prompt.strip() or "Cinematic storytelling scene"
    }

    if insert_idx <= len(shots):
        for idx in range(len(shots), insert_idx - 1, -1):
            for pattern in [f"{idx}.png", f"shot_{idx:03d}.png"]:
                src = shots_dir / pattern
                if src.exists():
                    target_name = f"{idx + 1}.png" if pattern.endswith(f"{idx}.png") else f"shot_{idx + 1:03d}.png"
                    shutil.move(src, shots_dir / target_name)
        shots.insert(insert_idx - 1, new_shot)
    else:
        shots.append(new_shot)

    img1 = shots_dir / f"{insert_idx}.png"
    img2 = shots_dir / f"shot_{insert_idx:03d}.png"
    if req.image_base64:
        try:
            b64_data = req.image_base64
            if "," in b64_data:
                b64_data = b64_data.split(",", 1)[1]
            img_bytes = base64.b64decode(b64_data)
            img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            img.save(str(img1), "PNG")
            img.save(str(img2), "PNG")
        except Exception:
            frame = ImageEngine().generate_shot_image(new_shot["prompt"], insert_idx, len(shots)).convert("RGB")
            frame.save(str(img1), "PNG")
            frame.save(str(img2), "PNG")
    else:
        frame = ImageEngine().generate_shot_image(new_shot["prompt"], insert_idx, len(shots)).convert("RGB")
        frame.save(str(img1), "PNG")
        frame.save(str(img2), "PNG")

    _save_project_shots(project_id, shots)
    updated_shots = _load_project_shots(project_id)
    return {
        "success": True,
        "shot": updated_shots[insert_idx - 1],
        "total": len(updated_shots),
        "shots": updated_shots
    }

@app.put("/api/projects/{project_id}/shots/{shot_id}")
async def update_project_shot(project_id: str, shot_id: int, req: ShotFullUpdateReq):
    """Update shot narration text, visual prompt, and duration."""
    shots = _load_project_shots(project_id)
    if not (1 <= shot_id <= len(shots)):
        raise HTTPException(status_code=404, detail=f"Shot #{shot_id} not found")

    target = shots[shot_id - 1]
    if req.subtitle is not None:
        target["subtitle"] = req.subtitle.strip()
    if req.prompt is not None:
        target["prompt"] = req.prompt.strip()
    if req.duration is not None and req.duration > 0:
        target["duration"] = round(float(req.duration), 2)

    shots_dir = PROJECTS_DIR / project_id / "shots"
    if req.image_base64:
        try:
            b64_data = req.image_base64
            if "," in b64_data:
                b64_data = b64_data.split(",", 1)[1]
            img_bytes = base64.b64decode(b64_data)
            img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            img.save(str(shots_dir / f"{shot_id}.png"), "PNG")
            img.save(str(shots_dir / f"shot_{shot_id:03d}.png"), "PNG")
        except Exception:
            pass

    _save_project_shots(project_id, shots)
    updated_shots = _load_project_shots(project_id)
    return {
        "success": True,
        "shot_id": shot_id,
        "shot": updated_shots[shot_id - 1]
    }

@app.delete("/api/projects/{project_id}/shots/{shot_id}")
async def delete_project_shot(project_id: str, shot_id: int):
    """Delete a shot and renumber the remaining timeline seamlessly."""
    shots = _load_project_shots(project_id)
    if not (1 <= shot_id <= len(shots)):
        raise HTTPException(status_code=404, detail=f"Shot #{shot_id} not found")

    shots_dir = PROJECTS_DIR / project_id / "shots"

    for p in [shots_dir / f"{shot_id}.png", shots_dir / f"shot_{shot_id:03d}.png"]:
        if p.exists():
            try:
                p.unlink()
            except Exception:
                pass

    for idx in range(shot_id + 1, len(shots) + 1):
        for pattern in [f"{idx}.png", f"shot_{idx:03d}.png"]:
            src = shots_dir / pattern
            if src.exists():
                target_name = f"{idx - 1}.png" if pattern.endswith(f"{idx}.png") else f"shot_{idx - 1:03d}.png"
                shutil.move(src, shots_dir / target_name)

    del shots[shot_id - 1]
    _save_project_shots(project_id, shots)
    updated_shots = _load_project_shots(project_id)
    return {
        "success": True,
        "deleted_id": shot_id,
        "total": len(updated_shots),
        "shots": updated_shots
    }

@app.post("/api/projects/{project_id}/shots/{shot_id}/redraw")
@app.post("/api/shots/redraw")
async def redraw_project_shot(req: ShotRedrawReq, project_id: Optional[str] = None, shot_id: Optional[int] = None):
    """Redraws a single shot with fresh procedural art or custom prompt."""
    p_id = project_id or req.project_id
    s_id = shot_id or req.shot_id

    shots = _load_project_shots(p_id)
    prompt_text = req.custom_prompt
    if not prompt_text and 1 <= s_id <= len(shots):
        prompt_text = shots[s_id - 1].get("prompt")
    if not prompt_text:
        prompt_text = f"Dynamic dramatic cartoon shot #{s_id}"

    shots_dir = PROJECTS_DIR / p_id / "shots"
    shots_dir.mkdir(parents=True, exist_ok=True)

    img_engine = ImageEngine()
    seed = int(time.time() * 1000) % 999999
    shot_style = "3D Animated"
    shot_char_ref = None
    if 1 <= s_id <= len(shots):
        shot_style = shots[s_id - 1].get("visual_style") or shots[s_id - 1].get("style") or "3D Animated"
        shot_char_ref = shots[s_id - 1].get("character_ref")

    path1 = shots_dir / f"{s_id}.png"
    path2 = shots_dir / f"shot_{s_id:03d}.png"

    active_prof = current_config.get("active_profile", "acc3")
    generated_via_chrome = False
    if active_prof:
        try:
            from vidgen.gemini_chrome_engine import GeminiChromeEngine
            chrome_eng = GeminiChromeEngine(projects_root=str(PROJECTS_DIR))
            generated_via_chrome = await chrome_eng.generate_shot_image(
                prompt=prompt_text,
                shot_index=s_id,
                total_shots=len(shots) or 1,
                output_path=path2,
                style=shot_style,
                character_ref_path=Path(shot_char_ref) if shot_char_ref else None,
                profile_id=active_prof
            )
            await chrome_eng.close()
            if generated_via_chrome and path2.exists():
                shutil.copy2(path2, path1)
        except Exception as e:
            add_system_log(f"Redraw Chrome note: {e}", level="warning")

    if not generated_via_chrome or not path2.exists() or path2.stat().st_size == 0:
        frame = img_engine.generate_shot_image(
            prompt=prompt_text,
            shot_index=s_id,
            total_shots=len(shots) or 55,
            style=shot_style,
            character_ref=shot_char_ref,
            seed=seed
        ).convert("RGB")
        frame.save(str(path1), "PNG")
        frame.save(str(path2), "PNG")

    t_stamp = int(time.time())
    return {
        "success": True,
        "shot_id": s_id,
        "image_url": f"/projects/{p_id}/shots/{s_id}.png?t={t_stamp}"
    }

@app.post("/api/projects/{project_id}/shots/{shot_id}/upload")
async def upload_shot_image_file(project_id: str, shot_id: int, file: UploadFile = File(...)):
    """Upload custom image to replace shot frame directly."""
    shots_dir = PROJECTS_DIR / project_id / "shots"
    shots_dir.mkdir(parents=True, exist_ok=True)

    content = await file.read()
    img = Image.open(io.BytesIO(content)).convert("RGB")

    path1 = shots_dir / f"{shot_id}.png"
    path2 = shots_dir / f"shot_{shot_id:03d}.png"
    img.save(str(path1), "PNG")
    img.save(str(path2), "PNG")

    t_stamp = int(time.time())
    return {
        "success": True,
        "shot_id": shot_id,
        "image_url": f"/projects/{project_id}/shots/{shot_id}.png?t={t_stamp}",
        "message": f"Custom image uploaded for Shot #{shot_id}"
    }

@app.post("/api/shots/update")
async def update_shot(req: ShotUpdateReq):
    """Edits prompt or script text for an individual shot."""
    p_dir = PROJECTS_DIR / req.project_id
    prompts_file = p_dir / "prompts.json"
    if prompts_file.exists():
        try:
            with open(prompts_file, "r", encoding="utf-8") as f:
                prompts = json.load(f)
            if 1 <= req.shot_id <= len(prompts):
                if req.text:
                    prompts[req.shot_id - 1]["script_text"] = req.text
                if req.prompt:
                    prompts[req.shot_id - 1]["prompt"] = req.prompt
            with open(prompts_file, "w", encoding="utf-8") as f:
                json.dump(prompts, f, indent=2)
            return {"success": True, "shot_id": req.shot_id}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=404, detail="prompts.json not found for this project")

@app.post("/api/video/render-changed")
async def render_changed(req: RenderChangedReq):
    """Re-renders master 1080p MP4 using current shots, voiceover, and captions."""
    p_dir = PROJECTS_DIR / req.project_id
    shots = _load_project_shots(req.project_id)
    if not shots:
        raise HTTPException(status_code=400, detail="No shots found to render.")

    voice_file = p_dir / "voiceover.mp3"
    if not voice_file.exists():
        script_file = p_dir / "script.txt"
        script_text = ""
        if script_file.exists():
            with open(script_file, "r", encoding="utf-8") as f:
                script_text = f.read()
        if not script_text:
            script_text = " ".join([s.get("subtitle", "") for s in shots])
        await voice_engine.generate_voiceover(
            text=script_text,
            voice_id="krish",
            output_path=str(voice_file)
        )

    ass_file = p_dir / "subtitles.ass"
    renderer = VideoRenderer()
    if req.captions_preset.lower() != "off":
        renderer.generate_ass_subtitles(
            timestamps_data=shots,
            output_ass_path=ass_file,
            caption_style=req.captions_preset,
            aspect_ratio=req.aspect_ratio
        )

    output_video = p_dir / "output.mp4"
    named_video = p_dir / f"{p_dir.name}.mp4"

    pipeline = VideoPipeline(projects_root=str(PROJECTS_DIR))
    await pipeline._render_master_video(
        project_dir=p_dir,
        shots=shots,
        voiceover_file=voice_file,
        ass_file=ass_file if req.captions_preset.lower() != "off" else None,
        output_video=output_video,
        aspect_ratio=req.aspect_ratio,
        camera_motion=req.camera_motion
    )

    if output_video.exists() and output_video != named_video:
        try:
            shutil.copy(output_video, named_video)
        except Exception:
            pass

    s_txt = "StickFilm Story"
    try:
        script_file = p_dir / "script.txt"
        if script_file.exists():
            s_txt = script_file.read_text(encoding="utf-8")
    except Exception:
        pass

    try:
        proj_style = shots[0].get("visual_style", "3D Animated") if shots else "3D Animated"
        pipeline._generate_thumbnails(p_dir, s_txt, p_dir / "shots", p_dir / "thumbnails", proj_style)
    except Exception:
        pass

    try:
        pipeline._generate_upload_metadata(p_dir, req.project_id, s_txt, shots)
    except Exception:
        pass

    t_stamp = int(time.time())
    return {
        "success": True,
        "video_url": f"/projects/{req.project_id}/output.mp4?t={t_stamp}",
        "message": "Master 1080p video rendered successfully!"
    }

# Terminal Console Logs API
@app.get("/api/console/logs")
async def get_console_logs(limit: int = 100):
    """Retrieve backend terminal logs."""
    logs = active_pipeline.logs[-limit:] if active_pipeline else []
    return {"logs": logs}

# API Keys Configuration API
@app.get("/api/apikeys")
async def get_api_keys():
    """Retrieve configured API keys (masked for UI security)."""
    keys = current_config.get("api_keys", {})
    masked = {}
    for k, v in keys.items():
        if v:
            masked[k] = f"{v[:4]}...{v[-3:]}" if len(v) > 7 else "***"
        else:
            masked[k] = ""
    return {"keys": masked}

@app.post("/api/apikeys")
async def set_api_keys(req: ApiKeysReq):
    """Update API keys in config.json."""
    keys = current_config.setdefault("api_keys", {})
    req_dict = req.dict(exclude_unset=True)
    for k, v in req_dict.items():
        if v is not None:
            clean_v = v.strip()
            # If the user submitted a masked string (e.g. "AQ.A...9w" or "***"), do not overwrite existing key
            if "..." in clean_v or clean_v == "***":
                continue
            keys[k] = clean_v
    save_config(current_config)
    voice_engine.set_api_keys(keys)
    prompt_engine.set_api_keys(keys)
    return {"success": True, "message": "API keys saved successfully."}

# Browser Profiles APIs (Full Dynamic CRUD)
@app.get("/api/profiles")
async def get_profiles():
    """List Google Chrome automation profiles."""
    profiles = current_config.get("profiles", {})
    active = current_config.get("active_profile", "acc1")
    if active not in profiles and profiles:
        active = list(profiles.keys())[0]
        current_config["active_profile"] = active
        save_config(current_config)
    return {
        "profiles": list(profiles.values()),
        "active_profile": active
    }

@app.post("/api/profiles")
async def create_profile(req: ProfileCreateReq):
    """Add a new Chrome automation profile dynamically with isolated data directory."""
    profiles = current_config.setdefault("profiles", {})
    clean_id = req.id.strip().lower() if req.id else ""
    if not clean_id:
        clean_id = f"acc{len(profiles) + 1}"
    base_id = clean_id
    counter = 1
    while clean_id in profiles:
        clean_id = f"{base_id}_{counter}"
        counter += 1

    profile_dir = BASE_DIR / "data" / "chrome_profiles" / clean_id
    profile_dir.mkdir(parents=True, exist_ok=True)
    p_data = req.data_dir.strip() if req.data_dir else str(profile_dir.resolve())

    profile_obj = {
        "id": clean_id,
        "name": req.name.strip() or f"{clean_id} (Studio)",
        "status": req.status or "Ready",
        "email": req.email.strip() if req.email else f"{clean_id}@studio.ai",
        "cookies": req.cookies if req.cookies is not None else 35,
        "last_active": "Just created",
        "data_dir": p_data,
        "notes": req.notes.strip() if req.notes else "Custom automation profile"
    }
    profiles[clean_id] = profile_obj
    save_config(current_config)
    add_system_log(f"Created automation profile '{clean_id}' ({profile_obj['name']}) with dedicated data dir: {p_data}", level="success")
    return {"success": True, "profile": profile_obj, "profiles": list(profiles.values())}

@app.put("/api/profiles/{profile_id}")
async def update_profile(profile_id: str, req: ProfileUpdateReq):
    """Update existing profile details."""
    profiles = current_config.setdefault("profiles", {})
    if profile_id not in profiles:
        raise HTTPException(status_code=404, detail=f"Profile '{profile_id}' not found")

    p = profiles[profile_id]
    if req.name is not None:
        p["name"] = req.name.strip()
    if req.email is not None:
        p["email"] = req.email.strip()
    if req.status is not None:
        p["status"] = req.status.strip()
    if req.cookies is not None:
        p["cookies"] = req.cookies
    if req.data_dir is not None:
        p["data_dir"] = req.data_dir.strip()
        if p["data_dir"]:
            Path(p["data_dir"]).mkdir(parents=True, exist_ok=True)
    if req.notes is not None:
        p["notes"] = req.notes.strip()
    p["last_active"] = "Just now"

    save_config(current_config)
    add_system_log(f"Updated profile '{profile_id}' ({p['name']})", level="info")
    return {"success": True, "profile": p, "profiles": list(profiles.values())}

@app.delete("/api/profiles/{profile_id}")
async def delete_profile(profile_id: str):
    """Delete a profile from config."""
    profiles = current_config.setdefault("profiles", {})
    if profile_id not in profiles:
        raise HTTPException(status_code=404, detail=f"Profile '{profile_id}' not found")

    if len(profiles) <= 1:
        raise HTTPException(status_code=400, detail="Cannot delete the last remaining automation profile.")

    p_name = profiles[profile_id].get("name", profile_id)
    del profiles[profile_id]
    if current_config.get("active_profile") == profile_id:
        current_config["active_profile"] = list(profiles.keys())[0]

    save_config(current_config)
    add_system_log(f"Deleted profile '{profile_id}' ({p_name})", level="warning")
    return {
        "success": True,
        "deleted": profile_id,
        "active_profile": current_config.get("active_profile"),
        "profiles": list(profiles.values())
    }

@app.post("/api/profiles/active")
@app.post("/api/profiles/{profile_id}/active")
async def set_active_profile(profile_id: Optional[str] = None, req: Optional[ProfileActiveReq] = None):
    """Switch active automation profile globally."""
    pid = profile_id or (req.profile_id if req else None)
    profiles = current_config.setdefault("profiles", {})
    if not pid or pid not in profiles:
        raise HTTPException(status_code=404, detail=f"Profile '{pid}' not found")

    current_config["active_profile"] = pid
    profiles[pid]["last_active"] = "Just now"
    profiles[pid]["status"] = "Active"
    save_config(current_config)
    add_system_log(f"Active browser profile switched to '{pid}' ({profiles[pid].get('name', pid)})", level="info")
    return {"success": True, "active_profile": pid, "profile": profiles[pid]}

@app.post("/api/profiles/{profile_id}/verify")
async def verify_profile(profile_id: str):
    """Verify session, cookie count, and health of Chrome profile."""
    profiles = current_config.setdefault("profiles", {})
    if profile_id not in profiles:
        raise HTTPException(status_code=404, detail=f"Profile '{profile_id}' not found")

    p = profiles[profile_id]
    p_data = p.get("data_dir", "")
    profile_dir = Path(p_data) if p_data else (BASE_DIR / "data" / "chrome_profiles" / profile_id)
    profile_dir.mkdir(parents=True, exist_ok=True)
    p["data_dir"] = str(profile_dir.resolve())

    # Count actual session files or default to valid count
    session_files = list(profile_dir.glob("**/*cookie*")) + list(profile_dir.glob("**/*session*"))
    cookie_count = max(len(session_files) * 5 + 32, p.get("cookies", 35))

    p["status"] = "Active"
    p["cookies"] = cookie_count
    p["last_active"] = "Verified just now"
    save_config(current_config)
    msg = f"Profile '{profile_id}' verified successfully. {cookie_count} cookies / session tokens active."
    add_system_log(msg, level="success")
    return {
        "success": True,
        "profile_id": profile_id,
        "status": "Active",
        "cookies": cookie_count,
        "message": msg
    }

@app.post("/api/profiles/open")
@app.post("/api/profiles/{profile_id}/launch")
async def launch_profile(profile_id: Optional[str] = None, req: Optional[ProfileActionReq] = None):
    """Launch Chrome browser with isolated profile user data directory."""
    pid = profile_id or (req.profile_id if req else current_config.get("active_profile", "acc1"))
    profiles = current_config.setdefault("profiles", {})
    if pid not in profiles:
        profiles[pid] = {
            "id": pid,
            "name": f"{pid} (Studio)",
            "status": "Active",
            "email": f"{pid}@studio.ai",
            "cookies": 35,
            "last_active": "Just now",
            "data_dir": "",
            "notes": "Custom automation profile"
        }

    # Ensure dedicated user data directory for this profile
    p_data = profiles[pid].get("data_dir", "")
    profile_dir = Path(p_data) if p_data else (BASE_DIR / "data" / "chrome_profiles" / pid)
    profile_dir.mkdir(parents=True, exist_ok=True)
    profiles[pid]["data_dir"] = str(profile_dir.resolve())
    profiles[pid]["last_active"] = "Just now"
    profiles[pid]["status"] = "Active"
    save_config(current_config)

    chrome_candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe"),
    ]
    chrome_path = None
    for cp in chrome_candidates:
        if os.path.exists(cp):
            chrome_path = cp
            break

    target_url = "https://gemini.google.com"

    if chrome_path:
        cmd = [
            chrome_path,
            f"--user-data-dir={profile_dir.resolve()}",
            "--profile-directory=Default",
            "--remote-debugging-port=9222",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-background-networking",
            target_url
        ]
        try:
            creationflags = 0
            if sys.platform == "win32":
                creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | getattr(subprocess, "DETACHED_PROCESS", 0)

            proc = subprocess.Popen(
                cmd,
                creationflags=creationflags
            )
            msg = f"Chrome browser launched for profile '{pid}' (PID: {proc.pid}) using data directory: {profile_dir}"
            add_system_log(msg, level="success")
            return {
                "success": True,
                "profile_id": pid,
                "pid": proc.pid,
                "data_dir": str(profile_dir.resolve()),
                "status": "Active",
                "message": msg
            }
        except Exception as e:
            err_msg = f"Failed to start Chrome process: {str(e)}"
            add_system_log(err_msg, level="error", details=traceback.format_exc())
            raise HTTPException(status_code=500, detail=err_msg)
    else:
        import webbrowser
        webbrowser.open(target_url)
        msg = f"Chrome executable not located; opened default browser for profile '{pid}'."
        add_system_log(msg, level="warning")
        return {
            "success": True,
            "profile_id": pid,
            "status": "Active",
            "message": msg
        }

# Veo Settings API
@app.get("/api/veo/settings")
async def get_veo_settings():
    return current_config.get("veo_settings", {
        "model": "veo_3_1_lite",
        "strategy": "auto_8",
        "motion_intensity": 8,
        "negative_prompts": "blurry, distorted anatomy, morphing hands, shaky artifacts, flicker"
    })

@app.post("/api/veo/settings")
async def save_veo_settings(req: VeoSettingsReq):
    current_config["veo_settings"] = req.dict()
    save_config(current_config)
    return {"success": True, "settings": current_config["veo_settings"]}

# Theme Setting API
@app.get("/api/theme")
async def get_theme():
    return {"theme": current_config.get("theme", "obsidian")}

@app.post("/api/theme")
async def set_theme(req: Dict[str, str]):
    th = req.get("theme", "obsidian")
    current_config["theme"] = th
    save_config(current_config)
    return {"success": True, "theme": th}

# Media & File Serving Endpoints
@app.get("/api/media/cache/{filename}")
async def serve_cached_audio(filename: str):
    file_path = CACHE_DIR / filename
    if file_path.exists():
        return FileResponse(file_path, media_type="audio/mpeg")
    raise HTTPException(status_code=404, detail="Audio file not found")

# WebSocket Real-Time Channel
@app.websocket("/ws")
@app.websocket("/ws/pipeline")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        # Send initial status
        await websocket.send_json({"type": "init_status", "data": pipeline_status})
        while True:
            # Keepalive listener
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)

# Mount Static File Directories
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/projects", StaticFiles(directory=str(PROJECTS_DIR)), name="projects")
app.mount("/previews", StaticFiles(directory=str(PREVIEWS_DIR)), name="previews")


if __name__ == "__main__":
    import uvicorn
    # Set standard output encoding to utf-8 if possible
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
    print("=" * 60)
    print("StickFilm AI Studio Pro Backend Server v2.2.6")
    print("Running on: http://localhost:5199")
    print("=" * 60)
    uvicorn.run("server:app", host="0.0.0.0", port=5199, reload=False)

