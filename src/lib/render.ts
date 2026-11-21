// HTML string renderers shared by server (SSR) and client scripts so markup stays identical.
import type { CardStrings, FeedEntry } from "./types";

export function escapeHtml(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

export const ICONS = {
  external:
    '<svg class="icon" viewBox="0 0 16 16" width="13" height="13" aria-hidden="true" focusable="false"><path d="M9.5 2.5h4v4M13.5 2.5 7.75 8.25M12 9.5v3a1 1 0 0 1-1 1H3.5a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1h3" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  chevron:
    '<svg class="icon chev" viewBox="0 0 16 16" width="14" height="14" aria-hidden="true" focusable="false"><path d="m4 6 4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  link: '<svg class="icon" viewBox="0 0 16 16" width="14" height="14" aria-hidden="true" focusable="false"><path d="M6.5 9.5a3 3 0 0 0 4.24 0l2-2a3 3 0 0 0-4.24-4.24l-.75.75M9.5 6.5a3 3 0 0 0-4.24 0l-2 2a3 3 0 0 0 4.24 4.24l.75-.75" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>',
};

export interface CardOptions {
  context: "feed" | "thread";
  headingLevel?: 2 | 3;
}

function sourcesList(e: FeedEntry, s: CardStrings): string {
  if (!e.sources.length) return "";
  const items = e.sources
    .map(
      (src) =>
        `<li><a class="source-pill" href="${escapeHtml(src.url)}" target="_blank" rel="noopener noreferrer" title="${escapeHtml(src.label)} (${escapeHtml(s.openSource)})"><span class="source-label">${escapeHtml(src.label)}</span>${src.domain ? `<span class="source-domain">${escapeHtml(src.domain)}</span>` : ""}${ICONS.external}</a></li>`,
    )
    .join("");
  return `<div class="sources"><span class="sources-title">${escapeHtml(s.sources)}</span><ul class="source-list">${items}</ul></div>`;
}

/** Renders one research entry card. `e.title`, `e.summary`, `e.detail` are trusted, pre-rendered HTML. */
export function renderEntryCard(e: FeedEntry, s: CardStrings, opts: CardOptions): string {
  const h = opts.headingLevel ?? 3;
  const langAttr = e.contentLang ? ` lang="${e.contentLang}"` : "";
  const meta = [
    `<time class="entry-date" datetime="${escapeHtml(e.date)}">${escapeHtml(e.dateLabel)}</time>`,
    `<span class="badge badge-type" data-type="${escapeHtml(e.type)}">${escapeHtml(e.typeLabel)}</span>`,
    e.design ? `<span class="badge badge-design">${escapeHtml(e.design)}</span>` : "",
    opts.context === "feed"
      ? `<a class="thread-pill" data-group="${escapeHtml(e.group)}" href="${escapeHtml(e.url.split("#")[0])}"><span class="dot" aria-hidden="true"></span>${escapeHtml(e.threadTitle)}</a>`
      : "",
  ].join("");

  const titleInner =
    opts.context === "thread"
      ? `<a class="entry-anchor" href="#${escapeHtml(e.id)}">${e.title}</a>`
      : `<a class="entry-anchor" href="${escapeHtml(e.url)}">${e.title}</a>`;

  const detailBody = e.detail ? `<div class="prose prose-sm"${langAttr}>${e.detail}</div>` : "";
  const toThread =
    opts.context === "feed" ? `<p class="to-thread"><a href="${escapeHtml(e.url)}">${escapeHtml(s.toThread)}</a></p>` : "";

  const hasDetails = opts.context === "feed" ? !!(detailBody || e.sources.length) : !!detailBody;
  const details = hasDetails
    ? `<details class="entry-details"><summary><span>${escapeHtml(opts.context === "feed" ? s.details : s.detailsThread)}</span>${ICONS.chevron}</summary><div class="details-body">${detailBody}${opts.context === "feed" ? sourcesList(e, s) + toThread : ""}</div></details>`
    : "";

  const idAttr = opts.context === "thread" ? ` id="${escapeHtml(e.id)}"` : "";
  return `<article class="entry"${idAttr} data-group="${escapeHtml(e.group)}" data-type="${escapeHtml(e.type)}" data-date="${escapeHtml(e.date)}"><div class="entry-meta">${meta}</div><h${h} class="entry-title"${langAttr}>${titleInner}</h${h}>${e.summary ? `<p class="entry-summary"${langAttr}>${e.summary}</p>` : ""}${details}${opts.context === "thread" ? sourcesList(e, s) : ""}</article>`;
}

export function normalize(s: string): string {
  return s
    .toLowerCase()
    .normalize("NFKD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/ß/g, "ss")
    .replace(/[^a-z0-9+/.\- ]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

/** Normalised, de-duplicated word list – compact haystack for per-term substring matching. */
export function wordSet(s: string, exclude = ""): string {
  const skip = new Set(normalize(exclude).split(" "));
  const seen = new Set<string>();
  for (const w of normalize(s).split(" ")) if (w && !skip.has(w)) seen.add(w);
  return [...seen].join(" ");
}
