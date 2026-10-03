import time
import os
from playwright.sync_api import sync_playwright

artifacts_dir = 'C:/Users/dvnlinh/.gemini/antigravity-ide/brain/8ac5cd63-aeab-47ae-b263-98727fb3d164'

def capture_studio():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='msedge', headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 880})
        print("Navigating to http://127.0.0.1:8000/ ...")
        page.goto('http://127.0.0.1:8000/')
        time.sleep(3)
        
        # 1. Female Front View
        p1 = os.path.join(artifacts_dir, 'pw_female_front.png')
        page.screenshot(path=p1)
        print(f"1. Saved {p1}")
        
        # 2. Female Side View
        page.click('#cam-side')
        time.sleep(1)
        p2 = os.path.join(artifacts_dir, 'pw_female_side.png')
        page.screenshot(path=p2)
        print(f"2. Saved {p2}")
        
        # 3. Female 3/4 View
        page.click('#cam-threeq')
        time.sleep(1)
        p3 = os.path.join(artifacts_dir, 'pw_female_threeq.png')
        page.screenshot(path=p3)
        print(f"3. Saved {p3}")
        
        # 4. Male Front View
        page.click('#gender-male')
        time.sleep(3)
        page.click('#cam-front')
        time.sleep(1)
        p4 = os.path.join(artifacts_dir, 'pw_male_front.png')
        page.screenshot(path=p4)
        print(f"4. Saved {p4}")
        
        # 5. Male Side View
        page.click('#cam-side')
        time.sleep(1)
        p5 = os.path.join(artifacts_dir, 'pw_male_side.png')
        page.screenshot(path=p5)
        print(f"5. Saved {p5}")
        
        # 6. Male 3/4 View
        page.click('#cam-threeq')
        time.sleep(1)
        p6 = os.path.join(artifacts_dir, 'pw_male_threeq.png')
        page.screenshot(path=p6)
        print(f"6. Saved {p6}")
        
        # 7. Slider deformation test (Athletic preset or sliders)
        page.click('#preset-athletic')
        time.sleep(3)
        page.click('#cam-front')
        time.sleep(1)
        p7 = os.path.join(artifacts_dir, 'pw_male_athletic.png')
        page.screenshot(path=p7)
        print(f"7. Saved {p7}")
        
        browser.close()
        print("All screenshots captured successfully!")

if __name__ == '__main__':
    capture_studio()
