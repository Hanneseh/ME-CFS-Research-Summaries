import { defineConfig } from "vitest/config";
import path from "path";

export default defineConfig({
  test: {
    environment: "node",
    include: ["test/**/*.test.ts"],
    reporters: ["default"],
    alias: {
      "./styles/explorer.scss": path.resolve(__dirname, "test/__mocks__/styleMock.ts"),
      "./scripts/explorer.inline.ts": path.resolve(__dirname, "test/__mocks__/scriptMock.ts"),
    },
  },
  esbuild: {
    jsx: "automatic",
    jsxImportSource: "preact",
  },
});
