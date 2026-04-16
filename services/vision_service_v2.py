from __future__ import annotations

import re
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
    score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class VisionServiceV2:
    """Robustere OCR-basierte UI-Erkennung mit Mehrwortsuche und Trefferbewertung."""

    def __init__(self, device_manager: DeviceManager, adb: ADBHandler, screenshot_dir: str = "./screenshots"):
        self.device_manager = device_manager
        self.adb = adb
        self.screenshot_dir = Path(screenshot_dir)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

    def take_screenshot(self, serial: Optional[str] = None, filename: str = "vision_capture.png") -> Path:
        serial = serial or self.device_manager.get_current_device()
        target = self.screenshot_dir / filename
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

    def find_text(self, query: str, image_path: Path, min_confidence: float = -1.0) -> List[OCRMatch]:
        if pytesseract is None or Image is None:
            raise RuntimeError("OCR-Abhängigkeiten fehlen: bitte pytesseract und Pillow installieren.")

        words = self._extract_words(image_path)
        query_norm = self._normalize(query)
        if not query_norm:
            return []

        matches: List[OCRMatch] = []

        # Einwortsuche / direkte Teiltreffer
        for word in words:
            text_norm = self._normalize(word["text"])
            conf = word["confidence"]
            if not text_norm or conf < min_confidence:
                continue
            if query_norm in text_norm:
                score = self._score_match(query_norm, text_norm, conf, exact=(query_norm == text_norm))
                matches.append(OCRMatch(word["text"], word["left"], word["top"], word["width"], word["height"], conf, score))

        # Mehrwortsuche über benachbarte OCR-Wörter
        tokens = [t for t in query_norm.split() if t]
        if len(tokens) > 1:
            for i in range(len(words)):
                combined_text = []
                left = top = width = height = None
                confidences = []
                for j in range(i, min(i + len(tokens) + 3, len(words))):
                    entry = words[j]
                    if entry["confidence"] < min_confidence:
                        continue
                    combined_text.append(entry["text"])
                    confidences.append(entry["confidence"])
                    left = entry["left"] if left is None else min(left, entry["left"])
                    top = entry["top"] if top is None else min(top, entry["top"])
                    right = entry["left"] + entry["width"]
                    bottom = entry["top"] + entry["height"]
                    if width is None:
                        width = right - left
                        height = bottom - top
                    else:
                        width = max((left + width), right) - left
                        height = max((top + height), bottom) - top

                    phrase = self._normalize(" ".join(combined_text))
                    if query_norm == phrase or query_norm in phrase:
                        avg_conf = sum(confidences) / len(confidences)
                        score = self._score_match(query_norm, phrase, avg_conf, exact=(query_norm == phrase)) + 5.0
                        matches.append(OCRMatch(" ".join(combined_text), left or 0, top or 0, width or 0, height or 0, avg_conf, score))

        matches = self._deduplicate(matches)
        matches.sort(key=lambda m: (m.score, m.confidence, -m.top, -m.left), reverse=True)
        logger.debug(f"VisionServiceV2 matches for '{query}': {[m.to_dict() for m in matches]}")
        return matches

    def best_match(self, query: str, image_path: Path, min_confidence: float = -1.0) -> Optional[OCRMatch]:
        matches = self.find_text(query, image_path, min_confidence=min_confidence)
        return matches[0] if matches else None

    def annotate_matches(self, image_path: Path, matches: List[OCRMatch], output_name: str = "vision_annotated.png") -> Path:
        if Image is None or ImageDraw is None:
            raise RuntimeError("Pillow fehlt für Annotationen.")
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        for match in matches:
            draw.rectangle([(match.left, match.top), (match.left + match.width, match.top + match.height)], outline="red", width=3)
        output_path = self.screenshot_dir / output_name
        image.save(output_path)
        logger.info(f"Annotierter Screenshot gespeichert: {output_path}")
        return output_path

    def _extract_words(self, image_path: Path) -> List[Dict[str, Any]]:
        image = Image.open(image_path)
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        words: List[Dict[str, Any]] = []
        for i, word in enumerate(data.get("text", [])):
            text = (word or "").strip()
            if not text:
                continue
            try:
                confidence = float(data["conf"][i])
            except Exception:
                confidence = -1.0
            words.append({
                "text": text,
                "left": int(data["left"][i]),
                "top": int(data["top"][i]),
                "width": int(data["width"][i]),
                "height": int(data["height"][i]),
                "confidence": confidence,
            })
        return words

    def _normalize(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^\w\säöüß-]", "", text)
        return text.strip()

    def _score_match(self, query_norm: str, text_norm: str, confidence: float, exact: bool = False) -> float:
        score = confidence
        if exact:
            score += 20.0
        elif text_norm.startswith(query_norm):
            score += 8.0
        elif query_norm in text_norm:
            score += 4.0
        score -= abs(len(text_norm) - len(query_norm)) * 0.3
        return score

    def _deduplicate(self, matches: List[OCRMatch]) -> List[OCRMatch]:
        seen = set()
        unique: List[OCRMatch] = []
        for match in matches:
            key = (self._normalize(match.text), match.left, match.top, match.width, match.height)
            if key in seen:
                continue
            seen.add(key)
            unique.append(match)
        return unique
