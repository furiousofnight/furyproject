document.addEventListener("DOMContentLoaded", () => {
  console.log("✨ Jogo iniciado! Preparando interface...");

  // Elementos da página a serem manipulados
  const perguntaContainer = document.querySelector(".pergunta");
  const respostaInput = document.querySelector("#resposta");
  const enviarResposta = document.querySelector("#botao-resposta");
  const statusContainer = document.querySelector(".status");
  const mensagemContainer = document.querySelector(".mensagem");
  const botaoTenteNovamente = document.querySelector("#botao-reiniciar");
  const contadorElemento = document.getElementById("contador-tempo"); // Elemento do contador
  let tempoRestante = contadorElemento
    ? parseInt(contadorElemento.dataset.tempo, 10)
    : 30; // Tempo inicial vindo do dataset ou default

  // Atualiza o contador de tempo
  function atualizarContador() {
    if (tempoRestante > 0) {
      contadorElemento.textContent = `Tempo restante: ${tempoRestante}s`;

      if (tempoRestante <= 5) {
        // Altera a cor do contador quando há pouco tempo restante
        contadorElemento.classList.add("alerta");
      }

      tempoRestante--;
    } else {
      contadorElemento.textContent = "Tempo esgotado!";
      contadorElemento.classList.remove("alerta");
      contadorElemento.classList.add("esgotado");

      // Para de atualizar o contador e redireciona para o fim do jogo
      clearInterval(intervaloContador);
      window.location.href = "/fim"; // Redireciona automaticamente
    }
  }

  // Configura intervalo do contador
  const intervaloContador = setInterval(atualizarContador, 1000);

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

  // Processar reinício do jogo quando o botão "Tente novamente" for clicado
  if (botaoTenteNovamente) {
    botaoTenteNovamente.addEventListener("click", () => {
      fetch("/reiniciar", { method: "POST" }) // Faz a requisição ao backend
        .then((res) => {
          if (res.ok) {
            console.log("🔄 Jogo reiniciado!");
            atualizarEstadoJogo(); // Atualiza a interface após reiniciar o jogo
          } else {
            console.error("❌ Erro ao tentar reiniciar o jogo.");
          }
        })
        .catch((err) => console.error("Erro ao reiniciar o jogo:", err));
    });
  } else {
    console.warn("⚠️ Botão 'Tente novamente' não encontrado na página.");
  }

  // Inicializa o estado do jogo ao carregar a página
  atualizarEstadoJogo();
});