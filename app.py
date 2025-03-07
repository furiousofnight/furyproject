import json
import operator
import os
import random
import time
from typing import Any

from flask import Flask, render_template, request, redirect, url_for

# ------------------------------
# Configuração do Flask
# ------------------------------

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "seu_super_segredo_avancado")

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
        """Inicializa os atributos principais do jogo."""
        self.nivel = 1
        self.pontuacao = 0
        self.perguntas_respondidas = 0
        self.pergunta_atual = {}
        self.fim_de_jogo = False
        self.tempo_inicio = None
        self.power_ups = {'eliminar': 3, 'tempo_extra': 3, 'resposta_certa': 1}
        self.ranking_file = "ranking.json"

        if not os.path.exists(self.ranking_file):
            with open(self.ranking_file, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def gerar_pergunta(self):
        """Gera perguntas de forma dinâmica com base no nível do jogador."""
        dificuldade = self.nivel
        if dificuldade <= 5:
            n1, n2 = random.randint(1, 20), random.randint(1, 20)
            operador = random.choice(["+", "-"])
        elif dificuldade <= 10:
            n1, n2 = random.randint(10, 50), random.randint(10, 50)
            operador = random.choice(["+", "-", "*"])
        else:
            n1, n2 = random.randint(20, 100), random.randint(1, 20)
            operador = random.choice(["+", "-", "*", "/"])

        resposta_correta = OPERADORES[operador](n1, n2)
        if operador == "/":
            resposta_correta = round(resposta_correta, 1)

        self.pergunta_atual = {
            "pergunta": f"Quanto é {n1} {operador} {n2}?",
            "resposta": str(resposta_correta),
        }
        self.tempo_inicio = time.time()

    def verificar_resposta(self, resposta: str) -> bool:
        """Verifica se a resposta está correta e atualiza o estado do jogo."""
        if self.calcular_tempo_restante() <= 0:
            self.fim_de_jogo = True
            return False

        if resposta == self.pergunta_atual["resposta"]:
            self.pontuacao += 10
            self.perguntas_respondidas += 1
            self.atualizar_nivel()
            return True
        else:
            self.pontuacao -= 5
            self.verificar_fim_de_jogo()
            return False

    def calcular_tempo_restante(self) -> int:
        """Calcula o tempo restante com base no limite de 30 segundos."""
        limite_tempo = 30
        if not self.tempo_inicio:
            return limite_tempo
        tempo_passado = time.time() - self.tempo_inicio
        return max(0, int(limite_tempo - tempo_passado))

    def atualizar_nivel(self):
        """Atualiza o nível com base na pontuação."""
        novo_nivel = self.pontuacao // 50 + 1
        if novo_nivel > self.nivel:
            self.nivel = novo_nivel
        self.verificar_fim_de_jogo()

    def verificar_fim_de_jogo(self):
        """Determina as condições de vitória ou derrota no jogo."""
        if self.pontuacao >= 1500:
            self.fim_de_jogo = True
        elif self.pontuacao <= 0:
            self.fim_de_jogo = True

    def salvar_ranking(self, nome: str):
        """Salva o jogador no arquivo de ‘ranking’."""
        ranking_data = self.carregar_ranking()
        ranking_data.append({"nome": nome, "pontuacao": self.pontuacao, "nivel": self.nivel})
        ranking_data = sorted(ranking_data, key=lambda x: x["pontuacao"], reverse=True)[:10]
        with open(self.ranking_file, "w", encoding="utf-8") as f:
            json.dump(ranking_data, f, ensure_ascii=False)

    def carregar_ranking(self) -> list[dict[str, Any]]:
        """Carrega o ranking do arquivo."""
        with open(self.ranking_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def usar_power_up(self, tipo: str) -> Any:
        """Aplica o efeito do Power-Up especificado."""
        if tipo not in self.power_ups or self.power_ups[tipo] <= 0:
            return {"erro": "Power-Up não disponível!"}

        # Eliminar opções incorretas
        if tipo == "eliminar":
            self.power_ups[tipo] -= 1
            resposta_correta = self.pergunta_atual["resposta"]
            opcoes = [resposta_correta]

            while len(opcoes) < 4:
                opcao = str(random.randint(-100, 100))
                if opcao not in opcoes and opcao != resposta_correta:
                    opcoes.append(opcao)
            opcoes_erradas = [op for op in opcoes if op != resposta_correta][:2]
            return {
                "mensagem": "Duas opções incorretas foram eliminadas.",
                "opcoes_restantes": [resposta_correta] + opcoes_erradas
            }

        # Tempo extra
        elif tipo == "tempo_extra":
            self.power_ups[tipo] -= 1
            tempo_extra = 10
            if self.tempo_inicio is not None:
                self.tempo_inicio += tempo_extra  # Corrigido para adicionar tempo corretamente
            return {"mensagem": f"Tempo adicional de {tempo_extra}s foi concedido!"}

        # Resposta correta
        elif tipo == "resposta_certa":
            self.power_ups[tipo] -= 1
            return {
                "mensagem": "A resposta correta é exibida!",
                "resposta": self.pergunta_atual["resposta"]
            }

        return {"erro": "Tipo de Power-Up inválido!"}

    def reiniciar(self):
        """Reinicia o estado do jogo."""
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

    tempo_restante = jogo.calcular_tempo_restante()
    if tempo_restante <= 0:
        jogo.fim_de_jogo = True
        return redirect(url_for("fim"))

    jogo.gerar_pergunta()

    resposta_correta = jogo.pergunta_atual["resposta"]
    opcoes = [resposta_correta]
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
        tempo_restante=tempo_restante
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
    resultado = jogo.usar_power_up(tipo)
    if "erro" in resultado:
        return render_template(
            "jogar.html",
            pergunta=jogo.pergunta_atual["pergunta"],
            opcoes=[jogo.pergunta_atual["resposta"]],
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


@app.route("/reiniciar", methods=["POST"])
def reiniciar():
    jogo.reiniciar()
    return {"mensagem": "Jogo reiniciado com sucesso!"}, 200


# ------------------------------
# Executando o Servidor
# ------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
