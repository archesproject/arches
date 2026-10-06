import type { NodeValueAliasedNodeData } from "@/arches_vue_components/datatypes/node-value/types.ts";

export function buildNodeValueAliasedNodeData(
    nodeValue: string | null,
): NodeValueAliasedNodeData {
    return {
        node_value: nodeValue,
        display_value: nodeValue ?? "",
        details: [],
    };
}
