import type { NumberAliasedNodeData } from "@/arches_vue_components/datatypes/number/types.ts";

export function buildNumberAliasedNodeData(
    nodeValue: number | null,
): NumberAliasedNodeData {
    return {
        node_value: nodeValue,
        display_value: nodeValue != null ? String(nodeValue) : "",
        details: [],
    };
}
