from trataentoPng import ImageOCR
from tramentoDados import TextoTratamento


imagem = "comprovanteNubank.jpeg"  # Ajuste para o caminho da sua imagem
tratamento_ocr = ImageOCR()
texto = tratamento_ocr.OCR(imagem)

tratamento_texto = TextoTratamento(texto)
linhas_tratadas = tratamento_texto.process()

print("\n=== TEXTO EXTRAÍDO ===\n")
print(texto)
print("\n=== LINHAS TRATADAS ===\n")
print(linhas_tratadas)

