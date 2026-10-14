"""
Seed Project Builder for StickFilm AI Studio Pro: project_bhai_1
Populates:
- script.txt
- timestamps.json (55 shots with word timings)
- prompts.json (55 cinematic visual prompts)
- shots/ (55 high-res shot images)
- voiceover.mp3 & bg_music.mp3
- thumbnails/ (4 viral thumbnails)
- upload.txt
- project bhai 1.mp4 (1080p rendered video)
"""

import os
import sys
import json
import math
import asyncio
import subprocess
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, os.path.abspath("."))

from vidgen.image_engine import ImageEngine
from vidgen.video_renderer import VideoRenderer
from vidgen.thumbnail_engine import ThumbnailEngine
from vidgen.metadata_engine import MetadataEngine

PROJECT_DIR = Path("c:/Users/SSC/Desktop/Stickman/projects/project_bhai_1")
PROJECT_DIR.mkdir(parents=True, exist_ok=True)
SHOTS_DIR = PROJECT_DIR / "shots"
SHOTS_DIR.mkdir(parents=True, exist_ok=True)
THUMBS_DIR = PROJECT_DIR / "thumbnails"
THUMBS_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# 1. 55 Shots Master Dataset
# -----------------------------------------------------------------------------
SHOTS_DATA = [
    {
        "index": 1, "duration": 2.6,
        "subtitle": "पूरा दुनिया बदल देने वाला खोज था।",
        "prompt": "Vast prehistoric landscape at golden sunset with dramatic rugged cliffs and ancient clouds, cinematic establishing shot 8k"
    },
    {
        "index": 2, "duration": 2.5,
        "subtitle": "वो पहली आग सिर्फ लकड़ी नहीं जला रही थी...",
        "prompt": "Extreme macro close-up of dry moss and prehistoric twigs slowly catching a glowing ember, soft smoke spiraling"
    },
    {
        "index": 3, "duration": 2.8,
        "subtitle": "उसने इंसानी दिमाग को जला दिया था।",
        "prompt": "Silhouetted prehistoric human head with glowing neural network of golden fire inside the brain, mind evolution concept"
    },
    {
        "index": 4, "duration": 2.4,
        "subtitle": "सोचो, लाखों साल पहले की दुनिया कैसी थी।",
        "prompt": "Cold vast ice age tundra plains under a frozen indigo twilight with distant glacier ridges"
    },
    {
        "index": 5, "duration": 2.5,
        "subtitle": "अंधेरे में घिरे हमारे लाचार पूर्वज...",
        "prompt": "Primitive prehistoric human tribe shivering and huddled closely together inside a pitch-black cave"
    },
    {
        "index": 6, "duration": 2.4,
        "subtitle": "ठंड से कांपते हुए और भूख से तड़पते हुए...",
        "prompt": "Prehistoric hunter wrapped in thin animal pelt braving a howling blizzard storm, looking desperate"
    },
    {
        "index": 7, "duration": 2.5,
        "subtitle": "रात होते ही चारों तरफ सिर्फ खौफ था।",
        "prompt": "Two glowing predatory eyes staring out from thick dark prehistoric jungle shadows, suspenseful atmosphere"
    },
    {
        "index": 8, "duration": 2.6,
        "subtitle": "क्योंकि रात इंसानों की नहीं, जानवरों की थी।",
        "prompt": "Fierce saber-toothed cat predator with long fangs pacing stealthily on a high rock shelf in moonlight"
    },
    {
        "index": 9, "duration": 2.5,
        "subtitle": "लेकिन फिर एक दिन, प्रकृति ने इशारा किया।",
        "prompt": "Ominous dark purple storm clouds gathering rapidly over an ancient prehistoric savannah valley"
    },
    {
        "index": 10, "duration": 2.7,
        "subtitle": "आसमान से गिरी एक भीषण बिजली!",
        "prompt": "Blinding fork of lightning striking a massive ancient tree, exploding into bright roaring orange fire"
    },
    {
        "index": 11, "duration": 2.5,
        "subtitle": "जंगल में भड़की पहली प्राकृतिक दावानल।",
        "prompt": "A line of wild fire burning across primeval dry brush, billowing smoke rising into the stormy sky"
    },
    {
        "index": 12, "duration": 2.4,
        "subtitle": "सारे खूंखार जानवर डर कर भाग रहे थे।",
        "prompt": "Silhouettes of running woolly mammoths and predators fleeing in panic from the advancing flames"
    },
    {
        "index": 13, "duration": 2.6,
        "subtitle": "लेकिन एक इंसान दूर खड़ा देखता रहा...",
        "prompt": "A brave prehistoric caveman with shaggy hair standing still, mesmerized by the dancing flames"
    },
    {
        "index": 14, "duration": 2.5,
        "subtitle": "उसने महसूस किया कि उस आग के पास गर्मी थी।",
        "prompt": "Caveman cautiously holding out a weather-beaten hand towards the glowing heat of a burning branch"
    },
    {
        "index": 15, "duration": 2.6,
        "subtitle": "और शिकारी जानवर भी उससे दूर भाग रहे थे!",
        "prompt": "A fierce predator hesitating and retreating into darkness as it faces the warm glow of the fire"
    },
    {
        "index": 16, "duration": 2.5,
        "subtitle": "उसने हिम्मत कर एक जलती टहनी उठाई।",
        "prompt": "Strong tanned caveman gripping a blazing branch, golden fire reflecting brightly in his determined eyes"
    },
    {
        "index": 17, "duration": 2.7,
        "subtitle": "वो दुनिया की सबसे पहली मशाल थी!",
        "prompt": "Heroic low-angle shot of the caveman raising a blazing wooden torch high into the starry prehistoric night sky"
    },
    {
        "index": 18, "duration": 2.4,
        "subtitle": "लेकिन वो आग ज्यादा देर नहीं टिक सकी...",
        "prompt": "Heavy raindrops falling from dark storm clouds, hitting the flame with clouds of white steam"
    },
    {
        "index": 19, "duration": 2.5,
        "subtitle": "बारिश की बूंदों ने उस लौ को बुझा दिया।",
        "prompt": "Close-up of the torch dying out into cold black charcoal and faint wisps of gray smoke"
    },
    {
        "index": 20, "duration": 2.5,
        "subtitle": "और इंसान फिर से अंधेरे में लौट आया।",
        "prompt": "Caveman kneeling on wet earth looking down at the cold extinguished wood with sorrow and longing"
    },
    {
        "index": 21, "duration": 2.6,
        "subtitle": "लेकिन उसके दिमाग में एक सवाल जाग चुका था।",
        "prompt": "Close-up portrait of the caveman with focused furrowed brow, intense curiosity and determination in his eyes"
    },
    {
        "index": 22, "duration": 2.5,
        "subtitle": "क्या इस आग को हम खुद बना सकते हैं?",
        "prompt": "Caveman holding two rough flint stones in his hands, examining their sharp fractured mineral edges"
    },
    {
        "index": 23, "duration": 2.5,
        "subtitle": "शुरू हुआ इतिहास का पहला वैज्ञानिक प्रयोग।",
        "prompt": "Inside the stone cave, sitting beside a neat bundle of dry wood shavings and powdered dry moss"
    },
    {
        "index": 24, "duration": 2.6,
        "subtitle": "उसने पत्थरों को आपस में टकराना शुरू किया।",
        "prompt": "Caveman vigorously striking two dark flint stones together with intense focus and muscle tension"
    },
    {
        "index": 25, "duration": 2.4,
        "subtitle": "पहली बार में कोई नतीजा नहीं निकला...",
        "prompt": "Dull impact of stones with no sparks, dust flying into the dim air of the cavern"
    },
    {
        "index": 26, "duration": 2.5,
        "subtitle": "हाथ छिल गए, उंगलियां थक कर चूर हो गईं।",
        "prompt": "Bruised and calloused hands resting on stone, sweat dripping down the caveman's face"
    },
    {
        "index": 27, "duration": 2.4,
        "subtitle": "सैकड़ों बार की नाकाम कोशिशें...",
        "prompt": "Scores of broken flint shards scattered across the rocky floor around the patient primitive inventor"
    },
    {
        "index": 28, "duration": 2.7,
        "subtitle": "और फिर अचानक—एक चमकीली चिंगारी निकली!",
        "prompt": "Macro flash of brilliant golden-white spark flying from the sharp collision point of two flint stones"
    },
    {
        "index": 29, "duration": 2.5,
        "subtitle": "वो चिंगारी सूखे पत्तों पर जा गिरी।",
        "prompt": "Glowing orange spark landing on a nest of shredded dry bark, beginning to glow and smolder"
    },
    {
        "index": 30, "duration": 2.6,
        "subtitle": "उसने बड़ी नजाकत से अपनी सांसों की फूंक दी...",
        "prompt": "Caveman blowing gentle breath onto the tinder, cheeks puffed, red ember glowing brighter with each breath"
    },
    {
        "index": 31, "duration": 2.7,
        "subtitle": "और धुआं एक सुनहरी लपट में बदल गया!",
        "prompt": "Sudden burst of golden yellow flame erupting from the dry tinder, lighting up the entire cave"
    },
    {
        "index": 32, "duration": 2.6,
        "subtitle": "इंसान ने पहली बार अपनी मर्जी से आग बनाई!",
        "prompt": "Caveman throwing both arms up in wild ecstatic celebration, shouting in triumph in front of the flame"
    },
    {
        "index": 33, "duration": 2.5,
        "subtitle": "गुफा की दीवारें उस उजाले से नहा उठीं।",
        "prompt": "Warm golden light dancing across ancient cave wall paintings of mammoths and running hunters"
    },
    {
        "index": 34, "duration": 2.6,
        "subtitle": "पूरा कबीला उस अजूबे को देखने दौड़ पड़ा।",
        "prompt": "Prehistoric men, women, and children running from cave shadows, staring in utter wonder at the campfire"
    },
    {
        "index": 35, "duration": 2.5,
        "subtitle": "पत्थरों के बीच एक सुरक्षित अलाव सजाया गया।",
        "prompt": "A tidy circular hearth of river stones enclosing a crackling campfire with orange coals"
    },
    {
        "index": 36, "duration": 2.5,
        "subtitle": "उस रात गुफा में किसी को ठंड नहीं लगी।",
        "prompt": "Tribe sleeping peacefully around the campfire, bathed in warm amber light and deep security"
    },
    {
        "index": 37, "duration": 2.6,
        "subtitle": "बाहर अंधेरे में खड़े शिकारी जानवर बेबस थे।",
        "prompt": "Giant predators pacing in the cold outer darkness, unable to breach the protective circle of light"
    },
    {
        "index": 38, "duration": 2.5,
        "subtitle": "आग ने इंसान को प्रकृति का शिकार बनने से बचाया।",
        "prompt": "Caveman guardian standing tall at cave entrance with glowing torch, keeping the wilderness at bay"
    },
    {
        "index": 39, "duration": 2.6,
        "subtitle": "अब इंसान शिकार नहीं, बल्कि स्वामी था।",
        "prompt": "Tribe gathering together with flint-tipped spears and flaming torches, standing proud atop a ridge"
    },
    {
        "index": 40, "duration": 2.4,
        "subtitle": "लेकिन सबसे बड़ा जादू अभी बाकी था...",
        "prompt": "Piece of wild hunt meat dropping into the glowing red embers of the fire pit"
    },
    {
        "index": 41, "duration": 2.5,
        "subtitle": "कच्चा मांस चबाने की वो पुरानी मजबूरी...",
        "prompt": "Primitive hunter looking at tough raw sinew in frustration before discovering roasting"
    },
    {
        "index": 42, "duration": 2.6,
        "subtitle": "आग ने खाने को स्वादिष्ट और कोमल बना दिया।",
        "prompt": "Tender cooked meat sizzling on wooden spits over glowing coals, mouth-watering aroma and steam"
    },
    {
        "index": 43, "duration": 2.5,
        "subtitle": "पके हुए भोजन से शरीर को मिली दोगुनी ऊर्जा।",
        "prompt": "Strong, well-nourished prehistoric clan smiling and feasting together around the crackling fire"
    },
    {
        "index": 44, "duration": 2.6,
        "subtitle": "और यही ऊर्जा इंसानी दिमाग के विकास में लगी।",
        "prompt": "Visual metaphor of human brain glowing with bright electric synapses, expanding intelligence"
    },
    {
        "index": 45, "duration": 2.5,
        "subtitle": "इंसानी दिमाग का आकार तेजी से बढ़ने लगा!",
        "prompt": "Morphing anatomical progression showing evolution of human skull and expanding cerebral cortex"
    },
    {
        "index": 46, "duration": 2.6,
        "subtitle": "अलाव के इर्द-गिर्द बैठकर कहानियों का जन्म हुआ।",
        "prompt": "Wise tribal elder gesturing animatedly as young listeners sit captivated by the campfire stories"
    },
    {
        "index": 47, "duration": 2.5,
        "subtitle": "भाषा बनी, संस्कृति पनपी, और रिश्ते मजबूत हुए।",
        "prompt": "Early humans exchanging gestures and spoken words, carving shared memories into the stone hearth"
    },
    {
        "index": 48, "duration": 2.6,
        "subtitle": "अकेले भटकने वाला जीव एक समाज बन गया।",
        "prompt": "A bustling ancient primitive settlement with wooden shelters and multiple glowing campfires under the stars"
    },
    {
        "index": 49, "duration": 2.5,
        "subtitle": "मिट्टी के बर्तन पकाने से धातु पिघलाने तक...",
        "prompt": "Bronze Age forge with glowing molten copper and bronze being poured into stone weapon molds"
    },
    {
        "index": 50, "duration": 2.6,
        "subtitle": "भाप के इंजन से लेकर बिजली के पहियों तक...",
        "prompt": "Victorian era steam locomotive engine charging forward through billows of fiery coal smoke"
    },
    {
        "index": 51, "duration": 2.5,
        "subtitle": "हर तकनीक की जड़ में वही पहली आग थी।",
        "prompt": "Glowing futuristic microchip circuitry transforming smoothly into golden flames of prehistoric fire"
    },
    {
        "index": 52, "duration": 2.4,
        "subtitle": "सोचो, अगर उस रात वो चिंगारी ना जलती...",
        "prompt": "Contemplative figure standing on a balcony overlooking a vast glittering modern metropolis at night"
    },
    {
        "index": 53, "duration": 2.6,
        "subtitle": "तो आज ये जगमगाते शहर कभी ना होते।",
        "prompt": "Stunning aerial panorama of illuminated modern skyscrapers and golden highways under the night sky"
    },
    {
        "index": 54, "duration": 2.7,
        "subtitle": "रॉकेट के इंजनों में जलती आग, उसी की संतान है।",
        "prompt": "Massive Saturn rocket blasting off into space on a roaring pillar of flame, heading towards the moon"
    },
    {
        "index": 55, "duration": 2.8,
        "subtitle": "एक पत्थर, एक चिंगारी, और पूरी कायनात बदल गई!",
        "prompt": "Epic split-screen composition: Caveman holding primitive torch on left, astronaut floating among stars on right"
    },
]

