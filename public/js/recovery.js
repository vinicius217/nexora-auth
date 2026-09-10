(() => {
  const $ = (id) => document.getElementById(id);
  const resetToken = new URLSearchParams(location.search).get("token");
  const form = $("form");
  const resetForm = $("resetForm");
  const message = $("mensagem");
  function heading(title, description) {
    $("titulo").textContent = title;
    $("descricao").textContent = description;
    $("titulo").tabIndex = -1;
    $("titulo").focus();
    message.className = "mensagem";
    message.textContent = "";
  }
  if (resetToken) {
    form.hidden = true;
    resetForm.hidden = false;
    heading("Crie uma nova senha", "Escolha sua nova senha e confirme abaixo para recuperar o acesso.");
  }
  $("requestAgain").addEventListener("click", () => {
    $("sentState").hidden = true;
    form.hidden = false;
    heading("Esqueceu sua senha?", "Informe o e-mail da sua conta para solicitar um novo link.");
    $("email").focus();
  });
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if ($("btn").disabled) return;
    setLoading($("btn"), true, "Enviando...");
    try {
      const result = await chamarApi("/auth/esqueci-senha", {
        method: "POST", body: JSON.stringify({ email: $("email").value.trim() }),
      });
      form.hidden = true;
      $("sentState").hidden = false;
      heading("Confira seu e-mail", "O próximo passo está na sua caixa de entrada.");
      $("devLink").hidden = !result.dev_token;
      if (result.dev_token) {
        $("devLink").href = `/recuperar.html?token=${encodeURIComponent(result.dev_token)}`;
        mostrarMensagem(message, "Modo de desenvolvimento: nenhum e-mail foi enviado. Use o link abaixo para continuar.", "sucesso");
      }
    } catch (error) {
      mostrarMensagem(message, error.message, "erro");
    } finally {
      setLoading($("btn"), false);
    }
  });
  const confirm = $("confirmarSenha");
  function validateConfirmation() {
    confirm.setCustomValidity(confirm.value === $("novaSenha").value ? "" : "As senhas precisam ser iguais.");
  }
  confirm.addEventListener("input", validateConfirmation);
  $("novaSenha").addEventListener("input", validateConfirmation);
  resetForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    validateConfirmation();
    if (!resetForm.reportValidity() || $("resetBtn").disabled) return;
    setLoading($("resetBtn"), true, "Atualizando...");
    try {
      await chamarApi("/auth/resetar-senha", {
        method: "POST", body: JSON.stringify({ token: resetToken, nova_senha: $("novaSenha").value }),
      });
      resetForm.hidden = true;
      resetForm.reset();
      history.replaceState(null, "", "/recuperar.html");
      heading("Senha atualizada!", "Tudo pronto. Volte para o login e entre com sua nova senha.");
      mostrarMensagem(message, "Sua senha foi redefinida com sucesso.", "sucesso");
    } catch (error) {
      mostrarMensagem(message, error.status === 400 ? "Este link é inválido ou expirou. Solicite outro link abaixo." : error.message, "erro");
    } finally {
      setLoading($("resetBtn"), false);
    }
  });
})();
