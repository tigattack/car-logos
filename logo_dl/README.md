# logo-downloader

Python script to asynchronously download logos for all vehicle manufacturers from [carlogos.org](https://www.carlogos.org).

The script searches for logo thumbnails since they were found to be reliably transparent and of consistent aspect ratio, allowing for predictability when used in other applications.

Once all images are downloaded, the script writes `logos.json` with a structure like:

```json
[
  {
    "name": "Land Rover",
    "slug": "land-rover",
    "image": {
      "source": "https://www.carlogos.org/car-logos/land-rover-logo.png",
      "path": "/images/land-rover.png"
    }
  },
  {
    "name": "Volkswagen",
    "slug": "volkswagen",
    "image": {
      "source": "https://www.carlogos.org/car-logos/volkswagen-logo.png",
      "path": "/images/volkswagen.png"
    }
  }
]
```

## Usage

```
❯ python3 downloader.py --help
Usage: downloader.py [OPTIONS]

  Download logos for all manufacturers.

Options:
  --target_dir PATH  Target directory for the download.
  --debug            Enable debug logging.
  --help             Show this message and exit.
```

### Example

```
❯ python3 downloader.py --target_dir ../ui/logos
[2024-09-12 18:57:56,201 - root - INFO] Discovering manufacturers...
[2024-09-12 18:57:56,884 - root - INFO] Creating target directory '../ui/logos'...
[2024-09-12 18:57:56,884 - root - INFO] Downloading manufacturer logos...
[2024-09-12 18:58:00,399 - root - INFO] Downloaded 383 logos to ../ui/logos/images.
[2024-09-12 18:58:00,401 - root - INFO] Logo data saved to ../ui/logos/logos.json.
```

## TODO

* if local files exist that aren't in the logo data file, remove them? or attempt to backfill logo data based on retrieved metadata?
* consider handling of non [A-Za-z0-9] - e.g. `Škoda`
