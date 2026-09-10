import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { runInNewContext } from "node:vm";

const source = readFileSync(new URL("../public/js/recovery.js", import.meta.url), "utf8");
function page(search = "", result = {}) {
  const elements = new Map();
  const calls = [];
  function get(id) {
    if (!elements.has(id)) elements.set(id, {
      hidden: ["resetForm", "sentState", "devLink"].includes(id),
      value: "", disabled: false, handlers: {},
      addEventListener(name, handler) { this.handlers[name] = handler; },
      focus() {}, setCustomValidity(message) { this.validation = message; },
      reportValidity() { return !get("confirmarSenha").validation; }, reset() {},
    });
    return elements.get(id);
  }
  runInNewContext(source, {
    document: { getElementById: get }, location: { search }, URLSearchParams,
    history: { replaceState() {} },
    chamarApi: async (path, options) => { calls.push({ path, body: JSON.parse(options.body) }); return result; },
    setLoading: (button, loading) => { button.disabled = loading; },
    mostrarMensagem: (element, text) => { element.textContent = text; },
  });
  return { get, calls, submit: (id) => get(id).handlers.submit({ preventDefault() {} }) };
}

test("pedido de recuperação exibe instruções sem abrir redefinição", async () => {
  const p = page();
  p.get("email").value = " pessoa@example.com ";
  await p.submit("form");
  assert.equal(p.get("sentState").hidden, false);
  assert.equal(p.get("resetForm").hidden, true);
  assert.equal(p.get("devLink").hidden, true);
  assert.equal(p.calls[0].body.email, "pessoa@example.com");
  p.get("requestAgain").handlers.click();
  assert.equal(p.get("form").hidden, false);
});

test("link de desenvolvimento aparece somente quando a API retorna token", async () => {
  const p = page("", { dev_token: "test-token" });
  await p.submit("form");
  assert.equal(p.get("devLink").hidden, false);
  assert.equal(p.get("devLink").href, "/recuperar.html?token=test-token");
});

test("redefinição exige senhas iguais e envia o token do link", async () => {
  const p = page("?token=reset-test");
  assert.equal(p.get("form").hidden, true);
  assert.equal(p.get("resetForm").hidden, false);
  p.get("novaSenha").value = "NovaSenha123!";
  p.get("confirmarSenha").value = "Diferente123!";
  await p.submit("resetForm");
  assert.equal(p.calls.length, 0);
  p.get("confirmarSenha").value = "NovaSenha123!";
  await p.submit("resetForm");
  assert.equal(p.calls[0].body.token, "reset-test");
  assert.equal(p.get("resetForm").hidden, true);
  assert.equal(p.get("titulo").textContent, "Senha atualizada!");
});
