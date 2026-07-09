import type { EDTFAliasedNodeData } from "@/arches_component_lab/datatypes/edtf/types.ts";

export function buildEDTFAliasedNodeData(
    nodeValue: string | null,
): EDTFAliasedNodeData {
    return {
        node_value: nodeValue,
        display_value: nodeValue ?? "",
        details: [],
    };
}
