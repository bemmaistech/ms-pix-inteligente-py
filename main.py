from trataentoPng import ImageOCR


imagem = "comprovanteNubank.jpeg"  # Ajuste para o caminho da sua imagem
tratamento = ImageOCR()
texto = tratamento.OCR(imagem)

print("\n=== TEXTO EXTRAÍDO ===\n")
print(texto)

