import { escapeHtml, normalize } from "../lib/render";
import type { SearchItem, SearchPayload } from "../lib/types";

const BASE = (import.meta.env.BASE_URL || "/").replace(/\/+$/, "");
const cache = new Map<string, Promise<SearchItem[]>>();

export function loadIndex(lang: string): Promise<SearchItem[]> {
  let p = cache.get(lang);
  if (!p) {
    p = fetch(`${BASE}/data/search-${lang}.json`)
      .then((r) => {
        if (!r.ok) throw new Error(`search index ${r.status}`);
        return r.json() as Promise<SearchPayload>;
      })
      .then((d) => d.items);
    p.catch(() => cache.delete(lang));
    cache.set(lang, p);
  }
  return p;
}

export function runQuery(items: SearchItem[], q: string, limit: number): SearchItem[] {
  const terms = normalize(q).split(" ").filter((t) => t.length > 0);
  if (!terms.length) return [];
  const scored: { item: SearchItem; score: number; i: number }[] = [];
  items.forEach((item, i) => {
    let score = 0;
    for (const term of terms) {
      const [title, keys, body] = item.h;
      let s = 0;
      if (title.includes(term)) s = title.startsWith(term) || title.includes(` ${term}`) ? 14 : 9;
      else if (keys.includes(term)) s = keys.includes(` ${term}`) || keys.startsWith(term) ? 7 : 5;
      else if (body.includes(term)) s = body.includes(` ${term}`) ? 2 : 1;
      if (!s) return;
      score += s;
    }
    if (item.kind === "thread") score *= 1.8;
    scored.push({ item, score, i });
  });
  scored.sort((a, b) => b.score - a.score || a.i - b.i);
  return scored.slice(0, limit).map((s) => s.item);
}

function highlight(text: string, q: string): string {
  const terms = q
    .trim()
    .split(/\s+/)
    .filter((t) => t.length > 1)
    .map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
  const safe = escapeHtml(text);
  if (!terms.length) return safe;
  return safe.replace(new RegExp(`(${terms.join("|")})`, "gi"), "<mark>$1</mark>");
}

interface MountOptions {
  limit: number;
  /** Hide results panel when the query is empty. */
  collapseWhenEmpty?: boolean;
}

/** Wires an input + listbox for instant search. Strings come from data attributes on the results element. */
export function mountSearch(input: HTMLInputElement, results: HTMLElement, opts: MountOptions): void {
  const lang = input.dataset.lang || document.documentElement.lang || "en";
  const d = results.dataset;
  let active = -1;
  let seq = 0;

  const setOpen = (open: boolean) => {
    if (opts.collapseWhenEmpty) results.hidden = !open;
    input.setAttribute("aria-expanded", String(open));
  };

  const options = () => Array.from(results.querySelectorAll<HTMLAnchorElement>("a.result"));

  const setActive = (i: number) => {
    const list = options();
    if (!list.length) return;
    active = (i + list.length) % list.length;
    list.forEach((el, j) => el.setAttribute("aria-selected", String(j === active)));
    list[active].scrollIntoView({ block: "nearest" });
    input.setAttribute("aria-activedescendant", list[active].id);
  };

  const render = async () => {
    const q = input.value;
    const my = ++seq;
    active = -1;
    input.removeAttribute("aria-activedescendant");
    if (!q.trim()) {
      results.innerHTML = d.hint ? `<p class="search-status">${escapeHtml(d.hint)}</p>` : "";
      setOpen(!opts.collapseWhenEmpty);
      return;
    }
    setOpen(true);
    let items: SearchItem[];
    try {
      const pending = loadIndex(lang);
      const timer = window.setTimeout(() => {
        if (my === seq) results.innerHTML = `<p class="search-status">${escapeHtml(d.loading || "…")}</p>`;
      }, 120);
      items = await pending;
      window.clearTimeout(timer);
    } catch {
      results.innerHTML = `<p class="search-status">${escapeHtml(d.empty || "")}</p>`;
      return;
    }
    if (my !== seq) return;
    const hits = runQuery(items, q, opts.limit);
    if (!hits.length) {
      results.innerHTML = `<p class="search-status">${escapeHtml(d.empty || "")}</p>`;
      return;
    }
    const base = results.id || "search";
    results.innerHTML = `<ul role="listbox" class="result-list">${hits
      .map(
        (h, i) =>
          `<li role="presentation"><a class="result" role="option" id="${base}-opt-${i}" aria-selected="false" href="${escapeHtml(h.url)}" data-group="${escapeHtml(h.group)}"><span class="result-head"><span class="result-kind" data-kind="${h.kind}"><span class="dot" aria-hidden="true"></span>${escapeHtml(h.kind === "thread" ? d.threadLabel || "" : d.entryLabel || "")}</span>${h.kind === "entry" ? `<span class="result-meta">${escapeHtml(h.meta)} · <span class="num">${escapeHtml(h.date)}</span></span>` : ""}</span><span class="result-title">${highlight(h.title, q)}</span>${h.text ? `<span class="result-text">${highlight(h.text, q)}</span>` : ""}</a></li>`,
      )
      .join("")}</ul>`;
  };

  let debounce = 0;
  input.addEventListener("input", () => {
    window.clearTimeout(debounce);
    debounce = window.setTimeout(render, 60);
  });
  input.addEventListener("focus", () => {
    loadIndex(lang).catch(() => undefined);
    if (input.value.trim()) setOpen(true);
  });
  input.addEventListener("keydown", (ev) => {
    if (ev.key === "ArrowDown") {
      ev.preventDefault();
      setActive(active + 1);
    } else if (ev.key === "ArrowUp") {
      ev.preventDefault();
      setActive(active - 1);
    } else if (ev.key === "Enter") {
      const list = options();
      const target = list[active] ?? (active === -1 ? list[0] : undefined);
      if (target) {
        ev.preventDefault();
        window.location.href = target.href;
      }
    } else if (ev.key === "Escape" && opts.collapseWhenEmpty) {
      if (input.value) {
        input.value = "";
        render();
      } else input.blur();
    }
  });
  if (opts.collapseWhenEmpty) {
    document.addEventListener("click", (ev) => {
      const t = ev.target as Node;
      if (!results.contains(t) && t !== input) setOpen(false);
    });
  }
  render();
}
