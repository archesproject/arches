import type { NumberAliasedNodeData } from "@/arches_component_lab/datatypes/number/types.ts";

export function buildNumberAliasedNodeData(
    nodeValue: number | null,
): NumberAliasedNodeData {
    return {
        node_value: nodeValue,
        display_value: nodeValue != null ? String(nodeValue) : "",
        details: [],
    };
}
