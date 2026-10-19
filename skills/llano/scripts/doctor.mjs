#!/usr/bin/env node
// llano doctor: checks language packs, installs and activation, and turns llano on.
//
// A skill alone loads on demand. --install adds one marked, plain-text block to the global
// instructions of each agent it finds:
//   ~/.claude/CLAUDE.md (Claude Code), ~/.codex/AGENTS.md (Codex), ~/.gemini/GEMINI.md (Gemini CLI).
// The block holds the configuration (mode, lang). The script adds no hooks and nothing that
// runs on its own. It shows what it will change and asks before writing. Each changed file
// is backed up first.
//
// Usage:
//   node doctor.mjs                       full report (exit 1 on a failure)
//   node doctor.mjs --install [k=v ...]   show the plan, ask, then add or update the block
//   node doctor.mjs --set k=v ...         same as --install, with new values (mode, lang)
//   node doctor.mjs --uninstall           show the plan, ask, then remove the block
// Options for --install, --set and --uninstall:
//   --dry-run   show the plan and exit
//   --yes       apply without asking (for scripts)

import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import crypto from "node:crypto";
import { createInterface } from "node:readline/promises";
import { fileURLToPath } from "node:url";

const SKILL_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const SCRIPT = path.join(SKILL_DIR, "scripts", "doctor.mjs");
const HOME = os.homedir();
const CWD = process.cwd();
if (!HOME || !path.isAbsolute(HOME)) {
  // An empty or relative HOME would make every path below relative to the current directory.
  console.error(`llano: HOME is not an absolute path (${JSON.stringify(HOME)}). Nothing changed.`);
  process.exit(1);
}
const SETTINGS = path.join(HOME, ".claude", "settings.json");
// Version 1 kept the configuration here and read it from a SessionStart hook.
const LEGACY_CONFIG = process.env.LLANO_CONFIG || path.join(HOME, ".config", "llano", "config.json");
const MODES = ["explain", "responses", "all", "off"];
const DEFAULTS = { mode: "responses", lang: "es" };
const PACK_FILES = ["rules.md", "examples.md"];
const STYLE_CONFLICTS = ["caveman"];
const LANG_ID = /^[A-Za-z0-9_-]+$/;

const START = "<!-- llano:start -->";
const END = "<!-- llano:end -->";
const BLOCK_RE = new RegExp(`\\n*${START}[\\s\\S]*?${END}\\n*`, "g");
const LINE_RE = /^llano:\s*mode=([^,\s]+),\s*lang=(\S+)\s*$/m;
const block = (config) =>
  `${START}\n` +
  `llano: mode=${config.mode}, lang=${config.lang}\n\n` +
  "Load the `llano` skill at the start of every session and apply it with this configuration. " +
  `If you cannot load skills, read ${path.join(SKILL_DIR, "SKILL.md")}. ` +
  `Doctor script for /llano commands: ${SCRIPT}\n` +
  `${END}\n`;

const AGENTS = [
  { agent: "Claude Code", path: path.join(HOME, ".claude", "CLAUDE.md") },
  { agent: "Codex", path: path.join(HOME, ".codex", "AGENTS.md") },
  { agent: "Gemini CLI", path: path.join(HOME, ".gemini", "GEMINI.md") },
].filter((a) => fs.existsSync(path.dirname(a.path)));
const NO_AGENT = "no agent found (~/.claude, ~/.codex or ~/.gemini)";

// Version 1 added a SessionStart hook that ran `node ".../doctor.mjs" --hook`.
const isLegacyHook = (h) => /llano.*doctor\.mjs"?\s+--hook\b/.test(String(h?.command ?? ""));

const exists = (p) => fs.existsSync(p);
const read = (p) => (exists(p) ? fs.readFileSync(p, "utf8") : "");

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

// Throws on an unknown mode or a missing language pack.
function validate(config) {
  if (!MODES.includes(config.mode)) throw new Error(`unknown mode "${config.mode}" (valid: ${MODES.join(", ")})`);
  if (!LANG_ID.test(config.lang) || !languages().includes(config.lang)) {
    throw new Error(`language pack "${config.lang}" not found (available: ${languages().join(", ") || "none"})`);
  }
}

