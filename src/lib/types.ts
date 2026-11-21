// Shared, serialisable types. Safe to import from client scripts.

export type Lang = "de" | "en";
export const LANGS: Lang[] = ["de", "en"];

export interface SourceLink {
  label: string;
  url: string;
  domain: string;
  kind: string;
}

/** One research entry, already localised and rendered to HTML. Used for SSR and the feed JSON. */
export interface FeedEntry {
  id: string;
  date: string;
  dateLabel: string;
  year: string;
  type: string;
  typeLabel: string;
  design: string | null;
  title: string;
  summary: string;
  detail: string;
  sources: SourceLink[];
  thread: string;
  threadTitle: string;
  group: string;
  url: string;
  /** Set when the entry was added or upgraded in the newest research update. */
  batch?: UpdateAction;
  /** Set when this entry is shown in a fallback language. */
  contentLang?: Lang;
}

export type UpdateAction = "added" | "upgraded";

export interface FeedPayload {
  lang: Lang;
  generated: string;
  total: number;
  entries: FeedEntry[];
}

export interface SearchItem {
  kind: "thread" | "entry";
  title: string;
  /** Short plain-text snippet. */
  text: string;
  url: string;
  group: string;
  /** Thread title for entries, joined topics for threads. */
  meta: string;
  date: string;
  /** Normalised haystacks: title, keywords, body. */
  h: [string, string, string];
}

export interface SearchPayload {
  lang: Lang;
  items: SearchItem[];
}

export interface CardStrings {
  details: string;
  detailsThread: string;
  toThread: string;
  sources: string;
  openSource: string;
  batchAdded: string;
  batchUpgraded: string;
}
