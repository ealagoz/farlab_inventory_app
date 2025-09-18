import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// // https://vite.dev/config/
// export default defineConfig({
//   plugins: [react()],
//   server: {
//     host: "0.0.0.0", // Allow external connections
//     port: 5173, // Use Vite's default port
//     strictPort: true, // Exit if port is already in use
//     watch: {
//       usePolling: true, // Fix for Docker file watching
//     },
//     hmr: {
//       // Use direct connection to Vite for HMR (bypasses nginx)
//       port: 5173,
//       host: 'localhost',
//     },
//   },
//   preview: {
//     host: "0.0.0.0",
//     port: 3000, // For production preview
//   },
// });



 /* Minimal and production-safe Vite config for a React SPA served by Nginx.
 * - Uses hashed filenames for long-term caching.
 * - Drops console/debugger in production.
 * - Keeps defaults for CORS (safer than wildcard).
 * - Adds predictable ports and no auto-open (Docker/CI friendly).
 */

export default defineConfig(({ mode }) => {
  /** True when building for production (`vite build`) or running with `--mode production ` */
  const isProduction = mode === 'production';

  return {
    /**
     * Vite plugins:
     * - React plugin adds JSX/TSX transform & Fast Refresh in dev.
     */
    plugins: [react()],

    
    /**
     * Public base path:
     * - Keep "/" when app is served at the domain root by Nginx.
     * - Change if you deploy under a subpath (e.g., "/app/").
     */
    base: '/',


    /**
     * Build options (used by `vite build`):
     * - `outDir`/`assetsDir`: standard dist layout expected by your Nginx.
     * - Hashed filenames -> great with Nginx "immutable" caching.
     * - No source maps in prod to avoid exposing source.
     * - Leave 'cors' unset to inherit safer defaults; only enable if you must load from another origin.
     */
    build: {
      outDir: 'dist',
      assetsDir: 'assets',
      sourcemap: false, // Donot expose source code in production
      minify: 'esbuild', // Fast and safe minification
      target: 'es2020', // Better browser compatibility
      rollupOptions: {
        output: {
          // Hashed filenames for cache busting
          entryFileNames: 'assets/js/[name]-[hash].js',
          chunkFileNames: 'assets/js/[name]-[hash].js',
          assetFileNames: 'assets/[ext]/[name]-[hash][extname]',
        },
      },
    },

    
    /**
     * esbuild options (applies to both dev transforms and prod minify):
     * - Drop console/debugger only in production builds.
     */
    esbuild: {
      drop: isProduction ? ['console', 'debugger'] : [],
      legalComments: 'none', // Remove license comments in production
    },

    
    /**
     * Dev server (`vite`):
     * - `host: '0.0.0.0'` for Docker/VM access.
     * - `strictPort: true` fails fast if the port is taken.
     * - `open: false` is typical for Docker/CI; set `true` locally if desired.
     * - File watching with polling helps in Docker bind mounts.
     * - CORS is left to Vite's safer default (localhost-only). Add a proxy if your API is on another origin.
     */
    server: {
      host: '0.0.0.0',
      port: 5173,
      strictPort: true,
      open: false,
      watch: { usePolling: true },
      proxy: {
        // Adjust if backend is on a different URL
        '/api': {target: 'http://localhost', changeOrigin: true},
        '/docs': { target: 'http://localhost', changeOrigin: true },
        '/openapi.json': { target: 'http://localhost', changeOrigin: true },

      },
    },


    /**
     * Preview server (`vite preview`):
     * - Serves the built `dist` locally for a quick prod-like check.
     * - `strictPort/open` mirror the dev choices for predictability.
     * - Leave `cors` unset to inherit safer defaults; only enable if you must load from another origin.
     */
    preview: {
      host: '0.0.0.0',
      port: 3000,
      strictPort: true,
      open: false, 
    },
  };
});