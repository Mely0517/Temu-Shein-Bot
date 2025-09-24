# boost.py
import asyncio
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

# Reusable headless browser (Render-friendly)
def _get_browser():
    options = uc.ChromeOptions()
    # Use the Render Chrome path; if your deploy fails, switch to the commented variant below.
    options.binary_location = "/opt/render/project/.render/chrome/opt/google/chrome"
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("user-agent=Mozilla/5.0")

    # If Chrome still can’t be found on your Render instance, try:
    # return uc.Chrome(
    #     driver_executable_path="/opt/render/project/.render/chromedriver/bin/chromedriver",
    #     options=options
    # )
    return uc.Chrome(options=options)

def _click_any_button(browser, words):
    buttons = browser.find_elements(By.TAG_NAME, "button")
    for btn in buttons:
        txt = (btn.text or "").lower()
        if any(w in txt for w in words):
            try:
                btn.click()
                return f"Clicked '{btn.text}'"
            except Exception:
                pass
    return None

def _boost_shein_sync(link: str) -> str:
    b = _get_browser()
    try:
        b.get(link)
        # Small delay to let page paint; Selenium’s waits could be added later.
        # Using implicit wait is also an option.
        b.implicitly_wait(5)
        # Try common action words
        msg = _click_any_button(b, ["accept", "claim", "open", "join", "help", "receive", "get"])
        return msg or "No clickable SHEIN buttons found"
    finally:
        try:
            b.quit()
        except Exception:
            pass

def _boost_temu_sync(link: str) -> str:
    b = _get_browser()
    try:
        b.get(link)
        b.implicitly_wait(5)
        msg = _click_any_button(b, ["accept", "join", "open", "claim", "start", "spin", "water", "harvest", "grow"])
        return msg or "No clickable TEMU buttons found"
    finally:
        try:
            b.quit()
        except Exception:
            pass

# Public async wrappers so we don’t block the Discord event loop
async def boost_shein_link(link: str) -> str:
    return await asyncio.to_thread(_boost_shein_sync, link)

async def boost_temu_link(link: str) -> str:
    return await asyncio.to_thread(_boost_temu_sync, link)
