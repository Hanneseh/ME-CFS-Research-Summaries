// Build-time content loader. Reads YAML from ./content and returns localised, rendered data.
// German fields that are still empty fall back to English; empty plain summaries are derived
// from the first sentence(s) of the detail/takeaway so the build never depends on translations.

import fs from "node:fs";
import path from "node:path";
import yaml from "js-yaml";
import { escapeHtml } from "./render";
import { firstSentences, renderBlock, renderInline, toPlain } from "./markdown";
import { formatDate, formatEntryDate, sourceTypeLabel, studyDesignLabel } from "./i18n";
import { threadUrl } from "./paths";
import type { FeedEntry, Lang, SourceLink, UpdateAction } from "./types";

const CONTENT_DIR = path.resolve(process.cwd(), "content");

type Loc<T> = { en?: Partial<T>; de?: Partial<T> };

interface RawGroup extends Loc<{ title: string; short_title: string; description: string }> {
  slug: string;
  order?: number;
  accent?: string;
}
interface RawTier extends Loc<{ label: string; short: string; description: string }> {
  id: string;
  order?: number;
}
interface RawTerm extends Loc<{ full_name: string; definition: string }> {
  term: string;
  category?: string;
}
interface RawBucket {
  status?: string;
  label?: string;
  items?: string[];
}
interface RawThreadText {
  title: string;
  subtitle: string;
  evidence_label: string;
  plain_summary: string;
  takeaway: string;
  why_it_matters: string;
  state_of_evidence: RawBucket[];
  open_questions: string[];
}
interface RawThread extends Loc<RawThreadText> {
  slug: string;
  group: string;
  status?: string;
  evidence_tier?: string;
  topics?: string[];
  aliases?: string[];
  related_threads?: string[];
  legacy_path?: string;
}
interface RawEntry extends Loc<{ title: string; plain_summary: string; detail: string }> {
  id: string;
  date: string | Date;
  date_display?: string | null;
  date_precision?: string | null;
  source_type?: string | null;
  study_design?: string | null;
  sources?: { label?: string; url?: string; kind?: string }[];
}

interface RawUpdateRef {
  thread?: string;
  entry_id?: string;
  action?: string;
}
interface RawUpdateText {
  title: string;
  lead: string;
  highlights: { tag?: string; title?: string; summary?: string; links?: RawUpdateRef[] }[];
  what_to_skip_or_caveats: string;
}
interface RawUpdate extends Loc<RawUpdateText> {
  id: string;
  date: string | Date;
  period_from?: string | Date;
  period_to?: string | Date;
  added_entries?: RawUpdateRef[];
}

export interface UpdateItem {
  action: UpdateAction;
  entry: FeedEntry;
}
export interface UpdateHighlight {
  tag: string;
  title: string;
  summary: string;
  entries: FeedEntry[];
}
export interface Update {
  id: string;
  date: string;
  dateLabel: string;
  periodFrom: string;
  periodTo: string;
  periodLabel: string;
  title: string;
  titleText: string;
  lead: string;
  leadText: string;
  highlights: UpdateHighlight[];
  caveats: string;
  items: UpdateItem[];
  counts: { added: number; upgraded: number; threads: number };
  contentLang?: Lang;
}

export interface Group {
  slug: string;
  order: number;
  accent: string;
  title: string;
  shortTitle: string;
  description: string;
}
export interface Tier {
  id: string;
  order: number;
  label: string;
  short: string;
  description: string;
}
export interface Term {
  id: string;
  term: string;
  category: string;
  fullName: string;
  definition: string;
  definitionText: string;
  contentLang?: Lang;
}
export interface EvidenceBucket {
  status: string;
  label: string;
  items: string[];
}
export interface Thread {
  slug: string;
  group: string;
  status: string;
  evidenceTier: string;
  topics: string[];
  aliases: string[];
  relatedThreads: string[];
  legacyPath: string;
  title: string;
  titleText: string;
  subtitle: string;
  evidenceLabel: string;
  plainSummary: string;
  plainSummaryText: string;
  plainSummaryDerived: boolean;
  takeaway: string;
  whyItMatters: string;
  stateOfEvidence: EvidenceBucket[];
  openQuestions: string[];
  lastUpdated: string;
  entryCount: number;
  entries: FeedEntry[];
  /** Plain text used for search indexing and filtering, per entry id. */
  entryText: Record<string, string>;
  contentLang?: Lang;
}
export interface Site {
  lang: Lang;
  groups: Group[];
  tiers: Tier[];
  terms: Term[];
  threads: Thread[];
  entries: FeedEntry[];
  lastUpdated: string;
  sourceTypes: string[];
}

