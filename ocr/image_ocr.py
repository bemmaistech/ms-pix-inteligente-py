import cv2
import numpy as np
import pytesseract
import os

# Ajuste do caminho do tesseract, mantenha se necessário
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\dener\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
os.environ["TESSDATA_PREFIX"] = r"C:\Users\dener\AppData\Local\Programs\Tesseract-OCR\tessdata"


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
