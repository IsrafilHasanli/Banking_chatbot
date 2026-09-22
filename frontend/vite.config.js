import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "node:path";

export default defineConfig({
  base: "/ui/",
  plugins: [react()],
  server: {
    proxy: {
      "/auth": "http://127.0.0.1:8000",
      "/chat": "http://127.0.0.1:8000",
      "/profile": "http://127.0.0.1:8000",
      "/product": "http://127.0.0.1:8000"
    }
  },
  build: {
    outDir: resolve(__dirname, "../app/static/chatbot"),
    emptyOutDir: true
  }
});
