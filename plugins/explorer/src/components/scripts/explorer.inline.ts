// @ts-nocheck - Required for inline scripts that run in browser context
import { simplifySlug } from "@quartz-community/utils/path";

function siteHref(slug) {
  let basePath = document.body?.dataset?.basepath || "";
  if (!basePath && window.location.pathname.startsWith("/ME-CFS-Research-Summaries")) {
    basePath = "/ME-CFS-Research-Summaries";
  }
  const normalizedSlug = simplifySlug(slug || "").replace(/^\/+|\/+$/g, "");
  const path = normalizedSlug ? "/" + normalizedSlug + "/" : "/";
  return basePath.replace(/\/$/, "") + path;
}

// Simple trie node implementation for client-side
class FileTrieNode {
  constructor(segments, data) {
    this.children = [];
    this.slugSegments = segments;
    this.data = data || null;
    this.isFolder = false;
    this.fileSegmentHint = null;
    this.displayNameOverride = undefined;
  }

  get displayName() {
    if (this.displayNameOverride !== undefined) return this.displayNameOverride;
    const nonIndexTitle = this.data?.title === "index" ? undefined : this.data?.title;
    return nonIndexTitle || this.fileSegmentHint || this.slugSegment || "";
  }

  set displayName(name) {
    this.displayNameOverride = name;
  }

  get slug() {
    const path = this.slugSegments.join("/");
    return this.isFolder ? path + "/index" : path;
  }

  get slugSegment() {
    return this.slugSegments[this.slugSegments.length - 1] || "";
  }

  makeChild(path, file) {
    const fullPath = [...this.slugSegments, path[0]];
    const child = new FileTrieNode(fullPath, file);
    this.children.push(child);
    return child;
  }

  insert(path, file) {
    if (path.length === 0) return;
    this.isFolder = true;
    const segment = path[0];
    if (path.length === 1) {
      if (segment === "index") {
        if (!this.data) this.data = file;
      } else {
        this.makeChild(path, file);
      }
    } else {
      let child = this.children.find((c) => c.slugSegment === segment);
      if (!child) {
        child = this.makeChild(path, undefined);
      }
      const fileParts = (file.filePath || file.slug || "").split("/");
      child.fileSegmentHint = fileParts[fileParts.length - path.length];
      child.insert(path.slice(1), file);
    }
  }

  add(file) {
    this.insert(file.slug.split("/"), file);
  }

  sort(sortFn) {
    this.children.sort(sortFn);
    this.children.forEach((c) => c.sort(sortFn));
  }

  filter(filterFn) {
    this.children = this.children.filter(filterFn);
    this.children.forEach((c) => c.filter(filterFn));
  }

  map(mapFn) {
    mapFn(this);
    this.children.forEach((c) => c.map(mapFn));
  }

  static fromEntries(entries) {
    const trie = new FileTrieNode([], null);
    entries.forEach(([, entry]) => trie.add(entry));
    return trie;
  }
}

// Process and sort nodes
const defaultSortFn = (a, b) => {
  if ((!a.isFolder && !b.isFolder) || (a.isFolder && b.isFolder)) {
    return a.displayName.localeCompare(b.displayName, undefined, {
      numeric: true,
      sensitivity: "base",
    });
  }
  if (!a.isFolder && b.isFolder) return 1;
  return -1;
};

const defaultFilterFn = (node) => node.slugSegment !== "tags";

function processTrie(trie, sortFn, filterFn, mapFn) {
  if (filterFn) trie.filter(filterFn);
  if (mapFn) trie.map(mapFn);
  if (sortFn) trie.sort(sortFn);
  return trie;
}

// Build trie from content index data
async function buildFileTrie(dataFns) {
  try {
    console.log("[Explorer] Fetching content index...");
    const data = await fetchData;
    console.log("[Explorer] Fetched data keys:", Object.keys(data).slice(0, 5));

    if (!data) {
      console.error("[Explorer] No data received");
      return null;
    }

    // Handle both formats: { "slug": {...} } or { "content": { "slug": {...} } }
    const contentData = data.content || data;
    const entries = Object.entries(contentData);

    console.log("[Explorer] Entry count:", entries.length);

    if (entries.length === 0) {
      console.warn("[Explorer] No content entries found");
      return null;
    }

    const trie = FileTrieNode.fromEntries(entries);
    console.log("[Explorer] Trie root children:", trie.children.length);

    // Parse data functions from string if provided
    let sortFn = defaultSortFn;
    let filterFn = defaultFilterFn;
    let mapFn = null;

    if (dataFns) {
      try {
        const parsed = JSON.parse(dataFns);
        if (parsed.sortFn) {
          sortFn = new Function("a", "b", "return (" + parsed.sortFn + ")(a, b)");
        }
        if (parsed.filterFn) {
          filterFn = new Function("node", "return (" + parsed.filterFn + ")(node)");
        }
        if (parsed.mapFn) {
          mapFn = new Function("node", "(" + parsed.mapFn + ")(node)");
        }
      } catch (e) {
        console.error("Error parsing data functions:", e);
      }
    }

    return processTrie(trie, sortFn, filterFn, mapFn);
  } catch (e) {
    console.error("Error building file trie:", e);
    return null;
  }
}

