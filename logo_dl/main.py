import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

import aiohttp
import requests
from aiofiles import open as aio_open
from bs4 import BeautifulSoup, Tag
from pydantic import BaseModel
from pydantic_core import to_jsonable_python
from slugify import slugify

BASE_URL = "https://www.carlogos.org"

log = logging.getLogger()


class LogoImage(BaseModel):
    source: str
    url: str


class ManufacturerLogo(BaseModel):
    name: str
    slug: str
    image: LogoImage


class VehicleManufacturerLogos:
    def __init__(
        self, target_dir: str, logos_subdir: str = "images", base_url: str = BASE_URL
    ) -> None:
        self.base_url = base_url
        self.target_dir = Path(target_dir)
        self.logos_subdir = Path.joinpath(self.target_dir, logos_subdir)
        self.logo_data_file = Path.joinpath(self.target_dir, "logos.json")

    async def download_logos(self) -> None:
        """Download logos for all manufacturers asynchronously and return the list of logos."""
        log.info("Starting the manufacturer logo download process.")

        manufacturers = self._get_manufacturers()

        if not self.target_dir.exists():
            log.info(f"Creating target directory in {self.target_dir}.")
            self.target_dir.mkdir(parents=True, exist_ok=True)

        async with aiohttp.ClientSession() as session:
            tasks = [
                self._fetch_logo(session, manufacturer)
                for manufacturer in manufacturers
            ]
            results = await asyncio.gather(*tasks)

        # Filter out None values and return the list of logos
        logos = [logo for logo in results if logo]

        if len(logos) == 0:
            log.error("No logos returned.")

        log.info(
            f"Manufacturer logo download complete. Downloaded {len(logos)} logos to {self.logos_subdir}."
        )

        async with aio_open(self.logo_data_file, "w") as f:
            await f.write(json.dumps(logos, default=to_jsonable_python))

        log.info(f"Logo data saved to {self.logo_data_file}.")

    def _fix_url(self, url: str) -> str:
        """Ensure the logo URL is absolute."""
        return url if url.startswith("http") else urljoin(self.base_url, url)

    def _get_manufacturers(self) -> list:
        """Scrape the list of manufacturers from the A-Z page."""
        manufacturers_css_selector = "html body div.main div.main-l div.a-z dl dd a"
        url = f"{self.base_url}/car-brands-a-z"

        log.debug(f"Fetching manufacturer list from {url}")

        response = requests.get(url, headers={"User-Agent": "XY"})
        soup = BeautifulSoup(response.content, "html.parser")

        manufacturers = []

        page_manufacturers = soup.select(manufacturers_css_selector)

        if not page_manufacturers:
            log.error("No manufacturers found on the page.")
            raise ValueError("No manufacturers found on the page.")

        for manufacturer_link in page_manufacturers:
            if isinstance(manufacturer_link, Tag):
                name = manufacturer_link.get_text()
                href = manufacturer_link.get("href")
                if name and href:
                    manufacturers.append({"name": name, "url": href})
                elif not name:
                    log.warning(f"Missing name for manufacturer: {href}")
                else:
                    log.warning(f"Missing href for manufacturer: {name}")

        log.debug(f"Found {len(manufacturers)} manufacturers.")

        manufacturers = sorted(manufacturers, key=lambda x: x["name"])

        return manufacturers

    @staticmethod
    async def _download_logo(
        session: aiohttp.ClientSession, url: str, target_path: Path
    ) -> None:
        """Download the logo image to a local file."""
        try:
            log.debug(f"Downloading {url}")
            async with session.get(url) as response:
                content = await response.read()
                target_path.parent.mkdir(exist_ok=True)
                async with aio_open(target_path, "wb") as f:
                    await f.write(content)
        except Exception as e:
            log.error(f"Error downloading {url}: {e}")
            raise e

    async def _fetch_logo(
        self, session: aiohttp.ClientSession, manufacturer: dict
    ) -> Optional[ManufacturerLogo]:
        """Fetch the logo for a specific manufacturer."""
        name = manufacturer["name"]
        url = manufacturer["url"]
        log.debug(f"Processing logo for {name}")

        try:
            # Fetch manufacturer's page
            response = await session.get(self._fix_url(url))
            page_content = await response.text()
            soup = BeautifulSoup(page_content, "html.parser")

            # Find logo URL in meta tag
            logo_tag = soup.find("meta", property="og:image")
            logo_url = None

            if isinstance(logo_tag, Tag):
                logo_url = logo_tag.get("content")

            if isinstance(logo_url, list):
                raise ValueError("Unexpected list returned from logo meta tag")

            if not logo_url:
                log.warning(f"Logo for {name} not found.")
                return None

            logo_url = self._fix_url(logo_url)
            extension = logo_url.split(".")[-1]
            slug = slugify(name).lower()
            file_name = f"{slug}.{extension}"
            target_location = self.logos_subdir.joinpath(file_name)

            # Ensure target directory exists
            target_location.parent.mkdir(parents=True, exist_ok=True)

            # TODO: check if image is different instead of blindly skipping when a matching file exists
            if target_location.exists():
                log.debug(f"Skipping {name} because {target_location} already exists.")
                return None

            # Download logo file
            await self._download_logo(session, logo_url, target_location)

            log.debug(f"Downloaded logo for {name} to {target_location}")

            return ManufacturerLogo(
                name=name,
                slug=slug,
                image=LogoImage(source=logo_url, url=str(target_location)),
            )

        except Exception as e:
            log.error(f"Failed to fetch logo for {name}: {e}")
            raise e


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <target_dir>")
        exit(1)

    target_dir = sys.argv[1]

    logos = VehicleManufacturerLogos(target_dir)
    asyncio.run(logos.download_logos())
