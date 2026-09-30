"""
Image loading utilities supporting base64, HTTP URLs, relative web paths, and mock fixtures.
"""

import base64
import os
from pathlib import Path
from typing import Optional
import httpx

# Paths to fixtures and frontend public directory
PROJECT_ROOT = Path(__file__).resolve().parents[3]
FRONTEND_PUBLIC = PROJECT_ROOT / "frontend" / "public"
FIXTURES_DIR = PROJECT_ROOT / "vision-service" / "benchmark" / "datasets" / "images" / "valid"


def load_image_bytes(
    raw_bytes: Optional[bytes] = None,
    image_base64: Optional[str] = None,
    image_url: Optional[str] = None,
    fallback_fixture: Optional[str] = None,
) -> Optional[bytes]:
    """Resolves image bytes from direct bytes, base64, data URI, URL, or mock path."""
    if raw_bytes is not None and len(raw_bytes) > 0:
        return raw_bytes

    # 1. Base64 string directly
    if image_base64:
        try:
            b64 = image_base64
            if "," in b64:
                b64 = b64.split(",", 1)[1]
            decoded = base64.b64decode(b64)
            if len(decoded) > 0:
                return decoded
        except Exception:
            pass

    # 2. Image URL handling
    if image_url:
        # 2a. Data URL (e.g. data:image/jpeg;base64,...)
        if image_url.startswith("data:"):
            try:
                b64 = image_url
                if "," in b64:
                    b64 = b64.split(",", 1)[1]
                decoded = base64.b64decode(b64)
                if len(decoded) > 0:
                    return decoded
            except Exception:
                pass

        # 2b. Check if it's a web/relative mock path
        clean_url = image_url.split("?")[0]
        if clean_url.startswith("/"):
            local_path = FRONTEND_PUBLIC / clean_url.lstrip("/")
            if local_path.is_file():
                return local_path.read_bytes()

        # 2c. Check if local absolute/relative file path
        try:
            p = Path(image_url)
            if p.is_file():
                return p.read_bytes()
        except Exception:
            pass

        # 2d. Check if HTTP(S) URL (external web URL)
        if image_url.startswith(("http://", "https://")):
            try:
                with httpx.Client(timeout=6.0) as client:
                    resp = client.get(image_url)
                    if resp.status_code == 200:
                        return resp.content
            except Exception:
                pass

        # 2e. Explicit mock/fixture fallback (only when explicitly requested with "mock" or "fixture")
        if "mock" in image_url.lower() or "fixture" in image_url.lower():
            if "side" in image_url.lower():
                side_fixture = FIXTURES_DIR / "sub_01_side.jpg"
                if side_fixture.is_file():
                    return side_fixture.read_bytes()
            elif fallback_fixture:
                front_fixture = FIXTURES_DIR / fallback_fixture
                if front_fixture.is_file():
                    return front_fixture.read_bytes()

    # 3. Fallback fixture if explicitly requested
    if fallback_fixture and not image_url and not image_base64 and not raw_bytes:
        fixture_path = FIXTURES_DIR / fallback_fixture
        if fixture_path.is_file():
            return fixture_path.read_bytes()

    return None
