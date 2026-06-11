import cv2
import numpy as np
import pytesseract
import os
import shutil
import logging

logger = logging.getLogger(__name__)


def _detect_tesseract():
    # Prefer explicit environment variable
    for key in ("TESSERACT_CMD", "TESSERACT_PATH"):
        v = os.environ.get(key)
        if v:
            return v

    # Then try system PATH
    which = shutil.which("tesseract")
    if which:
        return which

    # Finally try common Windows install locations (including current user's AppData)
    common = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.join(os.path.expanduser("~"), "AppData", "Local", "Programs", "Tesseract-OCR", "tesseract.exe"),
    ]
    for p in common:
        if os.path.exists(p):
            return p

    return None


# Detect and configure Tesseract (non-destructive: only set if found)
tesseract_cmd = _detect_tesseract()
if tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    # Set TESSDATA_PREFIX if not already set and tessdata folder exists
    if not os.environ.get("TESSDATA_PREFIX"):
        tessdata_guess = os.path.join(os.path.dirname(tesseract_cmd), "tessdata")
        if os.path.isdir(tessdata_guess):
            os.environ["TESSDATA_PREFIX"] = tessdata_guess
else:
    logger.warning(
        "Tesseract não encontrado automaticamente. Defina TESSERACT_CMD ou instale/adicione tesseract ao PATH."
    )


class ImageOCR:
    """Classe para extrair texto de uma imagem tratada usando OCR."""

    def __init__(self):
        pass

    def extrair_texto(self, imagem, lang: str = "eng", config: str = "--oem 3 --psm 6") -> str:
        """Extrai texto da imagem tratada usando Tesseract."""
        if imagem is None:
            raise ValueError("Nenhuma imagem fornecida. Use TratamentoImagem para pré-processar a imagem.")

        try:
            texto = pytesseract.image_to_string(imagem, lang=lang, config=config)
        except pytesseract.pytesseract.TesseractError:
            print(f"Aviso: '{lang}' indisponível. Usando OCR padrão.")
            texto = pytesseract.image_to_string(imagem, config=config)

        return texto.strip()

    def OCR(self, imagem, config: str = "--oem 3 --psm 6") -> str:
        """Método público para extrair texto a partir de uma imagem tratada."""
        return self.extrair_texto(imagem, config=config)


if __name__ == "__main__":
    from ocr.tratamento_imagem import TratamentoImagem

    caminho_imagem = "comprovanteNubank.jpeg"
    imagem_tratada = TratamentoImagem(caminho_imagem).preprocessar_imagem()
    texto = ImageOCR().extrair_texto(imagem_tratada)
    print("\n=== TEXTO EXTRAÍDO ===\n")
    print(texto)
