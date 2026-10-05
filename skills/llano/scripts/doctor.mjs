#!/usr/bin/env node
// llano doctor: checks config, language packs, installs and activation.
//
// Usage:
//   node doctor.mjs                 full report
//   node doctor.mjs --hook          SessionStart hook: inject activation, warn on problems
//   node doctor.mjs --init          create the config file with defaults
//   node doctor.mjs --set k=v ...   change config values (mode, lang)
//   node doctor.mjs --install-hook  add the SessionStart hook to ~/.claude/settings.json
//   node doctor.mjs --uninstall-hook

import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";

const SKILL_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const SCRIPT = path.join(SKILL_DIR, "scripts", "doctor.mjs");
const HOME = os.homedir();
const CONFIG = process.env.LLANO_CONFIG || path.join(HOME, ".config", "llano", "config.json");
const SETTINGS = path.join(HOME, ".claude", "settings.json");
const MODES = ["explain", "responses", "all", "off"];
const DEFAULTS = { mode: "responses", lang: "es" };
const PACK_FILES = ["rules.md", "dictionary.md", "examples.md"];
const STYLE_CONFLICTS = ["caveman"];
const isLlanoHook = (cmd) => /llano.*doctor\.mjs"?\s+--hook/.test(String(cmd ?? ""));

const readJson = (p) => JSON.parse(fs.readFileSync(p, "utf8"));
const exists = (p) => fs.existsSync(p);
const hash = (p) => crypto.createHash("sha1").update(fs.readFileSync(p)).digest("hex").slice(0, 8);

function languages() {
  const dir = path.join(SKILL_DIR, "languages");
  if (!exists(dir)) return [];
  return fs.readdirSync(dir, { withFileTypes: true })
    .filter((d) => d.isDirectory() && !d.name.startsWith("_"))
    .map((d) => d.name)
    .sort();
}

function loadConfig() {
  if (!exists(CONFIG)) return { config: { ...DEFAULTS }, error: `config not found: ${CONFIG} (using defaults)` };
  try {
    return { config: { ...DEFAULTS, ...readJson(CONFIG) } };
  } catch (e) {
    return { config: { ...DEFAULTS }, error: `invalid JSON in ${CONFIG}: ${e.message}` };
  }
}

function writeConfig(config) {
  fs.mkdirSync(path.dirname(CONFIG), { recursive: true });
  fs.writeFileSync(CONFIG, JSON.stringify(config, null, 2) + "\n");
}

function hookInstalled() {
  if (!exists(SETTINGS)) return false;
  try {
    return (readJson(SETTINGS).hooks?.SessionStart ?? []).some((g) => (g.hooks ?? []).some((h) => isLlanoHook(h.command)));
  } catch {
    return false;
  }
}

function checks() {
  const results = []; // { level: "ok" | "warn" | "fail", msg }
  const add = (level, msg) => results.push({ level, msg });

  // Config
  const { config, error } = loadConfig();
  if (error) add(exists(CONFIG) ? "fail" : "warn", error);
  else add("ok", `config: ${CONFIG}`);
  if (!MODES.includes(config.mode)) add("fail", `unknown mode "${config.mode}" (valid: ${MODES.join(", ")})`);
  else add("ok", `mode: ${config.mode}`);

  // Language pack
  const langs = languages();
  const packDir = path.join(SKILL_DIR, "languages", config.lang);
  if (!langs.includes(config.lang)) {
    add("fail", `language pack "${config.lang}" not found (available: ${langs.join(", ") || "none"})`);
  } else {
    const missing = PACK_FILES.filter((f) => !exists(path.join(packDir, f)));
    if (missing.length) add("fail", `pack "${config.lang}" is missing: ${missing.join(", ")}`);
    else add("ok", `lang: ${config.lang}`);
  }

  // Installs: more than one copy with different content is a problem
  const candidates = [
    path.join(HOME, ".claude", "skills", "llano"),
    path.join(HOME, ".agents", "skills", "llano"),
    path.join(process.cwd(), ".claude", "skills", "llano"),
    path.join(process.cwd(), ".agents", "skills", "llano"),
  ];
  const installs = [...new Set(candidates.filter((d) => exists(path.join(d, "SKILL.md"))).map((d) => fs.realpathSync(d)))];
  const hashes = new Set(installs.map((d) => hash(path.join(d, "SKILL.md"))));
  if (hashes.size > 1) add("warn", `${installs.length} llano installs with different SKILL.md: ${installs.join(", ")}`);
  else add("ok", `install: ${installs.join(", ") || SKILL_DIR}`);

  // Conflicting style skills
  const skillRoots = [path.join(HOME, ".claude", "skills"), path.join(HOME, ".agents", "skills")];
  const conflicts = skillRoots.flatMap((r) => STYLE_CONFLICTS.map((n) => path.join(r, n))).filter(exists);
  if (conflicts.length) add("warn", `conflicting style skill installed: ${conflicts.join(", ")}`);

  // Activation
  const agentsMd = [path.join(HOME, ".claude", "CLAUDE.md"), path.join(HOME, "AGENTS.md"), path.join(process.cwd(), "AGENTS.md")]
    .filter((p) => exists(p) && /^llano:/m.test(fs.readFileSync(p, "utf8")));
  if (hookInstalled()) add("ok", "activation: SessionStart hook");
  else if (agentsMd.length) add("ok", `activation: ${agentsMd.join(", ")}`);
  else add("warn", "no automatic activation (run --install-hook, or add a `llano:` line to AGENTS.md)");

  return { config, langs, results };
}

