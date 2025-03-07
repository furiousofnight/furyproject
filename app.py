from flask import Flask, render_template, request, redirect, flash, url_for
import random
import os

# Criação da aplicação Flask
app = Flask(__name__)

# Configuração de segurança: SECRET_KEY lida como variável de ambiente
# O padrão "chave_secreta_para_dev" é usado apenas em ambiente de desenvolvimento/local
app.secret_key = os.environ.get("SECRET_KEY", "chave_secreta_para_dev")


class Jogo:
    def __init__(self):
        self.pontuacao = 0
        self.nivel_atual = 1
        self.questoes_corretas = 0
        self.jogo_ativo = True
        self.resposta_correta = None
        self.tempo_limite = 30  # Tempo inicial por nível (em segundos)
        self.tempo_restante = self.tempo_limite
        self.power_ups = {"mais_tempo": 2, "mais_pontos": 2, "pular_questao": 2}
        self.nivel_dificuldade = 1
        self.inicio = True  # Para indicar se é o início do jogo

    def status_jogo(self):
        """Retorna o status atual do jogo."""
        return {
            "pontuacao": self.pontuacao,
            "nivel_atual": self.nivel_atual,
            "tempo_restante": self.tempo_restante,
            "power_ups": self.power_ups,
        }

    def gerar_questao(self):
        """Gera uma questão dinâmica e define a resposta correta."""
        num1 = random.randint(1, 10 * self.nivel_dificuldade)
        num2 = random.randint(1, 10 * self.nivel_dificuldade)

        operacao = random.choice(["+", "-", "*", "/"])
        questao = f"Quanto é {num1} {operacao} {num2}?"

        # Resolver operação explicitamente
        if operacao == "+":
            resultado = num1 + num2
        elif operacao == "-":
            resultado = num1 - num2
        elif operacao == "*":
            resultado = num1 * num2
        else:  # Divisão
            while num2 == 0:  # Evita divisão por zero
                num2 = random.randint(1, 10 * self.nivel_dificuldade)
            resultado = round(num1 / num2, 2)

        self.resposta_correta = resultado

        # Gera respostas únicas erradas
        respostas_erradas = set()
        while len(respostas_erradas) < 3:
            resposta_errada = random.randint(1, 10 * self.nivel_dificuldade)
            if resposta_errada != self.resposta_correta:
                respostas_erradas.add(resposta_errada)

        # Shufflar respostas (incluindo a certa)
        respostas = list(respostas_erradas) + [self.resposta_correta]
        random.shuffle(respostas)

        return questao, respostas, self.resposta_correta

    def atualizar_pontuacao(self, resposta_correta):
        """Atualiza a pontuação e gerencia mudanças de nível."""
        if resposta_correta:
            self.pontuacao += 10 * self.nivel_atual
            self.questoes_corretas += 1
        else:
            # Penaliza o jogador com redução de pontuação e tempo
            self.pontuacao = max(0, self.pontuacao - 5)  # Evita pontuação negativa
            self.tempo_restante -= 5

        # Progressão de nível
        if self.questoes_corretas % 3 == 0 and self.questoes_corretas > 0:
            self.nivel_atual += 1
            self.nivel_dificuldade += 1
            self.tempo_restante += self.nivel_atual * 5  # Bonificação de tempo ao subir de nível

    def usar_power_up(self, tipo):
        """Aplica os efeitos dos power-ups."""
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
            flash(f"❌ Você não possui mais o Power-Up: {tipo}", "error")

        return False


jogo = Jogo()


@app.route("/")
def index():
    """Página inicial e principal do jogo."""
    global jogo
    if not jogo.jogo_ativo:
        jogo = Jogo()  # Reinicia se o jogo não estiver ativo

    status = jogo.status_jogo()
    questao, respostas, jogo.resposta_correta = jogo.gerar_questao()

    return render_template("index.html", status=status, questao=questao, respostas=respostas)


@app.route("/responder", methods=["POST"])
def responder():
    """Rota que processa a resposta do jogador."""
    global jogo

    # Entrada do jogador
    resposta_jogador = request.form.get("escolha")
    try:
        resposta_jogador = float(resposta_jogador)
    except ValueError:
        flash("❌ Escolha inválida! Tente novamente.", "error")
        return redirect(url_for("index"))

    # Verifica a resposta
    if resposta_jogador == jogo.resposta_correta:
        flash("✅ Resposta correta! 🎉", "success")
        jogo.atualizar_pontuacao(resposta_correta=True)
    else:
        flash(f"❌ Resposta incorreta! A correta era {jogo.resposta_correta}.", "error")
        jogo.atualizar_pontuacao(resposta_correta=False)

    # Verifica se o tempo acabou
    if jogo.tempo_restante <= 0:
        return redirect(url_for("fim_do_jogo"))

    return redirect(url_for("index"))


@app.route("/power-up", methods=["POST"])
def power_up():
    """Rota que processa o uso de Power-Ups."""
    global jogo
    tipo_power_up = request.form.get("tipo")

    if jogo.usar_power_up(tipo_power_up):
        if tipo_power_up == "pular_questao":
            flash("✅ Você escolheu pular a questão!", "info")

    return redirect(url_for("index"))


@app.route("/fim")
def fim_do_jogo():
    """Rota que exibe a tela final de pontuação e finaliza o jogo."""
    global jogo
    jogo.jogo_ativo = False
    resultado = {
        "pontuacao": jogo.pontuacao,
        "nivel_atual": jogo.nivel_atual,
        "tempo_restante": jogo.tempo_restante,
    }
    return render_template("game_over.html", resultado=resultado)


if __name__ == "__main__":
    # Configuração para produção
    port = int(os.getenv("PORT", 5000))  # Porta configurada no ambiente (Heroku configura automaticamente)
    app.run(host="0.0.0.0", port=port)
