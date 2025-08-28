import arches from "arches";

import type { ConceptFetchResult } from "@/arches_component_lab/datatypes/concept/types.ts";
/*
 * @param graphSlug
 * @param nodeAlias
 */
export const fetchConceptsTree = async (
    graphSlug: string,
    nodeAlias: string,
): Promise<ConceptFetchResult> => {
    const response = await fetch(
        arches.urls.api_concepts_tree(graphSlug, nodeAlias),
    );

    const parsed = await response.json();
    if (!response.ok) throw new Error(parsed.message || response.statusText);
    return parsed;
};
