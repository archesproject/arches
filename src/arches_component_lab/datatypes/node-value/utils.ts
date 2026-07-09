import type { NodeValueAliasedNodeData } from "@/arches_component_lab/datatypes/node-value/types.ts";

export function buildNodeValueAliasedNodeData(
    nodeValue: string | null,
): NodeValueAliasedNodeData {
    return {
        node_value: nodeValue,
        display_value: nodeValue ?? "",
        details: [],
    };
}
