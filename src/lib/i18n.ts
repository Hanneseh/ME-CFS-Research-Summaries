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
    brand: "ME/CFS Forschung",
    siteTitle: "ME/CFS Forschung – verständliche Forschungszusammenfassungen",
    siteDescription:
      "Ruhig aufbereitete, laufend aktualisierte Zusammenfassungen der ME/CFS- und Long-COVID-Forschung – verständlich für Betroffene und Angehörige, mit Quellen für Fachleute.",
    nav: { overview: "Übersicht", feed: "Feed", glossary: "Glossar", imprint: "Impressum" },
    skip: "Zum Inhalt springen",
    menu: "Menü",
    closeMenu: "Menü schließen",
    search: "Suche",
    searchOpen: "Suche öffnen",
    searchPlaceholder: "Stränge, Themen und Einträge durchsuchen …",
    searchHint: "Zum Beispiel „PEM“, „Rituximab“ oder „Mikrogerinnsel“",
    searchEmpty: "Keine Treffer. Versuche einen anderen Begriff.",
    searchLoading: "Suche wird geladen …",
    searchThread: "Strang",
    searchEntry: "Eintrag",
    searchClose: "Schließen",
    langSwitch: "Sprache",
    themeToggle: "Hell- oder Dunkelmodus umschalten",
    heroTitle: "ME/CFS-Forschung, ruhig und verständlich erklärt",
    heroLead:
      "Hier wird die aktuelle Forschung zu ME/CFS und Long COVID gesammelt, eingeordnet und in einfacher Sprache zusammengefasst. Jeder Eintrag zeigt kurz, was neu ist – und bei Bedarf die fachlichen Details mit Quellen.",
    statThreads: "Forschungsstränge",
    statEntries: "kuratierte Einträge",
    statUpdated: "Stand",
    latestTitle: "Was zuletzt passiert ist",
    latestLead: "Die neuesten Einträge aus allen Forschungssträngen, neueste zuerst.",
    filterAll: "Alle",
    showMore: "Mehr laden",
    exploreFeed: "Gesamten Feed durchsuchen →",
    threadsTitle: "Forschungsstränge im Überblick",
    threadsLead: "Jeder Strang bündelt ein Thema und wird fortlaufend ergänzt.",
    viewByGroup: "Nach Bereich",
    viewRecent: "Zuletzt aktualisiert",
    lastUpdated: "Zuletzt aktualisiert",
    entries: (n: number) => (n === 1 ? "1 Eintrag" : `${n} Einträge`),
    noteTitle: "Zur Einordnung",
    noteText:
      "Diese Seite ist eine kuratierte Zusammenfassung veröffentlichter Forschung und ersetzt keine ärztliche Beratung. Viele Ergebnisse sind vorläufig. Die Evidenz-Kennzeichnung zeigt, wie belastbar ein Befund ist.",
    noteGlossary: "Evidenz-Stufen verstehen",
    noteImprint: "Impressum & Haftung",
    breadcrumbHome: "Übersicht",
    stand: "Stand",
    plainTitle: "Kurz erklärt",
    takeawayTitle: "Aktuelle Einordnung",
    whyTitle: "Warum das wichtig ist",
    evidenceTitle: "Stand der Evidenz",
    timelineTitle: "Forschungsverlauf",
    timelineLead: "Alle Einträge dieses Strangs. Die fachlichen Details lassen sich bei Bedarf aufklappen.",
    sortNewest: "Neueste zuerst",
    sortOldest: "Chronologisch",
    sortLabel: "Sortierung",
    filterKeyword: "In diesem Strang filtern …",
    filterType: "Quellenart",
    expandAll: "Alle Details ausklappen",
    collapseAll: "Alle Details einklappen",
    showNext: (n: number) => `Weitere ${n} anzeigen`,
    showAll: (n: number) => `Alle ${n} Einträge anzeigen`,
    showing: (a: number, b: number) => `Zeige ${a} von ${b} ${b === 1 ? "Eintrag" : "Einträgen"}`,
    noMatches: "Keine Einträge passen zu diesem Filter.",
    resetFilters: "Filter zurücksetzen",
    openQuestions: "Offene Fragen",
    relatedThreads: "Verwandte Stränge",
    topics: "Themen",
    feedTitle: "Forschungs-Feed",
    feedLead: "Alle Einträge aus allen Strängen an einem Ort – durchsuchbar und filterbar.",
    feedSearch: "Einträge durchsuchen …",
    feedThread: "Strang",
    feedAllThreads: "Alle Stränge",
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
      showing: "Zeige {a} von {b} Einträgen",
      showingOne: "Zeige {a} von {b} Eintrag",
      loadMore: "{n} weitere laden",
    },
    glossaryTitle: "Glossar & Lesehilfe",
    glossaryLead: "Fachbegriffe in einfacher Sprache und eine Erklärung, wie die Evidenz-Kennzeichnungen zu lesen sind.",
    tiersTitle: "Wie stark sind die Hinweise?",
    tiersLead:
      "Jeder Forschungsstrang trägt eine Kennzeichnung. Sie beschreibt, wie belastbar die Befunde insgesamt sind – von breitem Konsens bis zur frühen Hypothese.",
    termsTitle: "Begriffe",
    termsSearch: "Begriff suchen …",
    termsEmpty: "Kein Begriff gefunden.",
    imprintTitle: "Impressum & Hinweise",
    footerAbout:
      "Unabhängige, kuratierte Zusammenfassungen der ME/CFS- und Long-COVID-Forschung. Keine medizinische Beratung.",
    footerSite: "Diese Seite",
    footerCommunity: "Weiterlesen",
    footerContact: "Kontakt",
    footerLicense: "Eigene Texte gemeinfrei unter CC0 1.0.",
    footerSource: "Quellcode auf GitHub",
    card: {
      details: "Fachliche Details & Quellen",
      detailsThread: "Fachliche Details",
      toThread: "Zum Strang →",
      sources: "Quellen",
      openSource: "öffnet in neuem Tab",
    } satisfies CardStrings,
    fallbackNote: "Dieser Inhalt ist noch nicht übersetzt und wird auf Englisch angezeigt.",
    redirecting: "Weiterleitung …",
    chooseLang: "Sprache wählen",
    notFoundTitle: "Seite nicht gefunden",
    notFoundText: "Diese Seite gibt es nicht (mehr). Vielleicht hilft die Übersicht oder die Suche weiter.",
  },
  en: {
    htmlLang: "en",
    brand: "ME/CFS Research",
    siteTitle: "ME/CFS Research – plain-language research summaries",
    siteDescription:
      "Calm, continuously updated summaries of ME/CFS and Long COVID research – readable for patients and families, with sources for researchers.",
    nav: { overview: "Overview", feed: "Feed", glossary: "Glossary", imprint: "Imprint" },
    skip: "Skip to content",
    menu: "Menu",
    closeMenu: "Close menu",
    search: "Search",
    searchOpen: "Open search",
    searchPlaceholder: "Search threads, topics and entries …",
    searchHint: "For example “PEM”, “rituximab” or “microclots”",
    searchEmpty: "No results. Try another term.",
    searchLoading: "Loading search …",
    searchThread: "Thread",
    searchEntry: "Entry",
    searchClose: "Close",
    langSwitch: "Language",
    themeToggle: "Toggle light or dark mode",
    heroTitle: "ME/CFS research, calmly explained",
    heroLead:
      "This site collects, weighs and summarises current research on ME/CFS and Long COVID in plain language. Every entry says briefly what is new – with the technical detail and sources one click away.",
    statThreads: "research threads",
    statEntries: "curated entries",
    statUpdated: "Updated",
    latestTitle: "Latest Research Feed",
    latestLead: "The newest entries across all research threads, newest first.",
    filterAll: "All",
    showMore: "Show more",
    exploreFeed: "Explore full feed →",
    threadsTitle: "Research Threads",
    threadsLead: "Each thread follows one topic and is updated as new research appears.",
    viewByGroup: "By area",
    viewRecent: "Recently updated",
    lastUpdated: "Last updated",
    entries: (n: number) => (n === 1 ? "1 entry" : `${n} entries`),
    noteTitle: "How to read this site",
    noteText:
      "This is a curated synthesis of published research, not medical advice. Many findings are preliminary. The evidence badge on each thread shows how robust the findings are.",
    noteGlossary: "Understand evidence badges",
    noteImprint: "Imprint & liability",
    breadcrumbHome: "Overview",
    stand: "Updated",
    plainTitle: "In Plain Terms",
    takeawayTitle: "Current Takeaway",
    whyTitle: "Why This Matters",
    evidenceTitle: "State of Evidence",
    timelineTitle: "Research Timeline",
    timelineLead: "Every entry in this thread. Expand the technical detail whenever you need it.",
    sortNewest: "Newest first",
    sortOldest: "Oldest first",
    sortLabel: "Sort order",
    filterKeyword: "Filter this thread …",
    filterType: "Source type",
    expandAll: "Expand all details",
    collapseAll: "Collapse all details",
    showNext: (n: number) => `Show ${n} more`,
    showAll: (n: number) => `Show all ${n} entries`,
    showing: (a: number, b: number) => `Showing ${a} of ${b} ${b === 1 ? "entry" : "entries"}`,
    noMatches: "No entries match this filter.",
    resetFilters: "Reset filters",
    openQuestions: "Open Questions",
    relatedThreads: "Related Threads",
    topics: "Topics",
    feedTitle: "Research Feed",
    feedLead: "Every entry from every thread in one place – searchable and filterable.",
    feedSearch: "Search entries …",
    feedThread: "Thread",
    feedAllThreads: "All threads",
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
      showing: "Showing {a} of {b} entries",
      showingOne: "Showing {a} of {b} entry",
      loadMore: "Show {n} more",
    },
    glossaryTitle: "Glossary & Reading Guide",
    glossaryLead: "Technical terms in plain language, and a guide to reading the evidence badges.",
    tiersTitle: "How to read evidence badges",
    tiersLead:
      "Every research thread carries a badge. It describes how robust the findings are overall – from broad consensus to early hypothesis.",
    termsTitle: "Terms",
    termsSearch: "Search terms …",
    termsEmpty: "No matching term.",
    imprintTitle: "Legal Notice & Disclaimer",
    footerAbout: "Independent, curated summaries of ME/CFS and Long COVID research. Not medical advice.",
    footerSite: "This site",
    footerCommunity: "Further reading",
    footerContact: "Contact",
    footerLicense: "Own texts dedicated to the public domain under CC0 1.0.",
    footerSource: "Source on GitHub",
    card: {
      details: "Technical detail & sources",
      detailsThread: "Full technical detail",
      toThread: "Go to thread →",
      sources: "Sources",
      openSource: "opens in a new tab",
    } satisfies CardStrings,
    fallbackNote: "This content is not yet translated and is shown in English.",
    redirecting: "Redirecting …",
    chooseLang: "Choose language",
    notFoundTitle: "Page not found",
    notFoundText: "This page does not exist (any more). The overview or the search may help.",
  },
};

export type Strings = (typeof STRINGS)["en"];

export function t(lang: Lang): Strings {
  return STRINGS[lang] as Strings;
}

export function otherLang(lang: Lang): Lang {
  return lang === "de" ? "en" : "de";
}
