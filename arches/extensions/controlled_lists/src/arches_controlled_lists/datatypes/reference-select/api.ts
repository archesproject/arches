import arches from "arches";

import type { ReferenceSelectTreeNode } from "@/arches_controlled_lists/datatypes/reference-select/types.ts";

export async function fetchControlledListOptions(
    graphSlug: string,
    nodeAlias: string,
): Promise<ReferenceSelectTreeNode[]> {
    const queryParams = new URLSearchParams({
        graph_slug: graphSlug,
        node_alias: nodeAlias,
    });
    const response = await fetch(
        `${arches.urls.controlled_list_options}?${queryParams}`,
    );
    const parsed = await response.json();
    if (!response.ok) throw new Error(parsed.message || response.statusText);
    return parsed;
}
