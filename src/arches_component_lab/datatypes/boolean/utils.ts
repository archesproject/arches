import type { BooleanAliasedNodeData } from "@/arches_component_lab/datatypes/boolean/types.ts";

export function buildBooleanAliasedNodeData(
    nodeValue: boolean | null,
): BooleanAliasedNodeData {
    return {
        node_value: nodeValue,
        display_value: nodeValue != null ? String(nodeValue) : "",
        details: [],
    };
}
