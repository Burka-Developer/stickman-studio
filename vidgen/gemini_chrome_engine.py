"""
StickFilm AI Studio Pro - Gemini Chrome Engine
Automates Google Chrome with persistent user profiles (acc1, acc2, acc3)
to generate cinematic AI images from Gemini Canvas / gemini.google.com using Playwright.
"""

import os
import sys
import time
import asyncio
import io
from pathlib import Path
from typing import Dict, List, Optional, Any
from PIL import Image

try:
    from playwright.async_api import async_playwright
except ImportError:
    async_playwright = None


class GeminiChromeEngine:
    """
    Automates Google Chrome with persistent user profiles to generate
    cinematic shots from gemini.google.com / Gemini Canvas.
    """

    def __init__(self, projects_root: Optional[str] = None, event_callback=None):
        self.projects_root = Path(projects_root or Path.cwd() / "projects")
        self.event_callback = event_callback
        self.playwright_obj = None
        self.browser_or_context = None
        self.page = None
        self.active_profile = None

    def log(self, message: str, level: str = "info"):
        if self.event_callback:
            try:
                self.event_callback("gemini_chrome_log", {"message": message, "level": level})
            except Exception:
                pass
        print(f"[GeminiChromeEngine] {message}")

    async def connect_or_launch(self, profile_id: str = "acc3") -> bool:
        """
        Connects over CDP to an already open Chrome (port 9222) or launches Chrome
        with the specified user-data-dir persistent context.
        """
        if async_playwright is None:
            self.log("Playwright not installed, skipping browser automation.", "warning")
            return False

        if self.page and not self.page.is_closed():
            return True

        try:
            self.playwright_obj = await async_playwright().start()
            
            # 1. First try connecting over CDP to running Chrome instance
            import httpx
            cdp_available = False
            try:
                r = httpx.get("http://localhost:9222/json/version", timeout=1.5)
                if r.status_code == 200:
                    cdp_available = True
            except Exception:
                cdp_available = False

            if cdp_available:
                self.log("Connecting to active Chrome session on port 9222...", "info")
                self.browser_or_context = await self.playwright_obj.chromium.connect_over_cdp("http://localhost:9222")
                contexts = self.browser_or_context.contexts
                context = contexts[0] if contexts else await self.browser_or_context.new_context()
            else:
                # 2. Launch persistent context with the profile
                profile_dir = Path("data/chrome_profiles") / profile_id
                profile_dir.mkdir(parents=True, exist_ok=True)
                self.log(f"Launching Chrome with profile directory: {profile_dir.resolve()}...", "info")
                context = await self.playwright_obj.chromium.launch_persistent_context(
                    user_data_dir=str(profile_dir.resolve()),
                    channel="chrome",
                    headless=False,
                    args=[
                        "--remote-debugging-port=9222",
                        "--disable-blink-features=AutomationControlled",
                        "--no-first-run",
                        "--no-default-browser-check"
                    ]
                )
                self.browser_or_context = context

            # Locate or open Gemini page
            gemini_page = None
            for p in context.pages:
                if "gemini.google.com" in p.url:
                    gemini_page = p
                    break

            if gemini_page is None:
                self.log("Navigating to https://gemini.google.com/app...", "info")
                gemini_page = await context.new_page()
                await gemini_page.goto("https://gemini.google.com/app", wait_until="domcontentloaded", timeout=30000)
            else:
                await gemini_page.bring_to_front()

            self.page = gemini_page
            self.active_profile = profile_id
            self.log(f"Chrome Gemini session active for profile '{profile_id}'.", "success")
            return True
        except Exception as e:
            self.log(f"Browser connection error: {e}", "warning")
            return False

    async def generate_shot_image(
        self,
        prompt: str,
        shot_index: int,
        total_shots: int,
        output_path: Path,
        style: str = "3D Animated",
        character_ref_path: Optional[Path] = None,
        profile_id: str = "acc3"
    ) -> bool:
        """
        Submits prompt to Gemini in Chrome and retrieves generated image.
        """
        connected = await self.connect_or_launch(profile_id)
        if not connected or not self.page:
            return False

        try:
            self.log(f"Submitting prompt for Shot {shot_index}/{total_shots} to Gemini Canvas...", "info")
            # Extract core prompt to avoid overwhelming Gemini chat
            clean_prompt_text = prompt
            if "Action scene:" in prompt:
                # Extract first two key clauses
                parts = [p.strip() for p in prompt.split(",") if p.strip()]
                clean_prompt_text = ", ".join(parts[:3]) if parts else prompt[:120]
            
            gemini_prompt = (
                f"Generate a 16:9 cinematic image: {clean_prompt_text}. "
                f"Style: {style}. Masterpiece visual, high quality, no text, no captions."
            )

            # Wait for Gemini input box
            input_selector = 'div[contenteditable="true"], rich-textarea p, textarea, div[role="textbox"]'
            try:
                await self.page.wait_for_selector(input_selector, timeout=5000)
            except Exception:
                pass

            input_elem = await self.page.query_selector(input_selector)
            if input_elem:
                # Count current images on page before prompt dispatch
                existing_imgs = await self.page.query_selector_all('img[src*="googleusercontent.com"], div[data-test-id*="image"] img, img.generated-image')
                initial_count = len(existing_imgs)

                # Focus and thoroughly clear any previous or stuck text
                await input_elem.click()
                await self.page.keyboard.press("Control+A")
                await self.page.keyboard.press("Backspace")
                await asyncio.sleep(0.15)

                # Insert text to trigger rich editor state events
                try:
                    await self.page.keyboard.insert_text(gemini_prompt)
                except Exception:
                    await input_elem.fill(gemini_prompt)
                await asyncio.sleep(0.3)

                # Click send button if active or press Enter
                send_button = await self.page.query_selector('button[aria-label*="Send"], button.send-button, button[aria-label*="Submit"]')
                sent = False
                if send_button:
                    try:
                        if await send_button.is_enabled():
                            await send_button.click()
                            sent = True
                    except Exception:
                        pass
                
                if not sent:
                    await self.page.keyboard.press("Enter")

                self.log(f"Prompt dispatched for Shot {shot_index}. Waiting for Gemini image generation...", "info")

                # Wait for newly generated image to appear (bounded timeout: 10s max)
                start_t = time.time()
                img_found = False
                while time.time() - start_t < 10.0:
                    current_imgs = await self.page.query_selector_all('img[src*="googleusercontent.com"], div[data-test-id*="image"] img, img.generated-image')
                    if len(current_imgs) > initial_count:
                        # Grab the newest image generated after our prompt
                        last_img = current_imgs[-1]
                        src = await last_img.get_attribute("src")
                        if src and "http" in src:
                            import httpx
                            async with httpx.AsyncClient(timeout=10.0) as client:
                                r = await client.get(src)
                                if r.status_code == 200 and len(r.content) > 1000:
                                    with open(output_path, "wb") as f:
                                        f.write(r.content)
                                    img_found = True
                                    break
                        else:
                            await last_img.screenshot(path=str(output_path))
                            img_found = True
                            break

                    # Check if Gemini generated pure text response instead of an image
                    if time.time() - start_t > 5.0:
                        stop_btn = await self.page.query_selector('button[aria-label*="Stop"]')
                        if not stop_btn and len(current_imgs) == initial_count:
                            # Gemini has finished responding but produced no new image
                            break

                    await asyncio.sleep(1.0)

                if img_found:
                    self.log(f"Shot {shot_index}/{total_shots} image successfully captured from Gemini Canvas!", "success")
                    return True

            self.log(f"Gemini response timed out for Shot {shot_index}, continuing with enhanced visual compositor.", "warning")
            return False
        except Exception as e:
            self.log(f"Gemini generation error on Shot {shot_index}: {e}", "warning")
            return False

    async def close(self):
        try:
            if self.playwright_obj:
                await self.playwright_obj.stop()
        except Exception:
            pass
        self.page = None
        self.browser_or_context = None
        self.playwright_obj = None
