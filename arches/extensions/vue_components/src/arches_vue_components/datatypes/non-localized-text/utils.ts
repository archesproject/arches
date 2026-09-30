import type { NonLocalizedTextAliasedNodeData } from "@/arches_vue_components/datatypes/non-localized-text/types.ts";

export function buildNonLocalizedTextAliasedNodeData(
    nodeValue: string | null,
): NonLocalizedTextAliasedNodeData {
    return {
        node_value: nodeValue,
        display_value: nodeValue ?? "",
        details: [],
    };
}
