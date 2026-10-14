# StickFilm AI Studio Pro (v2.2.6) - Complete System Specification & Requirements Document

## 1. Executive Summary & Vision
**StickFilm AI Studio Pro** is an all-in-one desktop AI film studio designed for creators, documentary channels, stickman animators, 3D creators, and faceless YouTube/Shorts/Reels content machines. 
It automates the entire video production pipeline from raw script or idea to a published 1080p Full HD video with synchronized voiceover, character-consistent imagery, dynamic camera motions, word-highlighted karaoke captions, viral thumbnails, and YouTube SEO metadata.

---

## 2. Core Architectural Components

### 2.1 Backend Pipeline (`vidgen/pipeline.py` & API Server)
- **Runtime Environment**: Python 3.10+ / Node.js runtime, running local web server on `http://localhost:5199`.
- **Pipeline Runner**: 6-Stage Automated Pipeline with real-time SSE / WebSocket progress events and cancellation control:
  1. **Stage 1: Voiceover Generation**
     - Integrations: ElevenLabs API (Eleven v4 Turbo), Minimax API, offline Edge-TTS / Kokoro / Coqui voices (`Meri Eng`, `Krish`, `Madhur`, `Psi`, `Alpha`, `Beta`, `Jerry`, etc.).
     - Features: Word pacing calculation, multi-lingual audio synthesis (Hindi, English, Spanish, Portuguese, French, etc.), audio waveform generation, background music ducking.
  2. **Stage 2: Timestamps & Word-Level Entity Cuts**
     - Automatic speech-to-text alignment (faster-whisper / gentle / acoustic alignment).
     - Generates exact millisecond word timestamps and segments narration into coherent visual shots (typically 1.5s - 4.5s per shot).
  3. **Stage 3: Action-First Iconic Prompt Generation**
     - LLM Prompt Synthesis (Gemini 2.5 Flash / GPT-4o / Claude 3.5).
     - Translates each script sentence/dialogue into a cinematic scene description obeying character references, world setting, camera angles (wide establishing, medium action, close up macro), lighting, and artistic style.
  4. **Stage 4: Gemini Canvas Batch Generation (In-Memory JSZip)**
     - Chrome Browser Automation (Playwright/Selenium) with persistent user profiles (`acc1`, `acc2`) OR direct Gemini Imagen 3 / FLUX.1 / SDXL API fallback.
     - Real-time live screen capture streaming to the web UI monitor.
     - Character turnaround consistency enforcement using reference images (`138.png` style sheet).
     - In-memory batch packaging and fast extraction.
     - **Stage 4B: Veo 3 Video Clips (Google Flow)**: Optional short motion clip generation for hero moments.
  5. **Stage 5: Mandatory Image Verification (0 Blanks Guard)**
     - Integrity check verifying that 100% of the shots have valid, high-resolution, non-corrupted images.
     - Auto-retry / re-generate any failed or black/blank frames before passing to render.
  6. **Stage 6: 1080p Full HD Master Video Render**
     - `ffmpeg` hardware-accelerated compositor.
     - Applied camera motions: Ken Burns (slow zoom + drift), Slow zoom in, Slow zoom out, Pan left/right, Drone rise, Crash zoom, No motion, Mix of all.
     - Animated Subtitle Overlay: Word Highlight (gold on active word), Bold Comic, Karaoke Fill, Simple Green, Boxed, One Word Pop, Simple.
     - Seamless audio-video muxing with 320kbps AAC audio.

---

## 3. Detailed UI / UX Specifications (Matching Screenshots)

### 3.1 Design System & Theme
- **Color Palette**: Dark obsidian background (`#0d0f12`, `#14171d`, `#1c2029`), vibrant gold/yellow accents (`#f5b82e`, `#e5a812`), emerald green success badges (`#10b981`), red danger pills (`#ef4444`), subtle warm borders (`rgba(245, 184, 46, 0.15)`).
- **Typography**: Inter / Outfit modern sans-serif with monospace accents for timecodes and console logs.
- **Header**:
  - Logo: `STICKFILM STUDIO UNLIMITED v2.2.6` + `1 Update available` cyan badge.
  - Project Bar: `PROJECT:` dropdown selector + `[New]`, `[Delete]`, `[Clear All]`.
  - Referral Badge: `$5+ / referral`.
  - Utility Controls: `[API Keys]`, `[Restart Server]`, `[Run Pipeline]`, `[Stop]`.
  - Assistant: `[Gemini Writer]` AI script generation trigger.

