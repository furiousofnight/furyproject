import random
import time


class Jogo:
    def __init__(self, nivel_dificuldade="facil", tempo_limite=40):
        self.resposta_correta = None
        self.nivel_dificuldade = 1 if nivel_dificuldade == "facil" else 2
        self.tempo_limite = tempo_limite  # Tempo limite em segundos
        self.pontuacao = 0
        self.nivel_atual = 1
        self.questoes_corretas = 0
        self.power_ups = {"mais_tempo": 1, "mais_pontos": 1, "pular_questao": 1}

    def fim_do_jogo(self):
        """Exibe a mensagem de fim do jogo e a pontuação final."""
        print("\n" + "=" * 40)
        print(" 🎮 FIM DO JOGO! 🎮")
        print("=" * 40)
        print(f"Pontuação final: {self.pontuacao}")
        print(f"Nível atingido: {self.nivel_atual}")
        print(f"📊 Estatísticas: {self.questoes_corretas} questões corretas.")
        print("=" * 40)

    def imprimir_status(self, tempo_restante):
        """Exibe o status atualizado do jogo."""
        print(f"\n⏰ Tempo restante: {int(tempo_restante)} segundos")
        print(f"🔢 Pontuação: {self.pontuacao} | 🏆 Nível: {self.nivel_atual}")
        print(f"Power-ups disponíveis: {self.power_ups}")

    def gerar_questao(self):
        """Gera dinamicamente uma questão com respostas únicas."""
        num1 = random.randint(1, 10 * self.nivel_dificuldade)
        num2 = random.randint(1, 10 * self.nivel_dificuldade)
        operacao = random.choice(["+", "-", "*", "/"])

        questao = f"Quanto é {num1} {operacao} {num2}?"
        try:
            resposta_correta = eval(f"{num1} {operacao} {num2}")
            if operacao == "/":
                resposta_correta = round(resposta_correta, 2)
            self.resposta_correta = resposta_correta
        except ZeroDivisionError:
            return self.gerar_questao()  # Evita divisão por zero

        # Gera respostas únicas
        respostas_erradas = set()
        while len(respostas_erradas) < 3:
            resposta_errada = round(random.uniform(1, 10 * self.nivel_dificuldade), 2)
            if resposta_errada != self.resposta_correta:
                respostas_erradas.add(resposta_errada)

        # Combina a resposta correta com erradas
        respostas = list(respostas_erradas) + [self.resposta_correta]
        random.shuffle(respostas)
        return questao, respostas, self.resposta_correta

    def atualizar_pontuacao(self, resposta_correta):
        """Atualiza pontuação com base no resultado da questão."""
        pontos_base = 10
        if resposta_correta:
            extra = 5 if self.power_ups["mais_pontos"] > 0 else 0
            self.pontuacao += pontos_base + extra
            self.questoes_corretas += 1
        else:
            self.pontuacao = max(0, self.pontuacao - 5)  # Garante que a pontuação não seja negativa

    def verificar_nivel(self):
        """Atualiza o nível e ajusta a dificuldade."""
        pontos_para_evoluir = self.nivel_atual * 50
        if self.questoes_corretas >= 5 and self.pontuacao >= pontos_para_evoluir:
            self.nivel_atual += 1
            self.questoes_corretas = 0
            self.tempo_limite -= 5  # Reduz o tempo como desafio
            print("\n🔥 Você avançou para o NÍVEL", self.nivel_atual)

    def usar_power_up(self, tipo):
        """Permite o uso de power-ups."""
        if tipo == "mais_tempo" and self.power_ups["mais_tempo"] > 0:
            self.tempo_limite += 10
            self.power_ups["mais_tempo"] -= 1
            print("⏳ Power-up ativado: +10 segundos!")
        elif tipo == "mais_pontos" and self.power_ups["mais_pontos"] > 0:
            print("⭐ Power-up ativado! Pontuação aumentada!")
            self.power_ups["mais_pontos"] -= 1
        elif tipo == "pular_questao" and self.power_ups["pular_questao"] > 0:
            self.power_ups["pular_questao"] -= 1
            print("➡ Power-up ativado: Questão pulada!")
            return True
        else:
            print("❌ Power-up indisponível!")
        return False


def obter_escolha_usuario(qtd_opcoes, mensagem="Escolha: "):
    """Obtém a entrada do utilizador e valida-a."""
    while True:
        try:
            escolha = int(input(mensagem))
            if 1 <= escolha <= qtd_opcoes:
                return escolha
            else:
                print("⚠ Entrada fora do intervalo.")
        except ValueError:
            print("⚠ Entrada inválida, use apenas números.")


def main() -> None:
    """Loop principal do jogo."""
    jogo = Jogo("facil", 40)
    print("\n🎉 Bem-vindo ao Jogo Matemático! 🎉\n")

    inicio = time.time()

    while True:
        tempo_restante = jogo.tempo_limite - (time.time() - inicio)
        if tempo_restante <= 0:
            print("\n⏰ Tempo esgotado!")
            jogo.fim_do_jogo()
            break

        jogo.imprimir_status(tempo_restante)

        # Gera a questão e as respostas
        questao, respostas, resposta_correta = jogo.gerar_questao()
        print(f"\n{questao}")
        for i, resposta in enumerate(respostas, 1):
            print(f"{i}. {resposta}")

        # Obtém a escolha do utilizador
        escolha = obter_escolha_usuario(len(respostas) + 1, "Escolha uma resposta (1-4) ou 5 para usar power-ups: ")

        if escolha == 5:
            power_up = input("Escolha o power-up: mais_tempo, mais_pontos ou pular_questao: ").strip()
            if power_up in ["mais_tempo", "mais_pontos", "pular_questao"]:
                if jogo.usar_power_up(power_up):
                    continue  # Se pulou a questão, volta ao início do loop
            else:
                print("⚠ Power-up inválido! Tente um válido.")
        elif isinstance(respostas[escolha - 1], (int, float)) and respostas[escolha - 1] == resposta_correta:
            print("✅ Resposta correta!")
            jogo.atualizar_pontuacao(True)
        else:
            print(f"❌ Resposta incorreta! A resposta correta era {resposta_correta}")
            jogo.atualizar_pontuacao(False)

        jogo.verificar_nivel()

    jogo.fim_do_jogo()


if __name__ == "__main__":
    main()
