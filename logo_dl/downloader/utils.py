import hashlib
import json
import logging
import random
from asyncio import sleep as aio_sleep
from io import BytesIO
from pathlib import Path
from time import sleep
from typing import Optional, Union

import requests
from aiofiles import open as aio_open
from aiohttp import ClientSession
from aiohttp.web import HTTPError
from pydantic_core import to_jsonable_python

from .models import ManufacturerLogo

log = logging.getLogger("logo_dl")


def check_for_duplicate_list_items(items: list, key: str) -> Optional[set]:
    """Ensure that all items in the list have unique values for the specified key."""
    unique_values = set(getattr(item, key) for item in items)
    if len(items) != len(unique_values):
        seen = set()
        duplicates = set()
        for item in items:
            value = getattr(item, key)
            if value in seen:
                duplicates.add(value)
            else:
                seen.add(value)
        return duplicates
    return None


def hash_file(path: Path, buffer_size: int = 65536) -> str:
    """Return the MD5 hash of a file."""
    if not path.is_file():
        raise ValueError(f"Path {path} does not exist.")

    with open(path, "rb") as f:
        digest = hashlib.file_digest(f, "md5", _bufsize=buffer_size)
    return digest.hexdigest()


def hash_bytes(content: bytes, buffer_size: int = 65536) -> str:
    """Return the MD5 hash of the content as bytes."""
    md5 = hashlib.md5()
    content_stream = BytesIO(content)

    while chunk := content_stream.read(buffer_size):
        md5.update(chunk)

    return md5.hexdigest()


def merge_lists_sorted(a: list, b: list) -> list:
    """Merge all items in list a with items in list b."""
    for logo in a:
        if logo not in b:
            b.append(logo)

    return sorted(b, key=lambda x: x.name)


def read_logo_data(file_path: Path) -> list[ManufacturerLogo]:
    """Read the logo data from a JSON file."""
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, "r") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Unexpected data type for logo data")

    return [ManufacturerLogo(**logo) for logo in data]


async def read_url_async(
    session: ClientSession, url: str, retries: int = 3, backoff_factor: int = 1
) -> bytes:
    """Return URL content as bytes with retries and exponential backoff."""
    for attempt in range(retries):
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.read()
        except Exception as e:
            if attempt < retries - 1:
                # Exponential backoff with randomised jitter to avoid synchronised retries
                wait = backoff_factor * (2**attempt) + random.uniform(0, 1)
                log.warning(
                    f"Error reading {url}: {e}. Retrying in {wait:.2f} seconds..."
                )
                await aio_sleep(wait)
            else:
                log.error(f"Error reading {url}: {e}. No more retries left.")
    raise HTTPError(text=f"Failed to read {url} after {retries} attempts.")


def read_url(url: str, retries: int = 3, backoff_factor: int = 1) -> bytes:
    """Return URL content as bytes with retries and exponential backoff."""
    for attempt in range(retries):
        try:
            response = requests.get(url, headers={"User-Agent": "XY"})
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            if attempt < retries - 1:
                wait = backoff_factor * (2**attempt) + random.uniform(
                    0, 1
                )  # Exponential backoff with jitter
                log.warning(
                    f"Error reading {url}: {e}. Retrying in {wait:.2f} seconds..."
                )
                sleep(wait)
            else:
                log.error(f"Error reading {url}: {e}. No more retries left.")
    raise requests.exceptions.HTTPError(
        f"Failed to read {url} after {retries} attempts."
    )


async def save_file(target_path: Path, content: Union[bytes, str]) -> None:
    """Download the logo image to a local file."""
    try:
        if isinstance(content, str):
            content = content.encode()
        async with aio_open(target_path, "wb") as f:
            await f.write(content)
    except Exception as e:
        log.error(f"Error saving content to {target_path}: {e}")
        raise e


async def write_logo_data(
    file_path: Path,
    logo_data: list[ManufacturerLogo],
    existing_logo_data: Optional[list[ManufacturerLogo]],
) -> None:
    """Write the logo data to a JSON file."""
    if existing_logo_data:
        # Ensure any pre-existing logos that were not found in the scrape are not removed from the JSON file.
        logo_data = merge_lists_sorted(existing_logo_data, logo_data)

        if logo_data == existing_logo_data or len(logo_data) == 0:
            log.debug(f"Logo data is unchanged. Skipping update of {file_path}.")
            return None

    await save_file(file_path, json.dumps(logo_data, default=to_jsonable_python))
    log.info(f"Logo data saved to {file_path}.")