// ---------- helpers ----------

const str = (v: unknown): string => (typeof v === "string" ? v.trim() : v == null ? "" : String(v).trim());

function pick<T extends object>(obj: Loc<T>, key: keyof T, lang: Lang): { value: string; fellBack: boolean } {
  const own = str(obj[lang]?.[key]);
  if (own || lang === "en") return { value: own, fellBack: false };
  const en = str(obj.en?.[key]);
  return { value: en, fellBack: !!en };
}

function pickList<T>(own: T[] | undefined, en: T[] | undefined, lang: Lang): { value: T[]; fellBack: boolean } {
  const o = Array.isArray(own) ? own.filter(Boolean) : [];
  if (o.length || lang === "en") return { value: o, fellBack: false };
  const e = Array.isArray(en) ? en.filter(Boolean) : [];
  return { value: e, fellBack: e.length > 0 };
}

function readYaml<T>(file: string): T {
  return yaml.load(fs.readFileSync(file, "utf8")) as T;
}

function isoDate(v: string | Date): string {
  if (v instanceof Date) return v.toISOString().slice(0, 10);
  return str(v);
}

function domainOf(u: string): string {
  try {
    return new URL(u).hostname.replace(/^www\./, "");
  } catch {
    return "";
  }
}

export const slugify = (s: string) =>
  s
    .toLowerCase()
    .normalize("NFKD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");

function derivedHtml(text: string): string {
  return escapeHtml(text);
}

// ---------- raw loading (cached) ----------

interface RawData {
  groups: RawGroup[];
  tiers: RawTier[];
  terms: RawTerm[];
  threads: { raw: RawThread; entries: RawEntry[] }[];
  /** Newest first. */
  updates: RawUpdate[];
}

let rawCache: RawData | null = null;

function loadRaw(): RawData {
  if (rawCache) return rawCache;
  const groups = (readYaml<{ groups?: RawGroup[] }>(path.join(CONTENT_DIR, "groups.yaml"))?.groups ?? []).slice();
  const glossary = readYaml<{ evidence_tiers?: RawTier[]; terms?: RawTerm[] }>(path.join(CONTENT_DIR, "glossary.yaml")) ?? {};
  const threadsDir = path.join(CONTENT_DIR, "threads");
  const threads = fs
    .readdirSync(threadsDir, { withFileTypes: true })
    .filter((d) => d.isDirectory() && fs.existsSync(path.join(threadsDir, d.name, "thread.yaml")))
    .map((d) => {
      const dir = path.join(threadsDir, d.name);
      const raw = readYaml<RawThread>(path.join(dir, "thread.yaml"));
      raw.slug = str(raw.slug) || d.name;
      const entriesDir = path.join(dir, "entries");
      const entries = fs.existsSync(entriesDir)
        ? fs
            .readdirSync(entriesDir)
            .filter((f) => /\.ya?ml$/.test(f))
            .sort()
            .map((f) => {
              const e = readYaml<RawEntry>(path.join(entriesDir, f));
              e.id = str(e.id) || f.replace(/\.ya?ml$/, "");
              return e;
            })
            .filter((e) => e && e.date)
        : [];
      return { raw, entries };
    });
  const updatesDir = path.join(CONTENT_DIR, "updates");
  const updates = fs.existsSync(updatesDir)
    ? fs
        .readdirSync(updatesDir)
        .filter((f) => /\.ya?ml$/.test(f))
        .map((f) => {
          const u = readYaml<RawUpdate>(path.join(updatesDir, f));
          if (!u || typeof u !== "object") return null;
          u.id = str(u.id) || f.replace(/\.ya?ml$/, "");
          if (!/^[a-z0-9][a-z0-9-]*$/i.test(u.id)) throw new Error(`Invalid update id "${u.id}" in content/updates/${f}`);
          return u.date ? u : null;
        })
        .filter((u): u is RawUpdate => !!u)
        .sort((a, b) => byDateDesc({ date: isoDate(a.date), id: a.id }, { date: isoDate(b.date), id: b.id }))
    : [];
  rawCache = {
    groups,
    updates,
    tiers: (glossary.evidence_tiers ?? []).slice(),
    terms: (glossary.terms ?? []).slice(),
    threads,
  };
  return rawCache;
}

// ---------- localisation ----------

const siteCache = new Map<Lang, Site>();

