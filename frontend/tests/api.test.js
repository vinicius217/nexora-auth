import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { runInNewContext } from "node:vm";

const source = readFileSync(new URL("../public/js/api.js", import.meta.url), "utf8");
const response = (status, data = {}) => ({ status, ok: status < 400, json: async () => data });
function client(fetch) {
  const context = { fetch };
  runInNewContext(source, context);
  return context;
}

test("requisições simultâneas compartilham uma renovação", async () => {
  let refreshed = false;
  let refreshCount = 0;
  const api = client(async (path) => {
    if (path === "/auth/refresh") {
      refreshCount++;
      await new Promise((resolve) => setTimeout(resolve, 5));
      refreshed = true;
      return response(200);
    }
    return refreshed ? response(200, { nome: "Teste" }) : response(401);
  });
  const users = await Promise.all([api.getMe(), api.getMe()]);
  assert.equal(refreshCount, 1);
  assert.ok(users.every((user) => user.nome === "Teste"));
});

test("sessão expirada retorna null sem repetir indefinidamente", async () => {
  let calls = 0;
  const api = client(async () => { calls++; return response(401); });
  assert.equal(await api.getMe(), null);
  assert.equal(calls, 2);
});

test("falha de rede não é tratada como sessão expirada", async () => {
  const api = client(async () => { throw new TypeError("Failed to fetch"); });
  await assert.rejects(api.getMe(), /Verifique sua conexão/);
});

test("erros de validação exibem mensagens legíveis", async () => {
  const api = client(async () => response(422, { detail: [{ msg: "Nome inválido" }] }));
  await assert.rejects(api.chamarApi("/auth/registrar"), { message: "Nome inválido", status: 422 });
});

test("credenciais incorretas não provocam renovação", async () => {
  let calls = 0;
  const api = client(async () => { calls++; return response(401); });
  await assert.rejects(api.chamarApi("/auth/login", { method: "POST" }));
  assert.equal(calls, 1);
});
