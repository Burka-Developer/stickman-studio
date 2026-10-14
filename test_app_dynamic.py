"""
Verification suite for StickFilm AI Studio Pro v2.2.6
Tests all dynamic endpoints: Themes, Profiles CRUD, Shots CRUD, and Rendering
"""

import sys
import os
import json
import base64
import io
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

from fastapi.testclient import TestClient
from PIL import Image
from server import app, current_config

client = TestClient(app)

def test_theme_lifecycle():
    print("\n--- Testing Theme Lifecycle ---")
    # 1. Get current theme
    r = client.get("/api/theme")
    assert r.status_code == 200, f"Failed GET /api/theme: {r.text}"
    print("✓ GET /api/theme:", r.json())

    # 2. Test switching to all 3 themes
    for th in ["theme-obsidian", "theme-cyber", "theme-emerald"]:
        r = client.post("/api/theme", json={"theme": th})
        assert r.status_code == 200
        assert r.json()["theme"] == th
        print(f"✓ POST /api/theme -> {th}")

    # Reset to obsidian
    client.post("/api/theme", json={"theme": "theme-obsidian"})

def test_profiles_crud():
    print("\n--- Testing Profiles CRUD ---")
    # 1. Get profiles
    r = client.get("/api/profiles")
    assert r.status_code == 200
    data = r.json()
    assert "profiles" in data
    assert len(data["profiles"]) >= 1
    print(f"✓ GET /api/profiles returned {len(data['profiles'])} profiles. Active: {data['active_profile']}")

    # 2. Add new dynamic profile
    new_prof = {
        "id": "acc_tester",
        "name": "Test Automation Profile",
        "email": "test@studio.ai",
        "cookies": 50,
        "data_dir": "C:/tmp/test_dir",
        "notes": "Automated verification profile"
    }
    r = client.post("/api/profiles", json=new_prof)
    assert r.status_code == 200, f"Failed create profile: {r.text}"
    assert r.json()["profile"]["id"] == "acc_tester"
    print("✓ POST /api/profiles created profile: acc_tester")

    # 3. Update profile
    r = client.put("/api/profiles/acc_tester", json={
        "name": "Updated Test Profile",
        "cookies": 55,
        "notes": "Updated notes"
    })
    assert r.status_code == 200
    assert r.json()["profile"]["name"] == "Updated Test Profile"
    print("✓ PUT /api/profiles/acc_tester updated successfully")

    # 4. Set active
    r = client.post("/api/profiles/active", json={"profile_id": "acc_tester"})
    assert r.status_code == 200
    assert r.json()["active_profile"] == "acc_tester"
    print("✓ POST /api/profiles/active set to acc_tester")

    # 5. Verify session
    r = client.post("/api/profiles/acc_tester/verify")
    assert r.status_code == 200
    assert r.json()["status"] == "Active"
    print("✓ POST /api/profiles/acc_tester/verify session verified")

    # 6. Delete test profile
    # Switch back to acc1 first
    client.post("/api/profiles/active", json={"profile_id": "acc1"})
    r = client.delete("/api/profiles/acc_tester")
    assert r.status_code == 200
    print("✓ DELETE /api/profiles/acc_tester deleted successfully")

def test_shots_crud_and_images():
    print("\n--- Testing Shots CRUD & Image Management ---")
    project_id = "test_crud_proj"
    r_create = client.post("/api/projects/create", json={"name": project_id})
    assert r_create.status_code == 200

    # 1. Fetch project shots
    r = client.get(f"/api/projects/{project_id}/shots")
    assert r.status_code == 200
    data = r.json()
    initial_total = data["total"]
    print(f"✓ GET /api/projects/{project_id}/shots: {initial_total} shots found")

    # 2. Add a dynamic shot
    new_shot = {
        "project_id": project_id,
        "index": initial_total + 1,
        "subtitle": "A spark ignited the journey.",
        "prompt": "Vibrant dramatic prehistoric humans gathered around a radiant fire inside a mystical cavern, 8k cinematic lighting",
        "duration": 3.0
    }
    r = client.post(f"/api/projects/{project_id}/shots/add", json=new_shot)
    assert r.status_code == 200, f"Failed add shot: {r.text}"
    add_data = r.json()
    new_shot_idx = add_data["shot"]["index"]
    assert add_data["total"] == initial_total + 1
    print(f"✓ POST /api/projects/{project_id}/shots/add created shot #{new_shot_idx}")

    # Verify image was created
    shots_dir = Path("projects") / project_id / "shots"
    assert (shots_dir / f"{new_shot_idx}.png").exists() or (shots_dir / f"shot_{new_shot_idx:03d}.png").exists()
    print(f"✓ Frame for shot #{new_shot_idx} successfully generated and verified on disk")

    # 3. Edit shot subtitle, prompt, and duration
    r = client.put(f"/api/projects/{project_id}/shots/{new_shot_idx}", json={
        "project_id": project_id,
        "shot_id": new_shot_idx,
        "subtitle": "The spark changed history.",
        "prompt": "Ancient fire sparks rising into the starry night sky",
        "duration": 3.5
    })
    assert r.status_code == 200
    assert r.json()["shot"]["duration"] == 3.5
    assert r.json()["shot"]["subtitle"] == "The spark changed history."
    print(f"✓ PUT /api/projects/{project_id}/shots/{new_shot_idx} updated metadata")

    # 4. Redraw shot
    r = client.post(f"/api/projects/{project_id}/shots/{new_shot_idx}/redraw", json={
        "project_id": project_id,
        "shot_id": new_shot_idx
    })
    assert r.status_code == 200
    assert r.json()["success"] is True
    print(f"✓ POST /api/projects/{project_id}/shots/{new_shot_idx}/redraw frame redrawn")

    # 5. Upload custom image to shot
    buf = io.BytesIO()
    test_img = Image.new("RGB", (1280, 720), color=(20, 180, 120))
    test_img.save(buf, format="PNG")
    buf.seek(0)
    files = {"file": ("custom_upload.png", buf, "image/png")}
    r = client.post(f"/api/projects/{project_id}/shots/{new_shot_idx}/upload", files=files)
    assert r.status_code == 200
    assert r.json()["success"] is True
    print(f"✓ POST /api/projects/{project_id}/shots/{new_shot_idx}/upload custom image replaced frame")

    # 6. Delete the test shot to restore timeline
    r = client.delete(f"/api/projects/{project_id}/shots/{new_shot_idx}")
    assert r.status_code == 200
    assert r.json()["total"] == initial_total
    print(f"✓ DELETE /api/projects/{project_id}/shots/{new_shot_idx} deleted and timeline restored to {initial_total}")

    # 7. Clean up test project so projects directory stays pristine
    client.post("/api/projects/delete", json={"project_id": project_id})
    print(f"✓ Cleaned up test project {project_id}")