# Calculate running timecodes for all 55 shots
current_time = 0.0
for shot in SHOTS_DATA:
    shot["start_time"] = round(current_time, 2)
    current_time += shot["duration"]
    shot["end_time"] = round(current_time, 2)

    # Word-level breakdown for karaoke highlight
    words = shot["subtitle"].split()
    w_dur = shot["duration"] / max(1, len(words))
    word_list = []
    for wi, w in enumerate(words):
        word_list.append({
            "word": w,
            "start_time": round(shot["start_time"] + wi * w_dur, 2),
            "end_time": round(min(shot["end_time"], shot["start_time"] + (wi + 1) * w_dur), 2)
        })
    shot["words"] = word_list

print(f"Total shots: {len(SHOTS_DATA)}, Total duration: {current_time:.2f} seconds (~2:20 pace)")

# -----------------------------------------------------------------------------
# 2. Write script.txt, timestamps.json, and prompts.json
# -----------------------------------------------------------------------------
script_text = " ".join(s["subtitle"] for s in SHOTS_DATA)
with open(PROJECT_DIR / "script.txt", "w", encoding="utf-8") as f:
    f.write(script_text)

with open(PROJECT_DIR / "timestamps.json", "w", encoding="utf-8") as f:
    json.dump(SHOTS_DATA, f, ensure_ascii=False, indent=2)

