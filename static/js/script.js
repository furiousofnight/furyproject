document.addEventListener("DOMContentLoaded", () => {
  console.log("✨ Jogo iniciado! Preparando interface...");

  // Elementos da página a serem manipulados
  const perguntaContainer = document.querySelector(".pergunta");
  const respostaInput = document.querySelector("#resposta");
  const enviarResposta = document.querySelector("#botao-resposta");
  const statusContainer = document.querySelector(".status");
  const mensagemContainer = document.querySelector(".mensagem");

  // Função para carregar dinâmica do jogo (nova pergunta, pontuação e status)
  function atualizarEstadoJogo() {
    fetch("/jogar", { method: "GET" })
      .then((res) => res.json())
      .then((data) => {
        if (data.fim_de_jogo) {
          window.location.href = "/fim"; // Redireciona para a página final
          return;
        }

        // Atualiza a UI com os dados do backend
        perguntaContainer.textContent = data.pergunta_atual;
        statusContainer.innerHTML = `
          Pontuação: <span>${data.pontuacao}</span> |
          Nível: <span>${data.nivel}</span> |
          Perguntas Respondidas: <span>${data.perguntas_respondidas}</span>
        `;
        respostaInput.value = ""; // Limpa o campo de resposta
        mensagemContainer.textContent = ""; // Limpa mensagens anteriores
      })
      .catch((err) => console.error("Erro ao atualizar estado do jogo:", err));
  }

  // Processar resposta do jogador
  enviarResposta.addEventListener("click", () => {
    const resposta = respostaInput.value.trim();

    if (!resposta) {
      mensagemContainer.textContent = "⚠️ Por favor, insira uma resposta!";
      mensagemContainer.classList.remove("sucesso", "erro");
      mensagemContainer.classList.add("aviso");
      return;
    }

    fetch("/responder", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ resposta: resposta }), // Envia a resposta ao backend
    })
      .then((res) => res.json())
      .then((data) => {
        // Exibe o feedback do backend
        mensagemContainer.textContent = data.mensagem;
        mensagemContainer.classList.remove("sucesso", "erro", "aviso");
        mensagemContainer.classList.add(data.correta ? "sucesso" : "erro");

        // Atualiza estado do jogo após a resposta
        atualizarEstadoJogo();
      })
      .catch((err) => console.error("Erro ao enviar resposta:", err));
  });

  // Inicializa o estado do jogo ao carregar a página
  atualizarEstadoJogo();
});