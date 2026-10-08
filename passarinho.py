import turtle
import random
from pathlib import Path

# A janela do jogo
tela = turtle.Screen()
tela.setup(width=600, height=500)
tela.title("Passarinho no céu")
tela.bgcolor("skyblue")
tela.tracer(0)  # Atualizamos o desenho manualmente para a animação ficar suave.

# O lápis desenha o cenário; outra tartaruga mostra o personagem.
lapis = turtle.Turtle()
lapis.hideturtle()
lapis.speed(0)
lapis.penup()

# Estas variáveis guardam o estado atual do jogo.
passaro_y = 0                 # Altura do passarinho
velocidade = 0               # Velocidade vertical
canos = []                   # Cada cano guarda [posição_x, centro_do_vão]
pontos = 0
estado = "inicio"            # Pode ser: inicio, jogando ou fim

LARGURA_CANO = 55
ALTURA_VAO = 140
PASSARO_X = -180
LARGURA_PASSARO = 44
ALTURA_PASSARO = 24

IMAGEM_PERSONAGEM = Path(__file__).with_name("lula_voando.gif")
tela.register_shape(str(IMAGEM_PERSONAGEM))
personagem = turtle.Turtle(shape=str(IMAGEM_PERSONAGEM))
personagem.penup()
personagem.speed(0)
personagem.hideturtle()
personagem_stamp = None


def retangulo(x, y, largura, altura, cor):
    """Desenha um retângulo começando no canto inferior esquerdo (x, y)."""
    lapis.goto(x, y)
    lapis.color(cor)
    lapis.begin_fill()
    lapis.pendown()
    lapis.goto(x + largura, y)
    lapis.goto(x + largura, y + altura)
    lapis.goto(x, y + altura)
    lapis.goto(x, y)
    lapis.end_fill()
    lapis.penup()


def escrever(x, y, texto, tamanho=18):
    lapis.goto(x, y)
    lapis.color("black")
    lapis.write(texto, align="center", font=("Arial", tamanho, "bold"))


def desenhar_prisao():
    retangulo(-300, -250, 600, 500, "dimgray")

    # Blocos de pedra dão textura à parede da cela.
    lapis.color("gray")
    lapis.pensize(2)
    for y in range(-210, 240, 45):
        lapis.goto(-300, y)
        lapis.pendown()
        lapis.goto(300, y)
        lapis.penup()

    for y in range(-210, 240, 90):
        for x in range(-270, 300, 90):
            lapis.goto(x, y)
            lapis.pendown()
            lapis.goto(x, y + 45)
            lapis.penup()

    # Grades verticais ao fundo, atrás do jogo.
    lapis.color("lightgray")
    lapis.pensize(7)
    for x in range(-290, 301, 60):
        lapis.goto(x, -215)
        lapis.pendown()
        lapis.goto(x, 240)
        lapis.penup()

    lapis.color("black")
    lapis.pensize(1)


def desenhar():
    """Apaga o quadro anterior e desenha tudo na posição atual."""
    global personagem_stamp
    lapis.clear()
    if personagem_stamp is not None:
        personagem.clearstamp(personagem_stamp)

    desenhar_prisao()

    # Chão
    retangulo(-300, -250, 600, 35, "sienna")

    # Desenha os dois pedaços de cada cano, deixando um vão no meio.
    for x, centro, passou in canos:
        topo_do_vao = centro + ALTURA_VAO / 2
        baixo_do_vao = centro - ALTURA_VAO / 2
        retangulo(x, topo_do_vao, LARGURA_CANO, 300, "green")
        retangulo(x, -250, LARGURA_CANO, baixo_do_vao + 250, "green")

    personagem.goto(PASSARO_X, passaro_y)
    personagem_stamp = personagem.stamp()

    escrever(0, 205, "Pontos: " + str(pontos), 18)

    if estado == "inicio":
        escrever(0, 30, "Aperte ESPAÇO para começar", 17)
    elif estado == "fim":
        escrever(0, 30, "Fim de jogo! Aperte ESPAÇO para tentar de novo", 14)

    tela.update()


def novo_jogo():
    """Coloca o passarinho e os canos nas posições iniciais."""
    global passaro_y, velocidade, canos, pontos, estado
    passaro_y = 0
    velocidade = 0
    pontos = 0
    estado = "jogando"
    canos = [[180, 20, False], [430, -30, False], [680, 40, False]]
    atualizar()


def pular():
    """O espaço dá um impulso para cima."""
    global velocidade, estado

    if estado != "jogando":
        novo_jogo()

    velocidade = 7


def bateu():
    """Verifica se o passarinho tocou no chão, no teto ou em um cano."""
    if passaro_y - ALTURA_PASSARO < -215:
        return True
    if passaro_y + ALTURA_PASSARO > 240:
        return True

    for x, centro, passou in canos:
        # Só verificamos o cano quando ele está na mesma faixa horizontal.
        if PASSARO_X + LARGURA_PASSARO > x and PASSARO_X - LARGURA_PASSARO < x + LARGURA_CANO:
            topo_do_vao = centro + ALTURA_VAO / 2
            baixo_do_vao = centro - ALTURA_VAO / 2

            # Se o passarinho está acima ou abaixo do vão, bateu no cano.
            if passaro_y + ALTURA_PASSARO > topo_do_vao:
                return True
            if passaro_y - ALTURA_PASSARO < baixo_do_vao:
                return True

    return False


def atualizar():
    """Roda uma pequena etapa do jogo e agenda a próxima."""
    global passaro_y, velocidade, canos, pontos, estado

    if estado != "jogando":
        desenhar()
        return

    # Gravidade: a cada etapa, puxa o passarinho para baixo.
    velocidade = velocidade - 0.35
    passaro_y = passaro_y + velocidade

    # Move todos os canos para a esquerda.
    for cano in canos:
        cano[0] = cano[0] - 3

        # Quando um cano passa pelo passarinho, ganhamos um ponto.
        if cano[0] + LARGURA_CANO <= PASSARO_X and not cano[2]:
            pontos = pontos + 1
            cano[2] = True

    # O primeiro cano saiu da tela: colocamos ele de volta depois do último.
    if canos[0][0] < -350:
        canos.pop(0)
        novo_x = canos[-1][0] + 250
        novo_centro = random.randint(-40, 100)
        canos.append([novo_x, novo_centro, False])

    if bateu():
        estado = "fim"

    desenhar()

    # Chama esta função de novo daqui a 30 milissegundos.
    if estado == "jogando":
        tela.ontimer(atualizar, 30)


# A tecla espaço chama a função pular.
tela.listen()
tela.onkeypress(pular, "space")

desenhar()
tela.mainloop()
