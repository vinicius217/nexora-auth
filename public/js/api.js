const API_BASE = "";
let renovacaoPendente = null;
async function chamarApi(path, options = {}, tentarRenovar = true) {
  let resposta;
  try {
    resposta = await fetch(API_BASE + path, {
    credentials: "include",
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    });
  } catch {
    throw new Error("Não foi possível conectar. Verifique sua conexão e tente novamente.");
  }
  const protegida = path === "/auth/me" || path === "/auth/alterar-senha" || path.startsWith("/auth/sessoes");
  if (resposta.status === 401 && protegida && tentarRenovar) {
    if (!renovacaoPendente) {
      renovacaoPendente = chamarApi("/auth/refresh", { method: "POST" }, false)
        .finally(() => { renovacaoPendente = null; });
    }
    await renovacaoPendente;
    return chamarApi(path, options, false);
  }
  const dados = await resposta.json().catch(() => ({}));
  if (!resposta.ok) {
    const detalhe = dados.detail || dados.message;
    const texto = Array.isArray(detalhe)
      ? detalhe.map((erro) => erro.msg).filter(Boolean).join(" ")
      : typeof detalhe === "string" ? detalhe : "";
    const erro = new Error(texto || "Ocorreu um erro. Tente novamente.");
    erro.status = resposta.status;
    throw erro;
  }
  return dados;
}
function mostrarMensagem(elemento, texto, tipo) {
  elemento.textContent = texto;
  elemento.className = `mensagem ${tipo} show`;
}
function mostrarToast(texto, tipo = "sucesso") {
  const toast = document.createElement("div");
  toast.className = `toast ${tipo}`;
  toast.setAttribute("role", tipo === "erro" ? "alert" : "status");
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
    if (e.status === 401) return null;
    throw e;
  }
}
function logout() {
  return chamarApi("/auth/logout", { method: "POST" }).then(() =>
    location.replace("/index.html"),
  ).catch((erro) => mostrarToast(erro.message, "erro"));
}
