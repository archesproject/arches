import type {
    URLAliasedNodeData,
    URLNodeValue,
} from "@/arches_component_lab/datatypes/url/types.ts";

export function buildURLAliasedNodeData(
    nodeValue: URLNodeValue | null,
): URLAliasedNodeData {
    if (!nodeValue) {
        return { node_value: null, display_value: "", details: [] };
    }
    let displayValue = nodeValue.url;
    if (nodeValue.url_label) {
        displayValue = `${nodeValue.url_label} (${nodeValue.url})`;
    }
    return { node_value: nodeValue, display_value: displayValue, details: [] };
}