const byDateDesc = (a: { date: string; id: string }, b: { date: string; id: string }) =>
  a.date < b.date ? 1 : a.date > b.date ? -1 : a.id < b.id ? 1 : a.id > b.id ? -1 : 0;

const refKey = (thread: string, entryId: string) => `${thread}:${entryId}`;
const toAction = (v: unknown): UpdateAction => (str(v) === "upgraded" ? "upgraded" : "added");

let batchCache: Map<string, UpdateAction> | null = null;

/** `${thread}:${entry_id}` → action for every entry in the newest update file. */
export function getLatestBatch(): Map<string, UpdateAction> {
  if (batchCache) return batchCache;
  const latest = loadRaw().updates[0];
  batchCache = new Map(
    (latest?.added_entries ?? [])
      .filter((r) => r && str(r.thread) && str(r.entry_id))
      .map((r) => [refKey(str(r.thread), str(r.entry_id)), toAction(r.action)]),
  );
  return batchCache;
}

/** Set of `${thread}:${entry_id}` keys from the newest update file. */
export function getLatestBatchEntryKeys(): Set<string> {
  return new Set(getLatestBatch().keys());
}

function localiseEntry(e: RawEntry, thread: { slug: string; group: string; title: string }, lang: Lang): { entry: FeedEntry; text: string } {
  const title = pick(e, "title", lang);
  const detail = pick(e, "detail", lang);
  const summary = pick(e, "plain_summary", lang);
  const date = isoDate(e.date);
  const sourceType = str(e.source_type) || "other";
  const detailPlain = toPlain(detail.value);

  let summaryHtml: string;
  let summaryText: string;
  let summaryFell = summary.fellBack;
  if (summary.value) {
    summaryHtml = renderInline(summary.value, lang);
    summaryText = toPlain(summary.value);
  } else {
    // Derive from this language's detail if present, otherwise from English detail.
    summaryText = firstSentences(detailPlain, 1, 80, 300);
    summaryHtml = derivedHtml(summaryText);
    summaryFell = detail.fellBack;
  }

  const sources: SourceLink[] = (e.sources ?? [])
    .filter((s) => s && str(s.url))
    .map((s) => ({ label: str(s.label) || domainOf(str(s.url)), url: str(s.url), domain: domainOf(str(s.url)), kind: str(s.kind) || "other" }));

  const fell = title.fellBack || detail.fellBack || summaryFell;
  const entry: FeedEntry = {
    id: e.id,
    date,
    dateLabel: formatEntryDate(date, lang, str(e.date_precision) || "exact", str(e.date_display) || null),
    year: date.slice(0, 4),
    type: sourceType,
    typeLabel: sourceTypeLabel(sourceType, lang),
    design: studyDesignLabel(str(e.study_design) || null, sourceType, lang),
    title: renderInline(title.value || e.id, lang),
    summary: summaryHtml,
    detail: renderBlock(detail.value, lang),
    sources,
    thread: thread.slug,
    threadTitle: thread.title,
    group: thread.group,
    url: `${threadUrl(lang, thread.slug)}#${e.id}`,
    ...(getLatestBatch().has(refKey(thread.slug, e.id)) ? { batch: getLatestBatch().get(refKey(thread.slug, e.id)) } : {}),
    ...(fell ? { contentLang: "en" as Lang } : {}),
  };
  const text = [toPlain(title.value), summaryText, detailPlain, sources.map((s) => s.label).join(" ")].join(" ");
  return { entry, text };
}

