import { loadQuartzConfig, loadQuartzLayout } from "./quartz/plugins/loader/config-loader"
import * as ExternalPlugin from "./.quartz/plugins"
import type { ExplorerOptions } from "./.quartz/plugins/explorer/dist"

ExternalPlugin.Explorer({
  filterFn: ((node) => {
    const segment = node.slugSegment?.toLowerCase()
    return (
      segment !== "summaries" &&
      segment !== "sources" &&
      segment !== "tags" &&
      segment !== "imprint"
    )
  }) satisfies ExplorerOptions["filterFn"],
})

const config = await loadQuartzConfig()
export default config
export const layout = await loadQuartzLayout()
