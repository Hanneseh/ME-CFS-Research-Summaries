import { joinSegments, pathToRoot } from "../util/path"
import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { classNames } from "../util/lang"

const ArticleTitle: QuartzComponent = ({ fileData, displayClass }: QuartzComponentProps) => {
  const title = fileData.frontmatter?.title
  const baseDir = pathToRoot(fileData.slug!)
  const isTagPage = fileData.slug?.startsWith("tags/") && fileData.slug !== "tags/index"
  if (title) {
    return (
      <h1 class={classNames(displayClass, "article-title")}>
        {title}
        {isTagPage && (
          <a href={joinSegments(baseDir, "summaries/")} class="tag-clear-button" title="Clear tag selection">
            ✕
          </a>
        )}
      </h1>
    )
  } else {
    return null
  }
}

ArticleTitle.css = `
.article-title {
  margin: 2rem 0 0 0;
  display: flex;
  align-items: center;
}
.tag-clear-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.2rem;
  height: 1.2rem;
  margin-left: 0.75rem;
  border-radius: 50%;
  background-color: var(--highlight);
  color: var(--light);
  font-size: 0.8rem;
  text-decoration: none;
  line-height: 1;
  font-weight: normal;
  transition: background-color 0.2s ease;
}
.tag-clear-button:hover {
  background-color: var(--secondary);
}
`

export default (() => ArticleTitle) satisfies QuartzComponentConstructor
