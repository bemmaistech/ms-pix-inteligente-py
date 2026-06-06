import cv2
import numpy as np
from pathlib import Path

try:
    from pdf2image import convert_from_path
except ImportError:
    convert_from_path = None


class TratamentoImagem:
    """Classe para pré-processar a imagem antes do OCR.

    Parâmetros:
    - caminho_imagem: caminho do arquivo (imagem ou PDF)
    - poppler_path: caminho opcional para os binários do Poppler (ex: C:\\Poppler\\bin)
    """

    def __init__(self, caminho_imagem: str, poppler_path: str | None = None):
        self.caminho_imagem = Path(caminho_imagem)
        self.poppler_path = poppler_path
        self.diretorio_saida = Path("img")
        self.diretorio_saida.mkdir(exist_ok=True)

    def preprocessar_imagem(self, largura_minima: int = 1200):
        """Pré-processa a imagem e salva o resultado na pasta img."""
        if not self.caminho_imagem.exists():
            raise FileNotFoundError(f"Imagem não encontrada: {self.caminho_imagem}")

        # se for PDF, converter para imagem
        if self.caminho_imagem.suffix.lower() == ".pdf":
            if convert_from_path is None:
                raise ImportError("pdf2image não está instalado. Use: pip install pdf2image")
            try:
                if self.poppler_path:
                    paginas = convert_from_path(str(self.caminho_imagem), dpi=300, poppler_path=str(self.poppler_path))
                else:
                    paginas = convert_from_path(str(self.caminho_imagem), dpi=300)
            except Exception as e:
                if "poppler" in str(e).lower():
                    raise RuntimeError(
                        f"Poppler não está instalado ou não foi encontrado no PATH.\n"
                        f"Instale poppler usando uma das opções:\n"
                        f"  1. Chocolatey: choco install poppler\n"
                        f"  2. Conda: conda install -c conda-forge poppler\n"
                        f"  3. Manual: https://github.com/oschwartz10612/poppler-windows/releases\n"
                        f"Erro original: {e}"
                    )
                raise
            if not paginas:
                raise ValueError(f"Não foi possível converter o PDF: {self.caminho_imagem}")
            imagem_pil = paginas[0]
            imagem = cv2.cvtColor(np.array(imagem_pil), cv2.COLOR_RGB2BGR)
        else:
            imagem = cv2.imread(str(self.caminho_imagem))
            if imagem is None:
                raise ValueError(f"Não foi possível ler a imagem: {self.caminho_imagem}")

        imagem = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

        if imagem.shape[1] < largura_minima:
            escala = largura_minima / imagem.shape[1]
            imagem = cv2.resize(imagem, None, fx=escala, fy=escala, interpolation=cv2.INTER_CUBIC)

        imagem = cv2.bilateralFilter(imagem, d=9, sigmaColor=75, sigmaSpace=75)
        imagem = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8)).apply(imagem)
        imagem = cv2.filter2D(imagem, -1, np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]]))
        _, imagem = cv2.threshold(imagem, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        nome_saida = f"{self.caminho_imagem.stem}_preprocessed.png"
        caminho_saida = self.diretorio_saida / nome_saida
        cv2.imwrite(str(caminho_saida), imagem)

        return imagem


if __name__ == "__main__":
    caminho_imagem = "comprovanteNubank.jpeg"
    tratador = TratamentoImagem(caminho_imagem)
    imagem_tratada = tratador.preprocessar_imagem()
    print(f"Imagem tratada salva em: img/{imagem_tratada.shape}")
