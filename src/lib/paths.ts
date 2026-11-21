import type { Lang } from "./types";

/** Base path without trailing slash, e.g. "/ME-CFS-Research-Summaries". */
export const BASE = (import.meta.env.BASE_URL || "/").replace(/\/+$/, "");

/** Builds an absolute site path with a trailing slash (unless it has a hash/query/file extension). */
export function url(path = ""): string {
  const clean = path.replace(/^\/+/, "");
  if (!clean) return `${BASE}/`;
  const [p, suffix = ""] = clean.split(/(?=[#?])/);
  const withSlash = /\.[a-z0-9]+$/i.test(p) || p.endsWith("/") ? p : `${p}/`;
  return `${BASE}/${withSlash}${suffix}`;
}

export const langHome = (lang: Lang) => url(`${lang}/`);
export const threadUrl = (lang: Lang, slug: string) => url(`${lang}/threads/${slug}/`);
export const feedUrl = (lang: Lang) => url(`${lang}/feed/`);
export const glossaryUrl = (lang: Lang) => url(`${lang}/glossary/`);
export const imprintUrl = (lang: Lang) => url(`${lang}/imprint/`);
export const updatesUrl = (lang: Lang) => url(`${lang}/updates/`);
export const updateUrl = (lang: Lang, id: string) => url(`${lang}/updates/${id}/`);