prompts_data = [{"index": s["index"], "prompt": s["prompt"], "duration": s["duration"]} for s in SHOTS_DATA]
with open(PROJECT_DIR / "prompts.json", "w", encoding="utf-8") as f:
    json.dump(prompts_data, f, ensure_ascii=False, indent=2)

print("Saved script.txt, timestamps.json, prompts.json!")

# -----------------------------------------------------------------------------
# 3. Generate 55 High-Res Shot Images (ImageEngine) & Run 0 Blanks Guard
# -----------------------------------------------------------------------------
print("Synthesizing 55 shot images via ImageEngine...")
img_eng = ImageEngine(1920, 1080)
for s in SHOTS_DATA:
    idx = s["index"]
    p_primary = SHOTS_DIR / f"shot_{idx:03d}.png"
    p_alt = SHOTS_DIR / f"{idx}.png"

    # Only generate if missing or re-synthesizing
    img = img_eng.generate_shot_image(
        prompt=s["prompt"],
        shot_index=idx,
        total_shots=len(SHOTS_DATA),
        style="Colorful Prehistoric",
        seed=idx * 173,
    )
    img.save(p_primary, format="PNG", optimize=True)
    img.save(p_alt, format="PNG", optimize=True)

print("Stage 5 Image Verification (0 Blanks Guard) running...")
v_report = img_eng.verify_shots_integrity(SHOTS_DIR, expected_count=55)
print(f"0 Blanks Guard Report: Checked: {v_report['checked_count']}, Valid: {v_report['valid_count']}, Failed: {v_report['failed_count']}")
if not v_report["all_valid"]:
    print("Auto-healing failed shots...")
    img_eng.heal_blanks(SHOTS_DIR, SHOTS_DATA, style="Colorful Prehistoric")
    v_report = img_eng.verify_shots_integrity(SHOTS_DIR, expected_count=55)
    print(f"Post-heal verification: All Valid = {v_report['all_valid']}")

