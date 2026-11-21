import type { CardStrings, Lang } from "./types";

const MONTHS: Record<Lang, string[]> = {
  de: ["Jan", "Feb", "März", "Apr", "Mai", "Juni", "Juli", "Aug", "Sep", "Okt", "Nov", "Dez"],
  en: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
};

function parts(iso: string): [number, number, number] | null {
  const m = /^(\d{4})-(\d{2})(?:-(\d{2}))?/.exec(iso.trim());
  if (!m) return null;
  return [Number(m[1]), Number(m[2]), m[3] ? Number(m[3]) : 0];
}

function exact(y: number, mo: number, d: number, lang: Lang): string {
  if (lang === "de") return `${String(d).padStart(2, "0")}.${String(mo).padStart(2, "0")}.${y}`;
  return `${d} ${MONTHS.en[mo - 1]} ${y}`;
}

export function formatMonth(iso: string, lang: Lang): string {
  const p = parts(iso);
  if (!p) return iso;
  return `${MONTHS[lang][p[1] - 1]} ${p[0]}`;
}

/** Formats an entry date honouring its precision ("Before 2025-06-01", "2025-10", exact). */
export function formatEntryDate(
  date: string,
  lang: Lang,
  precision: string = "exact",
  display?: string | null,
): string {
  const raw = (display ?? "").trim();
  if (precision === "before" || /^before\s/i.test(raw)) {
    const p = parts(raw.replace(/^before\s+/i, "")) ?? parts(date);
    if (!p) return raw || date;
    const word = lang === "de" ? "Vor" : "Before";
    return p[2] ? `${word} ${exact(p[0], p[1], p[2], lang)}` : `${word} ${formatMonth(raw.replace(/^before\s+/i, ""), lang)}`;
  }
  if (precision === "month" || /^\d{4}-\d{2}$/.test(raw)) return formatMonth(raw || date, lang);
  if (precision === "year" || /^\d{4}$/.test(raw)) return (raw || date).slice(0, 4);
  const p = parts(date) ?? parts(raw);
  if (!p) return raw || date;
  return p[2] ? exact(p[0], p[1], p[2], lang) : formatMonth(date, lang);
}

export function formatDate(iso: string, lang: Lang): string {
  return formatEntryDate(iso, lang, "exact");
}

const SOURCE_TYPES: Record<string, Record<Lang, string>> = {
  paper: { de: "Studie", en: "Study" },
  preprint: { de: "Preprint", en: "Preprint" },
  review: { de: "Review", en: "Review" },
  conference: { de: "Konferenz", en: "Conference" },
  report: { de: "Bericht", en: "Report" },
  announcement: { de: "Mitteilung", en: "Announcement" },
  guideline: { de: "Leitlinie", en: "Guideline" },
  trial_registry: { de: "Studienregister", en: "Trial registry" },
  clinical_trial: { de: "Klinische Studie", en: "Clinical trial" },
  video: { de: "Video", en: "Video" },
  other: { de: "Sonstiges", en: "Other" },
};

export function sourceTypeLabel(type: string | null | undefined, lang: Lang): string {
  const key = (type ?? "other").trim();
  return SOURCE_TYPES[key]?.[lang] ?? key.replace(/_/g, " ").replace(/^\w/, (c) => c.toUpperCase());
}

const DESIGNS_DE: Record<string, string> = {
  "cohort study": "Kohortenstudie",
  "cross-sectional study": "Querschnittsstudie",
  "systematic review": "Systematisches Review",
  "meta-analysis": "Metaanalyse",
  "trial registry": "Studienregister",
  "case series": "Fallserie",
  "case report": "Fallbericht",
  "phase iii rct": "Phase-III-RCT",
  "case-control study": "Fall-Kontroll-Studie",
  "open-label trial": "Offene Studie",
  "pilot study": "Pilotstudie",
};

export function studyDesignLabel(design: string | null | undefined, sourceType: string, lang: Lang): string | null {
  if (!design) return null;
  const d = design.trim();
  if (!d) return null;
  const k = d.toLowerCase();
  // Avoid "Preprint · Preprint" style duplicates.
  if (k === sourceType.toLowerCase().replace(/_/g, " ")) return null;
  if (k === "trial registry" && sourceType === "trial_registry") return null;
  if (lang === "de") return DESIGNS_DE[k] ?? d;
  return d;
}

