// @ts-check
import { defineConfig } from "astro/config";

export default defineConfig({
  site: "https://hanneseh.github.io",
  base: "/ME-CFS-Research-Summaries",
  output: "static",
  outDir: "./dist",
  publicDir: "./static",
  trailingSlash: "always",
  build: { format: "directory" },
  devToolbar: { enabled: false },
});
