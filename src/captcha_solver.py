"""
CAPTCHA Solver using Tesseract OCR
"""
import cv2
import numpy as np
from PIL import Image
import pytesseract
import io
import re
from typing import Optional
import config
from .utils import setup_logger

class CaptchaSolver:
    """Solve image-based CAPTCHAs using Tesseract OCR"""

    def __init__(self):
        self.logger = setup_logger(__name__)

        # Set tesseract command path if configured
        if config.TESSERACT_CMD:
            pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_CMD

    def preprocess_image(self, image_bytes: bytes) -> Image.Image:
        """Preprocess CAPTCHA image for better OCR accuracy"""
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Apply thresholding
            _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

            # Denoise
            denoised = cv2.fastNlMeansDenoising(thresh)

            # Apply morphological operations to remove noise
            kernel = np.ones((2, 2), np.uint8)
            morph = cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, kernel)

            # Convert back to PIL Image
            pil_image = Image.fromarray(morph)

            # Increase contrast
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(pil_image)
            pil_image = enhancer.enhance(2.0)

            return pil_image

        except Exception as e:
            self.logger.error(f"Error preprocessing image: {e}")
            # Return original image as fallback
            return Image.open(io.BytesIO(image_bytes))

    def solve_captcha(self, image_bytes: bytes) -> Optional[str]:
        """Solve CAPTCHA from image bytes"""
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image_bytes)

            # Configure tesseract
            custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

            # Extract text
            text = pytesseract.image_to_string(processed_image, config=custom_config)

            # Clean text
            text = text.strip()
            text = re.sub(r'[^a-zA-Z0-9]', '', text)

            if len(text) >= 4:  # Most CAPTCHAs are 4-6 characters
                self.logger.info(f"CAPTCHA solved: {text}")
                return text
            else:
                self.logger.warning(f"CAPTCHA text too short: {text}")
                return None

        except Exception as e:
            self.logger.error(f"Error solving CAPTCHA: {e}")
            return None

    def solve_numeric_captcha(self, image_bytes: bytes) -> Optional[str]:
        """Solve numeric-only CAPTCHA"""
        try:
            processed_image = self.preprocess_image(image_bytes)

            # Configure for numbers only
            custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789'

            text = pytesseract.image_to_string(processed_image, config=custom_config)
            text = re.sub(r'[^0-9]', '', text.strip())

            if len(text) >= 4:
                self.logger.info(f"Numeric CAPTCHA solved: {text}")
                return text
            else:
                self.logger.warning(f"Numeric CAPTCHA text too short: {text}")
                return None

        except Exception as e:
            self.logger.error(f"Error solving numeric CAPTCHA: {e}")
            return None
