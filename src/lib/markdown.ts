import { Marked, type Tokens } from "marked";
import { BASE } from "./paths";
import type { Lang } from "./types";

const escapeAttr = (s: string) =>
  s.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

const marked = new Marked({
  gfm: true,
  breaks: false,
  renderer: {
    link(this: { parser: { parseInline(tokens: Tokens.Generic[]): string } }, token: Tokens.Link) {
      const text = this.parser.parseInline(token.tokens);
      const href = token.href ?? "";
      const title = token.title ? ` title="${escapeAttr(token.title)}"` : "";
      if (/^https?:\/\//i.test(href)) {
        return `<a href="${escapeAttr(href)}"${title} target="_blank" rel="noopener noreferrer" class="ext">${text}</a>`;
      }
      return `<a href="${escapeAttr(href)}"${title}>${text}</a>`;
    },
  },
});

const MATH_SYMBOLS: Record<string, string> = {
  ge: "≥", geq: "≥", le: "≤", leq: "≤", times: "×", pm: "±", approx: "≈", sim: "~", mu: "µ",
  alpha: "α", beta: "β", gamma: "γ", delta: "δ", Delta: "Δ", kappa: "κ", lambda: "λ", sigma: "σ",
  tau: "τ", rightarrow: "→", to: "→", cdot: "·", neq: "≠", infty: "∞", "%": "%", ",": " ",
};

/** Converts the small amount of inline LaTeX used in the notes into plain HTML. */
function mathToHtml(src: string): string {
  let s = src.replace(/\{\}/g, "");
  s = s.replace(/\\text\{([^}]*)\}|\\mathrm\{([^}]*)\}/g, (_m, a, b) => a ?? b ?? "");
  s = s.replace(/\\([A-Za-z]+|[%,])/g, (m, name: string) => MATH_SYMBOLS[name] ?? m.slice(1));
  s = s.replace(/\^\{([^}]*)\}|\^(\S)/g, (_m, a, b) => `<sup>${a ?? b}</sup>`);
  s = s.replace(/_\{([^}]*)\}|_(\S)/g, (_m, a, b) => `<sub>${a ?? b}</sub>`);
  return s.replace(/[{}]/g, "");
}

// Pandoc-style inline math: no space after opening / before closing $, not followed by a digit
// (so "$2,000 … around $3,000" stays currency). Backslash commands may be followed by digits ("$\ge$36").
const MATH_RE = /\$(?=\S)([^$\n]{1,80}?)(?<=\S)\$(?!\d)|\$(\\[A-Za-z]+)\$/g;

function preprocess(md: string, lang: Lang): string {
  return md
    .replace(/\]\(thread:([a-z0-9-]+)(#[^)\s]*)?\)/g, (_m, slug: string, hash = "") => `](${BASE}/${lang}/threads/${slug}/${hash})`)
    .replace(MATH_RE, (_m, a?: string, b?: string) => mathToHtml((a ?? b ?? "").trim()));
}

export function renderBlock(md: string | null | undefined, lang: Lang): string {
  if (!md || !md.trim()) return "";
  return (marked.parse(preprocess(md, lang), { async: false }) as string).trim();
}

export function renderInline(md: string | null | undefined, lang: Lang): string {
  if (!md || !md.trim()) return "";
  return (marked.parseInline(preprocess(md.trim(), lang), { async: false }) as string).trim();
}

/** Strips markdown and inline math to readable plain text. */
export function toPlain(md: string | null | undefined): string {
  if (!md) return "";
  return md
    .replace(MATH_RE, (_m, a?: string, b?: string) => mathToHtml((a ?? b ?? "").trim()).replace(/<[^>]+>/g, ""))
    .replace(/!\[[^\]]*\]\([^)]*\)/g, "")
    .replace(/\[([^\]]+)\]\([^)]*\)/g, "$1")
    .replace(/<[^>]+>/g, "")
    .replace(/`([^`]*)`/g, "$1")
    .replace(/(\*\*|__)(.+?)\1/g, "$2")
    .replace(/(^|[\s(])[*_]([^*_\n]+)[*_](?=[\s).,;:!?]|$)/g, "$1$2")
    .replace(/^\s{0,3}(#{1,6}|>|[-*+]|\d+\.)\s+/gm, "")
    .replace(/\s+/g, " ")
    .trim();
}

const ABBREV = new Set(
  [
    "al", "e.g", "i.e", "vs", "approx", "ca", "dr", "prof", "fig", "figs", "no", "nr", "st", "jr", "inc", "ltd",
    "z.b", "d.h", "bzw", "u.a", "ggf", "inkl", "vgl", "evtl", "sog", "etc", "mio", "mrd", "bspw", "s",
  ].map((s) => s.toLowerCase()),
);

/** Returns the first sentence(s) of a text, avoiding breaks after common abbreviations. */
export function firstSentences(text: string, count = 1, minLength = 60, maxLength = 340): string {
  const plain = text.replace(/\s+/g, " ").trim();
  if (!plain) return "";
  const re = /[.!?](?=["”“»)]?\s+["„“«(]?[A-ZÄÖÜ0-9])/g;
  let taken = 0;
  let end = -1;
  let m: RegExpExecArray | null;
  while ((m = re.exec(plain))) {
    const before = plain.slice(0, m.index);
    const word = (/(\S+)$/.exec(before)?.[1] ?? "").toLowerCase().replace(/^[("„“]+/, "");
    if (ABBREV.has(word) || /^[a-zäöü]$/i.test(word) || /^([a-z]\.)+[a-z]$/i.test(word)) continue;
    end = m.index + 1;
    taken++;
    if (taken >= count && end >= minLength) break;
  }
  let out = end > 0 ? plain.slice(0, end) : plain;
  if (out.length > maxLength) {
    const cut = out.slice(0, maxLength);
    out = `${cut.slice(0, Math.max(cut.lastIndexOf(" "), maxLength - 40)).replace(/[,;:\s]+$/, "")} …`;
  }
  return out;
}
