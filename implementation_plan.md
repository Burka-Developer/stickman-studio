# 🎬 StickFilm AI Studio Pro — Full Implementation Plan

> After deep analysis of every line across **server.py** (1389 lines), **app.js** (2065 lines), **index.html** (1189 lines), **pipeline.py** (826 lines), and all engine modules.

---

## Architecture Summary

| Layer | File | Lines | Status |
|-------|------|-------|--------|
| Backend API | [server.py](file:///c:/Users/SSC/Desktop/Stickman/server.py) | 1,389 | ⚠️ Has issues |
| Frontend JS | [app.js](file:///c:/Users/SSC/Desktop/Stickman/static/app.js) | 2,065 | ⚠️ Has issues |
| HTML Shell | [index.html](file:///c:/Users/SSC/Desktop/Stickman/static/index.html) | 1,189 | ⚠️ Hardcoded data remains |
| Pipeline Engine | [pipeline.py](file:///c:/Users/SSC/Desktop/Stickman/vidgen/pipeline.py) | 826 | ✅ Working |
| Voice Engine | [voice_engine.py](file:///c:/Users/SSC/Desktop/Stickman/vidgen/voice_engine.py) | 30,801 bytes | ✅ Working |
| Image Engine | [image_engine.py](file:///c:/Users/SSC/Desktop/Stickman/vidgen/image_engine.py) | 49,214 bytes | ✅ Working |
| CSS Styles | [styles.css](file:///c:/Users/SSC/Desktop/Stickman/static/styles.css) | — | ✅ Working |

---

## 🔴 Critical Issues Found (Must Fix)

### Issue 1: Gemini Writer Uses Fake Hardcoded Script
**File:** [app.js:1968-1978](file:///c:/Users/SSC/Desktop/Stickman/static/app.js#L1968-L1978)
**Problem:** The "✨ Generate Full Script" button uses a `setTimeout` to paste a hardcoded Hindi paragraph instead of calling any AI API.
```javascript
// FAKE — just pastes static text after 1 second delay
dom.btnGenerateAiScript?.addEventListener("click", () => {
    setTimeout(() => {
        dom.aiScriptResult.value = `पूरा दुनिया बदल देने वाला...`; // HARDCODED
    }, 1000);
});
```
**Fix:** Create a `POST /api/script/generate` endpoint in `server.py` that calls `prompt_engine.generate_script()` using the Gemini API key from config, passing the topic, tone, and duration parameters from the modal.

---

### Issue 2: Voice Preview Falls Back to Fake Timer Simulation
**File:** [app.js:806-836](file:///c:/Users/SSC/Desktop/Stickman/static/app.js#L806-L836)
**Problem:** When the voice preview API call fails (no API key configured), it calls `simulateAudioPlayback(5)` which fakes a 5-second timer counting up — no audio is actually played.
**Fix:** Remove the `simulateAudioPlayback()` function entirely. When the preview API fails, show an error toast: "Configure API keys to enable voice preview" instead of faking playback.

---

### Issue 3: Audio Play/Pause Button Uses Fake Timer
**File:** [app.js:842-844](file:///c:/Users/SSC/Desktop/Stickman/static/app.js#L842-L844)
**Problem:** The main audio play/pause button (`btn-audio-play-pause`) calls `simulateAudioPlayback(128)` — a 128-second fake counter. It never plays the actual project voiceover audio.
**Fix:** Wire this button to play the actual voiceover file:
```javascript
dom.btnAudioPlayPause?.addEventListener("click", () => {
    const voiceUrl = `/projects/${state.activeProject}/voiceover.mp3`;
    if (state.audioElement.paused) {
        state.audioElement.src = voiceUrl;
        state.audioElement.play();
    } else {
        state.audioElement.pause();
    }
});
```
Also hook `state.audioElement` events (`timeupdate`, `ended`) to update the scrubber and timecode display in real-time.

---

### Issue 4: HTML Has Hardcoded Static Project Options
**File:** [index.html:31-35](file:///c:/Users/SSC/Desktop/Stickman/static/index.html#L31-L35)
**Problem:** The project `<select>` has 3 hardcoded `<option>` elements. While `app.js` overwrites them on load via `loadProjectsList()`, if the API fails the user sees stale fake data.
**Fix:** Remove all hardcoded `<option>` tags. Keep only the empty `<select>` — `app.js` will populate it dynamically.

---

### Issue 5: HTML Has Hardcoded Voice Options
**File:** [index.html:186-195](file:///c:/Users/SSC/Desktop/Stickman/static/index.html#L186-L195)
**Problem:** The voice `<select>` has 8 hardcoded voices. `app.js` does overwrite these, but they flash on initial load creating a FOUC (flash of unstyled content).
**Fix:** Remove all hardcoded `<option>` tags. Show a single loading placeholder: `<option value="">Loading voices...</option>`.

---

### Issue 6: HTML Has Hardcoded Browser Profile Options
**File:** [index.html:242-245](file:///c:/Users/SSC/Desktop/Stickman/static/index.html#L242-L245)
**Problem:** The browser profile `<select>` has hardcoded `acc1` and `acc2` options. `syncProfileDropdowns()` replaces them, but they still show first.
**Fix:** Remove hardcoded options. Let `loadProfiles()` populate dynamically.

---

### Issue 7: Deliverables Thumbnails Use Hardcoded Paths
**File:** [index.html:701-717](file:///c:/Users/SSC/Desktop/Stickman/static/index.html#L701-L717)
**Problem:** The 4 thumbnail cards hardcode `project_bhai_1` paths and static badge text like "THE SECRET TRUTH" / "CAN YOU SURVIVE?". These should load dynamically from the active project's `thumbnails/` directory.
**Fix:** Remove the static thumbnail HTML. Add a `renderThumbnails()` function in `app.js` that dynamically loads from `/projects/{id}/thumbnails/thumbnail_{1-4}.png` with cache-busting.

---

### Issue 8: Deliverables Video Player Hardcodes `project_bhai_1`
**File:** [index.html:681](file:///c:/Users/SSC/Desktop/Stickman/static/index.html#L681)
**Problem:** `<video src="/projects/project_bhai_1/output.mp4">` — hardcoded.
**Fix:** Set `src=""` in HTML. `loadDeliverables()` already sets the correct src dynamically.

---

### Issue 9: Style Sample Strip Uses Hardcoded Images
**File:** [index.html:316-319](file:///c:/Users/SSC/Desktop/Stickman/static/index.html#L316-L319)
**Problem:** 3 static `<img>` tags reference `138.png`, `139.png`, `140.png` hardcoded.
**Fix:** Populate this strip dynamically. When the art style changes, load the first 3 reference images from the current `refs/` directory, or generate style preview samples.

---

### Issue 10: New Category Modal Has Hardcoded Samples
**File:** [index.html:878-886](file:///c:/Users/SSC/Desktop/Stickman/static/index.html#L878-L886)
**Problem:** The 8-sample grid hardcodes `138.png` through `145.png`. The `btnCreateStyleSamples` handler calls the API but never updates these images.
**Fix:** After `POST /api/style/generate-samples` returns, update `#samples-8-grid-container` with the returned `image_url` values from the response.

---

### Issue 11: Console View Has Hardcoded Log Lines
**File:** [index.html:811-817](file:///c:/Users/SSC/Desktop/Stickman/static/index.html#L811-L817)
**Problem:** 7 static log lines are hardcoded in the console terminal body.
**Fix:** Remove them. Let `initializeStudio()` log real startup messages via `logConsole()`.

---

### Issue 12: `Project Clear All` Button Does Nothing
**File:** [index.html:38](file:///c:/Users/SSC/Desktop/Stickman/static/index.html#L38) and app.js has NO handler for `btn-project-clear`.
**Problem:** Button exists in UI but no event listener is attached.
**Fix:** Add handler in `app.js`:
```javascript
dom.btnProjectClear?.addEventListener("click", async () => {
    if (!confirm("Clear ALL assets in this project? Script, voice, shots, video — everything.")) return;
    // Delete and recreate project
    await fetch("/api/projects/delete", { method: "POST", ... });
    await fetch("/api/projects/create", { method: "POST", ... });
    showToast("Project assets cleared.", "gold");
});
```

---

### Issue 13: `btn-add-to-queue` Does Nothing Meaningful
**File:** [app.js](file:///c:/Users/SSC/Desktop/Stickman/static/app.js) — No handler found for `btn-add-to-queue`.
**Problem:** The "Add to Queue" button in the production dock has no event listener.
**Fix:** Add handler that saves current production settings and adds the project to the queue view.

---

### Issue 14: `btn-verify-integrity` Does Nothing
**File:** [index.html:446](file:///c:/Users/SSC/Desktop/Stickman/static/index.html#L446) — No handler in app.js.
**Problem:** "Verify" button exists but has no functionality.
**Fix:** Add handler that calls `GET /api/projects/{id}/shots` and verifies all shot images exist, reporting results via toast.

---

### Issue 15: `btn-create-project-id` Does Nothing
**File:** [app.js](file:///c:/Users/SSC/Desktop/Stickman/static/app.js) — No handler for `btn-create-project-id`.
**Problem:** The "Create Project" button next to the project name input has no listener.
**Fix:** Wire it to `POST /api/projects/create` using the value from `input-project-identifier`.

---

### Issue 16: Veo Settings Page Doesn't Read Input Values
**File:** [app.js:1764-1782](file:///c:/Users/SSC/Desktop/Stickman/static/app.js#L1764-L1782)
**Problem:** The "Save Veo Profile" handler hardcodes `motion_intensity: 8` and `negative_prompts` instead of reading from the actual HTML inputs (which are plain `<input type="range">` and `<textarea>` without IDs).
**Fix:** Add `id` attributes to the motion intensity slider and negative prompts textarea in `index.html`, then read their values in the save handler.

---

## 🟡 Moderate Issues

### Issue 17: `_generate_youtube_metadata` Missing in server.py
**File:** [server.py:1107](file:///c:/Users/SSC/Desktop/Stickman/server.py#L1107)
**Problem:** `render_changed` calls `pipeline._generate_youtube_metadata()` but pipeline.py only has `_generate_upload_metadata()`. This will throw an AttributeError.
**Fix:** Rename the call to `pipeline._generate_upload_metadata()`.

---

### Issue 18: Deliverables Thumbnails Not Rendered Dynamically  
**File:** [app.js:1684-1728](file:///c:/Users/SSC/Desktop/Stickman/static/app.js#L1684-L1728)
**Problem:** `loadDeliverables()` updates the video player and upload.txt, but never touches the thumbnail row. The 4 thumbnail cards stay hardcoded to `project_bhai_1`.
**Fix:** Add a `renderDeliverableThumbnails()` function that rebuilds the thumbnails row HTML using the active project.

---

### Issue 19: Queue "Pause All" and "Clear Finished" Buttons Do Nothing
**File:** `btn-queue-pause-all`, `btn-queue-clear-finished` — No handlers in app.js.
**Fix:** Add stub handlers with toasts, or implement actual queue management logic.

---

### Issue 20: WebSocket Connection Silently Fails Without Reconnect
**File:** [app.js:2020-2041](file:///c:/Users/SSC/Desktop/Stickman/static/app.js#L2020-L2041)
**Problem:** If WebSocket fails, `onerror` does nothing. No reconnection attempt.
**Fix:** Add reconnection logic with exponential backoff (1s, 2s, 4s, max 30s).

---

### Issue 21: Audio Scrub Slider Not Wired to Actual Audio Element
**File:** [app.js](file:///c:/Users/SSC/Desktop/Stickman/static/app.js)
**Problem:** The `audio-scrub-slider` range input exists but is only updated by the fake `simulateAudioPlayback` timer. It's not connected to `state.audioElement`.
**Fix:** Sync slider with the HTML5 Audio element's `currentTime` and `duration` properties.

---

## 🟢 Implementation Phases

### Phase 1: Remove ALL Hardcoded/Fake Data ⏱️ ~2 hours
| # | Task | File(s) |
|---|------|---------|
| 1.1 | Remove hardcoded project `<option>` tags | `index.html:31-35` |
| 1.2 | Remove hardcoded voice `<option>` tags | `index.html:186-195` |
| 1.3 | Remove hardcoded browser profile `<option>` tags | `index.html:242-245` |
| 1.4 | Remove hardcoded video player `src` | `index.html:681` |
| 1.5 | Remove hardcoded thumbnail cards | `index.html:701-717` |
| 1.6 | Remove hardcoded style sample strip images | `index.html:316-319` |
| 1.7 | Remove hardcoded sample grid in New Category modal | `index.html:878-886` |
| 1.8 | Remove hardcoded console log lines | `index.html:811-817` |
| 1.9 | Remove `simulateAudioPlayback()` function | `app.js:812-836` |
| 1.10 | Remove fallback to fake timer in `playVoicePreview()` | `app.js:806-809` |

### Phase 2: Wire Dead Buttons ⏱️ ~1.5 hours
| # | Task | File(s) |
|---|------|---------|
| 2.1 | Wire `btn-project-clear` → clear project assets | `app.js` |
| 2.2 | Wire `btn-create-project-id` → create project from input | `app.js` |
| 2.3 | Wire `btn-add-to-queue` → queue current project | `app.js` |
| 2.4 | Wire `btn-verify-integrity` → verify all shots exist | `app.js` |
| 2.5 | Wire `btn-queue-pause-all` → pause queue handler | `app.js` |
| 2.6 | Wire `btn-queue-clear-finished` → clear completed items | `app.js` |
| 2.7 | Add IDs to Veo inputs and wire save handler properly | `index.html` + `app.js` |

### Phase 3: Make Audio Playback Real ⏱️ ~1 hour
| # | Task | File(s) |
|---|------|---------|
| 3.1 | Wire `btn-audio-play-pause` to actual voiceover.mp3 | `app.js` |
| 3.2 | Sync `audio-scrub-slider` with `Audio.currentTime` | `app.js` |
| 3.3 | Update `audio-timecode` display from `timeupdate` event | `app.js` |
| 3.4 | Handle `btn-audio-mute` toggle | `app.js` |
| 3.5 | Update voiceover status badge after generation | `app.js` |

### Phase 4: Make Gemini Writer Real ⏱️ ~1.5 hours
| # | Task | File(s) |
|---|------|---------|
| 4.1 | Create `POST /api/script/generate` endpoint | `server.py` |
| 4.2 | Implement Gemini API call in prompt_engine | `prompt_engine.py` |
| 4.3 | Wire frontend button to real API | `app.js` |
| 4.4 | Handle API key not configured gracefully | `app.js` + `server.py` |

### Phase 5: Dynamic Deliverables ⏱️ ~1 hour
| # | Task | File(s) |
|---|------|---------|
| 5.1 | Create `renderDeliverableThumbnails()` function | `app.js` |
| 5.2 | Remove static thumbnail HTML | `index.html` |
| 5.3 | Load thumbnails from `/projects/{id}/thumbnails/` | `app.js` |
| 5.4 | Handle missing thumbnails gracefully | `app.js` |

### Phase 6: Fix Server Bugs ⏱️ ~30 min
| # | Task | File(s) |
|---|------|---------|
| 6.1 | Fix `_generate_youtube_metadata` → `_generate_upload_metadata` | `server.py:1107` |
| 6.2 | Add WebSocket reconnection logic | `app.js` |
| 6.3 | Ensure `loadDeliverables` handles missing video gracefully | `app.js` |

### Phase 7: Final Dynamic Style Samples ⏱️ ~45 min
| # | Task | File(s) |
|---|------|---------|
| 7.1 | Update style sample strip when art style changes | `app.js` |
| 7.2 | Update 8-grid samples after API call returns | `app.js` |
| 7.3 | Load style preview from `previews/` directory | `app.js` |

---

## Summary: What Needs to Change

| Metric | Count |
|--------|-------|
| **Critical bugs** (broken features) | 6 |
| **Dead buttons** (no handler) | 6 |
| **Hardcoded static data** to remove | 9 blocks |
| **Fake simulations** to replace | 3 |
| **Missing API endpoints** | 1 (`/api/script/generate`) |
| **Wrong method names** | 1 (`_generate_youtube_metadata`) |
| **Files to edit** | 3 (`server.py`, `app.js`, `index.html`) |
| **Estimated total work** | ~8 hours |

---

> [!IMPORTANT]
> All 21 issues are traced to exact file paths and line numbers. No new files need to be created — this is purely fixing the 3 core files to make the existing UI fully dynamic and functional.