### 3.2 Navigation Sidebar (8 Dedicated Views)
1. **Production**: The primary dashboard for configuring script, voice, visual look, character refs, camera motions, and launching generation.
2. **Studio**: Real-time pipeline monitor with live screen capture of generation canvas, status bars, and 6-stage step indicators with timestamps.
3. **Queue**: Multi-project batch queue with pause, resume, reorder, and batch rendering.
4. **Image Wall**: Complete shot-by-shot visual story review (55+ shots grid), displaying frame thumbnails, duration overlays, script text, and single-shot `[Redraw]` and `[Edit]` buttons.
5. **Deliverables**: Final published video player, master MP4 download (`Download MP4`), open folder trigger, 4 viral thumbnail variations with bold high-CTR typography, and one-click copy YouTube upload metadata (`upload.txt` with title options, description, and chapters).
6. **Profiles**: Google Chrome automation profile manager (`acc1`, `acc2`), login validation, cookie management, session status.
7. **Veo Profiles**: Video motion model configuration (Google Veo 3 / 3.1 Lite prompt tuning, duration, aspect).
8. **Console**: Real-time terminal log stream from Python backend processes.

### 3.3 Main Configuration Modules (Production View)
- **Left Column: SCRIPT & VOICE**:
  - Script text editor with live pace & credit estimation (e.g., `About 2:20 at this pace · voice ready in ~2 min, -1,900 credits`).
  - Duration limiter / stretcher: `Make it [2] min [20] sec [Auto]`.
  - Saved script file picker (`-- Choose an existing script file --`).
  - Identifier input: `Project Name (Identifier)`.
  - Voice selector: Search & filter by `All`, `Favourites`, `Free`, `Hindi`, `My Clones`, `ElevenLabs`, `Minimax`, `English`.
  - Voice Model & Style selectors (`Eleven v4`, `Dramatic / thriller`, `Normal`).
  - Background music ducking toggle.
  - Browser profile picker (`acc1 (Primary)` + `Open & Login`).
  - Voiceover audio player with waveform & `Generate Voiceover Only` action.
- **Right Column: LOOK & STYLE**:
  - Visual Art Style selector with presets:
    - `3D Animated (Pixar / DreamWorks CGI Style)`
    - `2D Stickman (Moronomy Flat Vector)`
    - `Realistic / Cinematic Documentary`
    - `Playful Stick Figure Cartoon`
    - `Colorful Prehistoric`
    - `Finance Vector Storyboard`
    - `Vox Collage (Vox board)`
    - `Retro Space Collage (Vox board)`
    - Custom styles generated from the `+ New category` modal.
  - Aspect Ratio: `16:9 Landscape (YouTube 1080p)`, `9:16 Vertical (Shorts/Reels)`, `1:1 Square`.
  - Context prompt: `World / People (optional, auto from the script)`.
  - Character Reference Look: Turnaround selector, thumbnail preview, upload custom image button.
  - Reference Library: Clickable thumbnail carousel of 20+ standard character and environment reference assets.
  - Captions Preset Picker: Interactive preview cards for `Off`, `Simple`, `Simple Green`, `Bold Comic`, `Word Highlight`, `Karaoke Fill`, `Boxed`, `One Word Pop`.
- **Bottom Control Bar**:
  - Camera motion dropdown: `Ken Burns`, `Slow zoom in/out`, `Pan left/right`, `Drone rise`, `Crash zoom`, `No motion`, `Mix of all`.
  - Transitions dropdown: `Mix of all`, `Fade`, `Dissolve`, `Cut`.
  - Video model dropdown: `Off (picture...)`, `Veo 3.1 Lite`.
  - Motion speed dropdown: `Auto (motion...)`.
  - Master action button: **`Launch Full Video`** (giant yellow button), `Add to Queue`, `Verify`.

