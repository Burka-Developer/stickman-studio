import httpx
import json
import time

BASE_URL = "http://localhost:5199"

def run_tests():
    print("=== TEST 1: System and Console Logs ===")
    res = httpx.get(f"{BASE_URL}/api/console/logs")
    print(f"Status: {res.status_code}")
    data = res.json()
    print(f"Total Logs in Buffer: {data.get('total')}")
    for l in data.get("logs", [])[-5:]:
        print(f"  [{l.get('level')}] {l.get('message')}")
    assert res.status_code == 200

    print("\n=== TEST 2: Chrome Profile Launching ===")
    res = httpx.post(f"{BASE_URL}/api/profiles/acc3/launch")
    print(f"Status: {res.status_code}")
    launch_data = res.json()
    print(f"Response: {launch_data}")
    assert res.status_code == 200
    assert launch_data.get("success") is True
    assert "pid" in launch_data or "data_dir" in launch_data

    print("\n=== TEST 3: Profiles Verification ===")
    res = httpx.post(f"{BASE_URL}/api/profiles/acc3/verify")
    print(f"Verify Status: {res.status_code}")
    print(f"Verify Result: {res.json()}")
    assert res.status_code == 200

    print("\n=== TEST 4: Checking Console Logs After Profile Actions ===")
    res = httpx.get(f"{BASE_URL}/api/console/logs")
    logs = res.json().get("logs", [])
    print(f"Total Logs now: {len(logs)}")
    recent = [l["message"] for l in logs[-6:]]
    for m in recent:
        print(f"  * {m}")
    assert any("acc3" in m for m in recent)

    print("\n=== TEST 5: Pipeline with Custom Script & Art Style ===")
    custom_script = "In the year 2099, deep in the stellar reaches of Alpha Centauri, the scout vessel detected an unknown artifact pulsating with energy."
    test_proj = f"proj_test_dynamic_{int(time.time())}"

    # First get references to see available ref image
    refs_res = httpx.get(f"{BASE_URL}/api/references")
    refs = refs_res.json().get("references", [])
    ref_file = refs[0]["filename"] if refs else ""
    print(f"Using reference file: '{ref_file}'")

    run_payload = {
        "project_name": test_proj,
        "script_text": custom_script,
        "voice_id": "jerry",
        "visual_style": "3D Animated (Pixar / DreamWorks CGI Style)",
        "aspect_ratio": "16:9",
        "character_ref": ref_file,
        "world_setting": "Futuristic deep space starship bridge overlooking glowing nebulae",
        "camera_motion": "Ken Burns",
        "captions_preset": "Word Highlight",
        "profile": "acc3"
    }

    start_res = httpx.post(f"{BASE_URL}/api/pipeline/run", json=run_payload)
    print(f"Pipeline start status: {start_res.status_code}")
    print(f"Start Response: {start_res.json()}")
    assert start_res.status_code == 200

    # Wait for completion
    for _ in range(60):
        time.sleep(1.0)
        st = httpx.get(f"{BASE_URL}/api/pipeline/status").json()
        print(f"  Stage {st.get('stage')}: {st.get('stage_name')} ({st.get('progress')}%)")
        if st.get("status") in ["completed", "error"]:
            break

    print(f"Final Pipeline Status: {st.get('status')}")
    assert st.get("status") == "completed"

    # Check generated shots
    shots_res = httpx.get(f"{BASE_URL}/api/projects/{test_proj}/shots")
    shots_data = shots_res.json()
    print(f"Generated Shots Total: {shots_data.get('total')}")
    assert shots_data.get("total") > 0

    first_shot = shots_data["shots"][0]
    print(f"First Shot Subtitle: {first_shot.get('subtitle')}")
    print(f"First Shot Prompt: {first_shot.get('prompt')}")
    # Cleanup test project to keep workspace pristine
    httpx.post(f"{BASE_URL}/api/projects/delete", json={"project_id": test_proj})

    print("\nALL 5 TESTS PASSED WITH 100% SUCCESS!")

if __name__ == "__main__":
    run_tests()
