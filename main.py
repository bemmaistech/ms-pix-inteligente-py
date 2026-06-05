#cv2 é a abreviação de OpenCV, uma biblioteca de visão computacional que permite ler e processar imagens. Pytesseract é uma biblioteca Python que serve como um wrapper para o Tesseract OCR, permitindo extrair texto de imagens usando OCR (Optical Character Recognition).
import cv2 
import pytesseract



#Ler imgagem
imagem = cv2.imread('comprovante_pix.jpeg')

#Estamos definindo o caminho do tesseract para o pytesseract, para que ele possa usar o OCR para extrair texto da imagem.
caminho = r"C:\Users\dener\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

pytesseract.pytesseract.tesseract_cmd = caminho
#Pedir pytessact Estrair texto da imgagem 
texto = pytesseract.image_to_string(imagem)

#colocar cada linha dentro de uma posição de uma listagit
lista = texto.split('\n')
#limpando a lista, retirando linhas vazias.
listalimpa = [s for s in lista if s.strip()]
cont = 0

for linha in listalimpa:
    if 'R$' in linha:
        #Verificar valor do pix
        #print('Valor do Pix encontrado:', linha)
        #Separando a string ultilizando o separador R$ e atribuindo a posição 1, que contem o valor do pix. 
        VALOR_PIX = linha.split('R$')[1]
    print(f'{cont}: {linha}')
    acont += 1
