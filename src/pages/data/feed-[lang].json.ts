import type { APIRoute, GetStaticPaths } from "astro";
import { getSite } from "../../lib/content";
import { LANGS, type FeedPayload, type Lang } from "../../lib/types";

export const getStaticPaths = (() => LANGS.map((lang) => ({ params: { lang } }))) satisfies GetStaticPaths;

export const GET: APIRoute = ({ params }) => {
  const lang = params.lang as Lang;
  const site = getSite(lang);
  const payload: FeedPayload = {
    lang,
    generated: site.lastUpdated,
    total: site.entries.length,
    entries: site.entries,
  };
  return new Response(JSON.stringify(payload), { headers: { "Content-Type": "application/json; charset=utf-8" } });
};
