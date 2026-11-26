from pathlib import Path
import cv2
import numpy as np


class QRCodeDetectorService:
    """Detects and decodes QR codes from image files or bytes using OpenCV."""

    def __init__(self):
        self.detector = cv2.QRCodeDetector()

    def decode_from_bytes(self, img_bytes: bytes) -> tuple[bool, str | None]:
        try:
            nparr = np.frombuffer(img_bytes, np.uint8)
            cv_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if cv_img is None:
                return False, None

            val, points, _ = self.detector.detectAndDecode(cv_img)
            if val and val.strip():
                return True, val.strip()

            # Retry with grayscale and thresholding if direct decode fails
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
            val, points, _ = self.detector.detectAndDecode(gray)
            if val and val.strip():
                return True, val.strip()

            return False, None
        except Exception:
            return False, None

    def decode_from_file(self, img_path: str | Path) -> tuple[bool, str | None]:
        try:
            cv_img = cv2.imread(str(img_path))
            if cv_img is None:
                return False, None
            val, points, _ = self.detector.detectAndDecode(cv_img)
            if val and val.strip():
                return True, val.strip()
            return False, None
        except Exception:
            return False, None
