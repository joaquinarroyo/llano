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
const CWD = process.cwd();
const CONFIG = process.env.LLANO_CONFIG || path.join(HOME, ".config", "llano", "config.json");
const SETTINGS = path.join(HOME, ".claude", "settings.json");
const MODES = ["explain", "responses", "all", "off"];
const DEFAULTS = { mode: "responses", lang: "es" };
const PACK_FILES = ["rules.md", "dictionary.md", "examples.md"];
const STYLE_CONFLICTS = ["caveman"];
const LANG_ID = /^[A-Za-z0-9_-]+$/;
const HOOK_RE = /llano.*doctor\.mjs"?\s+--hook/;
const isLlanoHook = (cmd) => HOOK_RE.test(String(cmd ?? ""));

const readJson = (p) => JSON.parse(fs.readFileSync(p, "utf8"));
const exists = (p) => fs.existsSync(p);

function languages() {
  const dir = path.join(SKILL_DIR, "languages");
  if (!exists(dir)) return [];
  return fs.readdirSync(dir, { withFileTypes: true })
    .filter((d) => d.isDirectory() && !d.name.startsWith("_"))
    .map((d) => d.name)
    .sort();
}

// Hash of every file in an install, so any difference (pack, script, SKILL.md) shows.
function hashDir(dir) {
  const h = crypto.createHash("sha1");
  const walk = (d) => {
    for (const e of fs.readdirSync(d, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) {
      const p = path.join(d, e.name);
      if (e.isDirectory()) walk(p);
      else if (e.isFile()) h.update(path.relative(dir, p)).update(fs.readFileSync(p));
    }
  };
  walk(dir);
  return h.digest("hex").slice(0, 8);
}

function loadConfig() {
  if (!exists(CONFIG)) return { config: { ...DEFAULTS }, missing: true };
  try {
    const raw = readJson(CONFIG);
    if (raw === null || typeof raw !== "object" || Array.isArray(raw)) throw new Error("top level must be an object");
    return { config: { ...DEFAULTS, ...raw } };
  } catch (e) {
    return { config: { ...DEFAULTS }, error: `invalid config ${CONFIG}: ${e.message}` };
  }
}

function writeConfig(config) {
  fs.mkdirSync(path.dirname(CONFIG), { recursive: true });
  fs.writeFileSync(CONFIG, JSON.stringify(config, null, 2) + "\n");
}

// All llano hook commands in the user and project settings files.
function llanoHooks() {
  const files = [
    SETTINGS,
    path.join(HOME, ".claude", "settings.local.json"),
    path.join(CWD, ".claude", "settings.json"),
    path.join(CWD, ".claude", "settings.local.json"),
  ];
  const found = [];
  for (const file of new Set(files)) {
    if (!exists(file)) continue;
    let s;
    try { s = readJson(file); } catch { continue; }
    for (const g of s?.hooks?.SessionStart ?? []) {
      for (const h of g?.hooks ?? []) {
        if (!isLlanoHook(h?.command)) continue;
        const script = String(h.command).match(/"([^"]*doctor\.mjs)"|(\S*doctor\.mjs)/);
        found.push({ file, script: script ? script[1] ?? script[2] : null });
      }
    }
  }
  return found;
}