// Render generation to prevent race conditions
let currentRenderGeneration = 0;

// Render the file tree
function renderTree(node, container, currentSlug, folderBehavior, savedState, pathPrefix = "") {
  const folderTemplate = document.getElementById("template-folder");
  const fileTemplate = document.getElementById("template-file");

  if (!folderTemplate || !fileTemplate) return;

  const currentPath = pathPrefix ? pathPrefix + "/" + node.slugSegment : node.slugSegment;
  const simplifiedCurrentSlug = simplifySlug(currentSlug);

  if (node.isFolder) {
    const clone = folderTemplate.content.cloneNode(true);
    const folderContainer = clone.querySelector(".folder-container");
    let folderButton = clone.querySelector(".folder-button");
    const folderTitle = clone.querySelector(".folder-title");
    const folderOuter = clone.querySelector(".folder-outer");
    const contentUl = clone.querySelector(".content");

    if (folderTitle) folderTitle.textContent = node.displayName || node.slugSegment;
    if (folderContainer) folderContainer.dataset.folderpath = node.slug;

    if (folderBehavior === "link" && folderButton) {
      const folderLink = document.createElement("a");
      folderLink.className = folderButton.className;
      const folderHref = simplifySlug(node.slug);
      folderLink.href = siteHref(folderHref || "");
      if (folderTitle) {
        folderLink.appendChild(folderTitle);
      } else {
        folderLink.textContent = node.displayName || node.slugSegment;
      }
      folderButton.replaceWith(folderLink);
      folderButton = folderLink;
    }

    // Check saved state for collapsed status
    const isCollapsed = savedState[node.slug] !== undefined ? savedState[node.slug] : true; // Default collapsed

    // if this folder is a prefix of the current path we want to open it anyways
    const simpleFolderPath = simplifySlug(node.slug);
    const folderIsPrefixOfCurrentSlug =
      simpleFolderPath &&
      simpleFolderPath === simplifiedCurrentSlug.slice(0, simpleFolderPath.length);

    if ((!isCollapsed || folderIsPrefixOfCurrentSlug) && folderOuter) {
      folderOuter.classList.add("open");
    }

    // Render children
    if (node.children && node.children.length > 0 && contentUl) {
      for (const child of node.children) {
        renderTree(child, contentUl, currentSlug, folderBehavior, savedState, currentPath);
      }
    }

    container.appendChild(clone);
  } else if (node.data) {
    const clone = fileTemplate.content.cloneNode(true);
    const link = clone.querySelector("a");
    if (link) {
      link.href = siteHref(node.data.slug);
      link.textContent = node.displayName || node.slugSegment;
      if (node.data.slug === currentSlug) {
        link.classList.add("active", "is-active");
      }
    }
    container.appendChild(clone);
  }
}

