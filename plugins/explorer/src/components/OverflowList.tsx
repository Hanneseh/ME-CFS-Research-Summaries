import type { VNode, JSX } from "preact";

const OverflowList = ({
  children,
  ...props
}: JSX.HTMLAttributes<HTMLUListElement> & { id: string }) => {
  return (
    <ul {...props} class={[props.class, "overflow"].filter(Boolean).join(" ")} id={props.id}>
      {children}
      <li class="overflow-end" />
    </ul>
  );
};

let numLists = 0;

export interface OverflowListFactory {
  OverflowList: (props: JSX.HTMLAttributes<HTMLUListElement>) => VNode;
  overflowListAfterDOMLoaded: string;
}

export default (): OverflowListFactory => {
  const id = `list-${numLists++}`;

  return {
    OverflowList: (props: JSX.HTMLAttributes<HTMLUListElement>) => (
      <OverflowList {...props} id={id} />
    ),
    overflowListAfterDOMLoaded: `
document.addEventListener("nav", (e) => {
  const ul = document.getElementById("${id}")
  if (!ul) return

  const end = ul.querySelector(".overflow-end")
  if (!end) return

  const scrollContainer = ul.parentElement
  const observer = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      const parentUl = entry.target.parentElement
      if (!parentUl) return
      if (entry.isIntersecting) {
        parentUl.classList.remove("gradient-active")
      } else {
        parentUl.classList.add("gradient-active")
      }
    }
  }, scrollContainer ? { root: scrollContainer } : undefined)

  observer.observe(end)
  window.addCleanup(() => observer.disconnect())
})
`,
  };
};