function checks() {
  const results = []; // { level: "ok" | "warn" | "fail", msg }
  const add = (level, msg) => results.push({ level, msg });

  // Config
  const { config, missing, error } = loadConfig();
  if (error) add("fail", error);
  else if (missing) add("warn", `config not found: ${CONFIG} (using defaults, run --init)`);
  else add("ok", `config: ${CONFIG}`);
  if (!MODES.includes(config.mode)) add("fail", `unknown mode ${JSON.stringify(config.mode)} (valid: ${MODES.join(", ")})`);
  else add("ok", `mode: ${config.mode}`);

  // Language pack
  const langs = languages();
  if (typeof config.lang !== "string" || !LANG_ID.test(config.lang) || !langs.includes(config.lang)) {
    add("fail", `language pack ${JSON.stringify(config.lang)} not found (available: ${langs.join(", ") || "none"})`);
  } else {
    const missingFiles = PACK_FILES.filter((f) => !exists(path.join(SKILL_DIR, "languages", config.lang, f)));
    if (missingFiles.length) add("fail", `pack "${config.lang}" is missing: ${missingFiles.join(", ")}`);
    else add("ok", `lang: ${config.lang}`);
  }

  // Installs: more than one copy with different content is a problem
  const candidates = [
    path.join(HOME, ".claude", "skills", "llano"),
    path.join(HOME, ".agents", "skills", "llano"),
    path.join(CWD, ".claude", "skills", "llano"),
    path.join(CWD, ".agents", "skills", "llano"),
  ];
  const installs = [...new Set(candidates.filter((d) => exists(path.join(d, "SKILL.md"))).map((d) => fs.realpathSync(d)))];
  const hashes = new Set(installs.map(hashDir));
  if (hashes.size > 1) add("warn", `${installs.length} llano installs with different content: ${installs.join(", ")}`);
  else add("ok", `install: ${installs.join(", ") || SKILL_DIR}`);

  // Conflicting style skills
  const skillRoots = [path.join(HOME, ".claude", "skills"), path.join(HOME, ".agents", "skills"), path.join(CWD, ".claude", "skills")];
  const conflicts = skillRoots.flatMap((r) => STYLE_CONFLICTS.map((n) => path.join(r, n))).filter(exists);
  if (conflicts.length) add("warn", `conflicting style skill installed: ${conflicts.join(", ")}`);

  // Activation
  const hooks = llanoHooks();
  const liveHooks = hooks.filter((h) => h.script && exists(h.script));
  for (const h of hooks) {
    if (!h.script || !exists(h.script)) add("fail", `hook in ${h.file} points to a missing script: ${h.script} (run --install-hook)`);
    else if (fs.realpathSync(h.script) !== fs.realpathSync(SCRIPT)) add("warn", `hook in ${h.file} runs another install: ${h.script}`);
  }
  const lineFiles = [
    path.join(HOME, ".claude", "CLAUDE.md"),
    path.join(HOME, ".codex", "AGENTS.md"),
    path.join(CWD, "CLAUDE.md"),
    path.join(CWD, ".claude", "CLAUDE.md"),
    path.join(CWD, "AGENTS.md"),
  ].filter((p) => exists(p) && /^llano:/m.test(fs.readFileSync(p, "utf8")));
  if (liveHooks.length) add("ok", `activation: SessionStart hook (${[...new Set(liveHooks.map((h) => h.file))].join(", ")})`);
  else if (lineFiles.length) add("ok", `activation: ${lineFiles.join(", ")}`);
  else add("warn", "no automatic activation (run --install-hook, or add a `llano:` line to AGENTS.md)");

  return { config, langs, results };
}

function report() {
  const { langs, results } = checks();
  const icon = { ok: "✓", warn: "!", fail: "✗" };
  for (const r of results) console.log(`${icon[r.level]} ${r.msg}`);
  console.log(`  languages available: ${langs.join(", ") || "none"}`);
  console.log(`  doctor: ${SCRIPT}`);
  process.exitCode = results.some((r) => r.level === "fail") ? 1 : 0;
}

function hook() {
  const out = { hookSpecificOutput: { hookEventName: "SessionStart" } };
  try {
    const { config, results } = checks();
    const fails = results.filter((r) => r.level === "fail");
    const warns = results.filter((r) => r.level === "warn");
    const notes = [...fails, ...warns].map((r) => r.msg);
    if (notes.length) out.systemMessage = `llano: ${notes.join(". ")}. Run: node "${SCRIPT}"`;
    if (config.mode !== "off" && !fails.length) {
      out.hookSpecificOutput.additionalContext =
        `llano is active: mode=${config.mode}, lang=${config.lang}. ` +
        `Load the \`llano\` skill now and apply it as its SKILL.md says. ` +
        `Language pack: ${path.join(SKILL_DIR, "languages", config.lang)}. ` +
        `Doctor script (use this absolute path for /llano commands): ${SCRIPT}`;
    }
  } catch (e) {
    out.systemMessage = `llano: doctor failed: ${e.message}. Run: node "${SCRIPT}"`;
  }
  process.stdout.write(JSON.stringify(out));
}

