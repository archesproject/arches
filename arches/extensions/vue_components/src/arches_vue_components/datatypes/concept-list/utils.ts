import { getOption } from "@/arches_vue_components/datatypes/concept/utils.ts";

import type {
    CollectionItem,
    ConceptValueItem,
} from "@/arches_vue_components/datatypes/concept/types.ts";
import type { ConceptListAliasedNodeData } from "@/arches_vue_components/datatypes/concept-list/types.ts";

export function buildConceptListAliasedNodeData(
    nodeValues: string[] | null,
    options: CollectionItem[],
): ConceptListAliasedNodeData {
    if (!nodeValues?.length) {
        return { node_value: nodeValues, display_value: "", details: [] };
    }
    const resolvedOptions: ConceptValueItem[] = nodeValues
        .map((id) => getOption(id, options))
        .filter((option): option is CollectionItem => option !== null)
        .map((option) => ({
            concept_id: option.conceptid,
            language_id: "",
            value: option.label,
            valueid: option.key,
            valuetype_id: "",
        }));
    return {
        node_value: nodeValues,
        display_value: resolvedOptions.map((option) => option.value).join(", "),
        details: resolvedOptions,
    };
}
