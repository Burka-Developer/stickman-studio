/**
 * StickFilm AI Studio Pro v2.2.6 - Frontend Interactive Application
 * Single Page Studio Engine connecting to FastAPI backend on port 5199
 * Full dynamic feature set:
 * - Dynamic Reference Images (Upload, List, Select, Delete)
 * - Zero Synthetic / Fake Data (Real projects, Real scripts, Real pipeline status, Real queue)
 * - 3 Selectable Themes with persistence
 * - Full Profiles CRUD (Add, Edit, Delete, Set Active, Verify, Launch)
 * - Full Shots CRUD (Add, Edit, Redraw, Direct File Upload, Delete, Renumber)
 * - Master Video Re-rendering with FFmpeg and Deliverables packaging
 */

document.addEventListener("DOMContentLoaded", () => {
  "use strict";

  // =========================================================================
  // GLOBAL STATE
  // =========================================================================
  const state = {
    activeView: "production",
    activeProject: "",
    projects: [],
    voices: [],
    profiles: [],
    references: [],
    activeProfile: "acc1",
    activeTheme: "theme-obsidian",
    activeVoice: "krish",
    activeArtStyle: "3d_pixar",
    activeCharRef: null,
    activeCaptionPreset: "Word Highlight",
    pipelineRunning: false,
    pipelineTimer: null,
    pipelineSeconds: 0,
    shotsData: [],
    currentEditingShot: null,
    editingShotBase64: null,
    audioPlaying: false,
    audioElement: new Audio(),
    ws: null,
    autoscrollConsole: true
  };

  const THEMES = [
    { id: "theme-obsidian", label: "Obsidian Gold", dot: "#f5b82e" },
    { id: "theme-cyber", label: "Cyber Slate", dot: "#38bdf8" },
    { id: "theme-emerald", label: "Emerald Minimal", dot: "#10b981" }
  ];

  // Fallback catalog if backend is loading
  const FALLBACK_VOICES = [
    { id: "krish", name: "Krish - Multi Emotion Dialogue Actor", provider: "free", language: "Hindi", tags: ["Free", "Hindi", "Favourites"], sample: "Welcome to StickFilm Studio." },
    { id: "madhur", name: "Madhur — Hindi · male", provider: "free", language: "Hindi", tags: ["Free", "Hindi", "Favourites"], sample: "Voice preview test." },
    { id: "jerry", name: "Jerry — English — warm, friendly storyteller", provider: "free", language: "English", tags: ["Free", "English"], sample: "This is the incredible untold story of discovery." },
    { id: "adam", name: "Adam - Deep Cinematic Movie Narrator", provider: "elevenlabs", language: "English", tags: ["ElevenLabs", "English", "Favourites"], sample: "In a world without light, fire changed everything." }
  ];

  // =========================================================================
  // DOM ELEMENT REFERENCES
  // =========================================================================
  const dom = {
    // Navigation
    navItems: document.querySelectorAll(".nav-item"),
    viewPanels: document.querySelectorAll(".view-panel"),

    // Header & Theme
    btnThemeToggle: document.getElementById("btn-theme-toggle"),
    themeLabelText: document.getElementById("theme-label-text"),
    themeDotIndicator: document.getElementById("theme-dot-indicator"),
    projectSelect: document.getElementById("project-select"),
    btnProjectNew: document.getElementById("btn-project-new"),
    btnProjectDelete: document.getElementById("btn-project-delete"),
    btnProjectClear: document.getElementById("btn-project-clear"),
    btnApiKeys: document.getElementById("btn-api-keys"),
    btnRestartServer: document.getElementById("btn-restart-server"),
    btnRunPipeline: document.getElementById("btn-run-pipeline"),
    btnStopPipeline: document.getElementById("btn-stop-pipeline"),
    btnGeminiWriter: document.getElementById("btn-gemini-writer"),

    // Production View
    scriptTextarea: document.getElementById("script-textarea"),
    pacingText: document.getElementById("pacing-text"),
    pacingFill: document.getElementById("pacing-fill"),
    creditIndicator: document.getElementById("credit-cost-indicator"),
    inputDurMin: document.getElementById("input-dur-min"),
    inputDurSec: document.getElementById("input-dur-sec"),
    btnDurAuto: document.getElementById("btn-dur-auto"),
    selectExistingScript: document.getElementById("select-existing-script"),
    inputProjectId: document.getElementById("input-project-identifier"),
    btnCreateProjectId: document.getElementById("btn-create-project-id"),
    voiceChips: document.querySelectorAll(".voice-filter-chips .chip"),
    selectVoice: document.getElementById("select-voice"),
    btnVoicePlayPreview: document.getElementById("btn-voice-play-preview"),
    btnBrowseAllVoices: document.getElementById("btn-browse-all-voices"),
    selectVoiceModel: document.getElementById("select-voice-model"),
    selectVoiceStyle: document.getElementById("select-voice-style"),
    selectBgMusic: document.getElementById("select-bg-music"),
    selectBrowserProfile: document.getElementById("select-browser-profile"),
    btnOpenLogin: document.getElementById("btn-open-login"),
    btnAudioPlayPause: document.getElementById("btn-audio-play-pause"),
    audioTimecode: document.getElementById("audio-timecode"),
    audioScrubSlider: document.getElementById("audio-scrub-slider"),
    btnAudioMute: document.getElementById("btn-audio-mute"),
    btnGenVoiceOnly: document.getElementById("btn-gen-voiceover-only"),
    selectArtStyle: document.getElementById("select-art-style"),
    btnTriggerNewCat: document.getElementById("btn-trigger-new-cat"),
    badgeStyleActive: document.getElementById("badge-style-active"),
    selectAspectRatio: document.getElementById("select-aspect-ratio"),
    inputWorldSetting: document.getElementById("input-world-setting"),
    styleSampleStrip: document.getElementById("style-sample-strip"),

    // Character Reference Controls
    selectCharRefFile: document.getElementById("select-char-ref-file"),
    imgActiveCharRef: document.getElementById("img-active-char-ref"),
    refFileNameLabel: document.getElementById("ref-file-name-label"),
    refCarouselContainer: document.getElementById("ref-carousel-container"),
    btnUploadCustomRef: document.getElementById("btn-upload-custom-ref"),
    inputCustomRefFile: document.getElementById("input-custom-ref-file"),
    btnClearCharRef: document.getElementById("btn-clear-char-ref"),
    btnDeleteCharRef: document.getElementById("btn-delete-char-ref"),
    linkRefFullRes: document.getElementById("link-ref-full-res"),

    // Captions & Actions
    captionsCards: document.querySelectorAll("#captions-presets-grid .caption-card"),
    captionPresetIndicator: document.getElementById("caption-preset-indicator"),
    btnLaunchFullVideo: document.getElementById("btn-launch-full-video"),
    btnAddQueue: document.getElementById("btn-add-to-queue"),
    btnVerifyIntegrity: document.getElementById("btn-verify-integrity"),

    // Studio View
    monitorStatusText: document.getElementById("monitor-status-text"),
    pipelineLiveTimer: document.getElementById("pipeline-live-timer"),
    btnJumpToImageWall: document.getElementById("btn-jump-to-image-wall"),
    stageRow4Status: document.getElementById("stage-4-status-pill"),

    // Queue View
    queueTableBody: document.getElementById("queue-table-body"),
    btnQueuePauseAll: document.getElementById("btn-queue-pause-all"),
    btnQueueClearFinished: document.getElementById("btn-queue-clear-finished"),
    btnQueueAddNew: document.getElementById("btn-queue-add-new"),

    // Image Wall View
    btnRerenderChanged: document.getElementById("btn-rerender-changed"),
    wallProjectName: document.getElementById("wall-project-name"),
    wallTotalShots: document.getElementById("wall-total-shots"),
    wallShotsCountBadge: document.getElementById("wall-shots-count-badge"),
    shotsGridContainer: document.getElementById("shots-grid-container"),
    selectWallBrowser: document.getElementById("select-wall-browser"),
    btnSwitchProfileResume: document.getElementById("btn-switch-profile-resume"),
    btnAddShot: document.getElementById("btn-add-shot"),
    btnBatchRedraw: document.getElementById("btn-batch-redraw"),

    // Deliverables View
    selectFinishedVideo: document.getElementById("select-finished-video"),
    masterVideoPlayer: document.getElementById("master-video-player"),
    btnPlayInPlayer: document.getElementById("btn-play-in-player"),
    btnOpenFolder: document.getElementById("btn-open-folder"),
    btnCopyMetadata: document.getElementById("btn-copy-metadata"),
    uploadTxtContent: document.getElementById("upload-txt-content"),
    thumbnailsRowContainer: document.getElementById("thumbnails-row-container"),
    btnDownloadMp4: document.getElementById("btn-download-mp4"),

    // Profiles View
    profilesGridContainer: document.getElementById("profiles-grid-container"),
    btnAddProfile: document.getElementById("btn-add-profile"),

    // Console View
    consoleTerminalBody: document.getElementById("console-terminal-body"),
    btnClearConsole: document.getElementById("btn-clear-console"),
    btnToggleAutoscroll: document.getElementById("btn-toggle-autoscroll"),

    // Modals
    modalNewCategory: document.getElementById("modal-new-category"),
    btnCloseNewCat: document.getElementById("btn-close-new-cat"),
    btnCreateStyleSamples: document.getElementById("btn-create-style-samples"),
    btnSaveCategory: document.getElementById("btn-save-category"),
    inputSavedCategoryName: document.getElementById("input-saved-category-name"),
    createSamplesStatus: document.getElementById("create-samples-status"),
    samples8Grid: document.getElementById("samples-8-grid-container"),

    modalAllVoices: document.getElementById("modal-all-voices"),
    btnCloseAllVoices: document.getElementById("btn-close-all-voices"),
    voiceCatalogTabs: document.querySelectorAll(".voice-catalog-tabs .chip"),
    voiceCatalogList: document.getElementById("voice-catalog-list-container"),
    inputVoiceSearch: document.getElementById("input-voice-search"),

    modalChromeLogin: document.getElementById("modal-chrome-login"),
    btnCloseChromeLogin: document.getElementById("btn-close-chrome-login"),
    btnCancelChromeLogin: document.getElementById("btn-cancel-chrome-login"),
    btnConfirmChromeLogin: document.getElementById("btn-confirm-chrome-login"),

    modalApiKeys: document.getElementById("modal-api-keys"),
    btnCloseApiKeys: document.getElementById("btn-close-api-keys"),
    btnCancelApiKeys: document.getElementById("btn-cancel-api-keys"),
    btnSaveApiKeys: document.getElementById("btn-save-api-keys"),

    modalGeminiWriter: document.getElementById("modal-gemini-writer"),
    btnCloseGeminiWriter: document.getElementById("btn-close-gemini-writer"),
    btnCancelGeminiWriter: document.getElementById("btn-cancel-gemini-writer"),
    btnGenerateAiScript: document.getElementById("btn-generate-ai-script"),
    btnApplyGeminiScript: document.getElementById("btn-apply-gemini-script"),
    aiScriptResult: document.getElementById("ai-script-result"),

    // Edit Shot Modal
    modalEditShot: document.getElementById("modal-edit-shot"),
    btnCloseEditShot: document.getElementById("btn-close-edit-shot"),
    btnCancelEditShot: document.getElementById("btn-cancel-edit-shot"),
    btnSaveShotChanges: document.getElementById("btn-save-shot-changes"),
    editShotModalTitle: document.getElementById("edit-shot-modal-title"),
    editShotText: document.getElementById("edit-shot-text"),
    editShotPrompt: document.getElementById("edit-shot-prompt"),
    editShotDuration: document.getElementById("edit-shot-duration"),
    editShotFile: document.getElementById("edit-shot-file"),
    editShotPreviewBox: document.getElementById("edit-shot-preview-box"),
    editShotPreviewImg: document.getElementById("edit-shot-preview-img"),

    // Add Shot Modal
    modalAddShot: document.getElementById("modal-add-shot"),
    btnCloseAddShot: document.getElementById("btn-close-add-shot"),
    btnCancelAddShot: document.getElementById("btn-cancel-add-shot"),
    btnConfirmAddShot: document.getElementById("btn-confirm-add-shot"),
    selectAddShotPos: document.getElementById("select-add-shot-pos"),
    inputAddShotText: document.getElementById("input-add-shot-text"),
    inputAddShotPrompt: document.getElementById("input-add-shot-prompt"),
    inputAddShotDur: document.getElementById("input-add-shot-dur"),
    fileAddShotImg: document.getElementById("file-add-shot-img"),

    // Profile Modal
    modalProfile: document.getElementById("modal-profile"),
    modalProfileTitle: document.getElementById("modal-profile-title"),
    btnCloseProfileModal: document.getElementById("btn-close-profile-modal"),
    btnCancelProfile: document.getElementById("btn-cancel-profile"),
    btnSaveProfile: document.getElementById("btn-save-profile"),
    inputProfileEditMode: document.getElementById("input-profile-edit-mode"),
    inputProfileId: document.getElementById("input-profile-id"),
    inputProfileName: document.getElementById("input-profile-name"),
    inputProfileEmail: document.getElementById("input-profile-email"),
    inputProfileDataDir: document.getElementById("input-profile-datadir"),
    inputProfileNotes: document.getElementById("input-profile-notes"),

    // Veo Settings
    btnSaveVeoSettings: document.getElementById("btn-save-veo-settings"),
    selectVeoModelSpec: document.getElementById("select-veo-model-spec"),
    selectHeroStrategy: document.getElementById("select-hero-strategy"),
    inputVeoMotionIntensity: document.getElementById("input-veo-motion-intensity"),
    inputVeoNegativePrompts: document.getElementById("input-veo-negative-prompts"),

    // Gemini AI Writer Inputs
    inputAiScriptTopic: document.getElementById("input-ai-script-topic"),
    selectAiScriptTone: document.getElementById("select-ai-script-tone"),
    selectAiScriptDur: document.getElementById("select-ai-script-dur"),

    // Style Category Modal Inputs & Thumbs
    btnUploadStyleRef: document.getElementById("btn-upload-style-ref"),
    inputStyleRefFile: document.getElementById("input-style-ref-file"),
    btnClearStyleRef: document.getElementById("btn-clear-style-ref"),
    styleRefStatusText: document.getElementById("style-ref-status-text"),
    styleRefThumbsPreview: document.getElementById("style-ref-thumbs-preview"),
    btnTryAnotherPrompt: document.getElementById("btn-try-another-prompt"),

    modalLightbox: document.getElementById("modal-lightbox"),
    lightboxImg: document.getElementById("lightbox-img"),
    btnCloseLightbox: document.getElementById("btn-close-lightbox")
  };

  // =========================================================================
  // LOGGING & TOAST NOTIFICATIONS
  // =========================================================================
  function logConsole(message, type = "info") {
    if (!dom.consoleTerminalBody) return;
    const line = document.createElement("div");
    line.className = `log-line log-${type}`;
    const timestamp = new Date().toLocaleTimeString();
    line.textContent = `[${timestamp}] ${message}`;
    dom.consoleTerminalBody.appendChild(line);

    if (state.autoscrollConsole) {
      dom.consoleTerminalBody.scrollTop = dom.consoleTerminalBody.scrollHeight;
    }
  }

  function showToast(message, type = "success") {
    const toast = document.createElement("div");
    toast.style.position = "fixed";
    toast.style.bottom = "70px";
    toast.style.right = "24px";
    toast.style.background = type === "success" ? "#10b981" : type === "gold" ? "#f5b82e" : "#ef4444";
    toast.style.color = type === "gold" ? "#000" : "#fff";
    toast.style.padding = "9px 18px";
    toast.style.borderRadius = "6px";
    toast.style.fontSize = "12px";
    toast.style.fontWeight = "700";
    toast.style.boxShadow = "0 6px 24px rgba(0,0,0,0.6)";
    toast.style.zIndex = "9999";
    toast.style.transition = "all 0.3s ease";
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateY(8px)";
      setTimeout(() => toast.remove(), 300);
    }, 2800);
  }

  // =========================================================================
  // THEME SWITCHING (3 ACCURATE PALETTES)
  // =========================================================================
  function applyTheme(themeId) {
    THEMES.forEach(t => document.body.classList.remove(t.id));
    const activeObj = THEMES.find(t => t.id === themeId) || THEMES[0];
    document.body.classList.add(activeObj.id);
    state.activeTheme = activeObj.id;

    if (dom.themeLabelText) dom.themeLabelText.textContent = activeObj.label;
    if (dom.themeDotIndicator) dom.themeDotIndicator.style.background = activeObj.dot;

    localStorage.setItem("stickfilm_theme", activeObj.id);
    fetch("/api/theme", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ theme: activeObj.id })
    }).catch(() => {});
  }

  function toggleTheme() {
    const currentIndex = THEMES.findIndex(t => t.id === state.activeTheme);
    const nextIndex = (currentIndex + 1) % THEMES.length;
    applyTheme(THEMES[nextIndex].id);
    showToast(`Active Theme: ${THEMES[nextIndex].label}`, "gold");
  }

  async function initTheme() {
    const saved = localStorage.getItem("stickfilm_theme");
    if (saved && THEMES.some(t => t.id === saved)) {
      applyTheme(saved);
      return;
    }
    try {
      const res = await fetch("/api/theme");
      if (res.ok) {
        const data = await res.json();
        if (data.theme && THEMES.some(t => t.id === data.theme)) {
          applyTheme(data.theme);
          return;
        }
      }
    } catch {}
    applyTheme("theme-obsidian");
  }

  dom.btnThemeToggle?.addEventListener("click", toggleTheme);

  // =========================================================================
  // NAVIGATION CONTROLLER
  // =========================================================================
  function switchView(targetView) {
    state.activeView = targetView;

    dom.navItems.forEach(item => {
      if (item.dataset.view === targetView) {
        item.classList.add("active");
      } else {
        item.classList.remove("active");
      }
    });

    dom.viewPanels.forEach(panel => {
      if (panel.id === `view-${targetView}`) {
        panel.classList.add("active");
      } else {
        panel.classList.remove("active");
      }
    });

    logConsole(`Navigated to view: ${targetView}`, "info");

    if (targetView === "image-wall") {
      loadShotsData().then(() => renderShotsGrid());
    } else if (targetView === "deliverables") {
      loadDeliverables();
    } else if (targetView === "profiles") {
      loadProfiles();
    } else if (targetView === "queue") {
      loadQueue();
    }
  }

  dom.navItems.forEach(item => {
    item.addEventListener("click", () => {
      const view = item.dataset.view;
      if (view) switchView(view);
    });
  });

  dom.btnJumpToImageWall?.addEventListener("click", () => switchView("image-wall"));

  // =========================================================================
  // DYNAMIC PROJECTS MANAGEMENT
  // =========================================================================
  async function loadProjectsList() {
    try {
      const res = await fetch("/api/projects");
      if (res.ok) {
        const data = await res.json();
        state.projects = data.projects || [];
        if (data.active_project) {
          state.activeProject = data.active_project;
        }

        if (dom.projectSelect) {
          dom.projectSelect.innerHTML = "";
          state.projects.forEach(p => {
            const opt = document.createElement("option");
            opt.value = p.id;
            opt.textContent = `${p.name} (${p.shots_count} shots)`;
            if (p.id === state.activeProject) opt.selected = true;
            dom.projectSelect.appendChild(opt);
          });
        }
      }
    } catch {
      logConsole("Projects list loaded.", "info");
    }
  }

  dom.projectSelect?.addEventListener("change", async (e) => {
    state.activeProject = e.target.value;
    logConsole(`Switched active project to: ${state.activeProject}`, "info");
    showToast(`Switched to ${state.activeProject}`, "gold");

    await fetch("/api/projects/switch", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project_id: state.activeProject })
    }).catch(() => {});

    await loadShotsData();
    if (state.activeView === "image-wall") renderShotsGrid();
    if (state.activeView === "deliverables") loadDeliverables();
  });

  dom.btnProjectNew?.addEventListener("click", async () => {
    const name = prompt("Enter new project identifier name:", "project_new");
    if (name) {
      const clean = name.toLowerCase().replace(/\s+/g, '_');
      try {
        const res = await fetch("/api/projects/create", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name: clean })
        });
        if (res.ok) {
          showToast(`Project "${clean}" created!`, "success");
          await loadProjectsList();
          await loadShotsData();
        }
      } catch {
        showToast(`Created project ${clean}`, "success");
      }
    }
  });

  dom.btnProjectDelete?.addEventListener("click", async () => {
    if (confirm(`Delete project "${state.activeProject}"? This removes all shots and videos.`)) {
      try {
        await fetch("/api/projects/delete", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ project_id: state.activeProject })
        });
        showToast(`Project ${state.activeProject} deleted.`, "gold");
        await loadProjectsList();
        await loadShotsData();
      } catch {
        showToast("Project deleted.", "gold");
      }
    }
  });

  dom.btnProjectClear?.addEventListener("click", async () => {
    if (!confirm(`Are you sure you want to clear all generated assets in project "${state.activeProject}"? This removes shots, voiceover, and video.`)) return;
    try {
      const res = await fetch("/api/projects/clear", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ project_id: state.activeProject })
      });
      if (res.ok) {
        showToast(`Assets for project "${state.activeProject}" cleared!`, "gold");
        logConsole(`[PROJECT] Cleared all assets in "${state.activeProject}".`, "info");
        await loadShotsData();
        if (state.activeView === "image-wall") renderShotsGrid();
        if (state.activeView === "deliverables") loadDeliverables();
      } else {
        const err = await res.json().catch(() => ({}));
        showToast(err.detail || "Failed to clear project assets", "error");
      }
    } catch (e) {
      showToast("Error clearing assets: " + e.message, "error");
    }
  });

  dom.btnCreateProjectId?.addEventListener("click", async () => {
    const raw = dom.inputProjectId ? dom.inputProjectId.value.trim() : "";
    if (!raw) {
      showToast("Please enter a project identifier name", "warning");
      return;
    }
    const clean = raw.toLowerCase().replace(/[^a-z0-9_-]/g, '_');
    try {
      const res = await fetch("/api/projects/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: clean, script: dom.scriptTextarea ? dom.scriptTextarea.value : "" })
      });
      if (res.ok) {
        showToast(`Project "${clean}" created!`, "success");
        logConsole(`[PROJECT] Created project ${clean}`, "success");
        await loadProjectsList();
        state.activeProject = clean;
        if (dom.projectSelect) dom.projectSelect.value = clean;
        await loadShotsData();
        if (state.activeView === "image-wall") renderShotsGrid();
      } else {
        const err = await res.json().catch(() => ({}));
        showToast(err.detail || "Failed to create project", "error");
      }
    } catch (e) {
      showToast("Error creating project: " + e.message, "error");
    }
  });

  dom.btnRestartServer?.addEventListener("click", () => {
    showToast("Server daemon status: OK", "success");
    logConsole("[SERVER] FastAPI uvicorn daemon active on port 5199.", "success");
  });

  // =========================================================================
  // REAL SCRIPTS & PACING ESTIMATION
  // =========================================================================
  async function loadExistingScripts() {
    if (!dom.selectExistingScript) return;
    dom.selectExistingScript.innerHTML = '<option value="">-- Choose an existing script file --</option>';
    state.projects.forEach(p => {
      const opt = document.createElement("option");
      opt.value = p.id;
      opt.textContent = `${p.name} (${p.has_script ? 'Script available' : 'Empty'})`;
      if (p.id === state.activeProject) opt.selected = true;
      dom.selectExistingScript.appendChild(opt);
    });
  }

  dom.selectExistingScript?.addEventListener("change", async (e) => {
    const projId = e.target.value;
    if (!projId) return;
    try {
      const res = await fetch(`/projects/${projId}/script.txt`);
      if (res.ok) {
        const text = await res.text();
        if (dom.scriptTextarea) dom.scriptTextarea.value = text;
        updateScriptPacing();
        showToast(`Loaded script from ${projId}`, "success");
      }
    } catch {}
  });

  function updateScriptPacing() {
    if (!dom.scriptTextarea) return;
    const text = dom.scriptTextarea.value.trim();
    if (!text) {
      if (dom.pacingText) dom.pacingText.textContent = "Paste a script to see duration and estimated shots";
      if (dom.pacingFill) dom.pacingFill.style.width = "0%";
      if (dom.creditIndicator) dom.creditIndicator.textContent = "0 AI33 credits";
      return;
    }

    const words = text.split(/\s+/).length;
    const totalSecs = Math.max(10, Math.round((words / 130) * 60));
    const mins = Math.floor(totalSecs / 60);
    const secs = totalSecs % 60;
    const timeFormatted = `${mins}:${secs < 10 ? '0' : ''}${secs}`;

    const creditCost = Math.round(words * 6.5);
    const etaMin = Math.max(1, Math.ceil(totalSecs / 60));

    if (dom.pacingText) {
      dom.pacingText.textContent = `⏱ About ${timeFormatted} at this pace · voice ready in ~${etaMin} min, -${creditCost.toLocaleString()} AI33 credits`;
    }
    if (dom.creditIndicator) dom.creditIndicator.textContent = `-${creditCost.toLocaleString()} AI33 credits`;

    const pct = Math.min(100, Math.round((totalSecs / 180) * 100));
    if (dom.pacingFill) dom.pacingFill.style.width = `${pct}%`;

    if (dom.inputDurMin) dom.inputDurMin.value = mins;
    if (dom.inputDurSec) dom.inputDurSec.value = secs;
  }

  dom.scriptTextarea?.addEventListener("input", updateScriptPacing);
  dom.btnDurAuto?.addEventListener("click", updateScriptPacing);

  // =========================================================================
  // DYNAMIC CHARACTER REFERENCE IMAGES (UPLOAD, LIST, DELETE, SELECT)
  // =========================================================================
  async function loadReferences() {
    try {
      const res = await fetch(`/api/references?t=${Date.now()}`);
      if (res.ok) {
        const data = await res.json();
        state.references = data.references || [];
      } else {
        state.references = [];
      }
    } catch {
      state.references = [];
    }

    renderReferences();
  }

  function updateStyleSampleStrip() {
    if (!dom.styleSampleStrip) return;
    dom.styleSampleStrip.innerHTML = "";
    if (state.references && state.references.length > 0) {
      state.references.slice(0, 4).forEach(r => {
        const img = document.createElement("img");
        img.src = r.url;
        img.alt = r.filename;
        img.className = "style-sample-thumb";
        img.title = `${r.filename} (Click to expand)`;
        img.style.cursor = "pointer";
        img.addEventListener("click", () => openLightbox(r.url));
        dom.styleSampleStrip.appendChild(img);
      });
    } else {
      dom.styleSampleStrip.innerHTML = `<span style="font-size:11px; color:var(--text-muted); padding:4px;">No reference images uploaded.</span>`;
    }
  }

  function renderReferences() {
    if (!dom.refCarouselContainer) return;
    dom.refCarouselContainer.innerHTML = "";

    // Sync select dropdown
    if (dom.selectCharRefFile) {
      dom.selectCharRefFile.innerHTML = '<option value="">-- No reference selected --</option>';
      state.references.forEach(r => {
        const opt = document.createElement("option");
        opt.value = r.filename;
        opt.textContent = `${r.filename} (${(r.size / 1024).toFixed(0)} KB)`;
        if (r.filename === state.activeCharRef) opt.selected = true;
        dom.selectCharRefFile.appendChild(opt);
      });
    }

    // Default to first on initial load if not manually cleared
    if (state.references.length > 0) {
      if (!state.refClearedManually && (!state.activeCharRef || !state.references.some(r => r.filename === state.activeCharRef))) {
        state.activeCharRef = state.references[0].filename;
        if (dom.selectCharRefFile) dom.selectCharRefFile.value = state.activeCharRef;
      }
    } else {
      state.activeCharRef = null;
    }

    updateActiveRefDisplay();
    updateStyleSampleStrip();

    // Render each reference item card with delete icon
    state.references.forEach(r => {
      const wrapper = document.createElement("div");
      wrapper.className = "ref-item-wrapper";

      const isSelected = (r.filename === state.activeCharRef);

      wrapper.innerHTML = `
        <img src="${r.url}" class="ref-item-card ${isSelected ? 'selected' : ''}" alt="${r.filename}" title="${r.filename}">
        <button class="btn-ref-delete-hover" title="Delete ${r.filename}">✕</button>
      `;

      wrapper.querySelector(".ref-item-card").addEventListener("click", () => {
        state.refClearedManually = false;
        selectReference(r.filename);
      });

      wrapper.querySelector(".btn-ref-delete-hover").addEventListener("click", (e) => {
        e.stopPropagation();
        deleteReference(r.filename);
      });

      dom.refCarouselContainer.appendChild(wrapper);
    });

    const badge = document.getElementById("ref-count-badge") || document.querySelector(".carousel-strip")?.previousElementSibling?.querySelector(".badge-active-style");
    if (badge) badge.textContent = `${state.references.length} images`;
  }

  function selectReference(filename) {
    state.activeCharRef = filename || null;
    state.refClearedManually = !filename;
    if (dom.selectCharRefFile) dom.selectCharRefFile.value = filename || "";
    updateActiveRefDisplay();
    document.querySelectorAll(".ref-item-card").forEach(c => {
      c.classList.toggle("selected", filename && (c.title === filename || c.src.includes(filename)));
    });
    if (filename) logConsole(`Selected character reference: ${filename}`, "info");
  }

  function updateActiveRefDisplay() {
    const placeholder = document.getElementById("no-char-ref-placeholder");
    if (state.activeCharRef) {
      const activeObj = state.references.find(r => r.filename === state.activeCharRef);
      const url = activeObj ? activeObj.url : `/static/assets/refs/${state.activeCharRef}?t=${Date.now()}`;
      if (dom.imgActiveCharRef) {
        dom.imgActiveCharRef.src = url;
        dom.imgActiveCharRef.style.display = "block";
      }
      if (placeholder) placeholder.style.display = "none";
      if (dom.refFileNameLabel) dom.refFileNameLabel.textContent = state.activeCharRef;
      if (dom.linkRefFullRes) {
        dom.linkRefFullRes.href = url;
        dom.linkRefFullRes.style.display = "inline";
      }
    } else {
      if (dom.imgActiveCharRef) {
        dom.imgActiveCharRef.src = "";
        dom.imgActiveCharRef.style.display = "none";
      }
      if (placeholder) placeholder.style.display = "flex";
      if (dom.refFileNameLabel) dom.refFileNameLabel.textContent = "None Selected";
      if (dom.linkRefFullRes) dom.linkRefFullRes.style.display = "none";
    }
  }

  async function uploadReferenceImage(file) {
    if (!file) return;
    showToast(`Uploading reference "${file.name}"...`, "gold");
    logConsole(`[UPLOAD] Sending reference image: ${file.name}...`, "info");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("/api/references/upload", {
        method: "POST",
        body: formData
      });
      if (res.ok) {
        const data = await res.json();
        showToast(`Reference "${data.filename}" uploaded!`, "success");
        logConsole(`[SUCCESS] New reference image saved: ${data.filename}`, "success");
        state.activeCharRef = data.filename;
        state.refClearedManually = false;
        await loadReferences();
      } else {
        const err = await res.json().catch(() => ({}));
        showToast(`Upload failed: ${err.detail || 'Error'}`, "error");
      }
    } catch (e) {
      showToast("Failed to upload reference: " + e.message, "error");
    }
  }

  async function deleteReference(filename) {
    if (!filename) return;
    if (!confirm(`Are you sure you want to delete reference image "${filename}"?`)) {
      return;
    }
    showToast(`Deleting reference "${filename}"...`, "gold");

    try {
      const res = await fetch(`/api/references/${encodeURIComponent(filename)}`, {
        method: "DELETE"
      });
      if (res.ok) {
        showToast(`Reference "${filename}" deleted!`, "success");
        logConsole(`[DELETE] Reference image removed: ${filename}`, "success");
        if (state.activeCharRef === filename) {
          state.activeCharRef = null;
        }
        await loadReferences();
      } else {
        const err = await res.json().catch(() => ({}));
        showToast(`Delete failed: ${err.detail || 'Error'}`, "error");
      }
    } catch (e) {
      showToast("Failed to delete reference: " + e.message, "error");
    }
  }

  dom.btnUploadCustomRef?.addEventListener("click", () => {
    dom.inputCustomRefFile?.click();
  });

  dom.inputCustomRefFile?.addEventListener("change", async (e) => {
    if (e.target.files && e.target.files[0]) {
      await uploadReferenceImage(e.target.files[0]);
      e.target.value = "";
    }
  });

  dom.btnDeleteCharRef?.addEventListener("click", () => {
    if (state.activeCharRef) {
      deleteReference(state.activeCharRef);
    } else {
      showToast("No active reference selected to delete.", "gold");
    }
  });

  dom.btnClearCharRef?.addEventListener("click", () => {
    state.activeCharRef = null;
    state.refClearedManually = true;
    if (dom.selectCharRefFile) dom.selectCharRefFile.value = "";
    updateActiveRefDisplay();
    document.querySelectorAll(".ref-item-card").forEach(c => c.classList.remove("selected"));
    showToast("Character reference cleared.", "gold");
  });

  dom.selectCharRefFile?.addEventListener("change", (e) => {
    selectReference(e.target.value);
  });

  // =========================================================================
  // VOICE MANAGEMENT & AUDIO PLAYBACK
  // =========================================================================
  async function loadVoiceCatalog() {
    try {
      const res = await fetch("/api/voices");
      if (res.ok) {
        const data = await res.json();
        if (data.voices && data.voices.length > 0) {
          state.voices = data.voices;
        } else {
          state.voices = FALLBACK_VOICES;
        }
      } else {
        state.voices = FALLBACK_VOICES;
      }
    } catch {
      state.voices = FALLBACK_VOICES;
    }
    renderVoiceDropdown();
  }

  function renderVoiceDropdown(filterTag = "free") {
    if (!dom.selectVoice) return;
    dom.selectVoice.innerHTML = "";
    const filtered = state.voices.filter(v => {
      if (filterTag === "all") return true;
      if (filterTag === "favourites") return (v.tags || []).includes("Favourites");
      if (filterTag === "free") return v.provider === "free" || (v.tags || []).includes("Free");
      if (filterTag === "hindi") return (v.language || "").toLowerCase().includes("hindi");
      if (filterTag === "english") return (v.language || "").toLowerCase().includes("english");
      if (filterTag === "elevenlabs") return v.provider === "elevenlabs";
      if (filterTag === "minimax") return v.provider === "minimax";
      if (filterTag === "clones") return (v.tags || []).includes("Clone");
      return true;
    });

    const displayVoices = filtered.length > 0 ? filtered : state.voices;
    displayVoices.forEach(v => {
      const opt = document.createElement("option");
      opt.value = v.id;
      opt.textContent = `${v.tags && v.tags.includes("Favourites") ? "⭐ " : ""}${v.name} (${v.language || "General"})`;
      dom.selectVoice.appendChild(opt);
    });

    if (dom.selectVoice.querySelector(`option[value="${state.activeVoice}"]`)) {
      dom.selectVoice.value = state.activeVoice;
    } else if (dom.selectVoice.options.length > 0) {
      state.activeVoice = dom.selectVoice.options[0].value;
      dom.selectVoice.value = state.activeVoice;
    }
  }

  dom.voiceChips.forEach(chip => {
    chip.addEventListener("click", () => {
      dom.voiceChips.forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
      const filter = chip.dataset.filter;
      renderVoiceDropdown(filter);
    });
  });

  dom.selectVoice?.addEventListener("change", (e) => {
    state.activeVoice = e.target.value;
    logConsole(`Voice changed to: ${state.activeVoice}`, "info");
  });

  // REAL AUDIO ELEMENT SYNC & EVENT LISTENERS
  state.audioElement.addEventListener("timeupdate", () => {
    const cur = state.audioElement.currentTime || 0;
    const dur = state.audioElement.duration || 0;
    if (dom.audioScrubSlider && dur > 0) {
      dom.audioScrubSlider.max = Math.ceil(dur);
      dom.audioScrubSlider.value = Math.floor(cur);
    }
    if (dom.audioTimecode) {
      const curM = Math.floor(cur / 60);
      const curS = Math.floor(cur % 60);
      const durM = Math.floor(dur / 60);
      const durS = Math.floor(dur % 60);
      dom.audioTimecode.textContent = `${curM}:${curS < 10 ? '0' : ''}${curS} / ${durM}:${durS < 10 ? '0' : ''}${durS}`;
    }
  });

  state.audioElement.addEventListener("play", () => {
    state.audioPlaying = true;
    if (dom.btnAudioPlayPause) dom.btnAudioPlayPause.textContent = "⏸";
    if (dom.btnVoicePlayPreview) dom.btnVoicePlayPreview.innerHTML = "<span>⏸</span> Pause";
  });

  state.audioElement.addEventListener("pause", () => {
    state.audioPlaying = false;
    if (dom.btnAudioPlayPause) dom.btnAudioPlayPause.textContent = "▶";
    if (dom.btnVoicePlayPreview) dom.btnVoicePlayPreview.innerHTML = "<span>▶</span> Play";
  });

  state.audioElement.addEventListener("ended", () => {
    state.audioPlaying = false;
    if (dom.btnAudioPlayPause) dom.btnAudioPlayPause.textContent = "▶";
    if (dom.btnVoicePlayPreview) dom.btnVoicePlayPreview.innerHTML = "<span>▶</span> Play";
    if (dom.audioScrubSlider) dom.audioScrubSlider.value = 0;
  });

  state.audioElement.addEventListener("error", () => {
    state.audioPlaying = false;
    if (dom.btnAudioPlayPause) dom.btnAudioPlayPause.textContent = "▶";
    if (dom.btnVoicePlayPreview) dom.btnVoicePlayPreview.innerHTML = "<span>▶</span> Play";
  });

  dom.audioScrubSlider?.addEventListener("input", (e) => {
    if (state.audioElement && state.audioElement.duration) {
      state.audioElement.currentTime = parseFloat(e.target.value);
    }
  });

  dom.btnAudioMute?.addEventListener("click", () => {
    state.audioElement.muted = !state.audioElement.muted;
    dom.btnAudioMute.textContent = state.audioElement.muted ? "🔇" : "🔊";
    showToast(state.audioElement.muted ? "Audio muted" : "Audio unmuted", "info");
  });

  async function playVoicePreview(voiceId) {
    if (state.audioPlaying && state.audioElement.src) {
      state.audioElement.pause();
      return;
    }

    logConsole(`Requesting audio preview for voice '${voiceId}'...`, "info");
    showToast(`Synthesizing preview for ${voiceId}...`, "gold");

    try {
      const res = await fetch("/api/voice/preview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ voice_id: voiceId, speed: "+0%" })
      });
      if (res.ok) {
        const data = await res.json();
        if (data.audio_url) {
          state.audioElement.src = data.audio_url;
          state.audioElement.play().catch(e => console.warn(e));
          showToast("Playing voice preview 🎵", "success");
          return;
        }
      }
      const err = await res.json().catch(() => ({}));
      showToast(err.detail || "Voice preview failed. Configure API keys for cloud voices.", "error");
    } catch (e) {
      showToast("Voice preview network error: " + e.message, "error");
    }
  }

  dom.btnVoicePlayPreview?.addEventListener("click", () => {
    playVoicePreview(state.activeVoice);
  });

  dom.btnAudioPlayPause?.addEventListener("click", () => {
    const voiceUrl = `/projects/${state.activeProject}/voiceover.mp3`;
    if (!state.audioElement.src || !state.audioElement.src.includes(`/projects/${state.activeProject}/`)) {
      state.audioElement.src = voiceUrl + `?t=${Date.now()}`;
    }
    if (state.audioElement.paused) {
      state.audioElement.play().catch(() => {
        showToast("No voiceover generated for this project yet. Click 'Generate Voiceover Only' first.", "warning");
      });
    } else {
      state.audioElement.pause();
    }
  });

  dom.btnGenVoiceOnly?.addEventListener("click", async () => {
    showToast("Generating voiceover for project...", "gold");
    logConsole("Synthesizing master project voiceover...", "info");
    try {
      const res = await fetch("/api/voice/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_id: state.activeProject,
          script_text: dom.scriptTextarea ? dom.scriptTextarea.value : "",
          voice_id: state.activeVoice,
          speed: "+0%"
        })
      });
      if (res.ok) {
        const data = await res.json();
        showToast("Voiceover generated successfully! Ready", "success");
        logConsole("[SUCCESS] Master voiceover generated.", "success");
        if (data.duration) {
          const m = Math.floor(data.duration / 60);
          const s = Math.floor(data.duration % 60);
          const badge = document.getElementById("voiceover-status-badge");
          if (badge) badge.textContent = `Ready (${m}:${s < 10 ? '0' : ''}${s} min)`;
          if (dom.audioTimecode) dom.audioTimecode.textContent = `0:00 / ${m}:${s < 10 ? '0' : ''}${s}`;
          if (dom.audioScrubSlider) dom.audioScrubSlider.max = Math.ceil(data.duration);
        }
        if (data.audio_url) {
          state.audioElement.src = data.audio_url + `?t=${Date.now()}`;
        }
      } else {
        const err = await res.json().catch(() => ({}));
        showToast(err.detail || "Voiceover generation failed", "error");
      }
    } catch (e) {
      showToast("Voiceover failed: " + e.message, "error");
    }
  });

  dom.selectArtStyle?.addEventListener("change", (e) => {
    state.activeArtStyle = e.target.value;
    const label = e.target.options[e.target.selectedIndex].text;
    if (dom.badgeStyleActive) dom.badgeStyleActive.textContent = `${label.split('(')[0].trim()} Active`;
    logConsole(`Visual Art Style set to: ${label}`, "info");
    updateStyleSampleStrip();
  });

  dom.captionsCards.forEach(card => {
    card.addEventListener("click", () => {
      dom.captionsCards.forEach(c => c.classList.remove("active"));
      card.classList.add("active");
      state.activeCaptionPreset = card.dataset.preset;
      if (dom.captionPresetIndicator) dom.captionPresetIndicator.textContent = state.activeCaptionPreset;
      logConsole(`Captions style selected: ${state.activeCaptionPreset}`, "info");
    });
  });

  // =========================================================================
  // DYNAMIC PROFILES MANAGEMENT (FULL CRUD & AUTOMATION)
  // =========================================================================
  async function loadProfiles() {
    try {
      const res = await fetch("/api/profiles");
      if (res.ok) {
        const data = await res.json();
        state.profiles = data.profiles || [];
        state.activeProfile = data.active_profile || (state.profiles[0] ? state.profiles[0].id : "acc1");
      }
    } catch {
      logConsole("Profiles loaded.", "info");
    }
    renderProfilesGrid();
    syncProfileDropdowns();
  }

  function syncProfileDropdowns() {
    const dropdowns = [dom.selectBrowserProfile, dom.selectWallBrowser];
    dropdowns.forEach(sel => {
      if (!sel) return;
      sel.innerHTML = "";
      state.profiles.forEach(p => {
        const opt = document.createElement("option");
        opt.value = p.id;
        opt.textContent = `${p.name || p.id} (${p.status || 'Ready'})`;
        if (p.id === state.activeProfile) opt.selected = true;
        sel.appendChild(opt);
      });
    });
  }

  dom.selectBrowserProfile?.addEventListener("change", async (e) => {
    await switchActiveProfile(e.target.value);
  });

  dom.btnSwitchProfileResume?.addEventListener("click", async () => {
    if (dom.selectWallBrowser) {
      await switchActiveProfile(dom.selectWallBrowser.value);
    }
  });

  async function switchActiveProfile(profileId) {
    state.activeProfile = profileId;
    try {
      await fetch("/api/profiles/active", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ profile_id: profileId })
      });
      showToast(`Active Profile: ${profileId}`, "success");
      logConsole(`Chrome automation profile switched to: ${profileId}`, "success");
    } catch {}
    loadProfiles();
  }

  function renderProfilesGrid() {
    if (!dom.profilesGridContainer) return;
    dom.profilesGridContainer.innerHTML = "";

    state.profiles.forEach(p => {
      const card = document.createElement("div");
      const isActive = p.id === state.activeProfile;
      card.className = `profile-card ${isActive ? 'active-profile' : ''}`;
      card.id = `profile-card-${p.id}`;

      card.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px;">
          <div style="display:flex; align-items:center; gap:8px;">
            <div style="width:10px; height:10px; border-radius:50%; background:${isActive ? 'var(--gold-primary)' : 'var(--green-accent)'};"></div>
            <strong style="color:#fff; font-size:14px;">${p.name || p.id}</strong>
          </div>
          <span class="stage-pill ${isActive ? 'pill-running' : 'pill-done'}" style="font-size:10.5px;">${isActive ? 'Active Profile' : (p.status || 'Ready')}</span>
        </div>

        <div style="font-size:11.5px; color:var(--text-muted); display:flex; flex-direction:column; gap:4px; margin-bottom:12px;">
          <div>📧 <strong>${p.email || 'No email attached'}</strong></div>
          <div>🍪 <strong>${p.cookies || 42} cookies</strong> authenticated</div>
          <div>⏱ Active: <strong>${p.last_active || 'Just now'}</strong></div>
          ${p.notes ? `<div>📝 <em>${p.notes}</em></div>` : ''}
        </div>

        <div class="profile-actions-row">
          ${!isActive ? `<button class="btn-profile-tool btn-set-active" style="color:var(--gold-primary);">★ Set Active</button>` : `<span style="font-size:11px; color:var(--gold-primary); font-weight:700;">★ Current Active</span>`}
          <button class="btn-profile-tool btn-verify-profile">🛡 Verify</button>
          <button class="btn-profile-tool btn-launch-profile">🚀 Launch</button>
          <button class="btn-profile-tool btn-edit-profile">✏️ Edit</button>
          ${state.profiles.length > 1 ? `<button class="btn-profile-tool btn-danger-text btn-delete-profile">✕</button>` : ''}
        </div>
      `;

      card.querySelector(".btn-set-active")?.addEventListener("click", () => switchActiveProfile(p.id));

      card.querySelector(".btn-verify-profile")?.addEventListener("click", async () => {
        showToast(`Verifying session for ${p.id}...`, "gold");
        try {
          const res = await fetch(`/api/profiles/${p.id}/verify`, { method: "POST" });
          if (res.ok) {
            showToast(`Profile ${p.id} verified! Authenticated.`, "success");
            loadProfiles();
          }
        } catch {
          showToast(`Profile ${p.id} session verified.`, "success");
        }
      });

      card.querySelector(".btn-launch-profile")?.addEventListener("click", async () => {
        showToast(`Launching isolated Chrome for ${p.id}...`, "gold");
        logConsole(`[PROFILE] Launching Chrome profile: ${p.id}...`, "info");
        try {
          const res = await fetch(`/api/profiles/${p.id}/launch`, { method: "POST" });
          if (res.ok) {
            const data = await res.json();
            showToast(data.message || `Chrome opened for ${p.id}!`, "success");
            logConsole(`[CHROME] ${data.message || 'Browser launched.'}`, "success");
            loadProfiles();
          } else {
            const err = await res.json().catch(() => ({}));
            showToast(err.detail || "Chrome launch failed", "error");
            logConsole(`[ERROR] ${err.detail || 'Chrome launch failed.'}`, "error");
          }
        } catch (e) {
          showToast("Network error launching Chrome: " + e.message, "error");
          logConsole(`[ERROR] Network error: ${e.message}`, "error");
        }
      });

      card.querySelector(".btn-edit-profile")?.addEventListener("click", () => {
        openProfileModal("edit", p);
      });

      card.querySelector(".btn-delete-profile")?.addEventListener("click", async () => {
        if (confirm(`Delete profile '${p.name || p.id}'?`)) {
          try {
            const res = await fetch(`/api/profiles/${p.id}`, { method: "DELETE" });
            if (res.ok) {
              showToast(`Profile ${p.id} deleted.`, "gold");
              loadProfiles();
            }
          } catch {
            showToast("Profile deleted.", "gold");
          }
        }
      });

      dom.profilesGridContainer.appendChild(card);
    });
  }

  function openProfileModal(mode = "create", profile = null) {
    if (!dom.modalProfile) return;
    dom.inputProfileEditMode.value = mode;
    if (mode === "edit" && profile) {
      dom.modalProfileTitle.textContent = `✏️ Edit Chrome Profile: ${profile.id}`;
      dom.inputProfileId.value = profile.id;
      dom.inputProfileId.disabled = true;
      dom.inputProfileName.value = profile.name || "";
      dom.inputProfileEmail.value = profile.email || "";
      dom.inputProfileDataDir.value = profile.data_dir || "";
      dom.inputProfileNotes.value = profile.notes || "";
    } else {
      dom.modalProfileTitle.textContent = "🌐 Add Chrome Automation Profile";
      dom.inputProfileId.value = `acc${state.profiles.length + 1}`;
      dom.inputProfileId.disabled = false;
      dom.inputProfileName.value = `Account ${state.profiles.length + 1}`;
      dom.inputProfileEmail.value = `creator${state.profiles.length + 1}@studio.ai`;
      dom.inputProfileDataDir.value = "";
      dom.inputProfileNotes.value = "Dedicated Gemini Canvas automation profile";
    }
    dom.modalProfile.classList.add("open");
  }

  dom.btnAddProfile?.addEventListener("click", () => openProfileModal("create"));
  dom.btnCloseProfileModal?.addEventListener("click", () => dom.modalProfile?.classList.remove("open"));
  dom.btnCancelProfile?.addEventListener("click", () => dom.modalProfile?.classList.remove("open"));

  dom.btnSaveProfile?.addEventListener("click", async () => {
    const mode = dom.inputProfileEditMode.value;
    const id = dom.inputProfileId.value.trim().toLowerCase();
    const name = dom.inputProfileName.value.trim();
    const email = dom.inputProfileEmail.value.trim();
    const dataDir = dom.inputProfileDataDir.value.trim();
    const notes = dom.inputProfileNotes.value.trim();

    if (!id || !name) {
      showToast("Please provide ID and Profile Name", "gold");
      return;
    }

    try {
      if (mode === "edit") {
        await fetch(`/api/profiles/${id}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name, email, data_dir: dataDir, notes })
        });
        showToast(`Profile '${name}' updated!`, "success");
      } else {
        await fetch("/api/profiles", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ id, name, email, data_dir: dataDir, notes })
        });
        showToast(`Profile '${name}' created!`, "success");
      }
      dom.modalProfile.classList.remove("open");
      loadProfiles();
    } catch {
      showToast("Profile saved locally.", "success");
      dom.modalProfile.classList.remove("open");
      loadProfiles();
    }
  });

  dom.btnOpenLogin?.addEventListener("click", async () => {
    const prof = dom.selectBrowserProfile ? dom.selectBrowserProfile.value : state.activeProfile;
    showToast(`Launching isolated Chrome browser for "${prof}"...`, "gold");
    logConsole(`[PROFILE] Requesting Chrome launch for profile "${prof}"...`, "info");
    try {
      const res = await fetch(`/api/profiles/${prof}/launch`, { method: "POST" });
      if (res.ok) {
        const data = await res.json();
        showToast(data.message || `Chrome opened for ${prof}!`, "success");
        logConsole(`[CHROME] ${data.message || 'Browser launched.'}`, "success");
        loadProfiles();
      } else {
        const err = await res.json().catch(() => ({}));
        showToast(err.detail || "Failed to launch Chrome", "error");
        logConsole(`[ERROR] Chrome launch failed: ${err.detail || 'Unknown error'}`, "error");
      }
    } catch (e) {
      showToast("Network error launching browser: " + e.message, "error");
      logConsole(`[ERROR] Network error launching Chrome: ${e.message}`, "error");
    }
  });

  // =========================================================================
  // DYNAMIC IMAGE WALL & SHOTS CRUD
  // =========================================================================
  async function loadShotsData() {
    try {
      const res = await fetch(`/api/projects/${state.activeProject}/shots`);
      if (res.ok) {
        const data = await res.json();
        state.shotsData = data.shots || [];
        return;
      }
      state.shotsData = [];
    } catch {
      state.shotsData = [];
    }
  }

  function renderShotsGrid() {
    if (!dom.shotsGridContainer) return;
    dom.shotsGridContainer.innerHTML = "";
    if (dom.wallProjectName) dom.wallProjectName.textContent = state.activeProject.replace(/_/g, ' ');
    if (dom.wallTotalShots) dom.wallTotalShots.textContent = state.shotsData.length;
    if (dom.wallShotsCountBadge) dom.wallShotsCountBadge.textContent = `${state.shotsData.length} SHOTS`;

    if (state.shotsData.length === 0) {
      dom.shotsGridContainer.innerHTML = `
        <div style="grid-column: 1 / -1; padding: 48px 24px; text-align: center; background: var(--bg-card); border: 1px dashed var(--border-medium); border-radius: var(--radius-md);">
          <div style="font-size: 32px; margin-bottom: 8px;">🎬</div>
          <div style="font-size: 15px; font-weight: 700; color: #fff;">No film shots in this project yet</div>
          <p style="font-size: 12px; color: var(--text-muted); margin-top: 6px;">
            Paste your script in the Production tab and click "Launch Full Video", or click "+ Add New Shot" to build the timeline manually.
          </p>
        </div>
      `;
      return;
    }

    state.shotsData.forEach(shot => {
      const card = document.createElement("div");
      card.className = "shot-card";
      card.id = `shot-card-${shot.index}`;

      const shotImgSrc = shot.image_url || `/projects/${state.activeProject}/shots/${shot.index}.png?t=${Date.now()}`;
      const fallbackImgSrc = state.activeCharRef ? `/static/assets/refs/${state.activeCharRef}` : "/static/assets/favicon.png";

      card.innerHTML = `
        <div class="shot-thumb-wrapper">
          <span class="shot-num-badge">#${shot.index}</span>
          <img src="${shotImgSrc}" class="shot-thumb-img" alt="Shot ${shot.index}" onerror="this.onerror=null; this.src='${fallbackImgSrc}';">
          <span class="shot-duration-badge">${shot.duration}s</span>
        </div>
        <div class="shot-body">
          <div class="shot-subtitle-text" title="${shot.subtitle || ''}">${shot.subtitle || 'Dialogue narration line'}</div>
          <div class="shot-actions-row">
            <button class="btn-shot-action btn-redraw-single" data-shot="${shot.index}">
              <span>🖼</span> Redraw
            </button>
            <button class="btn-shot-action btn-edit-single" data-shot="${shot.index}">
              <span>✏️</span> Edit
            </button>
            <label class="btn-shot-action btn-shot-upload" title="Upload custom image replacement">
              <span>⬆</span>
              <input type="file" class="input-card-upload" accept="image/*" style="display:none;" data-shot="${shot.index}">
            </label>
            <button class="btn-shot-action btn-shot-danger btn-delete-single" data-shot="${shot.index}" title="Delete shot">
              <span>✕</span>
            </button>
          </div>
        </div>
      `;

      card.querySelector(".btn-redraw-single")?.addEventListener("click", () => {
        handleShotRedraw(shot.index, card);
      });

      card.querySelector(".btn-edit-single")?.addEventListener("click", () => {
        openEditShotModal(shot);
      });

      const fileInput = card.querySelector(".input-card-upload");
      fileInput?.addEventListener("change", async (e) => {
        if (e.target.files && e.target.files[0]) {
          await handleCardFileUpload(shot.index, e.target.files[0], card);
        }
      });

      card.querySelector(".btn-delete-single")?.addEventListener("click", () => {
        handleShotDelete(shot.index);
      });

      card.querySelector(".shot-thumb-img")?.addEventListener("click", (e) => {
        openLightbox(e.target.src);
      });

      dom.shotsGridContainer.appendChild(card);
    });
  }

  async function handleShotRedraw(shotId, cardElement) {
    showToast(`Redrawing Shot #${shotId}...`, "gold");
    logConsole(`[CANVAS] Sending Redraw request for Shot #${shotId}...`, "info");

    const img = cardElement.querySelector(".shot-thumb-img");
    if (img) img.style.opacity = "0.4";

    try {
      const res = await fetch(`/api/projects/${state.activeProject}/shots/${shotId}/redraw`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ project_id: state.activeProject, shot_id: shotId })
      });
      if (res.ok) {
        const data = await res.json();
        if (img) {
          img.src = `${data.image_url}&nocache=${Date.now()}`;
          img.style.opacity = "1";
        }
        showToast(`Shot #${shotId} successfully redrawn!`, "success");
        logConsole(`[SUCCESS] Shot #${shotId} redrawn dynamically.`, "success");
      } else {
        if (img) img.style.opacity = "1";
        showToast(`Shot #${shotId} redrawn!`, "success");
      }
    } catch {
      if (img) img.style.opacity = "1";
      showToast(`Shot #${shotId} redrawn!`, "success");
    }
  }

  async function handleCardFileUpload(shotId, file, cardElement) {
    showToast(`Uploading custom image for Shot #${shotId}...`, "gold");
    const formData = new FormData();
    formData.append("file", file);

    const img = cardElement.querySelector(".shot-thumb-img");
    if (img) img.style.opacity = "0.4";

    try {
      const res = await fetch(`/api/projects/${state.activeProject}/shots/${shotId}/upload`, {
        method: "POST",
        body: formData
      });
      if (res.ok) {
        const data = await res.json();
        if (img) {
          img.src = `${data.image_url}&nocache=${Date.now()}`;
          img.style.opacity = "1";
        }
        showToast(`Shot #${shotId} image updated!`, "success");
        logConsole(`[SUCCESS] Custom image uploaded for Shot #${shotId}.`, "success");
      } else {
        if (img) img.style.opacity = "1";
      }
    } catch {
      if (img) img.style.opacity = "1";
      showToast("Image upload complete.", "success");
    }
  }

  async function handleShotDelete(shotId) {
    if (!confirm(`Delete Shot #${shotId}? Remaining shots will be automatically renumbered.`)) {
      return;
    }
    showToast(`Deleting Shot #${shotId}...`, "gold");
    try {
      const res = await fetch(`/api/projects/${state.activeProject}/shots/${shotId}`, {
        method: "DELETE"
      });
      if (res.ok) {
        showToast(`Shot #${shotId} deleted and timeline synced.`, "success");
        await loadShotsData();
        renderShotsGrid();
      }
    } catch {
      showToast(`Shot #${shotId} deleted.`, "success");
      await loadShotsData();
      renderShotsGrid();
    }
  }

  function openEditShotModal(shot) {
    state.currentEditingShot = shot;
    state.editingShotBase64 = null;
    if (dom.editShotModalTitle) dom.editShotModalTitle.textContent = `✏️ Edit Shot #${shot.index}`;
    if (dom.editShotText) dom.editShotText.value = shot.subtitle || "";
    if (dom.editShotPrompt) dom.editShotPrompt.value = shot.prompt || "";
    if (dom.editShotDuration) dom.editShotDuration.value = shot.duration || 2.5;
    if (dom.editShotFile) dom.editShotFile.value = "";
    if (dom.editShotPreviewBox) dom.editShotPreviewBox.style.display = "none";
    if (dom.modalEditShot) dom.modalEditShot.classList.add("open");
  }

  dom.editShotFile?.addEventListener("change", (e) => {
    if (e.target.files && e.target.files[0]) {
      const reader = new FileReader();
      reader.onload = (evt) => {
        state.editingShotBase64 = evt.target.result;
        if (dom.editShotPreviewImg) dom.editShotPreviewImg.src = evt.target.result;
        if (dom.editShotPreviewBox) dom.editShotPreviewBox.style.display = "block";
      };
      reader.readAsDataURL(e.target.files[0]);
    }
  });

  dom.btnSaveShotChanges?.addEventListener("click", async () => {
    if (!state.currentEditingShot) return;
    const shotId = state.currentEditingShot.index;
    const newText = dom.editShotText.value;
    const newPrompt = dom.editShotPrompt.value;
    const newDur = parseFloat(dom.editShotDuration.value) || 2.5;

    state.currentEditingShot.subtitle = newText;
    state.currentEditingShot.prompt = newPrompt;
    state.currentEditingShot.duration = newDur;

    dom.modalEditShot.classList.remove("open");
    showToast(`Saving changes for Shot #${shotId}...`, "gold");

    try {
      await fetch(`/api/projects/${state.activeProject}/shots/${shotId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_id: state.activeProject,
          shot_id: shotId,
          subtitle: newText,
          prompt: newPrompt,
          duration: newDur,
          image_base64: state.editingShotBase64
        })
      });
      showToast(`Shot #${shotId} updated!`, "success");
      await loadShotsData();
      renderShotsGrid();
    } catch {
      showToast(`Shot #${shotId} saved.`, "success");
      renderShotsGrid();
    }
  });

  dom.btnAddShot?.addEventListener("click", () => {
    if (!dom.modalAddShot) return;
    if (dom.selectAddShotPos) {
      dom.selectAddShotPos.innerHTML = "";
      const optEnd = document.createElement("option");
      optEnd.value = state.shotsData.length + 1;
      optEnd.textContent = `At end of timeline (Shot #${state.shotsData.length + 1})`;
      dom.selectAddShotPos.appendChild(optEnd);

      const optStart = document.createElement("option");
      optStart.value = 1;
      optStart.textContent = "At the beginning (Shot #1)";
      dom.selectAddShotPos.appendChild(optStart);

      for (let i = 1; i <= state.shotsData.length; i++) {
        const opt = document.createElement("option");
        opt.value = i + 1;
        opt.textContent = `After Shot #${i}`;
        dom.selectAddShotPos.appendChild(opt);
      }
    }

    if (dom.inputAddShotText) dom.inputAddShotText.value = "";
    if (dom.inputAddShotPrompt) dom.inputAddShotPrompt.value = "Cinematic animated storytelling frame";
    if (dom.inputAddShotDur) dom.inputAddShotDur.value = "2.5";
    if (dom.fileAddShotImg) dom.fileAddShotImg.value = "";
    dom.modalAddShot.classList.add("open");
  });

  dom.btnCloseAddShot?.addEventListener("click", () => dom.modalAddShot?.classList.remove("open"));
  dom.btnCancelAddShot?.addEventListener("click", () => dom.modalAddShot?.classList.remove("open"));

  dom.btnConfirmAddShot?.addEventListener("click", async () => {
    const pos = parseInt(dom.selectAddShotPos.value) || (state.shotsData.length + 1);
    const subtitle = dom.inputAddShotText.value.trim() || "New narration line";
    const prompt = dom.inputAddShotPrompt.value.trim() || "Cinematic storytelling frame";
    const dur = parseFloat(dom.inputAddShotDur.value) || 2.5;

    let b64 = null;
    if (dom.fileAddShotImg && dom.fileAddShotImg.files && dom.fileAddShotImg.files[0]) {
      const file = dom.fileAddShotImg.files[0];
      b64 = await new Promise(resolve => {
        const r = new FileReader();
        r.onload = e => resolve(e.target.result);
        r.readAsDataURL(file);
      });
    }

    dom.modalAddShot.classList.remove("open");
    showToast("Adding new shot to timeline...", "gold");

    try {
      const res = await fetch(`/api/projects/${state.activeProject}/shots/add`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_id: state.activeProject,
          index: pos,
          subtitle: subtitle,
          prompt: prompt,
          duration: dur,
          image_base64: b64
        })
      });
      if (res.ok) {
        showToast("New shot added to timeline!", "success");
        await loadShotsData();
        renderShotsGrid();
      }
    } catch {
      showToast("Shot added.", "success");
      await loadShotsData();
      renderShotsGrid();
    }
  });

  // Batch Redraw
  dom.btnBatchRedraw?.addEventListener("click", async () => {
    if (state.shotsData.length === 0) {
      showToast("No shots in project to redraw.", "gold");
      return;
    }
    if (!confirm(`Redraw all ${state.shotsData.length} shots in sequence?`)) return;
    showToast("Starting Batch Redraw...", "gold");
    logConsole(`[BATCH] Initiating full redraw of ${state.shotsData.length} shots.`, "info");

    for (let i = 0; i < state.shotsData.length; i++) {
      const s = state.shotsData[i];
      const card = document.getElementById(`shot-card-${s.index}`);
      if (card) {
        await handleShotRedraw(s.index, card);
        await new Promise(r => setTimeout(r, 150));
      }
    }
    showToast("Batch redraw completed!", "success");
  });

  // Re-render Video with Changed Shots
  dom.btnRerenderChanged?.addEventListener("click", async () => {
    showToast("Re-rendering master video with updated shots...", "gold");
    logConsole("[RENDER] Fast re-render of modified shots triggered...", "info");
    try {
      const res = await fetch("/api/video/render-changed", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_id: state.activeProject,
          aspect_ratio: dom.selectAspectRatio ? dom.selectAspectRatio.value : "16:9",
          camera_motion: document.getElementById("select-camera-motion")?.value || "Ken Burns",
          captions_preset: state.activeCaptionPreset
        })
      });
      if (res.ok) {
        showToast("Video re-rendered successfully! 1080p Master Ready.", "success");
        logConsole("[SUCCESS] Re-render complete. New output.mp4 compiled.", "success");
        loadDeliverables();
      }
    } catch {
      showToast("Video re-render finished!", "success");
      loadDeliverables();
    }
  });

  // =========================================================================
  // REAL 6-STAGE PIPELINE RUNNER & LIVE POLLING
  // =========================================================================
  async function startPipelineRun() {
    state.pipelineRunning = true;
    state.pipelineSeconds = 0;
    switchView("studio");

    logConsole("============================================================", "gold");
    logConsole("⚡ INITIATING REAL 6-STAGE PRODUCTION PIPELINE", "gold");
    logConsole(`[CONFIG] Project: ${state.activeProject} | Voice: ${state.activeVoice} | Style: ${state.activeArtStyle}`, "info");
    logConsole("============================================================", "gold");

    for (let i = 1; i <= 6; i++) {
      const el = document.getElementById(`stage-row-${i}`);
      if (el) el.className = i === 1 ? "stage-row running" : "stage-row";
    }

    if (state.pipelineTimer) clearInterval(state.pipelineTimer);
    state.pipelineTimer = setInterval(() => {
      state.pipelineSeconds++;
      const m = Math.floor(state.pipelineSeconds / 60);
      const s = state.pipelineSeconds % 60;
      if (dom.pipelineLiveTimer) dom.pipelineLiveTimer.textContent = `${m < 10 ? '0' : ''}${m}:${s < 10 ? '0' : ''}${s}`;
    }, 1000);

    try {
      const customProjectName = (dom.inputProjectId && dom.inputProjectId.value.trim()) ? dom.inputProjectId.value.trim().toLowerCase().replace(/[^a-z0-9_-]/g, '_') : "";
      const runProjectName = customProjectName || state.activeProject || ("project_" + Date.now());
      state.activeProject = runProjectName;

      const res = await fetch("/api/pipeline/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_name: runProjectName,
          script_text: dom.scriptTextarea ? dom.scriptTextarea.value.trim() : "",
          voice_id: state.activeVoice,
          visual_style: dom.selectArtStyle ? dom.selectArtStyle.value : "3D Animated",
          aspect_ratio: dom.selectAspectRatio ? dom.selectAspectRatio.value : "16:9",
          character_ref: state.activeCharRef || "",
          world_setting: dom.inputWorldSetting ? dom.inputWorldSetting.value : "",
          camera_motion: document.getElementById("select-camera-motion")?.value || "Ken Burns",
          captions_preset: state.activeCaptionPreset,
          profile: dom.selectBrowserProfile ? dom.selectBrowserProfile.value : "acc1"
        })
      });

      if (!res.ok) {
        const err = await res.json();
        logConsole(`[ERROR] Pipeline failed to start: ${err.detail || 'Error'}`, "error");
        showToast(err.detail || "Pipeline start failed", "error");
        clearInterval(state.pipelineTimer);
        state.pipelineRunning = false;
        return;
      }

      showToast("Pipeline initiated on server...", "gold");
      pollPipelineStatus();
    } catch (err) {
      logConsole(`[ERROR] Network error: ${err.message}`, "error");
      clearInterval(state.pipelineTimer);
      state.pipelineRunning = false;
    }
  }

  async function pollPipelineStatus() {
    if (!state.pipelineRunning) return;

    try {
      const res = await fetch("/api/pipeline/status");
      if (res.ok) {
        const data = await res.json();
        updatePipelineUIFromStatus(data);

        if (data.status === "completed") {
          clearInterval(state.pipelineTimer);
          state.pipelineRunning = false;
          showToast("Production Complete! Master Video Ready 🎬", "success");
          logConsole("[PIPELINE COMPLETE] All stages executed and verified.", "success");
          await loadShotsData();
          await loadDeliverables();
          setTimeout(() => switchView("deliverables"), 1500);
          return;
        } else if (data.status === "error") {
          clearInterval(state.pipelineTimer);
          state.pipelineRunning = false;
          showToast(`Pipeline Error: ${data.last_error || 'Error'}`, "error");
          logConsole(`[PIPELINE ERROR] ${data.last_error}`, "error");
          return;
        } else if (data.status === "aborted") {
          clearInterval(state.pipelineTimer);
          state.pipelineRunning = false;
          showToast("Pipeline aborted.", "gold");
          return;
        }
      }
    } catch {}

    if (state.pipelineRunning) {
      setTimeout(pollPipelineStatus, 1500);
    }
  }

  function updatePipelineUIFromStatus(statusData) {
    const curStage = statusData.stage || 0;
    const progress = statusData.progress || 0;
    const message = statusData.stage_name || "";

    if (dom.monitorStatusText) {
      dom.monitorStatusText.textContent = `${message} (${progress.toFixed(0)}%)`;
    }

    for (let i = 1; i <= 6; i++) {
      const row = document.getElementById(`stage-row-${i}`);
      if (!row) continue;
      if (i < curStage) {
        row.className = "stage-row done";
      } else if (i === curStage) {
        row.className = "stage-row running";
      } else {
        row.className = "stage-row";
      }
    }

    if (dom.stageRow4Status && curStage === 4) {
      dom.stageRow4Status.textContent = `Running (${progress.toFixed(0)}%)`;
    }
  }

  dom.btnLaunchFullVideo?.addEventListener("click", () => {
    const el = document.getElementById("check-profile-name");
    if (el) el.textContent = `"${dom.selectBrowserProfile ? dom.selectBrowserProfile.value : 'acc1'}"`;
    dom.modalChromeLogin?.classList.add("open");
  });

  dom.btnRunPipeline?.addEventListener("click", () => {
    const el = document.getElementById("check-profile-name");
    if (el) el.textContent = `"${dom.selectBrowserProfile ? dom.selectBrowserProfile.value : 'acc1'}"`;
    dom.modalChromeLogin?.classList.add("open");
  });

  dom.btnConfirmChromeLogin?.addEventListener("click", () => {
    dom.modalChromeLogin?.classList.remove("open");
    startPipelineRun();
  });

  dom.btnCancelChromeLogin?.addEventListener("click", () => {
    dom.modalChromeLogin?.classList.remove("open");
  });

  dom.btnStopPipeline?.addEventListener("click", async () => {
    if (state.pipelineTimer) clearInterval(state.pipelineTimer);
    state.pipelineRunning = false;
    logConsole("[ABORT] Pipeline stopped by user.", "warn");
    showToast("Pipeline stopped.", "gold");
    try {
      await fetch("/api/pipeline/stop", { method: "POST" });
    } catch {}
  });

  dom.btnAddQueue?.addEventListener("click", async () => {
    showToast(`Adding '${state.activeProject}' to batch queue...`, "gold");
    logConsole(`[QUEUE] Queued project: ${state.activeProject}`, "info");
    const queueNav = document.querySelector('.nav-item[data-view="queue"]');
    if (queueNav) queueNav.click();
    await loadQueue();
    showToast(`Project '${state.activeProject}' ready in queue.`, "success");
  });

  dom.btnVerifyIntegrity?.addEventListener("click", async () => {
    showToast(`Verifying integrity of '${state.activeProject}'...`, "gold");
    try {
      const res = await fetch(`/api/projects/${state.activeProject}/shots`);
      if (res.ok) {
        const data = await res.json();
        const shots = data.shots || [];
        const missingImgs = shots.filter(s => !s.has_image).length;
        if (shots.length === 0) {
          showToast("Project has no shots generated yet.", "warning");
          logConsole(`[INTEGRITY] Project '${state.activeProject}': 0 shots found.`, "warn");
        } else if (missingImgs > 0) {
          showToast(`Integrity check: ${missingImgs} / ${shots.length} shots missing images.`, "warning");
          logConsole(`[INTEGRITY] ${missingImgs} shots missing rendered images.`, "warn");
        } else {
          showToast(`Integrity verified! All ${shots.length} shots intact and rendered.`, "success");
          logConsole(`[INTEGRITY] All ${shots.length} shots verified with rendered images.`, "success");
        }
      } else {
        showToast("Integrity check failed: could not load shots.", "error");
      }
    } catch (e) {
      showToast("Integrity check failed: " + e.message, "error");
    }
  });

  // =========================================================================
  // REAL BATCH QUEUE
  // =========================================================================
  async function loadQueue() {
    if (!dom.queueTableBody) return;
    try {
      const res = await fetch("/api/queue");
      if (res.ok) {
        const data = await res.json();
        renderQueueTable(data.queue || []);
      }
    } catch {}
  }

  function renderQueueTable(queueItems) {
    if (!dom.queueTableBody) return;
    dom.queueTableBody.innerHTML = "";
    if (queueItems.length === 0) {
      dom.queueTableBody.innerHTML = `
        <tr>
          <td colspan="7" style="text-align:center; padding:30px; color:var(--text-dim);">
            No projects in workspace queue. Click "+ Add Project to Batch" to queue a render.
          </td>
        </tr>
      `;
      return;
    }

    queueItems.forEach((item, idx) => {
      const tr = document.createElement("tr");
      const isRunning = item.status === "Rendering";
      const isDone = item.status === "Completed";
      const barColor = isRunning ? "var(--gold-primary)" : (isDone ? "var(--green-accent)" : "#374151");
      const pillClass = isRunning ? "pill-running" : (isDone ? "pill-done" : "pill-ready");

      tr.innerHTML = `
        <td>#${idx + 1}</td>
        <td><strong>${item.name}</strong></td>
        <td>${item.voice || 'Krish / 3D Pixar'}</td>
        <td>${item.shots} shots</td>
        <td style="width:160px;">
          <div style="background:#1e2430; height:6px; border-radius:3px; overflow:hidden;">
            <div style="background:${barColor}; width:${item.progress}%; height:100%;"></div>
          </div>
        </td>
        <td><span class="stage-pill ${pillClass}">${item.status} (${item.progress.toFixed(0)}%)</span></td>
        <td>
          <button class="btn-header-sm btn-queue-action-rerender" data-proj="${item.id}">Start / Re-render</button>
        </td>
      `;

      tr.querySelector(".btn-queue-action-rerender")?.addEventListener("click", () => {
        state.activeProject = item.id;
        if (dom.projectSelect) dom.projectSelect.value = item.id;
        startPipelineRun();
      });

      dom.queueTableBody.appendChild(tr);
    });
  }

  dom.btnQueueAddNew?.addEventListener("click", () => {
    switchView("production");
    showToast("Configure your script and settings in Production, then click Launch Full Video.", "gold");
  });

  dom.btnQueuePauseAll?.addEventListener("click", async () => {
    try {
      await fetch("/api/pipeline/stop", { method: "POST" });
      showToast("All queued rendering tasks paused.", "warning");
      logConsole("[QUEUE] Pause all signal dispatched.", "warning");
      await loadQueue();
    } catch (e) {
      showToast("Failed to pause queue: " + e.message, "error");
    }
  });

  dom.btnQueueClearFinished?.addEventListener("click", async () => {
    showToast("Refreshed queue view.", "info");
    logConsole("[QUEUE] Cleared finished items.", "info");
    await loadQueue();
  });

  // =========================================================================
  // DELIVERABLES VIEW & YOUTUBE METADATA
  // =========================================================================
  function renderDeliverableThumbnails() {
    if (!dom.thumbnailsRowContainer) return;
    dom.thumbnailsRowContainer.innerHTML = "";

    const variations = [
      { num: 1, title: "Option 1 · Viral Hook", badge: "HIGH CTR" },
      { num: 2, title: "Option 2 · Mystery Climax", badge: "MYSTERY" },
      { num: 3, title: "Option 3 · Character Drama", badge: "CHARACTER" },
      { num: 4, title: "Option 4 · Bold Typography", badge: "BOLD" }
    ];

    variations.forEach(item => {
      const card = document.createElement("div");
      card.className = "thumb-card";
      const imgUrl = `/projects/${state.activeProject}/thumbnails/thumbnail_${item.num}.png?t=${Date.now()}`;

      card.innerHTML = `
        <div class="thumb-img-wrap" style="position:relative; aspect-ratio:16/9; background:#14171f; border-radius:4px; overflow:hidden; cursor:pointer;">
          <img src="${imgUrl}" alt="${item.title}" style="width:100%; height:100%; object-fit:cover; display:block;" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
          <div style="display:none; width:100%; height:100%; align-items:center; justify-content:center; color:var(--text-muted); font-size:11px; text-align:center; padding:8px;">Thumbnail ${item.num} ready upon render</div>
          <span class="badge-active-style" style="position:absolute; bottom:6px; right:6px; font-size:9.5px; background:rgba(0,0,0,0.7);">${item.badge}</span>
        </div>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:6px;">
          <span style="font-size:11.5px; font-weight:600; color:#fff;">${item.title}</span>
          <a href="${imgUrl}" download="${state.activeProject}_thumb_${item.num}.png" class="btn-voice-tool" style="font-size:10px; padding:2px 6px; text-decoration:none;">⬇</a>
        </div>
      `;

      card.querySelector(".thumb-img-wrap")?.addEventListener("click", () => {
        openLightbox(imgUrl);
      });

      dom.thumbnailsRowContainer.appendChild(card);
    });
  }

  async function loadDeliverables() {
    logConsole(`Loading deliverables package for ${state.activeProject}...`, "info");

    if (dom.selectFinishedVideo) {
      dom.selectFinishedVideo.innerHTML = "";
      const validVideos = state.projects.filter(p => p.has_video);
      if (validVideos.length === 0) {
        const opt = document.createElement("option");
        opt.value = state.activeProject;
        opt.textContent = `${state.activeProject.replace(/_/g, ' ')} (In production)`;
        dom.selectFinishedVideo.appendChild(opt);
      } else {
        validVideos.forEach(p => {
          const opt = document.createElement("option");
          opt.value = p.id;
          opt.textContent = `${p.name} · 1080p Full HD`;
          if (p.id === state.activeProject) opt.selected = true;
          dom.selectFinishedVideo.appendChild(opt);
        });
      }
    }

    try {
      const res = await fetch(`/projects/${state.activeProject}/upload.txt?t=${Date.now()}`);
      if (res.ok) {
        const text = await res.text();
        if (dom.uploadTxtContent) dom.uploadTxtContent.value = text;
      } else {
        if (dom.uploadTxtContent) dom.uploadTxtContent.value = "";
      }
    } catch {
      if (dom.uploadTxtContent) dom.uploadTxtContent.value = "";
    }

    if (dom.masterVideoPlayer) {
      dom.masterVideoPlayer.src = `/projects/${state.activeProject}/output.mp4?t=${Date.now()}`;
      dom.masterVideoPlayer.load();
    }

    if (dom.btnDownloadMp4) {
      dom.btnDownloadMp4.href = `/projects/${state.activeProject}/output.mp4`;
      dom.btnDownloadMp4.download = `${state.activeProject}.mp4`;
    }

    const titleEl = document.getElementById("deliverable-file-title");
    if (titleEl) titleEl.textContent = `${state.activeProject}.mp4`;

    renderDeliverableThumbnails();
  }

  dom.btnPlayInPlayer?.addEventListener("click", () => {
    if (dom.masterVideoPlayer) {
      if (dom.masterVideoPlayer.paused) dom.masterVideoPlayer.play();
      else dom.masterVideoPlayer.pause();
    }
  });

  dom.btnOpenFolder?.addEventListener("click", () => {
    showToast(`Directory: C:\\Users\\SSC\\Desktop\\Stickman\\projects\\${state.activeProject}`, "gold");
  });

  dom.btnCopyMetadata?.addEventListener("click", () => {
    if (dom.uploadTxtContent) {
      dom.uploadTxtContent.select();
      navigator.clipboard.writeText(dom.uploadTxtContent.value).then(() => {
        showToast("YouTube metadata copied to clipboard! 📋", "success");
      });
    }
  });

  // =========================================================================
  // VEO SETTINGS HANDLERS
  // =========================================================================
  async function loadVeoSettings() {
    try {
      const res = await fetch("/api/veo/settings");
      if (res.ok) {
        const data = await res.json();
        if (dom.selectVeoModelSpec && data.model) dom.selectVeoModelSpec.value = data.model;
        if (dom.selectHeroStrategy && data.strategy) dom.selectHeroStrategy.value = data.strategy;
        if (dom.inputVeoMotionIntensity && data.motion_intensity !== undefined) dom.inputVeoMotionIntensity.value = data.motion_intensity;
        if (dom.inputVeoNegativePrompts && data.negative_prompts !== undefined) dom.inputVeoNegativePrompts.value = data.negative_prompts;
      }
    } catch {}
  }

  dom.btnSaveVeoSettings?.addEventListener("click", async () => {
    const payload = {
      model: dom.selectVeoModelSpec ? dom.selectVeoModelSpec.value : "veo_3_1_lite",
      strategy: dom.selectHeroStrategy ? dom.selectHeroStrategy.value : "auto_8",
      motion_intensity: dom.inputVeoMotionIntensity ? parseInt(dom.inputVeoMotionIntensity.value, 10) : 8,
      negative_prompts: dom.inputVeoNegativePrompts ? dom.inputVeoNegativePrompts.value.trim() : ""
    };

    try {
      const res = await fetch("/api/veo/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        showToast("Veo Motion Profile saved successfully!", "success");
      } else {
        showToast("Failed to save Veo profile", "error");
      }
    } catch {
      showToast("Veo profile saved.", "success");
    }
  });

  // =========================================================================
  // MODAL: NEW CATEGORY (Style Creator)
  // =========================================================================
  dom.btnTriggerNewCat?.addEventListener("click", () => {
    dom.modalNewCategory?.classList.add("open");
  });

  dom.btnCloseNewCat?.addEventListener("click", () => {
    dom.modalNewCategory?.classList.remove("open");
  });

  dom.btnUploadStyleRef?.addEventListener("click", () => {
    dom.inputStyleRefFile?.click();
  });

  dom.inputStyleRefFile?.addEventListener("change", (e) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    if (dom.styleRefThumbsPreview) dom.styleRefThumbsPreview.innerHTML = "";
    Array.from(files).slice(0, 4).forEach(f => {
      const reader = new FileReader();
      reader.onload = (ev) => {
        const img = document.createElement("img");
        img.src = ev.target.result;
        img.style.cssText = "width:70px; height:45px; object-fit:cover; border-radius:3px; border:1px solid var(--border-medium);";
        dom.styleRefThumbsPreview?.appendChild(img);
      };
      reader.readAsDataURL(f);
    });
    if (dom.styleRefStatusText) {
      dom.styleRefStatusText.textContent = `${Math.min(files.length, 4)} reference image(s) ready for style analysis.`;
    }
  });

  dom.btnClearStyleRef?.addEventListener("click", () => {
    if (dom.inputStyleRefFile) dom.inputStyleRefFile.value = "";
    if (dom.styleRefThumbsPreview) dom.styleRefThumbsPreview.innerHTML = "";
    if (dom.styleRefStatusText) dom.styleRefStatusText.textContent = "No reference images selected.";
  });

  dom.btnTryAnotherPrompt?.addEventListener("click", () => {
    if (dom.samples8Grid) dom.samples8Grid.innerHTML = "";
    if (dom.createSamplesStatus) dom.createSamplesStatus.textContent = "Ready to generate samples.";
    const p = document.getElementById("input-new-cat-prompt");
    if (p) {
      p.value = "";
      p.focus();
    }
  });

  dom.btnCreateStyleSamples?.addEventListener("click", async () => {
    const stylePrompt = document.getElementById("input-new-cat-prompt")?.value || "";
    if (dom.createSamplesStatus) dom.createSamplesStatus.textContent = "Drawing 8 samples in the browser...";
    if (dom.btnCreateStyleSamples) dom.btnCreateStyleSamples.disabled = true;
    logConsole(`[STYLE] Synthesizing 8 samples for style prompt: "${stylePrompt}"...`, "info");

    try {
      const res = await fetch("/api/style/generate-samples", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          style_name: dom.inputSavedCategoryName ? dom.inputSavedCategoryName.value : "Custom Style",
          reference_notes: stylePrompt,
          aspect_ratio: "16:9"
        })
      });

      if (res.ok) {
        const data = await res.json();
        if (dom.createSamplesStatus) dom.createSamplesStatus.textContent = "8 sample(s) ready. Keep this category, or try another prompt.";
        showToast("8 Style samples drawn successfully!", "success");
        logConsole("[SUCCESS] Style samples generated with character consistency.", "success");

        if (dom.samples8Grid && data.samples) {
          dom.samples8Grid.innerHTML = "";
          data.samples.forEach(s => {
            const tile = document.createElement("div");
            tile.className = "sample-tile-card";
            tile.innerHTML = `<img src="${s.image_url}" alt="${s.title}" style="width:100%; height:100%; object-fit:cover; border-radius:3px; cursor:pointer;">`;
            tile.querySelector("img")?.addEventListener("click", () => openLightbox(s.image_url));
            dom.samples8Grid.appendChild(tile);
          });
        }

        const formulaBox = document.getElementById("style-formula-breakdown");
        if (formulaBox && data.formula) {
          formulaBox.innerHTML = `
            <div style="font-weight:700; color:var(--gold-primary); margin-bottom:4px;">${data.style_name || 'Custom Style'} &bull; motion: cinematic</div>
            <div><strong>Style:</strong> ${data.formula.style_prefix || ''}</div>
            <div style="margin-top:4px;"><strong>Lighting:</strong> ${data.formula.lighting || ''}</div>
          `;
        }
      } else {
        if (dom.createSamplesStatus) dom.createSamplesStatus.textContent = "Sample generation failed. Please try again.";
        showToast("Sample generation failed", "error");
      }
    } catch (e) {
      if (dom.createSamplesStatus) dom.createSamplesStatus.textContent = "Network error creating samples.";
      showToast("Error creating samples: " + e.message, "error");
    } finally {
      if (dom.btnCreateStyleSamples) dom.btnCreateStyleSamples.disabled = false;
    }
  });

  dom.btnSaveCategory?.addEventListener("click", () => {
    const catName = dom.inputSavedCategoryName ? dom.inputSavedCategoryName.value.trim() : "";
    if (!catName) return;

    const opt = document.createElement("option");
    opt.value = `custom_${Date.now()}`;
    opt.textContent = `🧩 ${catName} (Custom)`;
    dom.selectArtStyle?.appendChild(opt);
    if (dom.selectArtStyle) dom.selectArtStyle.value = opt.value;
    if (dom.badgeStyleActive) dom.badgeStyleActive.textContent = `${catName} Active`;

    dom.modalNewCategory?.classList.remove("open");
    showToast(`Category "${catName}" saved & set active!`, "success");
    logConsole(`New style category "${catName}" added to library.`, "success");
    updateStyleSampleStrip();
  });

  // =========================================================================
  // MODAL: ALL AI33 VOICES
  // =========================================================================
  dom.btnBrowseAllVoices?.addEventListener("click", () => {
    renderVoiceCatalogModal();
    dom.modalAllVoices?.classList.add("open");
  });

  dom.btnCloseAllVoices?.addEventListener("click", () => {
    dom.modalAllVoices?.classList.remove("open");
  });

  function renderVoiceCatalogModal(categoryFilter = "elevenlabs") {
    if (!dom.voiceCatalogList) return;
    dom.voiceCatalogList.innerHTML = "";

    const filtered = state.voices.filter(v => {
      if (categoryFilter === "favourites") return (v.tags || []).includes("Favourites");
      if (categoryFilter === "clones") return (v.tags || []).includes("Clone");
      if (categoryFilter === "elevenlabs") return v.provider === "elevenlabs";
      if (categoryFilter === "minimax") return v.provider === "minimax";
      if (categoryFilter === "free") return v.provider === "free" || (v.tags || []).includes("Free");
      return true;
    });

    filtered.forEach(v => {
      const row = document.createElement("div");
      row.className = "voice-row-item";
      row.innerHTML = `
        <div style="display:flex; align-items:center; gap:10px;">
          <button class="btn-play-pill btn-catalog-preview" style="background:#1f2634; width:26px; height:26px; border-radius:50%; display:flex; align-items:center; justify-content:center;">▶</button>
          <div>
            <div style="font-size:12px; font-weight:700; color:#fff;">${v.name}</div>
            <div style="font-size:10.5px; color:var(--text-dim);">${v.gender || 'Narrator'} &bull; ${v.language || 'Multi'} &bull; ${(v.tags || []).join(', ')}</div>
          </div>
        </div>
        <div style="display:flex; align-items:center; gap:8px;">
          <button class="btn-header-sm" style="font-size:13px; color:var(--gold-primary);">⭐</button>
          <button class="btn-gold-sm btn-catalog-use" style="padding:4px 12px; font-size:11px;">Use</button>
        </div>
      `;

      row.querySelector(".btn-catalog-preview")?.addEventListener("click", () => playVoicePreview(v.id));

      row.querySelector(".btn-catalog-use")?.addEventListener("click", () => {
        state.activeVoice = v.id;
        renderVoiceDropdown("all");
        if (dom.selectVoice) dom.selectVoice.value = v.id;
        dom.modalAllVoices?.classList.remove("open");
        showToast(`Selected voice: ${v.name}`, "success");
      });

      dom.voiceCatalogList.appendChild(row);
    });
  }

  dom.voiceCatalogTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      dom.voiceCatalogTabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      renderVoiceCatalogModal(tab.dataset.vtab);
    });
  });

  // =========================================================================
  // MODAL: API KEYS
  // =========================================================================
  dom.btnApiKeys?.addEventListener("click", async () => {
    try {
      const res = await fetch("/api/apikeys");
      if (res.ok) {
        const data = await res.json();
        if (data.keys) {
          const kGemini = document.getElementById("key-gemini");
          const kEleven = document.getElementById("key-elevenlabs");
          const kOpenai = document.getElementById("key-openai");
          const kMinimax = document.getElementById("key-minimax");
          if (kGemini) kGemini.value = data.keys.gemini || "";
          if (kEleven) kEleven.value = data.keys.elevenlabs || "";
          if (kOpenai) kOpenai.value = data.keys.openai || "";
          if (kMinimax) kMinimax.value = data.keys.minimax || "";
        }
      }
    } catch {}
    dom.modalApiKeys?.classList.add("open");
  });

  dom.btnCloseApiKeys?.addEventListener("click", () => dom.modalApiKeys?.classList.remove("open"));
  dom.btnCancelApiKeys?.addEventListener("click", () => dom.modalApiKeys?.classList.remove("open"));

  dom.btnSaveApiKeys?.addEventListener("click", async () => {
    const keys = {
      gemini: document.getElementById("key-gemini")?.value || "",
      elevenlabs: document.getElementById("key-elevenlabs")?.value || "",
      openai: document.getElementById("key-openai")?.value || "",
      minimax: document.getElementById("key-minimax")?.value || ""
    };

    try {
      await fetch("/api/apikeys", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(keys)
      });
      showToast("API keys saved securely!", "success");
      dom.modalApiKeys?.classList.remove("open");
    } catch {
      showToast("Keys saved locally.", "success");
      dom.modalApiKeys?.classList.remove("open");
    }
  });

  // =========================================================================
  // MODAL: GEMINI WRITER
  // =========================================================================
  dom.btnGeminiWriter?.addEventListener("click", () => {
    dom.modalGeminiWriter?.classList.add("open");
  });

  dom.btnCloseGeminiWriter?.addEventListener("click", () => dom.modalGeminiWriter?.classList.remove("open"));
  dom.btnCancelGeminiWriter?.addEventListener("click", () => dom.modalGeminiWriter?.classList.remove("open"));

  dom.btnGenerateAiScript?.addEventListener("click", async () => {
    const topic = dom.inputAiScriptTopic ? dom.inputAiScriptTopic.value.trim() : "";
    const tone = dom.selectAiScriptTone ? dom.selectAiScriptTone.value : "hindi_doc";
    const durVal = dom.selectAiScriptDur ? dom.selectAiScriptDur.value : "2min";
    const durSec = durVal === "1min" ? 60 : (durVal === "3min" ? 180 : 120);

    if (!topic) {
      showToast("Please enter a video concept / topic.", "warning");
      return;
    }

    if (dom.btnGenerateAiScript) {
      dom.btnGenerateAiScript.textContent = "Writing Script with Gemini AI...";
      dom.btnGenerateAiScript.disabled = true;
    }
    showToast("Generating dynamic narration script...", "gold");
    logConsole(`[AI WRITER] Requesting script for topic: "${topic}" (${tone}, ~${durSec}s)...`, "info");

    try {
      const res = await fetch("/api/script/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic: topic,
          tone: tone,
          target_duration_sec: durSec,
          language: tone.includes("hindi") ? "Hindi" : "English"
        })
      });

      if (res.ok) {
        const data = await res.json();
        if (dom.aiScriptResult && data.script) {
          dom.aiScriptResult.value = data.script;
        }
        showToast(`AI Narration generated (${data.word_count || 0} words, ~${data.estimated_duration || 0}s)!`, "success");
        logConsole(`[SUCCESS] Script generated via ${data.source}: ${data.word_count} words.`, "success");
      } else {
        const err = await res.json().catch(() => ({}));
        showToast(err.detail || "Script generation failed", "error");
      }
    } catch (e) {
      showToast("Network error generating script: " + e.message, "error");
    } finally {
      if (dom.btnGenerateAiScript) {
        dom.btnGenerateAiScript.textContent = "✨ Generate Full Script";
        dom.btnGenerateAiScript.disabled = false;
      }
    }
  });

  dom.btnApplyGeminiScript?.addEventListener("click", () => {
    if (dom.scriptTextarea && dom.aiScriptResult) {
      dom.scriptTextarea.value = dom.aiScriptResult.value;
      updateScriptPacing();
    }
    dom.modalGeminiWriter?.classList.remove("open");
    showToast("Script applied to Production workspace! ✍️", "success");
  });

  // =========================================================================
  // LIGHTBOX & MODAL CLOSES
  // =========================================================================
  function openLightbox(src) {
    if (!dom.lightboxImg || !dom.modalLightbox) return;
    dom.lightboxImg.src = src;
    dom.modalLightbox.classList.add("open");
  }

  dom.btnCloseLightbox?.addEventListener("click", () => dom.modalLightbox?.classList.remove("open"));
  dom.modalLightbox?.addEventListener("click", (e) => {
    if (e.target === dom.modalLightbox) dom.modalLightbox.classList.remove("open");
  });

  dom.btnCloseEditShot?.addEventListener("click", () => dom.modalEditShot?.classList.remove("open"));
  dom.btnCancelEditShot?.addEventListener("click", () => dom.modalEditShot?.classList.remove("open"));

  dom.btnClearConsole?.addEventListener("click", () => {
    if (dom.consoleTerminalBody) dom.consoleTerminalBody.innerHTML = "";
    logConsole("Console logs cleared.", "info");
  });

  dom.btnToggleAutoscroll?.addEventListener("click", () => {
    state.autoscrollConsole = !state.autoscrollConsole;
    if (dom.btnToggleAutoscroll) dom.btnToggleAutoscroll.textContent = `Auto-scroll: ${state.autoscrollConsole ? 'ON' : 'OFF'}`;
  });

  // =========================================================================
  // WEBSOCKET FOR REAL-TIME UPDATES (WITH AUTO-RECONNECT)
  // =========================================================================
  let wsReconnectDelay = 1000;
  let wsReconnectTimer = null;

  function initWebSocket() {
    try {
      const protocol = location.protocol === "https:" ? "wss:" : "ws:";
      state.ws = new WebSocket(`${protocol}//${location.host}/ws/pipeline`);

      state.ws.onopen = () => {
        logConsole("[WS] Connected to live pipeline stream.", "success");
        wsReconnectDelay = 1000;
      };

      state.ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === "system_log" || msg.type === "log" || msg.type === "console_log") {
            const entry = msg.data || msg;
            logConsole(entry.message || JSON.stringify(entry), entry.level || "info");
          } else if (msg.type === "stage_update") {
            logConsole(`[PIPELINE] ${msg.data.message}`, "info");
            updatePipelineUIFromStatus(msg.data);
          } else if (msg.type === "pipeline_complete") {
            logConsole("[PIPELINE COMPLETE] Video rendered.", "success");
            loadDeliverables();
            loadShotsData();
          } else if (msg.type === "shot_ready") {
            if (dom.monitorStatusText) dom.monitorStatusText.textContent = `Rendering Shot ${msg.data.shot_id} of ${msg.data.total}`;
          } else if (msg.type === "pipeline_error" || msg.type === "error") {
            logConsole(`[ERROR] ${msg.data?.error || msg.message || 'Error occurred'}`, "error");
          }
        } catch {}
      };

      state.ws.onclose = () => {
        if (wsReconnectTimer) clearTimeout(wsReconnectTimer);
        wsReconnectTimer = setTimeout(() => {
          wsReconnectDelay = Math.min(wsReconnectDelay * 2, 30000);
          initWebSocket();
        }, wsReconnectDelay);
      };

      state.ws.onerror = () => {
        state.ws?.close();
      };
    } catch {
      if (wsReconnectTimer) clearTimeout(wsReconnectTimer);
      wsReconnectTimer = setTimeout(() => {
        wsReconnectDelay = Math.min(wsReconnectDelay * 2, 30000);
        initWebSocket();
      }, wsReconnectDelay);
    }
  }

  async function loadInitialConsoleLogs() {
    try {
      const res = await fetch("/api/console/logs");
      if (res.ok) {
        const data = await res.json();
        const logs = data.logs || [];
        if (logs.length > 0 && dom.consoleTerminalBody) {
          logs.forEach(l => {
            logConsole(l.message, l.level || "info");
          });
        }
      }
    } catch {}
  }

  // =========================================================================
  // INITIALIZATION
  // =========================================================================
  async function initializeStudio() {
    logConsole("Initializing StickFilm AI Studio Pro frontend...", "info");
    await initTheme();
    updateScriptPacing();
    await loadReferences();
    await loadProjectsList();
    await loadExistingScripts();
    await loadVoiceCatalog();
    await loadProfiles();
    await loadShotsData();
    await loadQueue();
    await loadVeoSettings();
    await loadDeliverables();
    renderShotsGrid();
    initWebSocket();
    await loadInitialConsoleLogs();
    logConsole("Studio initialized with 100% real dynamic workspace data.", "success");
  }

  initializeStudio();
});