export const TERM_CATEGORIES: Record<string, Record<Lang, string>> = {
  symptom: { de: "Symptome", en: "Symptoms" },
  research: { de: "Forschung", en: "Research" },
  biology: { de: "Biologie", en: "Biology" },
  diagnostic: { de: "Diagnostik", en: "Diagnostics" },
  care: { de: "Versorgung", en: "Care" },
};

export function categoryLabel(cat: string, lang: Lang): string {
  return TERM_CATEGORIES[cat]?.[lang] ?? cat;
}

const STRINGS = {
  de: {
    htmlLang: "de",
    brand: "ME/CFS-Forschung",
    siteTitle: "ME/CFS-Forschung",
    siteDescription:
      "Laufend aktualisierte Zusammenfassungen der ME/CFS- und Long-COVID-Forschung mit Originalquellen.",
    nav: { overview: "Übersicht", updates: "Updates", feed: "Feed", glossary: "Glossar", imprint: "Impressum" },
    skip: "Zum Inhalt springen",
    menu: "Menü",
    closeMenu: "Menü schließen",
    search: "Suche",
    searchOpen: "Suche öffnen",
    searchPlaceholder: "Suchen …",
    searchEmpty: "Keine Treffer.",
    searchLoading: "Suche wird geladen …",
    searchThread: "Thema",
    searchEntry: "Eintrag",
    searchClose: "Schließen",
    langSwitch: "Sprache",
    themeToggle: "Hell- oder Dunkelmodus umschalten",
    heroTitle: "ME/CFS-Forschung",
    howToggle: "So funktioniert’s",
    howUpdatesTitle: "Updates",
    howUpdatesText: "Erscheinen wöchentlich und fassen zusammen, was neu dazugekommen ist – für regelmäßige Besuche.",
    howFeedTitle: "Feed",
    howFeedText: "Alle einzelnen Studien, Preprints und Berichte aus verschiedenen Quellen, chronologisch und filterbar.",
    howTopicsTitle: "Themen",
    howTopicsText: "Dieselben Einträge nach Forschungsbereich gebündelt, jeweils mit aktueller Einordnung.",
    latestTitle: "Neueste Einträge",
    filterAll: "Alle",
    showMore: "Mehr laden",
    exploreFeed: "Alle Einträge →",
    threadsTitle: "Themen",
    viewByGroup: "Nach Bereich",
    viewRecent: "Zuletzt aktualisiert",
    entries: (n: number) => (n === 1 ? "1 Eintrag" : `${n} Einträge`),
    noteTitle: "Zur Einordnung",
    noteText:
      "Laufende Zusammenfassungen zur ME/CFS- und Long-COVID-Forschung mit Originalquellen. Keine medizinische Beratung – viele Befunde sind vorläufig.",
    noteGlossary: "Evidenz-Stufen",
    noteImprint: "Impressum",
    breadcrumbHome: "Übersicht",
    stand: "Stand",
    plainTitle: "Kurz erklärt",
    takeawayTitle: "Aktuelle Einordnung",
    whyTitle: "Warum das wichtig ist",
    evidenceTitle: "Stand der Evidenz",
    timelineTitle: "Forschungsverlauf",
    sortNewest: "Neueste zuerst",
    sortOldest: "Chronologisch",
    sortLabel: "Sortierung",
    filterKeyword: "Filtern …",
    filterType: "Quellenart",
    expandAll: "Alle Details ausklappen",
    collapseAll: "Alle Details einklappen",
    showNext: (n: number) => `Weitere ${n} anzeigen`,
    showAll: (n: number) => `Alle ${n} Einträge anzeigen`,
    showing: (a: number, b: number) => `${a} von ${b} ${b === 1 ? "Eintrag" : "Einträgen"}`,
    noMatches: "Keine Treffer für diesen Filter.",
    resetFilters: "Filter zurücksetzen",
    openQuestions: "Offene Fragen",
    relatedThreads: "Verwandte Themen",
    topics: "Themen",
    feedTitle: "Feed",
    feedDescription: "Alle Forschungs-Einträge zu ME/CFS und Long COVID, durchsuchbar und filterbar.",
    feedSearch: "Einträge durchsuchen …",
    feedThread: "Thema",
    feedAllThreads: "Alle Themen",
    feedType: "Quellenart",
    feedAllTypes: "Alle Quellenarten",
    feedYear: "Jahr",
    feedAllYears: "Alle Jahre",
    feedSort: "Sortierung",
    newest: "Neueste zuerst",
    oldest: "Älteste zuerst",
    loadMore: (n: number) => `${n} weitere laden`,
    tpl: {
      showNext: "Weitere {n} anzeigen",
      showAll: "Alle {n} Einträge anzeigen",
      showing: "{a} von {b} Einträgen",
      showingOne: "{a} von {b} Eintrag",
      loadMore: "{n} weitere laden",
    },
    glossaryTitle: "Glossar",
    glossaryDescription: "Evidenz-Stufen und Fachbegriffe zur ME/CFS- und Long-COVID-Forschung.",
    tiersTitle: "Evidenz-Stufen",
    termsTitle: "Begriffe",
    termsSearch: "Begriff suchen …",
    termsEmpty: "Kein Begriff gefunden.",
    imprintTitle: "Impressum & Hinweise",
    footerAbout:
      "Unabhängige Zusammenfassungen der ME/CFS- und Long-COVID-Forschung. Keine medizinische Beratung.",
    footerSite: "Diese Seite",
    footerCommunity: "Weiterlesen",
    footerContact: "Kontakt",
    footerLicense: "Eigene Texte gemeinfrei unter CC0 1.0.",
    footerSource: "Quellcode auf GitHub",
    card: {
      details: "Details & Quellen",
      detailsThread: "Details",
      toThread: "Zum Thema →",
      sources: "Quellen",
      openSource: "öffnet in neuem Tab",
      batchAdded: "Neu",
      batchUpgraded: "Aktualisiert",
    } satisfies CardStrings,
    upd: {
      eyebrowLatest: (d: string) => `Update · ${d}`,
      period: "Zeitraum",
      readSummary: "Weiterlesen →",
      allUpdates: "Alle Updates",
      archiveTitle: "Updates",
      archiveDescription: "Zusammenfassungen neuer Einträge in der ME/CFS- und Long-COVID-Forschung.",
      archiveEmpty: "Noch keine Updates veröffentlicht.",
      latestBadge: "Aktuell",
      highlightsTitle: "Das Wichtigste",
      toEntries: "Einträge",
      caveatsTitle: "Was man überspringen kann",
      entriesTitle: "Einträge",
      itemAdded: "Neu",
      itemUpgraded: "Aktualisiert",
      back: "← Alle Updates",
      breadcrumb: "Updates",
    },
    fallbackNote: "Dieser Inhalt ist noch nicht übersetzt und wird auf Englisch angezeigt.",
    redirecting: "Weiterleitung …",
    chooseLang: "Sprache wählen",
    notFoundTitle: "Seite nicht gefunden",
    notFoundText: "Diese Seite gibt es nicht (mehr).",
  },
  en: {
    htmlLang: "en",
    brand: "ME/CFS Research",
    siteTitle: "ME/CFS Research",
    siteDescription:
      "Continuously updated summaries of ME/CFS and Long COVID research with primary sources.",
    nav: { overview: "Overview", updates: "Updates", feed: "Feed", glossary: "Glossary", imprint: "Imprint" },
    skip: "Skip to content",
    menu: "Menu",
    closeMenu: "Close menu",
    search: "Search",
    searchOpen: "Open search",
    searchPlaceholder: "Search …",
    searchEmpty: "No results.",
    searchLoading: "Loading search …",
    searchThread: "Topic",
    searchEntry: "Entry",
    searchClose: "Close",
    langSwitch: "Language",
    themeToggle: "Toggle light or dark mode",
    heroTitle: "ME/CFS Research",
    howToggle: "How it works",
    howUpdatesTitle: "Updates",
    howUpdatesText: "Published weekly to summarise what has been added – built for regular visits.",
    howFeedTitle: "Feed",
    howFeedText: "All individual studies, preprints and reports from across sources, chronological and filterable.",
    howTopicsTitle: "Topics",
    howTopicsText: "The same entries grouped by research area, each with a current synthesis.",
    latestTitle: "Latest Entries",
    filterAll: "All",
    showMore: "Show more",
    exploreFeed: "All entries →",
    threadsTitle: "Topics",
    viewByGroup: "By area",
    viewRecent: "Recently updated",
    entries: (n: number) => (n === 1 ? "1 entry" : `${n} entries`),
    noteTitle: "About",
    noteText:
      "Ongoing summaries of ME/CFS and Long COVID research with primary sources. Not medical advice – many findings are preliminary.",
    noteGlossary: "Evidence levels",
    noteImprint: "Imprint",
    breadcrumbHome: "Overview",
    stand: "Updated",
    plainTitle: "In Plain Terms",
    takeawayTitle: "Current Takeaway",
    whyTitle: "Why This Matters",
    evidenceTitle: "State of Evidence",
    timelineTitle: "Research Timeline",
    sortNewest: "Newest first",
    sortOldest: "Oldest first",
    sortLabel: "Sort order",
    filterKeyword: "Filter …",
    filterType: "Source type",
    expandAll: "Expand all details",
    collapseAll: "Collapse all details",
    showNext: (n: number) => `Show ${n} more`,
    showAll: (n: number) => `Show all ${n} entries`,
    showing: (a: number, b: number) => `${a} of ${b} ${b === 1 ? "entry" : "entries"}`,
    noMatches: "No entries match this filter.",
    resetFilters: "Reset filters",
    openQuestions: "Open Questions",
    relatedThreads: "Related Topics",
    topics: "Topics",
    feedTitle: "Feed",
    feedDescription: "All ME/CFS and Long COVID research entries, searchable and filterable.",
    feedSearch: "Search entries …",
    feedThread: "Topic",
    feedAllThreads: "All topics",
    feedType: "Source type",
    feedAllTypes: "All source types",
    feedYear: "Year",
    feedAllYears: "All years",
    feedSort: "Sort",
    newest: "Newest first",
    oldest: "Oldest first",
    loadMore: (n: number) => `Show ${n} more`,
    tpl: {
      showNext: "Show {n} more",
      showAll: "Show all {n} entries",
      showing: "{a} of {b} entries",
      showingOne: "{a} of {b} entry",
      loadMore: "Show {n} more",
    },
    glossaryTitle: "Glossary",
    glossaryDescription: "Evidence levels and terminology for ME/CFS and Long COVID research.",
    tiersTitle: "Evidence Levels",
    termsTitle: "Terms",
    termsSearch: "Search terms …",
    termsEmpty: "No matching term.",
    imprintTitle: "Legal Notice & Disclaimer",
    footerAbout: "Independent summaries of ME/CFS and Long COVID research. Not medical advice.",
    footerSite: "This site",
    footerCommunity: "Further reading",
    footerContact: "Contact",
    footerLicense: "Own texts dedicated to the public domain under CC0 1.0.",
    footerSource: "Source on GitHub",
    card: {
      details: "Details & sources",
      detailsThread: "Details",
      toThread: "Go to topic →",
      sources: "Sources",
      openSource: "opens in a new tab",
      batchAdded: "New",
      batchUpgraded: "Upgraded",
    } satisfies CardStrings,
    upd: {
      eyebrowLatest: (d: string) => `Update · ${d}`,
      period: "Period",
      readSummary: "Read update →",
      allUpdates: "All updates",
      archiveTitle: "Updates",
      archiveDescription: "Summaries of new entries in ME/CFS and Long COVID research.",
      archiveEmpty: "No updates published yet.",
      latestBadge: "Latest",
      highlightsTitle: "Key Points",
      toEntries: "Entries",
      caveatsTitle: "What you can skip",
      entriesTitle: "Entries",
      itemAdded: "New",
      itemUpgraded: "Upgraded",
      back: "← All updates",
      breadcrumb: "Updates",
    },
    fallbackNote: "This content is not yet translated and is shown in English.",
    redirecting: "Redirecting …",
    chooseLang: "Choose language",
    notFoundTitle: "Page not found",
    notFoundText: "This page does not exist (any more).",
  },
};

export type Strings = (typeof STRINGS)["en"];

export function t(lang: Lang): Strings {
  return STRINGS[lang] as Strings;
}

export function otherLang(lang: Lang): Lang {
  return lang === "de" ? "en" : "de";
}
