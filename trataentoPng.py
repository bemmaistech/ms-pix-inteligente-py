import cv2
import numpy as np
import pytesseract
import os
from pathlib import Path

pytesseract.pytesseract.tesseract_cmd = r"C:\Users\dener\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
os.environ["TESSDATA_PREFIX"] = r"C:\Users\dener\AppData\Local\Programs\Tesseract-OCR\tessdata"


class ImageOCR:
    """Classe para extrair texto de uma imagem usando OCR."""

    def __init__(self, image_path: str):
        """Inicializa com o caminho da imagem."""
        self.image_path = Path(image_path)
        self.output_dir = Path("img")
        self.output_dir.mkdir(exist_ok=True)
        self.image = None

    def preprocess_image(self, min_width: int = 1200):
        """Pré-processa a imagem para melhorar OCR."""
        if not self.image_path.exists():
            raise FileNotFoundError(f"Imagem não encontrada: {self.image_path}")

        img = cv2.imread(str(self.image_path))
        if img is None:
            raise ValueError(f"Não foi possível ler a imagem: {self.image_path}")

        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        if img.shape[1] < min_width:
            scale = min_width / img.shape[1]
            img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

        img = cv2.bilateralFilter(img, d=9, sigmaColor=75, sigmaSpace=75)
        img = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8)).apply(img)
        img = cv2.filter2D(img, -1, np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]]))
        _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        output_path = self.output_dir / "page_preprocessed.png"
        cv2.imwrite(str(output_path), img)

        self.image = img
        return img

    def extract_text(self, config: str = "--oem 3 --psm 6") -> str:
        """Extrai texto da imagem processada usando Tesseract."""
        if self.image is None:
            raise ValueError("Nenhuma imagem processada. Chame preprocess_image() primeiro.")

        try:
            texto = pytesseract.image_to_string(self.image, lang="por", config=config)
        except pytesseract.pytesseract.TesseractError:
            print("Aviso: 'por' indisponível. Usando OCR padrão.")
            texto = pytesseract.image_to_string(self.image, config=config)

        return texto.strip()

    def process(self) -> str:
        """Executa o pipeline completo e retorna o texto extraído."""
        self.preprocess_image()
        return self.extract_text()


if __name__ == "__main__":
    ocr = ImageOCR("comprovanteNubank.png")
    texto = ocr.process()
    print("\n=== TEXTO EXTRAÍDO ===\n")
    print(texto)
