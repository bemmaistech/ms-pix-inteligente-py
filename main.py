from trataentoPng import ImageOCR


imagem = "comprovanteNubank.jpeg"  # Ajuste para o caminho da sua imagem
ocr = ImageOCR(imagem)
texto = ocr.process()

print("\n=== TEXTO EXTRAÍDO ===\n")
print(texto)

