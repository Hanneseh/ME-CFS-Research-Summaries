# @quartz-community/explorer

The Explorer component for Quartz - navigate your digital garden with an interactive file tree.

## Features

- 📁 Interactive folder tree with collapse/expand functionality
- 📱 Mobile-friendly slide-out navigation
- 💾 Persistent state (remembers open/closed folders)
- 🔗 Configurable folder click behavior (link or collapse)
- ⚡ Built-in search and overflow handling

## Installation

```bash
npx quartz plugin add github:quartz-community/explorer
```

## Usage

```yaml title="quartz.config.yaml"
plugins:
  - source: github:quartz-community/explorer
    enabled: true
    layout:
      position: left
      priority: 50
```

For advanced use cases, you can override in TypeScript:

```ts title="quartz.ts (override)"
import * as ExternalPlugin from "./.quartz/plugins";

ExternalPlugin.Explorer({
  title: "Explorer",
  folderDefaultState: "collapsed",
  folderClickBehavior: "link",
  useSavedState: true,
});
```

## Configuration Options

```typescript
interface ExplorerOptions {
  /** Title displayed above the explorer */
  title?: string;

  /** Default state for folders: "collapsed" or "open" */
  folderDefaultState: "collapsed" | "open";

  /** Behavior when clicking folders: "collapse" to toggle, "link" to navigate */
  folderClickBehavior: "collapse" | "link";

  /** Whether to persist folder state in localStorage */
  useSavedState: boolean;

  /** Custom sort function for entries */
  sortFn?: (a: FileTrieNode, b: FileTrieNode) => number;

  /** Custom filter function for entries */
  filterFn?: (node: FileTrieNode) => boolean;

  /** Custom map function for transforming entries */
  mapFn?: (node: FileTrieNode) => void;

  /** Order in which to apply filter, map, and sort */
  order?: Array<"filter" | "map" | "sort">;
}
```

## Default Behavior

By default, the Explorer:

- Shows folders in a collapsed state
- Opens folders when clicked (navigates to index page)
- Saves folder states between sessions
- Excludes the "tags" folder from the tree
- Sorts folders first, then files alphabetically

## Development

This is a first-party Quartz community plugin. It serves as both:

1. A production-ready Explorer component
2. A reference implementation for building Quartz community plugins

## Documentation

See the [Quartz documentation](https://quartz.jzhao.xyz/features/explorer) for more information.

## License

MIT