function localiseThread(raw: RawThread, rawEntries: RawEntry[], lang: Lang): Thread {
  const f = {
    title: pick(raw, "title", lang),
    subtitle: pick(raw, "subtitle", lang),
    evidenceLabel: pick(raw, "evidence_label", lang),
    plain: pick(raw, "plain_summary", lang),
    takeaway: pick(raw, "takeaway", lang),
    why: pick(raw, "why_it_matters", lang),
  };
  const soe = pickList(raw[lang]?.state_of_evidence, raw.en?.state_of_evidence, lang);
  const oq = pickList(raw[lang]?.open_questions, raw.en?.open_questions, lang);
  const title = f.title.value || raw.slug;
  const group = str(raw.group);

  const localised = rawEntries.map((e) => localiseEntry(e, { slug: raw.slug, group, title: toPlain(title) }, lang));
  localised.sort((a, b) => byDateDesc(a.entry, b.entry));
  const entries = localised.map((l) => l.entry);
  const entryText: Record<string, string> = {};
  for (const l of localised) entryText[l.entry.id] = l.text;

  let plainSummary: string;
  let plainSummaryText: string;
  let derived = false;
  let plainFell = f.plain.fellBack;
  if (f.plain.value) {
    plainSummary = renderBlock(f.plain.value, lang);
    plainSummaryText = toPlain(f.plain.value);
  } else {
    const source = toPlain(f.takeaway.value) || toPlain(f.subtitle.value);
    plainSummaryText = firstSentences(source, 2, 120, 420);
    plainSummary = plainSummaryText ? `<p>${derivedHtml(plainSummaryText)}</p>` : "";
    derived = true;
    plainFell = f.takeaway.fellBack || (!toPlain(f.takeaway.value) && f.subtitle.fellBack);
  }

  const anyFell = Object.values(f).some((x) => x.fellBack) || soe.fellBack || oq.fellBack || plainFell;

  return {
    slug: raw.slug,
    group,
    status: str(raw.status) || "active",
    evidenceTier: str(raw.evidence_tier) || "hypothesis",
    topics: (raw.topics ?? []).map(str).filter(Boolean),
    aliases: (raw.aliases ?? []).map(str).filter(Boolean),
    relatedThreads: (raw.related_threads ?? []).map(str).filter(Boolean),
    legacyPath: str(raw.legacy_path).replace(/^\/+|\/+$/g, ""),
    title: renderInline(title, lang),
    titleText: toPlain(title),
    subtitle: renderInline(f.subtitle.value, lang),
    evidenceLabel: renderInline(f.evidenceLabel.value, lang),
    plainSummary,
    plainSummaryText,
    plainSummaryDerived: derived,
    takeaway: renderBlock(f.takeaway.value, lang),
    whyItMatters: renderBlock(f.why.value, lang),
    stateOfEvidence: soe.value
      .map((b) => ({
        status: str(b.status) || "note",
        label: renderInline(str(b.label), lang),
        items: (b.items ?? []).map((i) => renderInline(str(i), lang)).filter(Boolean),
      }))
      .filter((b) => b.items.length || b.label),
    openQuestions: oq.value.map((q) => renderInline(str(q), lang)).filter(Boolean),
    lastUpdated: entries[0]?.date ?? "",
    entryCount: entries.length,
    entries,
    entryText,
    ...(anyFell ? { contentLang: "en" as Lang } : {}),
  };
}

export function getSite(lang: Lang): Site {
  const cached = siteCache.get(lang);
  if (cached) return cached;
  const raw = loadRaw();

  const groups: Group[] = raw.groups
    .map((g, i) => ({
      slug: g.slug,
      order: g.order ?? i + 1,
      accent: str(g.accent),
      title: pick(g, "title", lang).value || g.slug,
      shortTitle: pick(g, "short_title", lang).value || pick(g, "title", lang).value || g.slug,
      description: pick(g, "description", lang).value,
    }))
    .sort((a, b) => a.order - b.order);

  const tiers: Tier[] = raw.tiers
    .map((t, i) => ({
      id: t.id,
      order: t.order ?? i + 1,
      label: pick(t, "label", lang).value || t.id,
      short: pick(t, "short", lang).value || pick(t, "label", lang).value || t.id,
      description: pick(t, "description", lang).value,
    }))
    .sort((a, b) => a.order - b.order);

  const terms: Term[] = raw.terms
    .map((t) => {
      const def = pick(t, "definition", lang);
      const full = pick(t, "full_name", lang);
      return {
        id: slugify(t.term),
        term: str(t.term),
        category: str(t.category) || "research",
        fullName: full.value,
        definition: renderInline(def.value, lang),
        definitionText: toPlain(def.value),
        ...(def.fellBack || full.fellBack ? { contentLang: "en" as Lang } : {}),
      };
    })
    .sort((a, b) => a.term.localeCompare(b.term, lang, { sensitivity: "base" }));

  const groupOrder = new Map(groups.map((g) => [g.slug, g.order]));
  const threads = raw.threads
    .map(({ raw: r, entries }) => localiseThread(r, entries, lang))
    .sort((a, b) => (groupOrder.get(a.group) ?? 99) - (groupOrder.get(b.group) ?? 99) || toPlain(a.title).localeCompare(toPlain(b.title), lang));

  const entries = threads.flatMap((t) => t.entries).sort(byDateDesc);
  const sourceTypes = [...new Set(entries.map((e) => e.type))].sort();

  const site: Site = {
    lang,
    groups,
    tiers,
    terms,
    threads,
    entries,
    lastUpdated: entries[0]?.date ?? "",
    sourceTypes,
  };
  siteCache.set(lang, site);
  return site;
}

