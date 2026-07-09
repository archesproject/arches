import type {
    ResourceInstanceListAliasedNodeData,
    ResourceInstanceListOption,
    ResourceInstanceReference,
} from "@/arches_component_lab/datatypes/resource-instance-list/types.ts";

export function buildResourceInstanceListAliasedNodeData(
    nodeValues: ResourceInstanceReference[] | null,
    resolvedOptions: ResourceInstanceListOption[],
): ResourceInstanceListAliasedNodeData {
    return {
        node_value: nodeValues,
        display_value: resolvedOptions
            .map((option) => option.display_value)
            .join(", "),
        details: resolvedOptions,
    };
}
