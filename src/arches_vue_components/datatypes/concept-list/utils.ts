import { getOption } from "@/arches_vue_components/datatypes/concept/utils.ts";

import type { CollectionItem } from "@/arches_vue_components/datatypes/concept/types.ts";
import type { ConceptListAliasedNodeData } from "@/arches_vue_components/datatypes/concept-list/types.ts";

export function buildConceptListAliasedNodeData(
    nodeValues: string[] | null,
    options: CollectionItem[],
): ConceptListAliasedNodeData {
    if (!nodeValues?.length) {
        return { node_value: nodeValues, display_value: "", details: [] };
    }
    const resolvedOptions = nodeValues
        .map((id) => getOption(id, options))
        .filter((option): option is CollectionItem => option !== null);
    return {
        node_value: nodeValues,
        display_value: resolvedOptions.map((option) => option.label).join(", "),
        details: resolvedOptions,
    };
}
