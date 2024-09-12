import asyncio
import logging
import click
from downloader import VehicleManufacturerLogos

@click.command()
@click.option("--target_dir", type=click.Path(), default="logos", help="Target directory for the download.", required=False)
@click.option("--debug", is_flag=True, type=bool, help="Enable debug logging.")
def main(target_dir, debug) -> None:
    """Download logos for all manufacturers."""
    log = logging.getLogger("logo_dl")
    log.setLevel(logging.DEBUG if debug else logging.INFO)
    logos = VehicleManufacturerLogos(target_dir)
    asyncio.run(logos.download_logos())


if __name__ == "__main__":
    main()
