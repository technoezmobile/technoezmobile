"""Point the profile calendar images at the most recent generated run."""
import os
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
readme = root / "README.md"
run_id = os.environ.get("GITHUB_RUN_ID")
if not run_id:
    raise SystemExit("GITHUB_RUN_ID is required to refresh the image cache key")

text = readme.read_text(encoding="utf-8")
for asset in ("contributions-motion.gif", "contributions-motion-poster.png"):
    pattern = rf"https://raw\.githubusercontent\.com/technoezmobile/technoezmobile/[^/]+/assets/{re.escape(asset)}(?:\?v=[^\" ]+)?"
    replacement = f"https://raw.githubusercontent.com/technoezmobile/technoezmobile/main/assets/{asset}?v={run_id}"
    text, count = re.subn(pattern, replacement, text)
    if count != 1:
        raise SystemExit(f"Expected one README reference for {asset}; found {count}")

readme.write_text(text, encoding="utf-8")

