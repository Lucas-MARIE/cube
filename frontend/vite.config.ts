// ============================================================
// Cube.com Frontend - Vite Configuration
// Configures React plugin and API proxy to the gateway.
// ============================================================

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],

  // Path alias so imports can use @/ prefix
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },

  server: {
    host: "0.0.0.0",
    port: process.env.PORT ? parseInt(process.env.PORT, 10) : 3000,
    strictPort: true,
    // Proxy API requests to the Nginx gateway during development
    proxy: {
      "/api": {
        target: "http://localhost:8080",
        changeOrigin: true,
        // WebSocket support for session-service real-time features
        ws: true,
      },
    },
  },

  build: {
    // Output directory for production build
    outDir: "dist",
    sourcemap: false,
  },
});