function parsePairs(pairs) {
  const out = {};
  for (const pair of pairs) {
    const i = pair.indexOf("=");
    const k = i < 0 ? pair : pair.slice(0, i);
    if (k !== "mode" && k !== "lang") throw new Error(`unknown key "${k}" (valid: mode, lang)`);
    out[k] = i < 0 ? "" : pair.slice(i + 1);
  }
  return out;
}

// The configuration in a file's llano line, or null.
function configIn(text) {
  const m = text.match(LINE_RE);
  return m ? { mode: m[1], lang: m[2] } : null;
}

// The configuration of a file: the line inside its block, else a line added by hand. Null when
// the markers do not pair up.
function fileConfig(text) {
  if (blockState(text) === "broken") return null;
  return configIn(text.includes(START) ? text.slice(text.indexOf(START)) : text);
}

function legacyConfig() {
  try {
    const raw = JSON.parse(read(LEGACY_CONFIG) || "null");
    return raw && typeof raw === "object" && !Array.isArray(raw) ? raw : {};
  } catch {
    return {};
  }
}

// Values for a new block: the ones given, else an installed block, else the version 1 config file.
function resolveConfig(given) {
  const installed = AGENTS.map((a) => fileConfig(read(a.path))).find(Boolean);
  const { mode, lang } = { ...DEFAULTS, ...legacyConfig(), ...installed, ...given };
  const config = { mode: String(mode), lang: String(lang) };
  validate(config);
  return config;
}

// Removes every block with the blank lines around it; the text on each side joins with one blank line.
function stripBlock(text) {
  const out = text.replace(BLOCK_RE, "\n\n");
  if (out === text) return text;
  const trimmed = out.replace(/^\n+/, "").replace(/\n*$/, "\n");
  return trimmed === "\n" ? "" : trimmed;
}

// "installed", "outdated", "missing", or "broken" when the markers do not pair up.
// Without a config, any single block that this install would write counts as installed.
function blockState(text, config) {
  const starts = text.split(START).length - 1;
  if (starts !== text.split(END).length - 1) return "broken";
  if (!starts) return "missing";
  const wanted = config ?? configIn(text.slice(text.indexOf(START)));
  return starts === 1 && wanted && text.includes(block(wanted)) ? "installed" : "outdated";
}

// Anything that could not be checked or changed. Each one makes the script exit with 1.
const warnings = [];
function warn(text) {
  warnings.push(text);
  console.error(`Warning: ${text}`);
}

// settings.json without the version 1 hook, or null when there is nothing to remove or the
// file cannot be read (bad JSON or an unexpected shape).
function settingsWithoutLegacyHook(text) {
  try {
    const settings = JSON.parse(text || "{}");
    const groups = settings?.hooks?.SessionStart ?? [];
    if (!groups.some((g) => (g?.hooks ?? []).some(isLegacyHook))) return null;
    // Only the groups that held the old hook change; one left empty goes away.
    const kept = groups.flatMap((g) => {
      const hooks = g?.hooks ?? [];
      if (!hooks.some(isLegacyHook)) return [g];
      const rest = hooks.filter((h) => !isLegacyHook(h));
      return rest.length ? [{ ...g, hooks: rest }] : [];
    });
    if (kept.length) settings.hooks.SessionStart = kept;
    else delete settings.hooks.SessionStart;
    if (!Object.keys(settings.hooks).length) delete settings.hooks;
    return settings;
  } catch (e) {
    warn(`cannot read ${SETTINGS} (${e.message}), so the version 1 hook was not checked.`);
    return null;
  }
}

// Settings files other than SETTINGS that still hold the version 1 hook. The script does not
// change them; the report asks the person to.
function otherLegacyHooks() {
  const files = [
    path.join(HOME, ".claude", "settings.local.json"),
    path.join(CWD, ".claude", "settings.json"),
    path.join(CWD, ".claude", "settings.local.json"),
  ].filter((f) => f !== SETTINGS && exists(f));
  return files.filter((f) => {
    try {
      return (JSON.parse(read(f))?.hooks?.SessionStart ?? []).some((g) => (g?.hooks ?? []).some(isLegacyHook));
    } catch {
      return false;
    }
  });
}

