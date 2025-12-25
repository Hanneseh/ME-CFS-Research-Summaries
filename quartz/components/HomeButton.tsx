import { classNames } from "../util/lang"
import { pathToRoot } from "../util/path"

const HomeButton: QuartzComponent = ({ fileData, displayClass }: QuartzComponentProps) => {
  const baseDir = pathToRoot(fileData.slug!)
  return (
    <a href={baseDir} class={classNames(displayClass, "home-button")} title="Home">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="lucide lucide-house"
      >
        <path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8" />
        <path d="M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
      </svg>
    </a>
  )
}

HomeButton.css = `
.home-button {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--darkgray);
  transition: color 0.2s ease;
}

.home-button:hover {
  color: var(--secondary);
}

.home-button svg {
  width: 20px;
  height: 20px;
}
`

export default (() => HomeButton) satisfies QuartzComponentConstructor
