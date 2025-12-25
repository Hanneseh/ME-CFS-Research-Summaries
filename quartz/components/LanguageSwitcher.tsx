import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { i18n } from "../i18n"
import { classNames } from "../util/lang"

export default (() => {
  const LanguageSwitcher: QuartzComponent = ({ displayClass, cfg }: QuartzComponentProps) => {
    return (
      <div class={classNames(displayClass, "language-switcher")}>
        <a href="/en">English</a>
        <span> | </span>
        <a href="/de">Deutsch</a>
      </div>
    )
  }

  LanguageSwitcher.css = `
  .language-switcher {
    display: flex;
    gap: 0.5rem;
    align-items: center;
    font-family: var(--headerFont);
    font-weight: 600;
  }
  .language-switcher a {
    text-decoration: none;
    color: var(--darkgray);
  }
  .language-switcher a:hover {
    color: var(--secondary);
  }
  `
  return LanguageSwitcher
}) satisfies QuartzComponentConstructor
