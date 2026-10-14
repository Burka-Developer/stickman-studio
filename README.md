# 🎬 StickFilm AI Studio Pro (v2.2.6)

> **All-in-One Desktop AI Film Studio** for YouTube creators, documentary channels, stickman animators, and faceless video production.
> Converts a raw script or topic into a published **1080p Full HD video** with synchronized voiceovers, word-highlighted karaoke captions, character-consistent visuals, dynamic camera motions, 4 viral YouTube thumbnails, and upload-ready SEO metadata.

---

## 📑 Table of Contents
1. [Overview & Architecture](#-overview--architecture)
2. [Prerequisites & System Setup](#-prerequisites--system-setup)
3. [Quick Start: Launching the Studio](#-quick-start-launching-the-studio)
4. [Full Step-by-Step Tutorial: Creating a Video](#-full-step-by-step-tutorial-creating-a-video)
5. [How to Add & Manage Chrome Profiles (Gemini Canvas)](#-how-to-add--manage-chrome-profiles-gemini-canvas)
6. [API Keys Section: Are They Working? (Detailed Breakdown)](#-api-keys-section-are-they-working-detailed-breakdown)
7. [The 8 Studio Views Explained](#-the-8-studio-views-explained)
8. [Troubleshooting & FAQs](#-troubleshooting--faqs)

---

## 🌟 Overview & Architecture

StickFilm AI Studio Pro runs locally on your machine with a high-performance **FastAPI backend (port 5199)** and a zero-latency **Single Page Studio UI**.

```
[Script / Topic] 
       │
       ▼
[Stage 1: Voiceover Engine]       ──► Edge-TTS / ElevenLabs (Hindi & English)
       │
       ▼
[Stage 2: Alignment Engine]       ──► Word-level millisecond timings & shot chunking
       │
       ▼
[Stage 3: Prompt Engine]          ──► Action-first visual prompts across 8 art styles
       │
       ▼
[Stage 4: Canvas Generation]      ──► Chrome Gemini Canvas (CDP:9222) OR Procedural Vector
       │
       ▼
[Stage 5: 0-Blanks Guard]         ──► Frame integrity verification (auto-heals blank shots)
       │
       ▼
[Stage 6: FFmpeg Compositor]      ──► 1080p MP4 + Ken Burns motions + 7 Subtitle styles
       │
       ▼
[Deliverables Package]            ──► Master MP4 + 4 Viral Thumbnails + upload.txt SEO
```

### Key Highlights
- **100% Free / Offline Capable:** Runs without paid APIs using built-in Edge-TTS voices and procedural visual synthesis.
- **Chrome Automation:** Connects to persistent Google Chrome sessions over CDP (port 9222) to generate images directly in Gemini Canvas.
- **7 Animated Caption Styles:** Word Highlight (gold active word), Bold Comic, Simple Green, Karaoke Fill, Boxed, One Word Pop, and Simple.
- **Selective Re-rendering:** Tweak or redraw individual shots in the Image Wall without having to regenerate audio or the entire video.

---

## ⚙️ Prerequisites & System Setup

### 1. Python 3.10 or Higher
Make sure Python is installed and added to your system `PATH`:
```bash
python --version
```

### 2. FFmpeg (Required for Video Rendering)
FFmpeg is required to assemble frames, animate subtitles, and mux audio:
- **Windows (winget):**
  ```powershell
  winget install Gyan.FFmpeg
  ```
- **Windows (Chocolatey):**
  ```powershell
  choco install ffmpeg
  ```
- Check that FFmpeg is accessible:
  ```powershell
  ffmpeg -version
  ```

### 3. Google Chrome (Optional, for Gemini Canvas Generation)
If you want to use Google Gemini Canvas automated generation, Google Chrome should be installed on your system.

### 4. Install Python Dependencies
Open PowerShell or Command Prompt in the project folder and run:
```powershell
pip install -r requirements.txt
```

---

## 🚀 Quick Start: Launching the Studio

1. Open your terminal in `C:\Users\SSC\Desktop\Stickman`:
   ```powershell
   python server.py
   ```
2. You will see the server startup log:
   ```text
   INFO:     Started server process
   INFO:     Waiting for application startup.
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://127.0.0.1:5199 (Press CTRL+C to quit)
   ```
3. Open your web browser and navigate to:
   ```
   http://localhost:5199
   ```
4. You will be greeted by the **StickFilm AI Studio Pro** dark dashboard!

---

## 🎬 Full Step-by-Step Tutorial: Creating a Video

### Step 1: Create or Select a Project
1. Look at the top project bar in the header: `PROJECT: [Dropdown]`.
2. Click **`[+ New]`** to create a new workspace (e.g., `my_first_documentary`).
3. Enter your project identifier and confirm. All assets (audio, shots, thumbnails, master video) will be isolated inside `projects/my_first_documentary/`.

### Step 2: Write or Generate a Script
On the left column (**SCRIPT & VOICE**):
- **Manual Input:** Type or paste your narration script directly into the text area.
- **AI Script Writer:**
  1. Click the **`[✨ Gemini Writer]`** button in the top navigation bar.
  2. Enter your video topic (e.g., *"How Humans Discovered Fire"*).
  3. Choose your narrative tone (`Hindi Cinematic Documentary`, `English Historical`, or `Fast Viral Short`).
  4. Set target duration (e.g., `120` seconds).
  5. Click **`Generate Script`**. The AI will generate a cinematic script and paste it into your editor.
- **Pacing & Duration:** The live pacing indicator shows estimated speaking duration and word count in real time.

### Step 3: Choose Your Narrator Voice
1. Filter voices using the category chips: `All`, `Hindi`, `English`, `Favourites`, `Free`.
2. Select a voice from the dropdown:
   - **Hindi (Free, No API Key):** `Krish` (warm storyteller), `Madhur` (deep narration), `Swara` (clear female), `Psi` (mystery/thriller).
   - **English (Free, No API Key):** `Jerry` (friendly documentary), `Guy`, `Christopher`.
   - **ElevenLabs (API Key required):** `Adam` (cinematic movie narrator), `Antoni`.
3. Click the **▶ Play Preview** button next to the voice to hear a sample.
4. Optional: Click **`Generate Voiceover Only`** if you want to pre-render and review the speech audio before building images.

### Step 4: Pick Art Style & Character Reference
On the right column (**LOOK & STYLE**):
1. **Visual Art Style:** Choose from the 8 presets:
   - `3D Animated (Pixar / DreamWorks CGI Style)`
   - `2D Stickman (Moronomy Flat Vector)`
   - `Realistic / Cinematic Documentary`
   - `Playful Stick Figure Cartoon`
   - `Colorful Prehistoric`
   - `Finance Vector Storyboard`
   - `Vox Collage (Vox board)`
   - `Retro Space Collage (Vox board)`
2. **Aspect Ratio:** Choose `16:9 Landscape (YouTube 1080p)` or `9:16 Vertical (Shorts/Reels)`.
3. **World / Setting:** Add optional atmospheric context (e.g., *"Primeval misty jungle with active volcanoes"*).
4. **Character Reference:** Select a character turnaround style or click **`[Upload Custom]`** to upload your own PNG/JPEG reference image.

### Step 5: Configure Captions & Camera Motion
At the bottom dock:
1. **Captions Preset:** Select your subtitle style:
   - `Word Highlight` *(Recommended: Gold highlight on the active spoken word)*
   - `Bold Comic` *(High contrast yellow with thick black outline)*
   - `Simple Green` / `Karaoke Fill` / `Boxed` / `One Word Pop` / `Off`
2. **Camera Motion:** Choose `Ken Burns`, `Slow zoom in/out`, `Pan left/right`, `Drone rise`, or `Mix of all`.
3. **Master Launch:** Click the big yellow **`🚀 Launch Full Video`** button!

### Step 6: Monitor Generation in the Studio View
The interface automatically transitions to the **STUDIO** view:
- **3x3 Live Monitor:** Displays generated visual frames in real-time as they are synthesized.
- **Stage Progress Cards:** Tracks execution through:
  - `Stage 1`: Voiceover synthesis
  - `Stage 2`: Millisecond word alignment & shot cuts
  - `Stage 3`: Action-first scene prompt generation
  - `Stage 4`: Canvas generation
  - `Stage 5`: 0-Blanks Guard integrity check
  - `Stage 6`: 1080p master video render & FFmpeg muxing

### Step 7: Inspect & Refine in Image Wall
Click the **IMAGE WALL** tab on the sidebar:
- View all scene shots arranged chronologically with their exact timecodes and subtitles.
- **Redraw a Shot:** If you don't like a specific image, click **`[Redraw]`** on that card. You can customize the prompt or let the AI re-synthesize it.
- **Upload Replacement:** Click **`[Upload]`** to drop your own custom image for that exact shot.
- **Quick Re-render:** Once satisfied, click the golden **`[🎬 Re-render Changed Shots]`** button at the top right of the Image Wall. FFmpeg will immediately re-composite your master video in seconds without touching your audio!

### Step 8: Download Deliverables & Publish
Click the **DELIVERABLES** tab:
1. **Master Video Player:** Watch the rendered 1080p Full HD video with captions and camera moves. Click **`Download MP4`** to save it.
2. **4 Viral Thumbnails:** Click on any of the 4 high-CTR thumbnail variations (*"THE SECRET TRUTH"*, *"WHO MADE IT FIRST?"*, *"HOW WE SURVIVED"*, *"CAN YOU SURVIVE?"*) to download.
3. **YouTube Metadata Box:** Click **`Copy Metadata`** to get your pre-formatted title options, SEO description, hashtags, and exact timestamped video chapters ready for YouTube Studio.

---

## 🌐 How to Add & Manage Chrome Profiles (Gemini Canvas)

StickFilm AI Studio Pro includes a built-in Chrome automation engine (`GeminiChromeEngine`) that controls real Google Chrome browser sessions with persistent cookies so you can generate images inside Gemini Canvas.

### Why Use Chrome Profiles?
Instead of paying for expensive image APIs, you can automate your logged-in Google account in Gemini Canvas. Persistent profiles save your cookies and login sessions in `data/chrome_profiles/` so you only have to log in once.

### Step-by-Step: Adding and Connecting a Profile

#### Method 1: Via the Studio UI (Recommended)
1. Open the Studio and click **`Profiles`** on the left navigation bar.
2. You will see existing profiles (`acc1`, `acc2`, `acc3`).
3. Click the **`[+ Add New Profile]`** button:
   - **Profile ID:** (e.g., `acc_creator`)
   - **Name:** (e.g., `Creator Main Account`)
   - **Google Email:** (e.g., `yourname@gmail.com`)
   - **Data Directory:** Leave empty to auto-assign to `data/chrome_profiles/acc_creator`, or specify a custom path.
   - **Notes:** (e.g., `Primary YouTube animation account`)
4. Click **`Save Profile`**.
5. Find your newly created profile card and click **`[🚀 Launch Browser]`** (or `Open & Login`):
   - The system launches Google Chrome with remote debugging on port **`9222`** and opens `https://gemini.google.com/app`.
6. **Log In:** In the opened Chrome window, log in to your Google Account.
7. Return to the Studio UI and click **`[✓ Verify Session]`**:
   - The status badge changes to **`Active`** (green) with your verified cookie count.
8. Click **`[Set as Active]`** to make this profile the default generator for your studio.

#### Method 2: Manual Terminal Launch
You can also launch your Chrome profile directly via Windows PowerShell:
```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" `
  --user-data-dir="C:\Users\SSC\Desktop\Stickman\data\chrome_profiles\acc1" `
  --remote-debugging-port=9222 `
  "https://gemini.google.com/app"
```
Once opened and logged in, StickFilm will automatically detect and connect to port `9222` over Chrome DevTools Protocol (CDP)!

> [!TIP]
> **What if Chrome is not open or not logged in?**  
> Don't worry! If Chrome is not connected or Gemini is unreachable, the system's Stage 4 engine **automatically falls back** to the procedural graphics engine. Your pipeline will **never crash** or halt.

---

## 🔑 API Keys Section: Are They Working? (Detailed Breakdown)

To check or update your API keys, click the **`[🔑 API Keys]`** button in the top navigation header.

Here is the exact technical reality of how every key is wired in the backend:

| API Key | Status in v2.2.6 | Where It Is Used | What Happens If Empty? |
|---|---|---|---|
| **Google Gemini (`gemini`)** | ✅ **WORKING** | `server.py:506` (`/api/script/generate`) for AI script generation in the Gemini Writer modal | Automatically falls back to the built-in local creative documentary engine |
| **ElevenLabs (`elevenlabs`)** | ✅ **WORKING** | `vidgen/voice_engine.py:503` for high-end cloned voices (e.g., `adam`, `antoni`) | Free Edge-TTS voices (`krish`, `madhur`, `jerry`, etc.) work with zero API key |
| **Minimax (`minimax`)** | ✅ **WORKING** | `vidgen/voice_engine.py:529` for Minimax speech API | Falls back to Edge-TTS voices |
| **OpenAI / OpenRouter (`openai`)** | ⚙️ **Configured & Stored** | Saved in `config.json` for custom LLM prompt generation | PromptEngine uses built-in cinematic formulas and camera staging presets |

### 1. Google Gemini API Key
- **Input Field:** `key-gemini` (Modal -> Google Gemini API Key)
- **Format:** Usually begins with `AIzaSy...` (from [Google AI Studio](https://aistudio.google.com/))
- **How it works:** When you click **Gemini Writer** and generate a script, `server.py` sends an HTTP POST request to:
  ```
  https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={YOUR_KEY}
  ```
- **Fallback:** If you leave it blank or don't have a key, the system uses its internal creative engine to write dramatic Hindi or English narration scripts based on your topic.
- **Canvas Generation Note:** Image generation in Gemini Canvas uses the **Chrome Profile (CDP)** browser session, not the REST API key.

### 2. ElevenLabs API Key
- **Input Field:** `key-elevenlabs`
- **Format:** `sk_...` (from [ElevenLabs](https://elevenlabs.io/))
- **How it works:** When you select an ElevenLabs voice (such as `adam`) and run voice generation, `voice_engine.py` passes your key in the `xi-api-key` header to synthesize ultra-realistic voices.
- **Fallback:** If left blank, you have full access to **7+ free neural voices** (`krish`, `madhur`, `swara`, `psi`, `alpha`, `beta`, `jerry`) via Edge-TTS without needing any API key or subscription!

### 3. Minimax API Key
- **Input Field:** `key-minimax`
- **How it works:** When using Minimax voice options, `voice_engine.py` passes the bearer token to Minimax T2A.
- **Fallback:** Free Edge-TTS fallback.

### 4. How Keys Are Saved & Masked
- When you click **`Save Keys`**, values are sent to `POST /api/apikeys` and securely saved inside `config.json`.
- The in-memory engines (`voice_engine`, `prompt_engine`) are reloaded immediately without restarting the server.
- Existing keys are masked in the UI (e.g., `AQ.A...9w`) for security. Submitting the modal will never overwrite an existing key with masked text.

---

## 🖥️ The 8 Studio Views Explained

| View | Purpose & Key Features |
|---|---|
| **1. Production** | Main creation workstation: script editor, duration slider, voice filter chips, art style presets, character turnaround reference carousel, caption preview cards, and master launch button. |
| **2. Studio** | Real-time generation monitor: 3x3 live canvas stream, stage 1 through 6 progress indicators with timestamps, and live runtime timer. |
| **3. Queue** | Multi-project batch queue: pause, resume, reorder, and render multiple video projects sequentially. |
| **4. Image Wall** | Shot-by-shot story grid: inspect all 55+ scenes, edit subtitles, edit prompts, redraw single shots, upload custom frames, and trigger fast re-renders. |
| **5. Deliverables** | Final publishing hub: 1080p video player, master MP4 download, 4 viral YouTube thumbnails, and copy-paste YouTube metadata (`upload.txt`). |
| **6. Profiles** | Chrome automation hub: create, edit, verify, and launch persistent Chrome profiles on port 9222. |
| **7. Veo Profiles** | Google Veo 3.1 Lite motion model configuration: motion intensity slider (1–10) and negative prompt tuning. |
| **8. Console** | Live terminal log stream: real-time Python and FFmpeg console output with color-coded level badges (`INFO`, `WARNING`, `ERROR`). |

---

## ❓ Troubleshooting & FAQs

### Q1: Can I use this tool completely free without paying for any APIs?
**Yes, 100%!**  
StickFilm AI Studio Pro is built specifically so creators don't need expensive subscriptions:
- **Narration:** Use the free voices (`Krish`, `Madhur`, `Jerry`, etc.) via Edge-TTS.
- **Visuals:** Use the procedural rendering engine or connect your free Google account via Chrome Profiles.
- **Subtitles & Video:** Rendered locally via FFmpeg on your own CPU/GPU.

### Q2: FFmpeg is showing an error during Stage 6. What should I do?
Make sure FFmpeg is installed and added to your system `PATH`:
1. Open PowerShell and run: `ffmpeg -version`.
2. If not recognized, install it using `winget install Gyan.FFmpeg` and restart your terminal.

### Q3: My voiceover preview or audio isn't playing.
1. Check that your browser tab isn't muted.
2. In the Production view, check the audio player scrubber next to the script editor.
3. If using an ElevenLabs voice without an API key, switch the voice dropdown to a free voice like **`Krish`** or **`Jerry`**.

### Q4: How do I change the visual theme?
Click the theme button on the top right of the header (`Obsidian Gold` / `Cyber Slate` / `Emerald Minimal`). Your preferred theme is saved automatically in `config.json` and persists across reloads.

### Q5: How do I run the automated verification test suite?
You can verify all endpoints, profiles, shots CRUD, and rendering by running the included test scripts:
```powershell
python test_app_dynamic.py
python test_fixes.py
```

---

*StickFilm AI Studio Pro v2.2.6 — Developed for Next-Gen Automated Creators.*
