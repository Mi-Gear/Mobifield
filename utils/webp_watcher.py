#!/usr/bin/env python3
"""Automatically create WebP copies of PNG/JPEG images in the Mobifield project.

Install cwebp first:
    sudo apt install webp

Install and start the per-user systemd service:
    python3 utils/webp_watcher.py --install

Original images are kept. Existing WebP files are refreshed when their source
image changes. The watcher scans the project recursively, excluding virtual
environments and VCS/build directories.
"""

from __future__ import annotations

import argparse
import logging
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = Path(__file__).resolve()
SERVICE_NAME = "mobifield-webp-watcher.service"
SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg"}
EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "dist",
    "build",
}
POLL_INTERVAL = 3
STABLE_SCANS = 2


def iter_images():
    for current, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [
            name for name in dirs
            if name not in EXCLUDED_DIRS and not name.startswith(".")
        ]
        for filename in files:
            path = Path(current) / filename
            if path.suffix.lower() in SUPPORTED_EXTENSIONS and not path.is_symlink():
                yield path


def convert_image(source: Path) -> bool:
    converter = shutil.which("cwebp")
    if converter is None:
        logging.error("cwebp не найден. Установи его: sudo apt install webp")
        return False

    destination = source.with_suffix(".webp")
    try:
        source_stat = source.stat()
        if destination.exists() and destination.stat().st_mtime_ns >= source_stat.st_mtime_ns:
            return False
    except OSError:
        return False

    temporary = destination.with_name(destination.name + ".tmp.webp")
    command = [
        converter,
        "-quiet",
        "-q", "90",
        "-m", "6",
        str(source),
        "-o", str(temporary),
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode != 0 or not temporary.is_file():
            logging.warning("Не удалось конвертировать %s: %s", source, result.stderr.strip())
            temporary.unlink(missing_ok=True)
            return False

        # Do not publish a conversion if the source changed while cwebp was running.
        if source.stat().st_mtime_ns != source_stat.st_mtime_ns:
            temporary.unlink(missing_ok=True)
            return False

        os.replace(temporary, destination)
        logging.info("%s -> %s", source.relative_to(PROJECT_ROOT), destination.name)
        return True
    except (OSError, subprocess.SubprocessError) as error:
        temporary.unlink(missing_ok=True)
        logging.warning("Ошибка обработки %s: %s", source, error)
        return False


def watch() -> None:
    if shutil.which("cwebp") is None:
        raise SystemExit("Не найден cwebp. Установи: sudo apt install webp")

    logging.info("Наблюдение за изображениями в %s", PROJECT_ROOT)
    observed: dict[Path, tuple[int, int, int]] = {}

    while True:
        current_paths = set()
        for path in iter_images():
            current_paths.add(path)
            try:
                stat = path.stat()
                signature = (stat.st_size, stat.st_mtime_ns, stat.st_ino)
            except OSError:
                continue

            previous = observed.get(path)
            if previous is None:
                observed[path] = (*signature, 1)
            elif previous[:3] == signature:
                stable_count = previous[3] + 1
                observed[path] = (*signature, stable_count)
                if stable_count >= STABLE_SCANS:
                    convert_image(path)
            else:
                observed[path] = (*signature, 1)

        for stale_path in observed.keys() - current_paths:
            del observed[stale_path]

        time.sleep(POLL_INTERVAL)


def install_service() -> None:
    if shutil.which("cwebp") is None:
        raise SystemExit("Сначала установи конвертер: sudo apt install webp")

    config_dir = Path.home() / ".config" / "systemd" / "user"
    config_dir.mkdir(parents=True, exist_ok=True)
    service_path = config_dir / SERVICE_NAME
    python = sys.executable

    service = f"""[Unit]
Description=Mobifield automatic PNG/JPEG to WebP converter
After=default.target

[Service]
Type=simple
WorkingDirectory={PROJECT_ROOT}
ExecStart={python} {SCRIPT_PATH} --watch
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
"""
    service_path.write_text(service, encoding="utf-8")
    subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
    subprocess.run(
        ["systemctl", "--user", "enable", "--now", SERVICE_NAME],
        check=True,
    )
    print(f"Служба установлена и запущена: {SERVICE_NAME}")
    print("Проверить состояние: systemctl --user status " + SERVICE_NAME)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--watch", action="store_true", help="запустить наблюдатель")
    group.add_argument("--install", action="store_true", help="установить user systemd service")
    group.add_argument("--once", action="store_true", help="однократно обработать все изображения")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    if args.install:
        install_service()
    elif args.once:
        for image in iter_images():
            convert_image(image)
    else:
        watch()


if __name__ == "__main__":
    main()