# -----------------------------------------------------------------------------
# 4. Generate Voiceover (edge-tts / hi-IN-MadhurNeural) & Background Music
# -----------------------------------------------------------------------------
voiceover_path = PROJECT_DIR / "voiceover.mp3"
async def generate_speech():
    try:
        import edge_tts
        print("Synthesizing voiceover with edge-tts (hi-IN-MadhurNeural)...")
        # Synthesize full script
        communicate = edge_tts.Communicate(script_text, voice="hi-IN-MadhurNeural", rate="+0%", volume="+0%")
        await communicate.save(str(voiceover_path))
        print("Voiceover synthesized successfully!")
    except Exception as e:
        print(f"edge-tts error ({e}), generating synthesized tone track...")
        # Fallback silent/tone audio using ffmpeg
        cmd = [
            "ffmpeg", "-y", "-f", "lavfi", "-i", f"sine=frequency=440:duration={current_time}",
            "-af", "volume=0.0", "-c:a", "libmp3lame", str(voiceover_path)
        ]
        subprocess.run(cmd, capture_output=True, check=True)

asyncio.run(generate_speech())

# Generate atmospheric cinematic background music (warm ambient drone with chord swell)
bg_music_path = PROJECT_DIR / "bg_music.mp3"
static_music_path = Path("c:/Users/SSC/Desktop/Stickman/static/assets/music/cinematic_ambient.mp3")
static_music_path.parent.mkdir(parents=True, exist_ok=True)