### 3.4 Modal Dialogues
1. **New Category Modal (Style Creator)**:
   - Text input for desired visual style.
   - Reference image uploader (up to 4 images).
   - Generates 8 sample variations (character turnaround, environment, close-up, action shot) with style breakdown and prompt formula before saving to library.
2. **All AI33 Voices Modal**:
   - Comprehensive voice catalog with search, language filters, and category tabs (`Favourites`, `Clones`, `ElevenLabs`, `Minimax`, `Free`).
   - Live sample audio playback and `[Use]` selection.
3. **Chrome Login Verification Modal**:
   - Prompts confirmation of Google account authentication before launching automated canvas generations.
4. **API Keys Settings Modal**:
   - Secure local storage for Gemini, ElevenLabs, OpenAI, OpenRouter, and Minimax API keys.

---

## 4. Technical File Structure Plan
```
StickFilm/
├── server.py                   # FastAPI / Python backend & HTTP API on port 5199
├── vidgen/
│   ├── pipeline.py             # 6-stage video creation pipeline CLI & engine
│   ├── voice_engine.py         # Voiceover synthesis (ElevenLabs, Edge-TTS, Minimax, audio ducking)
│   ├── alignment_engine.py     # Speech-to-text word alignment & shot timecode chunking
│   ├── prompt_engine.py        # Action-First prompt generation via LLM
│   ├── image_engine.py         # Canvas automation / Gemini Imagen 3 / local SD generator
│   ├── video_renderer.py       # FFmpeg master renderer (Ken Burns motion, karaoke captions, mux)
│   ├── thumbnail_engine.py     # Viral high-CTR YouTube thumbnail generator
│   └── metadata_engine.py      # YouTube upload.txt metadata & chapters generator
├── static/                     # Full Single Page Web Studio UI
│   ├── index.html              # Main Studio layout (Production, Studio, Image Wall, Deliverables, etc.)
│   ├── app.js                  # Frontend state machine, audio players, live monitors, modals
│   ├── styles.css              # Obsidian & Gold UI styling matching screenshots exactly
│   └── assets/
│       ├── refs/               # 20+ reference character turnarounds & styles
│       ├── audio_samples/      # Pre-generated voice previews
│       └── music/              # Royalty-free background music tracks
├── projects/                   # Saved project workspace directories
│   └── project_bhai_1/
│       ├── script.txt
│       ├── voiceover.mp3
│       ├── timestamps.json
│       ├── prompts.json
│       ├── shots/              # 55+ shot images
│       ├── thumbnails/         # 4 viral thumbnail variations
│       ├── output.mp4          # Final 1080p rendered video
│       └── upload.txt          # Ready-to-copy YouTube metadata
└── requirements.txt            # Python dependencies (fastapi, uvicorn, edge-tts, pillow, etc.)
```

---

## 5. Execution Strategy with Parallel Subagents
- **Agent 1 (Frontend UI Specialist)**: Builds the complete, pixel-perfect frontend interface in `static/index.html`, `static/styles.css`, and `static/app.js` replicating all 8 views, all modals, live canvas monitor, captions preview, and audio controls.
- **Agent 2 (Backend Core & Pipeline Specialist)**: Implements `server.py`, `vidgen/pipeline.py`, `vidgen/voice_engine.py`, `vidgen/alignment_engine.py`, and `vidgen/prompt_engine.py`.
- **Agent 3 (Rendering & Deliverables Specialist)**: Implements `vidgen/image_engine.py`, `vidgen/video_renderer.py`, `vidgen/thumbnail_engine.py`, `vidgen/metadata_engine.py`, reference asset library, and sample project data.
- **Main Agent (Integration & Verification)**: Orchestrates coordination, launches the server on `http://localhost:5199`, tests API endpoints, verifies UI responsiveness and end-to-end video production, and validates complete fidelity against user screenshots.
