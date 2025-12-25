import { PageLayout, SharedLayout } from "./quartz/cfg"
import * as Component from "./quartz/components"

// components shared across all pages
export const sharedPageComponents: SharedLayout = {
  head: Component.Head(),
  header: [
    Component.Flex({
      direction: "row",
      components: [
        { Component: Component.PageTitle(), grow: true },
        { Component: Component.Search() },
        { Component: Component.HomeButton() },
        { Component: Component.Darkmode() },
      ],
    }),
  ],
  afterBody: [],
  footer: Component.Footer({
    links: {
      Home: "/",
      GitHub: "https://github.com/hanneseh/ME-CFS-Research-Summaries",
      Imprint: "/imprint",
    },
  }),
}

// components for pages that display a single page (e.g. a single note)
export const defaultContentPageLayout: PageLayout = {
  beforeBody: [
    Component.ArticleTitle(),
    Component.TagList(),
    Component.ContentMeta(),
  ],
  left: [],
  right: [],
}

// components for pages that display lists of pages  (e.g. tags or folders)
export const defaultListPageLayout: PageLayout = {
  beforeBody: [
    Component.ArticleTitle(),
    //Component.ContentMeta(),
  ],
  left: [],
  right: [],
}
