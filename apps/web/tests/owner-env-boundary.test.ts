import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import { describe, it } from "vitest";

const banned = [
  "USER_" + "PASSWORD",
  "PASSWORD_" + "RESET_PHRASE",
  "OWNER_" + "PASSWORD",
  "NEXT_PUBLIC_" + "USER_",
  "GET_" + "PASSWORD",
  "USER_" + "NAME",
  "USER_" + "EMAIL",
];

function walk(directory: string): string[] {
  const files: string[] = [];
  for (const entry of readdirSync(directory)) {
    if (entry === "node_modules" || entry === ".next" || entry === "tests") continue;
    const path = join(directory, entry);
    if (statSync(path).isDirectory()) files.push(...walk(path));
    else if (/\.(ts|tsx|js|mjs|css|json)$/.test(entry)) files.push(path);
  }
  return files;
}

describe("frontend owner-secret boundary", () => {
  it("does not embed owner environment variables in application source", () => {
    for (const file of walk(process.cwd())) {
      const text = readFileSync(file, "utf8");
      for (const token of banned) {
        if (text.includes(token)) {
          throw new Error(`Owner environment token found in ${file}`);
        }
      }
    }
  });
});