async function handleNavOrRender(e) {
  const thisGeneration = ++currentRenderGeneration;
  try {
    console.log("[Explorer] Nav event received, generation:", thisGeneration);
    const currentSlug = (e.detail?.url || "").replace(/^\/+/, "");
    const allExplorers = document.querySelectorAll("div.explorer");
    console.log("[Explorer] Found", allExplorers.length, "explorers");

    const savedState = {};
    try {
      const saved = JSON.parse(localStorage.getItem("fileTree") || "[]");
      saved.forEach((item) => {
        savedState[item.path] = item.collapsed;
      });
    } catch (e) {
      console.error("[Explorer] Error loading saved state:", e);
    }

    for (const explorer of allExplorers) {
      const explorerUl = explorer.querySelector(".explorer-ul");
      if (!explorerUl) {
        console.warn("[Explorer] No explorer-ul found");
        continue;
      }

      // Clear existing content
      explorerUl.innerHTML = '<li class="overflow-end"></li>';

      // Get data functions configuration
      const dataFns = explorer.dataset.dataFns;
      const folderBehavior = explorer.dataset.behavior || "collapse";

      // Build and render the tree
      console.log("[Explorer] Starting tree build...");
      const trie = await buildFileTrie(dataFns);

      // Check if another nav event started while we were fetching
      if (thisGeneration === currentRenderGeneration) {
        console.log("[Explorer] Render generation is current, rendering tree");
        console.log("[Explorer] Trie result:", trie ? "success" : "null");
        if (trie && trie.children && trie.children.length > 0) {
          // Clear again before rendering to ensure clean state
          explorerUl.innerHTML = '<li class="overflow-end"></li>';

          console.log("[Explorer] Rendering", trie.children.length, "children");
          for (const child of trie.children) {
            renderTree(child, explorerUl, currentSlug, folderBehavior, savedState, "");
          }
          console.log("[Explorer] Render complete, final list length:", explorerUl.children.length);
        } else {
          console.warn("[Explorer] No trie or empty children");
        }

        // restore scrollTop position or scroll to active element
        const scrollTop = sessionStorage.getItem("explorerScrollTop");
        if (scrollTop) {
          explorerUl.scrollTop = parseInt(scrollTop, 10);
        } else {
          const activeElement = explorerUl.querySelector(".active");
          if (activeElement) {
            activeElement.scrollIntoView({ behavior: "smooth" });
          }
        }
      } else {
        console.log("[Explorer] Stale render generation, skipping tree render");
      }

      // Always set up event listeners, regardless of render generation
      const cleanupHandlers = [];

      const explorerButtons = explorer.getElementsByClassName("explorer-toggle");
      for (const button of explorerButtons) {
        const clickHandler = function () {
          const nearestExplorer = this.closest(".explorer");
          if (!nearestExplorer) return;
          const explorerCollapsed = nearestExplorer.classList.toggle("collapsed");
          nearestExplorer.setAttribute("aria-expanded", explorerCollapsed ? "false" : "true");

          if (!explorerCollapsed) {
            document.documentElement.classList.add("mobile-no-scroll");
          } else {
            document.documentElement.classList.remove("mobile-no-scroll");
          }
        };
        button.addEventListener("click", clickHandler);
        cleanupHandlers.push(() => button.removeEventListener("click", clickHandler));
      }

      const folderIcons = explorer.getElementsByClassName("folder-icon");
      for (const icon of folderIcons) {
        const iconClickHandler = function (evt) {
          evt.stopPropagation();
          const folderContainer = this.parentElement;
          if (!folderContainer) return;
          const childFolderContainer = folderContainer.nextElementSibling;
          if (!childFolderContainer) return;

          childFolderContainer.classList.toggle("open");
          const isCollapsed = !childFolderContainer.classList.contains("open");

          const folderPath = folderContainer.dataset.folderpath;
          const savedState = JSON.parse(localStorage.getItem("fileTree") || "[]");
          const existingIndex = savedState.findIndex((item) => item.path === folderPath);

          if (existingIndex >= 0) {
            savedState[existingIndex].collapsed = isCollapsed;
          } else {
            savedState.push({ path: folderPath, collapsed: isCollapsed });
          }
          localStorage.setItem("fileTree", JSON.stringify(savedState));
        };
        icon.addEventListener("click", iconClickHandler);
        cleanupHandlers.push(() => icon.removeEventListener("click", iconClickHandler));
      }

      const folderButtons = explorer.getElementsByClassName("folder-button");
      for (const button of folderButtons) {
        const buttonClickHandler = function (evt) {
          const folderContainer = this.closest(".folder-container");
          if (!folderContainer) return;

          const folderBehavior = explorer.dataset.behavior || "collapse";
          const childFolderContainer = folderContainer.nextElementSibling;
          const folderPath = folderContainer.dataset.folderpath;

          if (folderBehavior === "link") {
            // When folderBehavior is "link", the <button> has been replaced with an <a> tag
            // that has the correct absolute href (e.g. "/features/"). Let the <a> tag's
            // native click propagate to the SPA router — don't navigate imperatively here,
            // as that would use a relative URL and break SPA navigation.
            return;
          } else {
            evt.stopPropagation();
            if (!childFolderContainer) return;

            childFolderContainer.classList.toggle("open");
            const isCollapsed = !childFolderContainer.classList.contains("open");

            const savedState = JSON.parse(localStorage.getItem("fileTree") || "[]");
            const existingIndex = savedState.findIndex((item) => item.path === folderPath);

            if (existingIndex >= 0) {
              savedState[existingIndex].collapsed = isCollapsed;
            } else {
              savedState.push({ path: folderPath, collapsed: isCollapsed });
            }
            localStorage.setItem("fileTree", JSON.stringify(savedState));
          }
        };
        button.addEventListener("click", buttonClickHandler);
        cleanupHandlers.push(() => button.removeEventListener("click", buttonClickHandler));
      }

      if (typeof window !== "undefined" && window.addCleanup) {
        window.addCleanup(() => cleanupHandlers.forEach((fn) => fn()));
      }
    }

    for (const explorer of document.getElementsByClassName("explorer")) {
      const mobileExplorer = explorer.querySelector(".mobile-explorer");
      if (!mobileExplorer) continue;

      mobileExplorer.classList.remove("hide-until-loaded");

      if (mobileExplorer.checkVisibility && mobileExplorer.checkVisibility()) {
        explorer.classList.add("collapsed");
        explorer.setAttribute("aria-expanded", "false");
        document.documentElement.classList.remove("mobile-no-scroll");
      }
    }
  } catch (err) {
    console.error("[Explorer] Fatal error in nav handler:", err);
  }
}

document.addEventListener("nav", handleNavOrRender);
document.addEventListener("render", handleNavOrRender);

document.addEventListener("prenav", () => {
  const explorer = document.querySelector(".explorer-ul");
  if (!explorer) return;
  sessionStorage.setItem("explorerScrollTop", explorer.scrollTop.toString());
});
