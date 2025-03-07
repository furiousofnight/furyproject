document.addEventListener("DOMContentLoaded", () => {
    // Gerencia o tempo restante no jogo
    const iniciarContagemTempo = () => {
        const tempoRestanteEl = document.getElementById("tempo-restante");

        if (tempoRestanteEl) {
            let tempoAtual = parseInt(tempoRestanteEl.textContent, 10);

            const atualizarTempo = () => {
                if (tempoAtual > 0) {
                    tempoAtual--;
                    tempoRestanteEl.textContent = tempoAtual;
                } else {
                    clearInterval(intervalo); // Para o intervalo da contagem
                    alert("⏰ Tempo esgotado! Você será redirecionado para o Fim do Jogo.");
                    window.location.replace("/fim"); // Redireciona para a página de fim do jogo
                }
            };

            // Define o intervalo para atualizar o tempo a cada 1 segundo
            const intervalo = setInterval(atualizarTempo, 1000);
        }
    };

    // Oculta mensagens flash após um tempo configurado
    const ocultarMensagensFlash = () => {
        const flashMessages = document.querySelector(".flash-messages");
        if (flashMessages) {
            // Aguarda 5 segundos antes de iniciar a transição de saída
            setTimeout(() => {
                flashMessages.style.transition = "opacity 0.5s ease"; // Animação suave
                flashMessages.style.opacity = "0"; // Torna o elemento invisível

                // Remove o elemento completamente após a animação
                setTimeout(() => {
                    flashMessages.remove();
                }, 500); // Match do tempo da transição
            }, 5000); // 5 segundos visíveis antes de iniciar a remoção
        }
    };

    // Inicializa as funcionalidades
    iniciarContagemTempo();
    ocultarMensagensFlash();
});