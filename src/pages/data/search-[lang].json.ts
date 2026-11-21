import type { APIRoute, GetStaticPaths } from "astro";
import { getSite } from "../../lib/content";
import { firstSentences, toPlain } from "../../lib/markdown";
import { normalize, wordSet } from "../../lib/render";
import { threadUrl } from "../../lib/paths";
import { LANGS, type Lang, type SearchItem, type SearchPayload } from "../../lib/types";

export const getStaticPaths = (() => LANGS.map((lang) => ({ params: { lang } }))) satisfies GetStaticPaths;

const strip = (html: string) => html.replace(/<[^>]+>/g, "").replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#39;/g, "'");

export const GET: APIRoute = ({ params }) => {
  const lang = params.lang as Lang;
  const site = getSite(lang);
  const groupTitle = new Map(site.groups.map((g) => [g.slug, g.title]));
  const items: SearchItem[] = [];

  for (const t of site.threads) {
    const title = strip(t.title);
    items.push({
      kind: "thread",
      title,
      text: firstSentences(t.plainSummaryText || strip(t.subtitle), 1, 60, 200),
      url: threadUrl(lang, t.slug),
      group: t.group,
      meta: t.topics.join(" · "),
      date: t.lastUpdated,
      h: [
        normalize(title),
        wordSet([...t.topics, ...t.aliases, groupTitle.get(t.group) ?? "", t.slug.replace(/-/g, " ")].join(" ")),
        wordSet([strip(t.subtitle), t.plainSummaryText, toPlain(strip(t.takeaway))].join(" "), title),
      ],
    });
  }

  for (const t of site.threads) {
    for (const e of t.entries) {
      const title = strip(e.title);
      items.push({
        kind: "entry",
        title,
        text: firstSentences(strip(e.summary), 1, 60, 180),
        url: e.url,
        group: e.group,
        meta: e.threadTitle,
        date: e.dateLabel,
        h: [normalize(title), wordSet([e.threadTitle, e.typeLabel, e.design ?? ""].join(" ")), wordSet(t.entryText[e.id] ?? "", title)],
      });
    }
  }

  const payload: SearchPayload = { lang, items };
  return new Response(JSON.stringify(payload), { headers: { "Content-Type": "application/json; charset=utf-8" } });
};