if not bg_music_path.exists() or bg_music_path.stat().st_size == 0:
    print("Generating cinematic ambient soundtrack...")
    cmd_music = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"anoisesrc=c=pink:r=44100:a=0.08:d={current_time + 10}",
        "-f", "lavfi", "-i", f"sine=frequency=110:duration={current_time + 10}",
        "-f", "lavfi", "-i", f"sine=frequency=164.81:duration={current_time + 10}",
        "-f", "lavfi", "-i", f"sine=frequency=220:duration={current_time + 10}",
        "-filter_complex", "[1:a]volume=0.06[s1];[2:a]volume=0.04[s2];[3:a]volume=0.03[s3];[0:a][s1][s2][s3]amix=inputs=4:duration=first[mix];[mix]lowpass=f=450,afade=t=in:st=0:d=4,afade=t=out:st=135:d=5[aout]",
        "-map", "[aout]",
        "-c:a", "libmp3lame", "-b:a", "192k",
        str(bg_music_path)
    ]
    subprocess.run(cmd_music, capture_output=True, check=True)
    import shutil
    shutil.copy2(bg_music_path, static_music_path)
    print("Background music generated!")

# -----------------------------------------------------------------------------
# 5. Generate 4 High-CTR Viral Thumbnails (ThumbnailEngine)
# -----------------------------------------------------------------------------
print("Generating 4 viral YouTube thumbnails...")
thumb_eng = ThumbnailEngine(1280, 720)
thumb_paths = thumb_eng.generate_thumbnail_set(THUMBS_DIR)
print(f"Generated thumbnails: {thumb_paths}")

# -----------------------------------------------------------------------------
# 6. Generate YouTube upload.txt Metadata (MetadataEngine)
# -----------------------------------------------------------------------------
print("Generating YouTube metadata package (upload.txt)...")
meta_eng = MetadataEngine()
meta_eng.generate_upload_txt(script_text, SHOTS_DATA, PROJECT_DIR / "upload.txt", project_name="project_bhai_1")
print("Saved upload.txt!")

# -----------------------------------------------------------------------------
# 7. Render 1080p Master Video Output (VideoRenderer)
# -----------------------------------------------------------------------------
master_video_path = PROJECT_DIR / "project bhai 1.mp4"
alt_video_path = PROJECT_DIR / "output.mp4"

print("Rendering 1080p Full HD master video with FFmpeg...")
vid_ren = VideoRenderer()
vid_ren.render_master_video(
    project_dir=PROJECT_DIR,
    output_mp4_path=master_video_path,
    motion="Mix of all",
    caption_style="Word Highlight",
    aspect_ratio="16:9",
    fps=30,
)

if master_video_path.exists():
    import shutil
    shutil.copy2(master_video_path, alt_video_path)
    print(f"Master video rendered successfully! Size: {master_video_path.stat().st_size / (1024*1024):.2f} MB")

print("Project bhai 1 seed setup completed 100%!")
