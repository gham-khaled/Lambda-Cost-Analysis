import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv } from "vite";
import { ViteEjsPlugin } from "vite-plugin-ejs";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  console.log("🟢🟢🟢 -  defineConfig -  env:", env);

  const configBase = {
    plugins: [
      react(),
      /**
       * To enable EJS templating in Vite)
       */
      ViteEjsPlugin({
        mode: env.MODE,
      }),
    ],

    define: {
      "process.env": env,
    },
    build: {
      target: "ES2022",
      sourcemap: true,
    },
  };

  return configBase;
});