def test_static_files():
    print("\n--- Testing Frontend Assets ---")
    r = client.get("/")
    assert r.status_code == 200
    assert "StickFilm AI Studio Pro" in r.text
    # Verify removal of $5+ referral
    assert "$5+ referral" not in r.text
    assert "partner-box" not in r.text
    print("✓ Frontend root HTML loaded clean (no referral artifacts)")

    r = client.get("/static/styles.css")
    assert r.status_code == 200
    assert "theme-obsidian" in r.text
    assert "theme-cyber" in r.text
    assert "theme-emerald" in r.text
    print("✓ styles.css loaded with 3 theme palettes")

    r = client.get("/static/app.js")
    assert r.status_code == 200
    assert "applyTheme" in r.text
    assert "loadProfiles" in r.text
    assert "handleShotRedraw" in r.text
    print("✓ app.js loaded with full dynamic event loop")

def test_veo_and_voices():
    print("\n--- Testing Veo Settings & Voices ---")
    r = client.get("/api/veo/settings")
    assert r.status_code == 200
    print("✓ GET /api/veo/settings:", r.json())

    r = client.get("/api/voices")
    assert r.status_code == 200
    assert r.json()["total"] > 0
    print(f"✓ GET /api/voices returned {r.json()['total']} voices")

def test_character_references():
    print("\n--- Testing Character References Management ---")
    # 1. List existing references
    r = client.get("/api/references")
    assert r.status_code == 200, f"Failed GET /api/references: {r.text}"
    data = r.json()
    assert "references" in data
    assert data["total"] >= 0
    initial_total = data["total"]
    print(f"✓ GET /api/references: Found {initial_total} character reference images")

    # 2. Upload custom reference image
    buf = io.BytesIO()
    test_img = Image.new("RGB", (512, 512), color=(180, 50, 90))
    test_img.save(buf, format="PNG")
    buf.seek(0)
    files = {"file": ("unit_test_hero.png", buf, "image/png")}
    r = client.post("/api/references/upload", files=files)
    assert r.status_code == 200, f"Failed upload reference: {r.text}"
    uploaded_name = r.json()["filename"]
    print(f"✓ POST /api/references/upload: Saved {uploaded_name}")

    # Verify file exists on disk
    ref_path = Path("static/assets/refs") / uploaded_name
    assert ref_path.exists(), f"Uploaded file {ref_path} not found on disk"

    # Verify listed in GET
    r2 = client.get("/api/references")
    assert r2.status_code == 200
    assert r2.json()["total"] == initial_total + 1
    assert any(ref["filename"] == uploaded_name for ref in r2.json()["references"])
    print(f"✓ GET /api/references: Confirmed {uploaded_name} in catalog")

    # 3. Delete reference image
    r3 = client.delete(f"/api/references/{uploaded_name}")
    assert r3.status_code == 200, f"Failed delete reference: {r3.text}"
    assert not ref_path.exists(), f"Deleted file {ref_path} still exists on disk"
    print(f"✓ DELETE /api/references/{uploaded_name}: File successfully deleted from disk")

    # Verify count restored
    r4 = client.get("/api/references")
    assert r4.json()["total"] == initial_total
    print(f"✓ References catalog restored to {initial_total} images")

def test_queue():
    print("\n--- Testing Real Workspace Queue ---")
    r = client.get("/api/queue")
    assert r.status_code == 200, f"Failed GET /api/queue: {r.text}"
    data = r.json()
    assert "queue" in data
    print(f"✓ GET /api/queue: {len(data['queue'])} workspace project tasks found")

if __name__ == "__main__":
    print("==================================================")
    print("🚀 RUNNING STICKFILM FULL DYNAMIC SYSTEM TEST SUITE")
    print("==================================================")
    try:
        test_theme_lifecycle()
        test_profiles_crud()
        test_character_references()
        test_shots_crud_and_images()
        test_static_files()
        test_veo_and_voices()
        test_queue()
        print("\n==================================================")
        print("🎉 ALL TESTS PASSED WITH 100% SUCCESS!")
        print("==================================================")
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
