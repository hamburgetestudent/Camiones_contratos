import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT_DIR = path.resolve(__dirname, "..");
const isWindows = process.platform === "win32";

/**
 * Busca el ejecutable de Python priorizando los entornos virtuales locales (.venv / venv).
 */
export function resolvePythonExecutable(rootDir = ROOT_DIR) {
  const candidates = isWindows
    ? [
        path.join(rootDir, ".venv", "Scripts", "python.exe"),
        path.join(rootDir, "venv", "Scripts", "python.exe"),
      ]
    : [
        path.join(rootDir, ".venv", "bin", "python"),
        path.join(rootDir, "venv", "bin", "python"),
      ];

  for (const candidate of candidates) {
    if (fs.existsSync(candidate)) {
      return candidate;
    }
  }
  return isWindows ? "python" : "python3";
}

if (
  process.argv[1] &&
  import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href
) {
  const args = process.argv.slice(2);
  const pythonExe = resolvePythonExecutable();
  const result = spawnSync(pythonExe, args, {
    cwd: ROOT_DIR,
    stdio: "inherit",
  });
  process.exit(result.status ?? 1);
}
