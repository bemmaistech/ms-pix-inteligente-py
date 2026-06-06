from ocr.tratamento_imagem import TratamentoImagem
from ocr.image_ocr import ImageOCR
from ocr.texto_tratamento import TextoTratamento
from ocr.separacao_dados import SeparadorDados
import shutil
import os
from pathlib import Path
from Controller.controlador import Controlador


def main() -> None:
    caminho_imagem = Controlador("ComprovanteSantander.pdf").salvar_para_projeto()

    # detectar se poppler está disponível no PATH
    poppler_path = None
    if Path(caminho_imagem).suffix.lower() == ".pdf":
        if shutil.which("pdfinfo"):
            poppler_path = None
        else:
            # tenta variável de ambiente customizada
            poppler_env = os.environ.get("POPPLER_PATH") or os.environ.get("POPLER_PATH")
            if poppler_env and Path(poppler_env).exists():
                poppler_path = poppler_env
            else:
                # tentativa por caminho padrão comum de download
                candidate = Path(r"C:\Users\dener\Downloads\Release-26.02.0-0\poppler-26.02.0\Library\bin")
                if candidate.exists():
                    poppler_path = str(candidate)

    # 1) tratamento da imagem
    tratamento_imagem = TratamentoImagem(caminho_imagem, poppler_path=poppler_path)
    imagem_tratada = tratamento_imagem.preprocessar_imagem()

    # 2) OCR na imagem já tratada
    ocr = ImageOCR()
    texto = ocr.extrair_texto(imagem_tratada)

    linhas = TextoTratamento(texto).process()
    dados = SeparadorDados(linhas).processar()

    print("\n=== TEXTO EXTRAÍDO ===\n", texto, sep="")
    print("\n=== LINHAS TRATADAS ===\n", linhas, sep="")
    print("\n=== DADOS SEPARADOS ===\n", dados, sep="")


if __name__ == "__main__":
    main()

