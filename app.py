from flask import Flask, render_template, request, redirect, url_for
from PIL import Image, ImageChops
import os

app = Flask(__name__)

#-------------------------------------- Número -> Imagem --------------------------------------------------

def classifyDigits(numero: int):
    if not (0 <= numero <= 9999):
        raise ValueError("Número deve ter no máximo 4 dígitos (entre 0 e 9999)")

    unidades = numero % 10
    dezenas = (numero // 10 % 10) * 10
    centenas = (numero // 100 % 10) * 100
    milhares = (numero // 1000 % 10) * 1000

    return [v for v in (milhares, centenas, dezenas, unidades) if v > 0]

def padronizar_simbolo(imagem: Image.Image, tamanho: tuple = (200, 200)) -> Image.Image:
   
    imagem = imagem.convert("RGBA")
    fundo = Image.new("RGBA", tamanho, (255, 255, 255, 0))
    img_w, img_h = imagem.size
    pos_x = (tamanho[0] - img_w) // 2
    pos_y = (tamanho[1] - img_h) // 2
    fundo.paste(imagem, (pos_x, pos_y), imagem)
    return fundo

def removeBackground(imagem: Image.Image, tolerancia: int = 240) -> Image.Image:
    imagem = imagem.convert("RGBA")
    nova_imagem = []
    for r, g, b, a in imagem.getdata():
        if r >= tolerancia and g >= tolerancia and b >= tolerancia:
            nova_imagem.append((255, 255, 255, 0))
        else:
            nova_imagem.append((r, g, b, a))
    imagem.putdata(nova_imagem)
    return imagem

def generateImage(numero: int, imagesFolder='simbolos', output='static/output.png'):

    componentes = classifyDigits(numero)

    simbolos_padronizados = []

    for valor in componentes:
        caminho = os.path.join(imagesFolder, f"{valor}.png")
        imagem = Image.open(caminho)
        imagem = removeBackground(imagem)
        imagem = padronizar_simbolo(imagem)  
        simbolos_padronizados.append(imagem)

    resultado = simbolos_padronizados[0].copy()
    for simbolo in simbolos_padronizados[1:]:
        resultado = Image.alpha_composite(resultado, simbolo)

    os.makedirs(os.path.dirname(output), exist_ok=True)
    resultado.save(output)
    print(f"Imagem salva como {output}")

#-------------------------------------- Imagem -> Número  --------------------------------------------------

UPLOAD_FOLDER = 'uploads'
TEMPLATES_FOLDER = 'simbolos'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def compareImage(img1: Image.Image, img2: Image.Image, tolerancia=25) -> bool:
   
    diff = ImageChops.difference(img1, img2)
    bbox = diff.getbbox()
    if not bbox:
        return True
    else:
        hist = diff.histogram()
        rms = sum(h * (i % 256) ** 2 for i, h in enumerate(hist)) / float(img1.size[0] * img1.size[1])
        return rms < tolerancia

def indetifyCisterciansNumbers(caminho_entrada: str, simbolos_dir='simbolos') -> int:
    entrada = Image.open(caminho_entrada).convert("RGBA")
    entrada = removeBackground(entrada)

    largura, altura = entrada.size
    metade_largura = largura // 2
    metade_altura = altura // 2

    q1 = entrada.crop((metade_largura, 0, largura, metade_altura))
    # Inferior direito (centenas)
    q2 = entrada.crop((metade_largura, metade_altura, largura, altura))
    # Superior esquerdo (dezenas)
    q3 = entrada.crop((0, 0, metade_largura, metade_altura))
    # Inferior esquerdo (unidades)
    q4 = entrada.crop((0, metade_altura, metade_largura, altura))

    quadrantes = [q4, q3, q2, q1] 
    resultado = 0

    for i, quadrante in enumerate(quadrantes):
        digito_detectado = -1
        for simbolo_arquivo in sorted(os.listdir(simbolos_dir)):
            if not simbolo_arquivo.endswith('.png'):
                continue
            valor = int(simbolo_arquivo.replace('.png', ''))
            simbolo_path = os.path.join(simbolos_dir, simbolo_arquivo)
            simbolo_img = removeBackground(Image.open(simbolo_path).convert("RGBA"))
            simbolo_img = simbolo_img.resize(quadrante.size)

            if compareImage(quadrante, simbolo_img, tolerancia=100):
                digito_detectado = valor
                break

        if digito_detectado == -1:
            return -1  # Se algum dígito não for detectado, retorna -1

        resultado += digito_detectado * (10 ** i)

    return resultado 

#--------------------------------------------------- ROTAS -----------------------------------------------------

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        numero = int(request.form['numero'])
        generateImage(numero)
        return render_template('index.html', numero=numero, imagem='output.png')
    return render_template('index.html')

@app.route('/reconhecer', methods=['GET', 'POST'])
def reconhecer():
    numero_detectado = None
    imagem = None

    if request.method == 'POST':
        if 'imagem' not in request.files:
            return render_template('reconhecer.html', numero=None, imagem=None)

        arquivo = request.files['imagem']
        caminho = os.path.join(UPLOAD_FOLDER, 'entrada.png')
        arquivo.save(caminho)

        numero_detectado = indetifyCisterciansNumbers(caminho)
        imagem = 'entrada.png'

    return render_template('reconhecer.html', numero=numero_detectado, imagem=imagem)

if __name__ == '__main__':
    app.run(debug=True)
        
    


