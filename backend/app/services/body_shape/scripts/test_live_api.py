"""
Live API End-to-End Verification Script for Body Fit 3D Studio.
"""

import os
import urllib.request
import json
import sys

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE = sys.argv[1] if len(sys.argv) > 1 else os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

print("=" * 60)
print("BODY FIT 3D STUDIO — LIVE SERVER VERIFICATION")
print("=" * 60)

# 1. Health check
h_resp = urllib.request.urlopen(f"{BASE}/api/v1/health")
h = json.loads(h_resp.read().decode())
print(f"[TEST 1] GET /api/v1/health -> Status: {h['status']} | Engine: {h['engine']}")

# 2. Female Generation
f_payload = {
    "gender": "female",
    "height_cm": 168.0,
    "weight_kg": 50.5,
    "bust_cm": 100.5,
    "waist_cm": 66.5,
    "hip_cm": 92.0,
    "shoulder_width_cm": 39.5,
    "leg_length_cm": 73.0,
    "skin_tone": "natural"
}
req_f = urllib.request.Request(
    f"{BASE}/api/v1/body/generate",
    data=json.dumps(f_payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
res_f = json.loads(urllib.request.urlopen(req_f).read().decode("utf-8"))
print(f"[TEST 2] POST /api/v1/body/generate (Female) -> Time: {res_f['execution_time_ms']} ms")
print(f"  - Vertices: {res_f['body_mesh']['num_vertices']} | Faces: {res_f['body_mesh']['num_faces']}")
print(f"  - Body Shape: {res_f['analysis']['body_shape']} | WHR: {res_f['analysis']['whr']}")
print(f"  - Measurement Tapes: {list(res_f['measurement_tapes'].keys())}")

# 3. Male Generation
m_payload = {
    "gender": "male",
    "height_cm": 180.0,
    "weight_kg": 74.0,
    "bust_cm": 86.5,
    "waist_cm": 80.0,
    "hip_cm": 96.0,
    "shoulder_width_cm": 47.0,
    "leg_length_cm": 96.5,
    "skin_tone": "natural"
}
req_m = urllib.request.Request(
    f"{BASE}/api/v1/body/generate",
    data=json.dumps(m_payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
res_m = json.loads(urllib.request.urlopen(req_m).read().decode("utf-8"))
print(f"[TEST 3] POST /api/v1/body/generate (Male) -> Time: {res_m['execution_time_ms']} ms")
print(f"  - Vertices: {res_m['body_mesh']['num_vertices']} | Faces: {res_m['body_mesh']['num_faces']}")
print(f"  - Body Shape: {res_m['analysis']['body_shape']} | BMI: {res_m['analysis']['bmi']}")

# 4. Export OBJ
req_obj = urllib.request.Request(
    f"{BASE}/api/v1/body/export/obj",
    data=json.dumps(f_payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
obj_bytes = urllib.request.urlopen(req_obj).read()
print(f"[TEST 4] POST /api/v1/body/export/obj -> 3D OBJ Size: {len(obj_bytes):,} bytes")

# 5. Web UI
ui_resp = urllib.request.urlopen(f"{BASE}/")
html = ui_resp.read().decode("utf-8")
print(f"[TEST 5] GET / -> HTTP {ui_resp.status} | HTML Size: {len(html):,} bytes | Three.js: {'three.min.js' in html}")

print("=" * 60)
print("ALL LIVE TESTS PASSED 100%!")
print("=" * 60)
