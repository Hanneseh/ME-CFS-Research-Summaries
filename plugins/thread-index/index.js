const marker = "THREAD_INDEX_PLACEHOLDER"

const groupNames = {
  "treatments-interventions": "Treatments & Interventions",
  "disease-models-mechanisms": "Disease Models & Mechanisms",
  "diagnostics-symptoms-care": "Diagnostics, Symptoms & Care Context",
}

function text(value) {
  return { type: "text", value }
}

function element(tagName, properties = {}, children = []) {
  return { type: "element", tagName, properties, children }
}

function dateValue(value) {
  if (!value) return null
  if (value instanceof Date) return value
  const parsed = new Date(String(value))
  return Number.isNaN(parsed.getTime()) ? null : parsed
}

function formatDate(value, locale) {
  const date = dateValue(value)
  if (!date) return String(value)
  return new Intl.DateTimeFormat(locale ?? "en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    timeZone: "UTC",
  }).format(date)
}

function hrefForSlug(slug) {
  return `./${slug.replace(/\/index$/, "/")}`
}

function threadGroup(slug) {
  return groupNames[slug.split("/")[0]] ?? "Research Thread"
}

function threadPages(componentData) {
  return componentData.allFiles
    .filter((page) => {
      const fm = page.frontmatter ?? {}
      return page.slug && page.slug.endsWith("/index") && fm.thread_status && fm.last_updated
    })
    .sort((a, b) => {
      const aDate = dateValue(a.frontmatter.last_updated)?.getTime() ?? 0
      const bDate = dateValue(b.frontmatter.last_updated)?.getTime() ?? 0
      if (aDate !== bDate) return bDate - aDate
      return String(a.frontmatter.title ?? "").localeCompare(String(b.frontmatter.title ?? ""))
    })
}

function buildThreadIndex(componentData) {
  const items = threadPages(componentData).map((page) => {
    const fm = page.frontmatter ?? {}
    const date = formatDate(fm.last_updated, componentData.cfg.locale)
    const status = threadGroup(page.slug)

    return element("li", { className: ["thread-index-item"] }, [
      element("span", { className: ["thread-index-date"] }, [text(date)]),
      text(" - "),
      element(
        "a",
        {
          href: hrefForSlug(page.slug),
          className: ["internal", "internal-link"],
        },
        [text(fm.title ?? page.slug)],
      ),
      element("span", { className: ["thread-index-group"] }, [text(` (${status})`)]),
    ])
  })

  return element("ul", { className: ["thread-index-list"] }, items)
}

function replaceMarker(root, slug, componentData) {
  if (slug !== "index") return

  function visit(parent) {
    if (!parent.children) return false

    for (let index = 0; index < parent.children.length; index += 1) {
      const child = parent.children[index]
      const childText =
        child.type === "element" &&
        child.children?.length === 1 &&
        child.children[0].type === "text"
          ? child.children[0].value.trim()
          : child.type === "text"
            ? child.value.trim()
            : ""

      if (childText === marker) {
        parent.children.splice(index, 1, buildThreadIndex(componentData))
        return true
      }

      if (visit(child)) return true
    }

    return false
  }

  visit(root)
}

function EmptyBody() {
  return () => null
}

export const ThreadIndex = () => ({
  name: "ThreadIndex",
  priority: -100,
  match: () => false,
  layout: "content",
  body: EmptyBody,
  treeTransforms: () => [replaceMarker],
})

export default ThreadIndex
