import type { BooleanAliasedNodeData } from "@/arches_vue_components/datatypes/boolean/types.ts";

export function buildBooleanAliasedNodeData(
    nodeValue: boolean | null,
): BooleanAliasedNodeData {
    return {
        node_value: nodeValue,
        display_value: nodeValue != null ? String(nodeValue) : "",
        details: [],
    };
}
