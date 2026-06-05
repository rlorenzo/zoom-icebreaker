import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "jsdom",
    include: ["tests/**/*.test.js"],
    coverage: {
      // Istanbul provider so coverage/coverage-final.json is emitted in the
      // format fallow's --coverage flag consumes for accurate CRAP scoring.
      provider: "istanbul",
      include: ["app.js", "roster.js"],
      reporter: ["text", "json"],
      reportsDirectory: "coverage",
    },
  },
});
