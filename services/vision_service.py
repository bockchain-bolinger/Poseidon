from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.adb_handler import ADBHandler
from core.device_manager import DeviceManager
from core.logger import logger

try:
    from PIL import Image, ImageDraw
    import pytesseract
except Exception:  # pragma: no cover
    Image = None
    ImageDraw = None
    pytesseract = None


@dataclass
class OCRMatch:
    text: str
    left: int
    top: int
    width: int
    height: int
    confidence: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class VisionService:
    """Erste OCR-basierte UI-Erkennung für Textsuche auf Screenshots."""

    def __init__(self, device_manager: DeviceManager, adb: ADBHandler, screenshot_dir: str = "./screenshots"):
        self.device_manager = device_manager
        self.adb = adb
        self.screenshot_dir = Path(screenshot_dir)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

    def take_screenshot(self, serial: Optional[str] = None, filename: str = "vision_capture.png") -> Path:
        serial = serial or self.device_manager.get_current_device()
        target = self.screenshot_dir / filename

        out, err, rc = self.adb.run(f"exec-out screencap -p", serial=serial, timeout=20)
        if rc != 0:
            raise RuntimeError(f"Screenshot fehlgeschlagen: {err}")

        # adb_handler arbeitet textbasiert; für binäre Screenshots wird vorerst der Shell-Umweg genutzt.
        tmp_remote = "/sdcard/poseidon_vision_capture.png"
        out, err, rc = self.adb.run_shell(f"screencap -p {tmp_remote}", serial=serial, use_cache=False)
        if rc != 0:
            raise RuntimeError(f"Remote screenshot fehlgeschlagen: {err}")

        out, err, rc = self.adb.run(f"pull {tmp_remote} {str(target)}", serial=serial, timeout=30)
        if rc != 0:
            raise RuntimeError(f"Screenshot pull fehlgeschlagen: {err}")

        self.adb.run_shell(f"rm {tmp_remote}", serial=serial, use_cache=False)
        logger.info(f"Screenshot gespeichert: {target}")
        return target

    def find_text(self, query: str, image_path: Path) -> List[OCRMatch]:
        if pytesseract is None or Image is None:
            raise RuntimeError("OCR-Abhängigkeiten fehlen: bitte pytesseract und Pillow installieren.")

        image = Image.open(image_path)
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        matches: List[OCRMatch] = []

        for i, word in enumerate(data.get("text", [])):
            if not word:
                continue
            if query.lower() in word.lower():
                try:
                    confidence = float(data["conf"][i])
                except Exception:
                    confidence = -1.0
                matches.append(
                    OCRMatch(
                        text=word,
                        left=int(data["left"][i]),
                        top=int(data["top"][i]),
                        width=int(data["width"][i]),
                        height=int(data["height"][i]),
                        confidence=confidence,
                    )
                )
        logger.debug(f"OCR-Matches für '{query}': {[m.to_dict() for m in matches]}")
        return matches

    def annotate_matches(self, image_path: Path, matches: List[OCRMatch], output_name: str = "vision_annotated.png") -> Path:
        if Image is None or ImageDraw is None:
            raise RuntimeError("Pillow fehlt für Annotationen.")

        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        for match in matches:
            draw.rectangle(
                [
                    (match.left, match.top),
                    (match.left + match.width, match.top + match.height),
                ],
                outline="red",
                width=3,
            )

        output_path = self.screenshot_dir / output_name
        image.save(output_path)
        logger.info(f"Annotierter Screenshot gespeichert: {output_path}")
        return output_path