export function getThread(lang: Lang, slug: string): Thread | undefined {
  return getSite(lang).threads.find((t) => t.slug === slug);
}

export function getGroup(lang: Lang, slug: string): Group | undefined {
  return getSite(lang).groups.find((g) => g.slug === slug);
}

export function getTier(lang: Lang, id: string): Tier | undefined {
  return getSite(lang).tiers.find((t) => t.id === id);
}

/** Legacy Quartz paths (without base or slashes) mapped to their new, language-less target. */
export function getLegacyRedirects(): { from: string; to: string }[] {
  const raw = loadRaw();
  const out: { from: string; to: string }[] = [];
  for (const { raw: t } of raw.threads) {
    const legacy = str(t.legacy_path).replace(/^\/+|\/+$/g, "") || `${str(t.group)}/${t.slug}`;
    out.push({ from: legacy, to: `threads/${t.slug}/` });
  }
  for (const g of raw.groups) out.push({ from: g.slug, to: `#${g.slug}` });
  out.push({ from: "imprint", to: "imprint/" });
  out.push({ from: "glossary", to: "glossary/" });
  out.push({ from: "updates", to: "updates/" });
  for (const u of raw.updates) out.push({ from: `updates/${u.id}`, to: `updates/${u.id}/` });
  const seen = new Set<string>();
  return out.filter((r) => r.from && !seen.has(r.from) && seen.add(r.from));
}

// ---------- research updates ----------

const updatesCache = new Map<Lang, Update[]>();

function localiseUpdate(u: RawUpdate, lang: Lang): Update {
  const site = getSite(lang);
  const index = new Map(site.entries.map((e) => [refKey(e.thread, e.id), e]));
  const resolve = (r: RawUpdateRef): FeedEntry | undefined => {
    const key = refKey(str(r.thread), str(r.entry_id));
    const hit = index.get(key);
    if (!hit && lang === "en") console.warn(`[updates] ${u.id}: unknown entry ${key}`);
    return hit;
  };

  const title = pick(u, "title", lang);
  const lead = pick(u, "lead", lang);
  const caveats = pick(u, "what_to_skip_or_caveats", lang);
  const hl = pickList(u[lang]?.highlights, u.en?.highlights, lang);

  const seen = new Set<string>();
  const items: UpdateItem[] = [];
  for (const r of u.added_entries ?? []) {
    if (!r) continue;
    const entry = resolve(r);
    const key = refKey(str(r.thread), str(r.entry_id));
    if (!entry || seen.has(key)) continue;
    seen.add(key);
    items.push({ action: toAction(r.action), entry });
  }

  const date = isoDate(u.date);
  const from = u.period_from ? isoDate(u.period_from) : "";
  const to = u.period_to ? isoDate(u.period_to) : date;
  const titleValue = title.value || date;

  return {
    id: u.id,
    date,
    dateLabel: formatDate(date, lang),
    periodFrom: from,
    periodTo: to,
    periodLabel: from ? `${formatDate(from, lang)} – ${formatDate(to, lang)}` : formatDate(to, lang),
    title: renderInline(titleValue, lang),
    titleText: toPlain(titleValue),
    lead: renderBlock(lead.value, lang),
    leadText: toPlain(lead.value),
    highlights: hl.value
      .filter(Boolean)
      .map((h) => ({
        tag: toPlain(str(h.tag)),
        title: renderInline(str(h.title), lang),
        summary: renderBlock(str(h.summary), lang),
        entries: (h.links ?? []).map((r) => (r ? resolve(r) : undefined)).filter((e): e is FeedEntry => !!e),
      }))
      .filter((h) => h.title || h.summary),
    caveats: renderBlock(caveats.value, lang),
    items,
    counts: {
      added: items.filter((i) => i.action === "added").length,
      upgraded: items.filter((i) => i.action === "upgraded").length,
      threads: new Set(items.map((i) => i.entry.thread)).size,
    },
    ...(title.fellBack || lead.fellBack || caveats.fellBack || hl.fellBack ? { contentLang: "en" as Lang } : {}),
  };
}

/** All research update briefings, newest first. Empty when content/updates/ is missing. */
export function getUpdates(lang: Lang): Update[] {
  const cached = updatesCache.get(lang);
  if (cached) return cached;
  const list = loadRaw().updates.map((u) => localiseUpdate(u, lang));
  updatesCache.set(lang, list);
  return list;
}

export function getUpdate(lang: Lang, id: string): Update | undefined {
  return getUpdates(lang).find((u) => u.id === id);
}
