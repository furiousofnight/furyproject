from flask import Flask, render_template, request, redirect, flash, url_for
import random
import os

# Criação da aplicação Flask
app = Flask(__name__)

# Configuração de segurança: SECRET_KEY lida como variável de ambiente
# "chave_secreta_para_dev" é usada apenas em desenvolvimento/local
app.secret_key = os.environ.get("SECRET_KEY", "chave_secreta_para_dev")


class Jogo:
    def __init__(self):
        self.pontuacao = 0
        self.nivel_atual = 1
        self.questoes_corretas = 0
        self.jogo_ativo = True
        self.resposta_correta = None
        self.tempo_limite = 30  # Tempo inicial (em segundos)
        self.tempo_restante = self.tempo_limite
        self.power_ups = {"mais_tempo": 2, "mais_pontos": 2, "pular_questao": 2}
        self.nivel_dificuldade = 1

    def status_jogo(self):
        """Retorna o status atual do jogo."""
        return {
            "pontuacao": self.pontuacao,
            "nivel_atual": self.nivel_atual,
            "tempo_restante": self.tempo_restante,
            "power_ups": self.power_ups,
        }

    def gerar_questao(self):
        """Gera uma questão aleatória e define a resposta correta."""
        num1 = random.randint(1, 10 * self.nivel_dificuldade)
        num2 = random.randint(1, 10 * self.nivel_dificuldade)
        operacao = random.choice(["+", "-", "*", "/"])
        questao = f"Quanto é {num1} {operacao} {num2}?"

        if operacao == "+":
            resultado = num1 + num2
        elif operacao == "-":
            resultado = num1 - num2
        elif operacao == "*":
            resultado = num1 * num2
        else:  # Divisão
            while num2 == 0:  # Evita divisão por zero
                num2 = random.randint(1, 10)
            resultado = round(num1 / num2, 2)

        self.resposta_correta = resultado

        # Gera respostas erradas exclusivas
        respostas_erradas = set()
        while len(respostas_erradas) < 3:
            resposta_errada = random.randint(1, 10 * self.nivel_dificuldade)
            if resposta_errada != self.resposta_correta:
                respostas_erradas.add(resposta_errada)

        # Mescla respostas e embaralha
        respostas = list(respostas_erradas) + [self.resposta_correta]
        random.shuffle(respostas)

        return questao, respostas

    def atualizar_pontuacao(self, resposta_correta):
        """Atualiza a pontuação e faz progresso no nível."""
        if resposta_correta:
            self.pontuacao += 10 * self.nivel_atual
            self.questoes_corretas += 1
        else:
            self.pontuacao = max(0, self.pontuacao - 5)  # Sem pontuações negativas

        # Checa progresso para subir de nível
        if self.questoes_corretas % 3 == 0 and self.questoes_corretas > 0:
            self.nivel_atual += 1
            self.nivel_dificuldade += 1
            self.tempo_restante += 5  # Bonificação ao subir de nível

    def usar_power_up(self, tipo):
        """Aplica os efeitos de Power-Ups."""
        if self.power_ups.get(tipo, 0) > 0:
            if tipo == "mais_tempo":
                self.tempo_restante += 10
                flash("🕒 Você ganhou +10 segundos!", "info")
            elif tipo == "mais_pontos":
                self.pontuacao += 50
                flash("⭐ +50 pontos adicionados!", "info")
            elif tipo == "pular_questao":
                flash("➡ Questão pulada com sucesso!", "info")
                return True

            self.power_ups[tipo] -= 1
        else:
            flash(f"❌ Power-Up {tipo} indisponível!", "error")
        return False


# Gerencia o objeto do jogo
jogo = Jogo()


@app.route("/")
def index():
    """Página inicial."""
    global jogo

    if not jogo.jogo_ativo:
        jogo = Jogo()  # Reinicia jogo

    status = jogo.status_jogo()
    questao, respostas = jogo.gerar_questao()

    return render_template("index.html", status=status, questao=questao, respostas=respostas)


@app.route("/responder", methods=["POST"])
def responder():
    """Processa a resposta do jogador."""
    global jogo
    resposta_jogador = request.form.get("escolha")

    try:
        resposta_jogador = float(resposta_jogador)
    except ValueError:
        flash("❌ Resposta inválida.", "error")
        return redirect(url_for("index"))

    if resposta_jogador == jogo.resposta_correta:
        jogo.atualizar_pontuacao(resposta_correta=True)
        flash("✅ Resposta correta!", "info")
    else:
        jogo.atualizar_pontuacao(resposta_correta=False)
        flash(f"❌ Resposta errada! A correta era {jogo.resposta_correta}.", "error")

    # Checa se o tempo acabou
    if jogo.tempo_restante <= 0:
        return redirect(url_for("fim_do_jogo"))

    return redirect(url_for("index"))


@app.route("/power-up", methods=["POST"])
def power_up():
    """Usa um Power-Up."""
    global jogo
    tipo_power_up = request.form.get("tipo")
    jogo.usar_power_up(tipo_power_up)
    return redirect(url_for("index"))


@app.route("/ranking")
def ranking():
    """Exibe a tabela de rankings."""
    # Exemplo de dados de ranking
    ranking_data = [
        {"jogador": "Maria", "pontuacao": 1500, "nivel": 12},
        {"jogador": "José", "pontuacao": 1350, "nivel": 10},
        {"jogador": "Ana", "pontuacao": 1200, "nivel": 9}
    ]

    return render_template("ranking.html", ranking=ranking_data)


@app.route("/fim")
def fim_do_jogo():
    """Tela de fim do jogo."""
    global jogo
    jogo.jogo_ativo = False
    resultado = {
        "pontuacao": jogo.pontuacao,
        "nivel_atual": jogo.nivel_atual,
    }
    return render_template("game_over.html", resultado=resultado)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
