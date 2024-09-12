import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

import aiohttp
from bs4 import BeautifulSoup, Tag
from slugify import slugify

from .models import LogoImage, Manufacturer, ManufacturerLogo
from .utils import (
    check_for_duplicate_list_items,
    hash_bytes,
    hash_file,
    read_logo_data,
    read_url,
    read_url_async,
    save_file,
    write_logo_data,
)

BASE_URL = "https://www.carlogos.org"

log = logging.getLogger()
formatter = logging.Formatter("[%(asctime)s - %(name)s - %(levelname)s] %(message)s")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
log.addHandler(handler)


class VehicleManufacturerLogos:
    def __init__(
        self, target_dir: str, logos_subdir: str = "images", base_url: str = BASE_URL
    ) -> None:
        self.base_url = base_url
        self.target_dir = Path(target_dir)
        self.logos_dir = Path.joinpath(self.target_dir, logos_subdir)
        self.logo_data_file = Path.joinpath(self.target_dir, "logos.json")

    async def download_logos(self) -> None:
        """Download logos for all manufacturers asynchronously and return the list of logos."""
        log.info("Discovering manufacturers...")
        manufacturers = self._get_manufacturers()

        duplicate_manufacturers = check_for_duplicate_list_items(manufacturers, "name")
        if duplicate_manufacturers:
            log.error(
                f"Duplicate manufacturers found: {sorted(duplicate_manufacturers)}"
            )
            raise ValueError("Manufacturer names must be unique.")

        if not self.target_dir.exists():
            log.info(f"Creating target directory '{self.target_dir}'...")
            self.target_dir.mkdir(parents=True, exist_ok=True)

        existing_logo_data = None
        local_logos_exist = False
        existing_logos_count = 0

        if self.logo_data_file.exists():
            log.debug("Existing logo data file found.")
            existing_logo_data = read_logo_data(self.logo_data_file)
            existing_logos_count = len(existing_logo_data)
            local_logos_exist = existing_logos_count > 0
            log.debug(
                f"Found {existing_logos_count} existing logos in the logo data file."
            )

        discovered_manufacturers_count = len(manufacturers)
        log.debug(f"Discovered {discovered_manufacturers_count} manufacturers.")

        log.info("Downloading manufacturer logos...")
        async with aiohttp.ClientSession() as session:
            tasks = [
                self._fetch_logo(session, manufacturer)
                for manufacturer in manufacturers
            ]
            results = await asyncio.gather(*tasks)

        downloaded_logos = [logo for logo in results if logo]
        downloaded_logos_count = len(downloaded_logos)

        # Scenario 1: Local logos exist and downloaded logos are less than the difference
        if local_logos_exist:
            required_new_logos_count = (
                discovered_manufacturers_count - existing_logos_count
            )
            if downloaded_logos_count < required_new_logos_count:
                log.warning(
                    f"Downloaded only {downloaded_logos_count} logos out of a desired {required_new_logos_count} new logos ({existing_logos_count} already exist)."
                )

                # Log the list of manufacturers whose logos were not downloaded and were not found in the logo data file
                downloaded_manufacturer_names = {logo.name for logo in downloaded_logos}
                desired_manufacturer_names = {
                    manufacturer.name for manufacturer in manufacturers
                }
                existing_manufacturer_names = {logo.name for logo in existing_logo_data}  # type: ignore
                missing_manufacturers = (
                    desired_manufacturer_names
                    - downloaded_manufacturer_names
                    - existing_manufacturer_names
                )

                log.warning(
                    f"Logos could not be downloaded for the following manufacturers: {sorted(missing_manufacturers)}"
                )

        # Scenario 2: No local logos exist and downloaded logos are less than discovered manufacturers
        elif downloaded_logos_count < discovered_manufacturers_count:
            missing_logos = [
                manufacturer.name
                for manufacturer, result in zip(manufacturers, results)
                if not result
            ]
            log.warning(
                f"Downloaded only {downloaded_logos_count} logos out of {discovered_manufacturers_count} discovered manufacturers: {sorted(missing_logos)}"
            )

        elif downloaded_logos_count == 0:
            log.error("No logos were downloaded.")

        else:
            log.info(f"Downloaded {downloaded_logos_count} logos to {self.logos_dir}.")

        # TODO: if local files exist that aren't in the logo data file, remove them? or attempt to backfill logo data based on retrieved metadata?

        # Merge and save the logo data
        await write_logo_data(self.logo_data_file, downloaded_logos, existing_logo_data)

    def _fix_url(self, url: str) -> str:
        """Ensure URLs are absolute."""
        return url if url.startswith("http") else urljoin(self.base_url, url)

    def _get_manufacturers(self) -> list[Manufacturer]:
        """Scrape the list of manufacturers from the A-Z page."""
        manufacturers_css_selector = "html body div.main div.main-l div.a-z dl dd a"
        url = f"{self.base_url}/car-brands-a-z"

        log.debug(f"Fetching manufacturer list from {url}")

        page_content = read_url(url)
        soup = BeautifulSoup(page_content, "html.parser")

        manufacturers: list[Manufacturer] = []

        page_manufacturers = soup.select(manufacturers_css_selector)

        if not page_manufacturers:
            log.error("No manufacturers found on the page.")
            raise ValueError("No manufacturers found on the page.")

        for manufacturer_link in page_manufacturers:
            if isinstance(manufacturer_link, Tag):
                name = manufacturer_link.get_text()
                href = manufacturer_link.get("href")

                if isinstance(href, list):
                    raise ValueError("Unexpected list returned from logo meta tag")

                if name and href:
                    manufacturers.append(Manufacturer(name=name, url=href))
                elif not name:
                    log.warning(f"Missing name for manufacturer: {href}")
                else:
                    log.warning(f"Missing href for manufacturer: {name}")

        log.debug(f"Found {len(manufacturers)} manufacturers.")

        manufacturers = sorted(manufacturers, key=lambda x: x.name)

        return manufacturers

    async def _fetch_logo(
        self, session: aiohttp.ClientSession, manufacturer: Manufacturer
    ) -> Optional[ManufacturerLogo]:
        """Fetch the logo for a specific manufacturer."""
        name = manufacturer.name
        url = manufacturer.url

        log.debug(f"Processing logo for {name}")

        try:
            # Fetch manufacturer's page
            page_content = await read_url_async(session, self._fix_url(url))

            # Find logo URL in meta tag
            soup = BeautifulSoup(page_content, "html.parser")
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
            target_location = self.logos_dir.joinpath(file_name)

            # Fetch logo content as bytes
            logo = await read_url_async(session, logo_url)

            if target_location.exists():
                files_match = hash_file(target_location) == hash_bytes(logo)
                if files_match:
                    log.debug(
                        f"{target_location.name} exists and hashes match. Skipping download."
                    )
                    return None

            else:
                # Ensure target directory exists
                target_location.parent.mkdir(parents=True, exist_ok=True)

                # Save logo file
                await save_file(target_location, logo)

                log.debug(f"Downloaded logo for {name} to {target_location}")

                return ManufacturerLogo(
                    name=name,
                    slug=slug,
                    image=LogoImage(source=logo_url, path=str(target_location)),
                )

            return None

        except Exception as e:
            log.error(f"Failed to fetch logo for {name}: {e}")
            raise e
