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
        }

    def gerar_questao(self):
        """Gera uma questão mais desafiadora e define a resposta correta."""
        num1 = random.randint(1, 10 * self.nivel_dificuldade)
        num2 = random.randint(1, 10 * self.nivel_dificuldade)
        operacao = random.choice(["+", "-", "*", "/"])

        questao = f"Quanto é {num1} {operacao} {num2}?"

        try:
            resultado = eval(f"{num1} {operacao} {num2}")
            if operacao == "/":
                resultado = round(resultado, 2)  # Arredonda em casos de divisão
            self.resposta_correta = resultado
        except ZeroDivisionError:
            return self.gerar_questao()  # Gera novamente se houver divisão por zero

        respostas_erradas = set()
        while len(respostas_erradas) < 3:
            resposta_errada = random.randint(1, 10 * self.nivel_atual)
            if resposta_errada != self.resposta_correta:
                respostas_erradas.add(resposta_errada)

        respostas = list(respostas_erradas) + [self.resposta_correta]
        random.shuffle(respostas)

        return questao, respostas, self.resposta_correta

    def atualizar_pontuacao(self):
        """Atualiza a pontuação e verifica se o nível deve aumentar."""
        self.pontuacao += 10 * self.nivel_atual
        self.questoes_corretas += 1
        if self.questoes_corretas % 3 == 0:  # Sobe de nível a cada 3 respostas corretas
            self.nivel_atual += 1
            self.nivel_dificuldade += 1
            # Adiciona tempo extra ao subir de nível
            self.tempo_restante += self.nivel_atual * 10

    def usar_power_up(self, tipo):
        """Aplica o efeito do Power-Up."""
        if self.power_ups[tipo] > 0:
            if tipo == "mais_tempo":
                self.tempo_restante += 10
            elif tipo == "mais_pontos":
                self.pontuacao += 50
            elif tipo == "pular_questao":
                return True  # Indica que a questão deve ser pulada
            self.power_ups[tipo] -= 1
        else:
            flash(f"Você não tem mais o Power-Up: {tipo}", "error")
        return False


jogo = Jogo()


@app.route("/")
def index():
    """Página inicial e principal do jogo."""
    global jogo
    if not jogo.jogo_ativo:
        jogo = Jogo()

    status = jogo.status_jogo()
    questao, respostas, jogo.resposta_correta = jogo.gerar_questao()

    return render_template("index.html", status=status, questao=questao, respostas=respostas)


@app.route("/responder", methods=["POST"])
def responder():
    """Rota que processa a resposta do jogador."""
    global jogo
    resposta_jogador = request.form["escolha"]

    if float(resposta_jogador) == jogo.resposta_correta:
        flash("Resposta correta! 🎉", "success")
        jogo.atualizar_pontuacao()
    else:
        flash(f"Resposta incorreta! A correta era {jogo.resposta_correta} 😞", "error")
        jogo.tempo_restante -= 10  # Penalidade por resposta errada

    if jogo.tempo_restante <= 0:
        return redirect(url_for("fim_do_jogo"))

    return redirect(url_for("index"))


@app.route("/power-up", methods=["POST"])
def power_up():
    """Rota que processa o uso de Power-Ups."""
    global jogo
    tipo_power_up = request.form["tipo"]

    if jogo.usar_power_up(tipo_power_up):
        if tipo_power_up == "pular_questao":
            flash("Você pulou a questão!", "info")

    return redirect(url_for("index"))


@app.route("/fim")
def fim_do_jogo():
    """Rota que exibe a tela final de pontuação."""
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
