const API_BASE = "";
async function chamarApi(path, options = {}) {
  const resposta = await fetch(API_BASE + path, { credentials: "include", ...options, headers: { "Content-Type": "application/json", ...(options.headers || {}) } });
  const dados = await resposta.json().catch(() => ({}));
  if (!resposta.ok) throw new Error(dados.detail || dados.message || "Ocorreu um erro. Tente novamente.");
  return dados;
}
function mostrarMensagem(el, texto, tipo) { el.textContent = texto; el.className = `mensagem ${tipo} show`; }
function mostrarToast(texto, tipo="sucesso") { const t=document.createElement("div"); t.className=`toast ${tipo}`; t.textContent=texto; document.body.appendChild(t); requestAnimationFrame(()=>t.classList.add("visible")); setTimeout(()=>{t.classList.remove("visible");setTimeout(()=>t.remove(),300)},3500); }
function setLoading(btn, loading, label="Processando...") { btn.disabled=loading; if(loading){btn.dataset.label=btn.textContent;btn.innerHTML='<span class="spinner"></span>'+label}else btn.textContent=btn.dataset.label||btn.textContent; }
function togglePassword(inputId, button) { const i=document.getElementById(inputId); const hidden=i.type==="password"; i.type=hidden?"text":"password"; button.textContent=hidden?"◌":"◉"; button.setAttribute("aria-label",hidden?"Ocultar senha":"Mostrar senha"); }
async function getMe(){ try{return await chamarApi("/auth/me")}catch(e){ if(e.message.includes("Sessão")||e.message.includes("credenciais")){try{return await chamarApi("/auth/refresh",{method:"POST"}) && await chamarApi("/auth/me")}catch{return null}} return null }}
function logout(){ return chamarApi("/auth/logout",{method:"POST"}).finally(()=>location.replace("/index.html")); }
