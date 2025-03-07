document.addEventListener("DOMContentLoaded", () => {
    // Atualiza dinamicamente o tempo restante no jogo
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

        const intervalo = setInterval(atualizarTempo, 1000);
    }

    // Ocultação automática de mensagens flash
    const flashMessages = document.querySelector(".flash-messages");
    if (flashMessages) {
        setTimeout(() => {
            flashMessages.style.transition = "opacity 0.5s ease";
            flashMessages.style.opacity = "0";

            // Remove o elemento após a animação
            setTimeout(() => {
                if (flashMessages.parentNode) {
                    flashMessages.parentNode.removeChild(flashMessages);
                }
            }, 500); // Aguarda a transição terminar
        }, 5000); // Mensagens visíveis por 5 segundos
    }
});