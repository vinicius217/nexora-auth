import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { resolve } from "node:path";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  define: { "process.env.NODE_ENV": JSON.stringify("production") },
  publicDir: false,
  resolve: { alias: { "@": resolve(import.meta.dirname, "src") } },
  build: {
    outDir: "public/assets",
    emptyOutDir: true,
    lib: { entry: resolve(import.meta.dirname, "src/main.tsx"), formats: ["es"], fileName: () => "login-button.js" },
    cssCodeSplit: false,
    rollupOptions: { output: { assetFileNames: "login-button.[ext]" } }
  }
});