function set(pairs) {
  const { config, error } = loadConfig();
  if (error) throw new Error(`${error}. Fix or delete the file first`);
  if (!pairs.length) throw new Error("nothing to set (example: --set mode=all lang=es)");
  for (const pair of pairs) {
    const i = pair.indexOf("=");
    const k = i < 0 ? pair : pair.slice(0, i);
    const v = i < 0 ? "" : pair.slice(i + 1);
    if (k === "mode") {
      if (!MODES.includes(v)) throw new Error(`unknown mode "${v}" (valid: ${MODES.join(", ")})`);
    } else if (k === "lang") {
      if (!LANG_ID.test(v) || !languages().includes(v)) throw new Error(`language pack "${v}" not found (available: ${languages().join(", ")})`);
    } else {
      throw new Error(`unknown key "${k}" (valid: mode, lang)`);
    }
    config[k] = v;
  }
  writeConfig(config);
  console.log(`llano config: mode=${config.mode}, lang=${config.lang} (${CONFIG})`);
}

// Edits ~/.claude/settings.json. Each call keeps its own timestamped backup.
function editSettings(fn) {
  let settings = {};
  let backup = null;
  if (exists(SETTINGS)) {
    settings = readJson(SETTINGS);
    backup = `${SETTINGS}.bak-llano-${new Date().toISOString().replace(/[:.]/g, "-")}`;
    fs.copyFileSync(SETTINGS, backup);
  }
  fn(settings);
  fs.mkdirSync(path.dirname(SETTINGS), { recursive: true });
  fs.writeFileSync(SETTINGS, JSON.stringify(settings, null, 2) + "\n");
  return backup;
}

function removeHook(settings) {
  const groups = settings.hooks?.SessionStart;
  if (!Array.isArray(groups)) return;
  settings.hooks.SessionStart = groups
    .map((g) => ({ ...g, hooks: (g.hooks ?? []).filter((h) => !isLlanoHook(h.command)) }))
    .filter((g) => g.hooks.length);
  if (!settings.hooks.SessionStart.length) delete settings.hooks.SessionStart;
  if (!Object.keys(settings.hooks).length) delete settings.hooks;
}

function installHook() {
  const backup = editSettings((s) => {
    removeHook(s);
    s.hooks ??= {};
    s.hooks.SessionStart ??= [];
    s.hooks.SessionStart.push({ hooks: [{ type: "command", command: `node "${SCRIPT}" --hook` }] });
  });
  if (!exists(CONFIG)) writeConfig(DEFAULTS);
  console.log(`llano: SessionStart hook added to ${SETTINGS}${backup ? ` (backup: ${backup})` : ""}`);
}

function uninstallHook() {
  const backup = editSettings(removeHook);
  console.log(`llano: SessionStart hook removed${backup ? ` (backup: ${backup})` : ""}`);
}

const [cmd, ...rest] = process.argv.slice(2);
try {
  switch (cmd) {
    case undefined: report(); break;
    case "--hook": hook(); break;
    case "--init": if (exists(CONFIG)) console.log(`config exists: ${CONFIG}`); else { writeConfig(DEFAULTS); console.log(`created ${CONFIG}`); } break;
    case "--set": set(rest); break;
    case "--install-hook": installHook(); break;
    case "--uninstall-hook": uninstallHook(); break;
    default: console.error(`unknown option: ${cmd}`); process.exitCode = 2;
  }
} catch (e) {
  console.error(`llano: ${e.message}`);
  process.exitCode = 1;
}
