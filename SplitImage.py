from PIL import Image
import os


def cortar_simbolos(imagem_path: str, output_dir: str = "simbolos", margem: int = 0):
    imagem = Image.open(imagem_path)
    largura_total, altura_total = imagem.size

    colunas = 9
    linhas = 4

    simbolo_largura = largura_total / colunas
    simbolo_altura = altura_total / linhas

    os.makedirs(output_dir, exist_ok=True)

    for linha in range(linhas):
        for coluna in range(colunas):
            # Coordenadas com margem opcional
            left = int(coluna * simbolo_largura) + margem
            upper = int(linha * simbolo_altura) + margem
            right = int((coluna + 1) * simbolo_largura) - margem
            lower = int((linha + 1) * simbolo_altura) - margem

            simbolo = imagem.crop((left, upper, right, lower))

            valor = (coluna + 1) * (10 ** linha)
            nome_arquivo = os.path.join(output_dir, f"{valor}.png")
            simbolo.save(nome_arquivo)

    print(f"{colunas * linhas} símbolos salvos em: {output_dir}")

image = 'numbers.png'
cortar_simbolos(image)