# temu_booster.py
import asyncio
from typing import Dict
from seleniumwire import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from proxy_utils import get_random_proxy

def _build_driver() -> webdriver.Chrome:
    p: Dict = get_random_proxy()  # {ip, port, username?, password?, scheme}
    proxy_url = f"{p['scheme']}://{p['ip']}:{p['port']}"

    sw_options = {"proxy": {"http": proxy_url, "https": proxy_url}}
    if p.get("username") and p.get("password"):
        sw_options["proxy"]["auth"] = (p["username"], p["password"])

    chrome_options = uc.ChromeOptions()
    chrome_options.binary_location = "/opt/render/project/.render/chrome/opt/google/chrome"
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("user-agent=Mozilla/5.0")

    # If Chrome path fails on your instance, switch to the executable_path variant:
    # driver = webdriver.Chrome(
    #     executable_path="/opt/render/project/.render/chromedriver/bin/chromedriver",
    #     options=chrome_options,
    #     seleniumwire_options=sw_options
    # )
    driver = webdriver.Chrome(options=chrome_options, seleniumwire_options=sw_options)
    driver.implicitly_wait(6)
    return driver

def _click_any_button(driver, words):
    buttons = driver.find_elements(By.TAG_NAME, "button")
    for b in buttons:
        t = (b.text or "").lower()
        if any(w in t for w in words):
            try:
                b.click()
                return f"Clicked '{b.text}'"
            except Exception:
                pass
    return None

def _boost_temu_sync(link: str) -> str:
    d = _build_driver()
    try:
        d.get(link)
        # Try common actions across Temu invite + games
        msg = _click_any_button(d, [
            "accept", "join", "open", "claim",
            "start", "spin", "tap",           # spin/stack/tap
            "water", "harvest", "grow"       # farmland
        ])
        return msg or "No clickable TEMU buttons found"
    finally:
        try:
            d.quit()
        except Exception:
            pass

async def boost_temu_link(link: str) -> str:
    # Run the blocking Selenium work off the event loop
    return await asyncio.to_thread(_boost_temu_sync, link)