function report() {
  const { langs, results } = checks();
  const icon = { ok: "✓", warn: "!", fail: "✗" };
  for (const r of results) console.log(`${icon[r.level]} ${r.msg}`);
  console.log(`  languages available: ${langs.join(", ") || "none"}`);
  process.exitCode = results.some((r) => r.level === "fail") ? 1 : 0;
}

function hook() {
  const { config, results } = checks();
  const problems = results.filter((r) => r.level === "fail");
  const out = { hookSpecificOutput: { hookEventName: "SessionStart" } };
  if (problems.length) {
    out.systemMessage = `llano: ${problems.map((p) => p.msg).join("; ")}. Run: node ${SCRIPT}`;
  }
  if (config.mode !== "off" && !problems.length) {
    out.hookSpecificOutput.additionalContext =
      `llano is active: mode=${config.mode}, lang=${config.lang}. ` +
      `Load the \`llano\` skill now and apply it as its SKILL.md says. ` +
      `Language pack: ${path.join(SKILL_DIR, "languages", config.lang)}. ` +
      `Doctor: node ${SCRIPT}`;
  }
  process.stdout.write(JSON.stringify(out));
}

function set(pairs) {
  const { config } = loadConfig();
  for (const pair of pairs) {
    const [k, v] = pair.split("=");
    if (k === "mode" && !MODES.includes(v)) throw new Error(`unknown mode "${v}" (valid: ${MODES.join(", ")})`);
    if (k === "lang" && !languages().includes(v)) throw new Error(`language pack "${v}" not found (available: ${languages().join(", ")})`);
    if (!["mode", "lang"].includes(k)) throw new Error(`unknown key "${k}" (valid: mode, lang)`);
    config[k] = v;
  }
  writeConfig(config);
  console.log(`llano config: mode=${config.mode}, lang=${config.lang} (${CONFIG})`);
}

function editSettings(fn) {
  const settings = exists(SETTINGS) ? readJson(SETTINGS) : {};
  if (exists(SETTINGS)) fs.copyFileSync(SETTINGS, SETTINGS + ".bak-llano");
  fn(settings);
  fs.mkdirSync(path.dirname(SETTINGS), { recursive: true });
  fs.writeFileSync(SETTINGS, JSON.stringify(settings, null, 2) + "\n");
}

function removeHook(settings) {
  const groups = settings.hooks?.SessionStart;
  if (!groups) return;
  settings.hooks.SessionStart = groups
    .map((g) => ({ ...g, hooks: (g.hooks ?? []).filter((h) => !isLlanoHook(h.command)) }))
    .filter((g) => g.hooks.length);
  if (!settings.hooks.SessionStart.length) delete settings.hooks.SessionStart;
}

function installHook() {
  editSettings((s) => {
    removeHook(s);
    s.hooks ??= {};
    s.hooks.SessionStart ??= [];
    s.hooks.SessionStart.push({ hooks: [{ type: "command", command: `node "${SCRIPT}" --hook` }] });
  });
  if (!exists(CONFIG)) writeConfig(DEFAULTS);
  console.log(`llano: SessionStart hook added to ${SETTINGS} (backup: settings.json.bak-llano)`);
}

const [cmd, ...rest] = process.argv.slice(2);
try {
  switch (cmd) {
    case undefined: report(); break;
    case "--hook": hook(); break;
    case "--init": if (exists(CONFIG)) console.log(`config exists: ${CONFIG}`); else { writeConfig(DEFAULTS); console.log(`created ${CONFIG}`); } break;
    case "--set": set(rest); break;
    case "--install-hook": installHook(); break;
    case "--uninstall-hook": editSettings(removeHook); console.log("llano: SessionStart hook removed"); break;
    default: console.error(`unknown option: ${cmd}`); process.exitCode = 2;
  }
} catch (e) {
  console.error(`llano: ${e.message}`);
  process.exitCode = 1;
}
