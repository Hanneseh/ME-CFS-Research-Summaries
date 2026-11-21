// Global behaviour: theme toggle, language memory, mobile menu, search dialog.
import { mountSearch } from "./search";

const root = document.documentElement;

// ----- theme -----
const media = window.matchMedia("(prefers-color-scheme: dark)");
const stored = () => {
  try {
    return localStorage.getItem("theme");
  } catch {
    return null;
  }
};
const applyTheme = (theme: "light" | "dark") => {
  root.dataset.theme = theme;
  document.querySelector('meta[name="theme-color"]')?.setAttribute("content", theme === "dark" ? "#121618" : "#FAF9F5");
  document.querySelectorAll<HTMLButtonElement>("[data-theme-toggle]").forEach((b) => b.setAttribute("aria-pressed", String(theme === "dark")));
};
applyTheme(root.dataset.theme === "dark" ? "dark" : "light");
media.addEventListener("change", (e) => {
  if (!stored()) applyTheme(e.matches ? "dark" : "light");
});
document.querySelectorAll<HTMLButtonElement>("[data-theme-toggle]").forEach((btn) =>
  btn.addEventListener("click", () => {
    const next = root.dataset.theme === "dark" ? "light" : "dark";
    applyTheme(next);
    try {
      localStorage.setItem("theme", next);
    } catch {
      /* private mode */
    }
  }),
);

// ----- language switch: remember choice and keep the hash (e.g. entry deep links) -----
document.querySelectorAll<HTMLAnchorElement>("[data-lang-link]").forEach((a) =>
  a.addEventListener("click", (ev) => {
    const lang = a.dataset.langLink;
    try {
      if (lang) localStorage.setItem("lang", lang);
    } catch {
      /* ignore */
    }
    if (location.hash && !a.href.includes("#")) {
      ev.preventDefault();
      location.href = a.href + location.hash;
    }
  }),
);

// ----- mobile menu -----
const menuBtn = document.querySelector<HTMLButtonElement>("[data-menu-toggle]");
const menu = document.getElementById("mobile-menu");
if (menuBtn && menu) {
  const set = (open: boolean) => {
    menu.hidden = !open;
    menuBtn.setAttribute("aria-expanded", String(open));
    menuBtn.setAttribute("aria-label", open ? menuBtn.dataset.labelClose || "" : menuBtn.dataset.labelOpen || "");
  };
  menuBtn.addEventListener("click", () => set(menu.hidden));
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !menu.hidden) {
      set(false);
      menuBtn.focus();
    }
  });
  menu.querySelectorAll("a").forEach((a) => a.addEventListener("click", () => set(false)));
}

// ----- search dialog -----
const dialog = document.getElementById("search-dialog") as HTMLDialogElement | null;
const dInput = document.getElementById("search-dialog-input") as HTMLInputElement | null;
const dResults = document.getElementById("search-dialog-results");
if (dialog && dInput && dResults) {
  mountSearch(dInput, dResults, { limit: 24 });
  const open = () => {
    if (dialog.open) return;
    // On the homepage, prefer the inline hero search when it is visible.
    const hero = document.getElementById("hero-search-input") as HTMLInputElement | null;
    if (hero) {
      const r = hero.getBoundingClientRect();
      if (r.top >= 64 && r.bottom <= window.innerHeight) {
        hero.focus();
        return;
      }
    }
    dialog.showModal();
    dInput.focus();
    dInput.select();
  };
  document.querySelectorAll("[data-search-open]").forEach((b) => b.addEventListener("click", open));
  dialog.querySelector("[data-search-close]")?.addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", (e) => {
    if (e.target === dialog) dialog.close();
  });
  document.addEventListener("keydown", (e) => {
    const target = e.target as HTMLElement;
    const typing = target.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName);
    if ((e.key === "k" || e.key === "K") && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      if (dialog.open) dialog.close();
      else open();
    } else if (e.key === "/" && !typing && !dialog.open) {
      e.preventDefault();
      open();
    }
  });
}

// Show the right shortcut hint.
if (!/Mac|iPhone|iPad/.test(navigator.userAgent)) {
  document.querySelectorAll<HTMLElement>("[data-kbd]").forEach((k) => (k.textContent = "Ctrl K"));
}