function checks() {
  const results = []; // { level: "ok" | "info" | "warn" | "fail", msg }
  const add = (level, msg) => results.push({ level, msg });
  const langs = languages();

  // Activation and configuration
  if (!AGENTS.length) add("warn", NO_AGENT);
  const configs = [];
  for (const { agent, path: p } of AGENTS) {
    const text = read(p);
    const state = blockState(text);
    const config = fileConfig(text);
    if (config) configs.push(config);
    if (state === "installed") add("ok", `${agent}: active, mode=${config.mode}, lang=${config.lang} (${p})`);
    else if (state === "outdated") add("warn", `${agent}: block is outdated (${p}): run --install`);
    else if (state === "broken") add("fail", `${agent}: a llano marker has no pair in ${p}: fix it by hand`);
    else if (config) add("ok", `${agent}: llano line added by hand, mode=${config.mode}, lang=${config.lang} (${p})`);
    else add("warn", `${agent}: not active: run --install`);
  }
  const projectFiles = [path.join(CWD, "CLAUDE.md"), path.join(CWD, ".claude", "CLAUDE.md"), path.join(CWD, "AGENTS.md")]
    .filter((p) => configIn(read(p)));
  for (const p of projectFiles) add("ok", `project activation: ${p}`);
  for (const config of configs) {
    try { validate(config); } catch (e) { add("fail", e.message); }
  }
  if (new Set(configs.map((c) => `${c.mode}/${c.lang}`)).size > 1) add("warn", "agents have different configurations: run --set to align them");

  // Version 1 leftovers
  if (settingsWithoutLegacyHook(read(SETTINGS))) add("fail", `old SessionStart hook in ${SETTINGS}: run --install to remove it`);
  for (const f of otherLegacyHooks()) add("fail", `old SessionStart hook in ${f}: remove it by hand`);
  if (exists(LEGACY_CONFIG)) add("info", `${LEGACY_CONFIG} is no longer read; the configuration lives in the block. You can delete it.`);

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

  // Language packs
  for (const lang of langs) {
    const missingFiles = PACK_FILES.filter((f) => !exists(path.join(SKILL_DIR, "languages", lang, f)));
    if (missingFiles.length) add("fail", `pack "${lang}" is missing: ${missingFiles.join(", ")}`);
  }

  // Conflicting style skills
  const skillRoots = [path.join(HOME, ".claude", "skills"), path.join(HOME, ".agents", "skills"), path.join(CWD, ".claude", "skills")];
  const conflicts = skillRoots.flatMap((r) => STYLE_CONFLICTS.map((n) => path.join(r, n))).filter(exists);
  if (conflicts.length) add("warn", `conflicting style skill installed: ${conflicts.join(", ")}`);

  return { langs, results };
}

function report() {
  const { langs, results } = checks();
  const icon = { ok: "✓", info: "·", warn: "!", fail: "✗" };
  for (const r of results) console.log(`${icon[r.level]} ${r.msg}`);
  console.log(`  languages available: ${langs.join(", ") || "none"}`);
  console.log(`  doctor: ${SCRIPT}`);
  process.exitCode = results.some((r) => r.level === "fail") || warnings.length ? 1 : 0;
}

function plan(config) {
  const install = config !== null;
  const steps = [];
  for (const { agent, path: p } of AGENTS) {
    const before = read(p);
    const state = blockState(before, config);
    if (state === "broken") {
      warn(`${p} has a llano marker without its pair. Fix it by hand; this file was skipped.`);
      continue;
    }
    if (install ? state === "installed" : state === "missing") continue;
    const base = stripBlock(before);
    const after = install ? (base.trimEnd() ? base.trimEnd() + "\n\n" : "") + block(config) : base;
    if (after !== before) steps.push({ agent, path: p, before, after, what: install ? "write the llano block" : "remove the llano block" });
  }
  const before = read(SETTINGS);
  const settings = settingsWithoutLegacyHook(before);
  if (settings) {
    const what = "remove the old llano hook (version 1); the whole file is rewritten with 2-space indentation";
    steps.push({ agent: "Claude Code", path: SETTINGS, before, after: JSON.stringify(settings, null, 2) + "\n", what });
  }
  for (const f of otherLegacyHooks()) warn(`${f} still has the old llano hook. Remove it by hand.`);
  return steps;
}

