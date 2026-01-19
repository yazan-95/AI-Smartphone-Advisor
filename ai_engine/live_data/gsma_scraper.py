"""
ai_engine.live_data.gsma_scraper

Fetches phone specs and downloads main phone image from GSMArena.
Returns LOCAL filesystem paths only.
"""

import time
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from django.conf import settings


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Research Project)"
}

GSMA_SEARCH = "https://www.gsmarena.com/results.php3?sQuickSearch=yes&sName={}"


def fetch_phone_specs(model_name: str) -> dict:
    url = GSMA_SEARCH.format(model_name.replace(" ", "+"))
    res = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")

    first = soup.select_one(".makers li a")
    if not first:
        return {}

    phone_url = "https://www.gsmarena.com/" + first["href"]
    page = requests.get(phone_url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(page.text, "html.parser")

    specs = {}
    for row in soup.select("table tr"):
        th = row.find("th")
        td = row.find("td")
        if th and td:
            specs[th.text.strip()] = td.text.strip()

    return specs


def fetch_phone_image(model_name: str) -> str | None:
    """
    Downloads the main phone image from GSMArena.
    Returns LOCAL filesystem path or None.
    """

    model_safe = model_name.lower().replace(" ", "_")

    images_dir = Path(settings.MEDIA_ROOT) / "phone_images"
    images_dir.mkdir(parents=True, exist_ok=True)

    image_path = images_dir / f"{model_safe}.jpg"

    # ✅ CACHE HIT — do not re-download
    if image_path.exists():
        return str(image_path)

    time.sleep(2)  # polite scraping

    search_url = GSMA_SEARCH.format(model_name.replace(" ", "+"))
    res = requests.get(search_url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")

    phone_link = soup.select_one(".makers a")
    if not phone_link:
        return None

    phone_page = "https://www.gsmarena.com/" + phone_link["href"]
    phone_res = requests.get(phone_page, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(phone_res.text, "html.parser")

    img = soup.select_one(".specs-photo-main img")
    if not img or not img.get("src"):
        return None

    img_url = img["src"]
    if img_url.startswith("//"):
        img_url = "https:" + img_url

    # Download image
    img_data = requests.get(img_url, headers=HEADERS, timeout=15).content
    image_path.write_bytes(img_data)

    return str(image_path)
