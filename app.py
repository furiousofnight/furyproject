import json
import os
import random
import time
import operator
from typing import Any

from flask import Flask, render_template, request, redirect, url_for

# ------------------------------
# Configuração do Flask
# ------------------------------

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "seu_super_segredo_avancado")  # Variável de ambiente para o segredo

# ------------------------------
# Módulo de Operadores Seguros
# ------------------------------

OPERADORES = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
}


# ------------------------------
# Classe Central - Jogo
# ------------------------------

class Jogo:
    def __init__(self):
        """
        Inicializa os atributos principais do jogo.
        """
        self.nivel = 1
        self.pontuacao = 0
        self.perguntas_respondidas = 0
        self.pergunta_atual = {}
        self.fim_de_jogo = False
        self.tempo_inicio = None
        self.power_ups = {'eliminar': 3, 'tempo_extra': 3, 'resposta_certa': 1}  # Power-Ups iniciais
        self.ranking_file = "ranking.json"

        # Criação do ranking.json caso não exista
        if not os.path.exists(self.ranking_file):
            with open(self.ranking_file, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def gerar_pergunta(self):
        """
        Gera perguntas de forma dinâmica com base no nível do jogador.
        """
        dificuldade = self.nivel

        # Definição dos números e do operador baseados no nível
        if dificuldade <= 5:
            n1, n2 = random.randint(1, 20), random.randint(1, 20)
            operador = random.choice(["+", "-"])
        elif dificuldade <= 10:
            n1, n2 = random.randint(10, 50), random.randint(10, 50)
            operador = random.choice(["+", "-", "*"])
        else:
            n1, n2 = random.randint(20, 100), random.randint(1, 20)  # Evitar divisão por zero
            operador = random.choice(["+", "-", "*", "/"])

        # Cálculo da resposta usando operadores válidos
        resposta_correta = OPERADORES[operador](n1, n2)

        # Arredonda a resposta no caso de divisões
        if operador == "/":
            resposta_correta = round(resposta_correta, 1)

        # Salva a pergunta gerada
        self.pergunta_atual = {
            "pergunta": f"Quanto é {n1} {operador} {n2}?",
            "resposta": str(resposta_correta),
        }
        self.tempo_inicio = time.time()

    def verificar_resposta(self, resposta: str) -> bool:
        """
        Verifica se a resposta está correta, atualizando a pontuação e o estado do jogo.
        """
        if resposta == self.pergunta_atual["resposta"]:
            self.pontuacao += 10
            self.perguntas_respondidas += 1
            self.atualizar_nivel()
            return True
        else:
            self.pontuacao -= 5
            self.verificar_fim_de_jogo()
            return False

    def atualizar_nivel(self):
        """
        Atualiza o nível com base na pontuação acumulada.
        """
        novo_nivel = self.pontuacao // 50 + 1
        if novo_nivel > self.nivel:
            self.nivel = novo_nivel
        self.verificar_fim_de_jogo()

    def verificar_fim_de_jogo(self):
        """
        Determina as condições de fim de jogo (vitória ou derrota).
        """
        if self.pontuacao >= 1500:
            self.fim_de_jogo = True  # Vitória
        elif self.pontuacao <= 0:
            self.fim_de_jogo = True  # Derrota

    def salvar_ranking(self, nome: str):
        """
        Salva o jogador no ranking.
        """
        ranking_data = self.carregar_ranking()
        ranking_data.append({"nome": nome, "pontuacao": self.pontuacao, "nivel": self.nivel})
        ranking_data = sorted(ranking_data, key=lambda x: x["pontuacao"], reverse=True)[:10]
        with open(self.ranking_file, "w", encoding="utf-8") as f:
            json.dump(ranking_data, f, ensure_ascii=False)

    def carregar_ranking(self) -> list[dict[str, Any]]:
        """
        Carrega o ranking do arquivo.
        """
        with open(self.ranking_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def usar_power_up(self, tipo: str) -> Any:
        """
        Aplica o efeito de um Power-Up ao jogo.
        """
        if tipo not in self.power_ups or self.power_ups[tipo] <= 0:
            return {"erro": "Power-Up não disponível!"}

        if tipo == "resposta_certa":
            self.power_ups[tipo] -= 1
            return {"resposta": self.pergunta_atual["resposta"]}

        elif tipo == "tempo_extra":
            self.power_ups[tipo] -= 1
            self.tempo_inicio -= 10  # Adiciona mais 10 segundos ao timer
            return {"mensagem": "Mais 10 segundos adicionados!"}

        elif tipo == "eliminar":
            self.power_ups[tipo] -= 1
            return {"mensagem": "Opções incorretas removidas!"}

        return {"erro": "Tipo de Power-Up inválido!"}

    def reiniciar(self):
        """
        Reinicia o jogo.
        """
        self.__init__()


# Instância única do jogo
jogo = Jogo()


# ------------------------------
# Rotas do Flask
# ------------------------------

@app.route("/")
def index():
    jogo.reiniciar()
    return render_template("index.html")


@app.route("/jogar")
def jogar():
    if jogo.fim_de_jogo:
        return redirect(url_for("fim"))

    jogo.gerar_pergunta()

    # Geração de opções múltiplas e embaralhamento
    resposta_correta = jogo.pergunta_atual["resposta"]
    opcoes = [resposta_correta]  # Adiciona a resposta correta
    while len(opcoes) < 4:
        opcao = str(random.randint(-100, 100))
        if opcao not in opcoes:
            opcoes.append(opcao)
    random.shuffle(opcoes)

    return render_template(
        "jogar.html",
        pergunta=jogo.pergunta_atual["pergunta"],
        opcoes=opcoes,
        nivel=jogo.nivel,
        pontuacao=jogo.pontuacao,
        power_ups=jogo.power_ups,
    )


@app.route("/responder", methods=["POST"])
def responder():
    resposta = request.form.get("resposta")
    acertou = jogo.verificar_resposta(resposta)

    if jogo.fim_de_jogo:
        return redirect(url_for("fim"))

    return render_template(
        "responder.html",
        correta=acertou,
        resposta_certa=jogo.pergunta_atual["resposta"],
        pontuacao=jogo.pontuacao,
        nivel=jogo.nivel,
    )


@app.route("/power_up/<tipo>", methods=["POST"])
def power_up(tipo):
    """
    Rota para uso de Power-Up.
    """
    resultado = jogo.usar_power_up(tipo)

    if "erro" in resultado:  # Caso o Power-Up não esteja disponível
        return render_template(
            "jogar.html",
            pergunta=jogo.pergunta_atual["pergunta"],
            opcoes=[jogo.pergunta_atual["resposta"]],  # Garante que a resposta seja exibida
            nivel=jogo.nivel,
            pontuacao=jogo.pontuacao,
            power_ups=jogo.power_ups,
            erro=resultado["erro"]
        )

    return redirect(url_for("jogar", mensagem=resultado.get("mensagem", "")))


@app.route("/fim", methods=["GET", "POST"])
def fim():
    if request.method == "POST":
        nome = request.form.get("nome")
        jogo.salvar_ranking(nome)
        return redirect(url_for("ver_ranking"))
    return render_template("fim.html", pontuacao=jogo.pontuacao, nivel=jogo.nivel)


@app.route("/ranking")
def ver_ranking():
    ranking = jogo.carregar_ranking()
    return render_template("ranking.html", ranking=ranking)


@app.route("/regras")
def regras():
    return render_template("regras.html")


# ------------------------------
# Executando o Servidor
# ------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
