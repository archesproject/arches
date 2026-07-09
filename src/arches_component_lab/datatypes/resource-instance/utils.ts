import type {
    ResourceInstanceAliasedNodeData,
    ResourceInstanceReference,
} from "@/arches_component_lab/datatypes/resource-instance/types.ts";

export function buildResourceInstanceAliasedNodeData(
    nodeValue: ResourceInstanceReference | null,
    displayName: string,
): ResourceInstanceAliasedNodeData {
    if (!nodeValue) {
        return { node_value: null, display_value: displayName, details: [] };
    }
    return {
        node_value: [nodeValue],
        display_value: displayName,
        details: [
            { resource_id: nodeValue.resourceId, display_value: displayName },
        ],
    };
}