function show(steps, config) {
  if (!steps.length) {
    if (!AGENTS.length) console.log(`llano: ${NO_AGENT}. Nothing to change.`);
    else if (warnings.length) console.log("Nothing else to change, but see the warnings above.");
    else console.log(config ? "llano is installed. Nothing to change." : "llano is not installed. Nothing to change.");
    return;
  }
  console.log("This will change:");
  for (const s of steps) console.log(`  - ${s.agent}: ${s.what} in ${s.path}`);
  if (config && steps.some((s) => s.after.includes(START))) console.log(`\nThe block is plain text:\n\n${block(config)}`);
  console.log("Each file is backed up next to itself (*.llano-backup-<time>) before it changes.");
}

async function confirm() {
  if (!process.stdin.isTTY) {
    // Without a terminal the caller is usually an agent: the plan goes to a person first.
    console.error("\nNo terminal to ask in. Show this plan to the user; apply it with --yes only with their approval.");
    return false;
  }
  const rl = createInterface({ input: process.stdin, output: process.stdout });
  try {
    return /^y(es)?$/i.test((await rl.question("\nApply these changes? [y/N] ")).trim());
  } catch {
    return false; // Ctrl-D or Ctrl-C at the prompt
  } finally {
    rl.close();
  }
}

// Returns false when any file could not be written. A file that changed after the plan was
// shown is left alone, so the answer to the prompt never overwrites newer edits.
function apply(steps) {
  const stamp = new Date().toISOString().replace(/[:.]/g, "-");
  let ok = true;
  for (const s of steps) {
    try {
      if (read(s.path) !== s.before) throw new Error("it changed after the plan was shown; run the script again");
      if (exists(s.path)) fs.copyFileSync(s.path, `${s.path}.llano-backup-${stamp}`);
      fs.writeFileSync(s.path, s.after);
      console.log(`  done: ${s.path}`);
    } catch (e) {
      ok = false;
      console.error(`  failed: ${s.path} (${e.message})`);
    }
  }
  if (!ok) console.error("Some files did not change. The files marked done did; their backups are next to them.");
  return ok;
}

// Exit 1 tells a script or an agent that something was not installed, applied or checked.
async function change(config, flags) {
  const steps = plan(config);
  show(steps, config);
  let ok = !(config && !AGENTS.length);
  if (steps.length && !flags.has("--dry-run")) {
    if (flags.has("--yes") || (await confirm())) ok = apply(steps) && ok;
    else {
      console.log("Nothing changed.");
      ok = false;
    }
  }
  process.exitCode = ok && !warnings.length ? 0 : 1;
}

const [cmd, ...rest] = process.argv.slice(2);
const flags = new Set(rest.filter((a) => a.startsWith("--")));
const pairs = rest.filter((a) => !a.startsWith("--"));
try {
  for (const f of flags) if (f !== "--dry-run" && f !== "--yes") throw new Error(`unknown option: ${f}`);
  if (flags.has("--dry-run") && flags.has("--yes")) throw new Error("--dry-run and --yes do not go together");
  switch (cmd) {
    case undefined: report(); break;
    case "--install": await change(resolveConfig(parsePairs(pairs)), flags); break;
    case "--set":
      if (!pairs.length) throw new Error("nothing to set (example: --set mode=all lang=es)");
      await change(resolveConfig(parsePairs(pairs)), flags);
      break;
    case "--uninstall": await change(null, flags); break;
    case "--hook":
      // The version 1 SessionStart hook still calls this. systemMessage goes to the person, not to
      // the model, and the script does nothing else.
      console.log(JSON.stringify({ systemMessage: `llano: the old hook is still in ${SETTINGS}. To remove it and keep llano active, run: node "${SCRIPT}" --install` }));
      break;
    case "--install-hook":
    case "--uninstall-hook":
    case "--init":
      throw new Error(`${cmd} was removed: use --install or --uninstall`);
    default: throw new Error(`unknown option: ${cmd}`);
  }
} catch (e) {
  console.error(`llano: ${e.message}`);
  process.exitCode = 1;
}
