const API_BASE = "";
async function chamarApi(path, options = {}) {
  const resposta = await fetch(API_BASE + path, {
    credentials: "include",
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  const dados = await resposta.json().catch(() => ({}));
  if (!resposta.ok)
    throw new Error(
      dados.detail || dados.message || "Ocorreu um erro. Tente novamente.",
    );
  return dados;
}
function mostrarMensagem(elemento, texto, tipo) {
  elemento.textContent = texto;
  elemento.className = `mensagem ${tipo} show`;
}
function mostrarToast(texto, tipo = "sucesso") {
  const toast = document.createElement("div");
  toast.className = `toast ${tipo}`;
  toast.textContent = texto;
  document.body.appendChild(toast);
  requestAnimationFrame(() => toast.classList.add("visible"));
  setTimeout(() => {
    toast.classList.remove("visible");
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}
function setLoading(btn, loading, label = "Processando...") {
  btn.disabled = loading;
  if (btn.classList.contains("react-3d-button")) {
    if (!btn.dataset.label)
      btn.dataset.label = btn.getAttribute("aria-label") || "Entrar na conta";
    btn.classList.toggle("is-loading", loading);
    btn.setAttribute("aria-busy", String(loading));
    btn.setAttribute("aria-label", loading ? label : btn.dataset.label);
    return;
  }
  if (loading) {
    btn.dataset.label = btn.textContent;
    btn.innerHTML = '<span class="spinner"></span>' + label;
  } else btn.textContent = btn.dataset.label || btn.textContent;
}
function togglePassword(inputId, button) {
  const input = document.getElementById(inputId);
  const hidden = input.type === "password";
  input.type = hidden ? "text" : "password";
  button.textContent = hidden ? "◌" : "◉";
  button.setAttribute("aria-label", hidden ? "Ocultar senha" : "Mostrar senha");
}
async function getMe() {
  try {
    return await chamarApi("/auth/me");
  } catch (e) {
    if (e.message.includes("Sessão") || e.message.includes("credenciais")) {
      try {
        return (
          (await chamarApi("/auth/refresh", { method: "POST" })) &&
          (await chamarApi("/auth/me"))
        );
      } catch {
        return null;
      }
    }
    return null;
  }
}
function logout() {
  return chamarApi("/auth/logout", { method: "POST" }).finally(() =>
    location.replace("/index.html"),
  );
}
