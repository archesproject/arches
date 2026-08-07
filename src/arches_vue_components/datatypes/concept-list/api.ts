import { generateArchesURL } from "@/arches_vue_components/application/generate-arches-url.ts";

import type { ConceptFetchResult } from "@/arches_vue_components/datatypes/concept/types.ts";
/*
 * @param graphSlug
 * @param nodeAlias
 */
export const fetchConceptsTree = async (
    graphSlug: string,
    nodeAlias: string,
): Promise<ConceptFetchResult> => {
    const response = await fetch(
        generateArchesURL("arches_vue_components:api-concepts-tree", {
            graph_slug: graphSlug,
            node_alias: nodeAlias,
        }),
    );

    const parsed = await response.json();
    if (!response.ok) throw new Error(parsed.message || response.statusText);
    return parsed;
};
