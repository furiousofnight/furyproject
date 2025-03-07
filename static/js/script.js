document.addEventListener("DOMContentLoaded", () => {
  console.log("✨ Jogo iniciado! Preparando interface...");

  // Elementos da página a serem manipulados
  const perguntaContainer = document.querySelector(".pergunta");
  const respostaInput = document.querySelector("#resposta");
  const enviarResposta = document.querySelector("#botao-resposta");
  const statusContainer = document.querySelector(".status");
  const mensagemContainer = document.querySelector(".mensagem");
  const botaoTenteNovamente = document.querySelector("#botao-reiniciar");
  const contadorElemento = document.getElementById("contador-tempo");
  const botaoPowerUpTempoExtra = document.querySelector("#powerup-tempo-extra");

  // Tempo inicial e configuração do temporizador
  let tempoRestante = contadorElemento
    ? parseInt(contadorElemento.dataset.tempo, 10)
    : 30;

  // Função para atualizar o contador de tempo
  function atualizarContador() {
    if (tempoRestante > 0) {
      contadorElemento.textContent = `⏳ Tempo restante: ${tempoRestante}s`;

      if (tempoRestante <= 5) {
        contadorElemento.classList.add("alerta");
      }

      tempoRestante--;
    } else {
      contadorElemento.textContent = "⏰ Tempo esgotado!";
      contadorElemento.classList.remove("alerta");
      contadorElemento.classList.add("esgotado");

      // Cancela o intervalo e redireciona para a página de fim de jogo
      clearInterval(intervaloContador);
      window.location.href = "/fim";
    }
  }

  // Configuração do intervalo do contador
  const intervaloContador = setInterval(atualizarContador, 1000);

  // Função para carregar o estado do jogo
  function atualizarEstadoJogo() {
    mensagemContainer.textContent = "🔄 Carregando próxima pergunta...";
    mensagemContainer.classList.remove("sucesso", "erro", "aviso");
    mensagemContainer.classList.add("aviso");

    fetch("/jogar", { method: "GET" })
      .then((res) => res.json())
      .then((data) => {
        if (data.fim_de_jogo) {
          window.location.href = "/fim";
          return;
        }

        // Atualiza os elementos do jogo com os novos dados
        perguntaContainer.textContent = data.pergunta_atual;
        statusContainer.innerHTML = `
          Pontuação: <span>${data.pontuacao}</span> |
          Nível: <span>${data.nivel}</span> |
          Perguntas Respondidas: <span>${data.perguntas_respondidas}</span>
        `;
        respostaInput.value = "";
        mensagemContainer.textContent = "";
      })
      .catch((err) => {
        console.error("Erro ao atualizar o estado do jogo:", err);
        mensagemContainer.textContent = "⚠️ Erro ao carregar a próxima pergunta. Tente novamente!";
        mensagemContainer.classList.add("erro");
      });
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

    // Desabilita o botão enquanto processa a solicitação
    enviarResposta.disabled = true;
    mensagemContainer.textContent = "🔄 Verificando resposta...";
    mensagemContainer.classList.remove("sucesso", "erro", "aviso");
    mensagemContainer.classList.add("aviso");

    fetch("/responder", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ resposta: resposta }),
    })
      .then((res) => res.json())
      .then((data) => {
        mensagemContainer.textContent = data.mensagem;
        mensagemContainer.classList.remove("sucesso", "erro", "aviso");
        mensagemContainer.classList.add(data.correta ? "sucesso" : "erro");

        if (data.correta) {
          atualizarEstadoJogo();
        }
      })
      .catch((err) => {
        console.error("Erro ao enviar resposta:", err);
        mensagemContainer.textContent = "⚠️ Erro ao enviar resposta. Tente novamente!";
        mensagemContainer.classList.add("erro");
      })
      .finally(() => {
        enviarResposta.disabled = false;
      });
  });

  // Reiniciar Jogo
  if (botaoTenteNovamente) {
    botaoTenteNovamente.addEventListener("click", () => {
      mensagemContainer.textContent = "🔄 Reiniciando o jogo...";
      mensagemContainer.classList.remove("sucesso", "erro", "aviso");
      mensagemContainer.classList.add("aviso");

      fetch("/reiniciar", { method: "POST" })
        .then((res) => {
          if (res.ok) {
            atualizarEstadoJogo();
          } else {
            mensagemContainer.textContent = "⚠️ Não foi possível reiniciar o jogo!";
            mensagemContainer.classList.add("erro");
          }
        })
        .catch((err) => {
          console.error("Erro ao reiniciar o jogo:", err);
          mensagemContainer.textContent = "⚠️ Erro ao reiniciar o jogo.";
          mensagemContainer.classList.add("erro");
        });
    });
  }

  // Power-Up: Tempo Extra
  if (botaoPowerUpTempoExtra) {
    botaoPowerUpTempoExtra.addEventListener("click", () => {
      mensagemContainer.textContent = "🔄 Ativando Power-Up: Tempo Extra...";
      mensagemContainer.classList.remove("sucesso", "erro", "aviso");
      mensagemContainer.classList.add("aviso");

      fetch("/power_up/tempo_extra", { method: "POST" })
        .then((res) => res.json())
        .then((data) => {
          if (data.erro) {
            mensagemContainer.textContent = `⚠️ ${data.erro}`;
            mensagemContainer.classList.add("erro");
          } else {
            tempoRestante += 10; // Incrementa tempo no contador
            mensagemContainer.textContent = data.mensagem;
            mensagemContainer.classList.add("sucesso");
          }
        })
        .catch((err) => {
          console.error("Erro ao ativar Power-Up de Tempo Extra:", err);
          mensagemContainer.textContent = "⚠️ Erro ao ativar Power-Up.";
          mensagemContainer.classList.add("erro");
        });
    });
  }

  // Carregar o estado inicial do jogo
  atualizarEstadoJogo();
});