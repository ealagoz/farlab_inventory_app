import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0", // Allow external connections
    port: 5173, // Use Vite's default port
    strictPort: true, // Exit if port is already in use
    watch: {
      usePolling: true, // Fix for Docker file watching
    },
    hmr: {
      // Use direct connection to Vite for HMR (bypasses nginx)
      port: 5173,
      host: 'localhost',
    },
  },
  preview: {
    host: "0.0.0.0",
    port: 3000, // For production preview
  },
});
