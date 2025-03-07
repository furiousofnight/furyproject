document.addEventListener("DOMContentLoaded", () => {
    // Função para gerenciar o tempo restante no jogo
    const iniciarContagemTempo = () => {
        const tempoRestanteEl = document.getElementById("tempo-restante");

        if (tempoRestanteEl) {
            let tempoAtual = parseInt(tempoRestanteEl.textContent, 10);

            const atualizarTempo = () => {
                if (tempoAtual > 0) {
                    tempoAtual--;
                    tempoRestanteEl.textContent = tempoAtual;
                } else {
                    clearInterval(intervalo);
                    alert("⏰ Tempo esgotado! Você será redirecionado para o Fim do Jogo.");
                    window.location.replace("/fim"); // Redireciona para a tela final
                }
            };

            // Atualiza o tempo a cada 1 segundo
            const intervalo = setInterval(atualizarTempo, 1000);
        }
    };

    // Função para ocultar mensagens flash após um tempo
    const ocultarMensagensFlash = () => {
        const flashMessages = document.querySelector(".flash-messages");
        if (flashMessages) {
            setTimeout(() => {
                flashMessages.style.transition = "opacity 0.5s ease";
                flashMessages.style.opacity = "0";

                // Remove o elemento após a animação de saída
                setTimeout(() => {
                    flashMessages.remove();
                }, 500); // Tempo para completar a transição
            }, 5000); // Visível por 5 segundos
        }
    };

    // Inicialização das funcionalidades
    iniciarContagemTempo();
    ocultarMensagensFlash();
});