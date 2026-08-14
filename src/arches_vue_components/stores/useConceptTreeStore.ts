import { defineStore } from "pinia";

import { generateArchesURL } from "@/arches_vue_components/application/generate-arches-url.ts";

import type { ConceptFetchResult } from "@/arches_vue_components/datatypes/concept/types.ts";

export const useConceptTreeStore = defineStore(
    "arches_vue_components:conceptTree",
    () => {
        const cache = new Map<
            string,
            Map<string, Promise<ConceptFetchResult>>
        >();

        function fetchTree(
            graphSlug: string,
            nodeAlias: string,
        ): Promise<ConceptFetchResult> {
            if (!cache.has(graphSlug)) {
                cache.set(graphSlug, new Map());
            }
            const inner = cache.get(graphSlug)!;
            if (!inner.has(nodeAlias)) {
                const promise = (async () => {
                    const response = await fetch(
                        generateArchesURL(
                            "arches_vue_components:api-concepts-tree",
                            {
                                graph_slug: graphSlug,
                                node_alias: nodeAlias,
                            },
                        ),
                    );
                    const parsed = await response.json();
                    if (!response.ok) {
                        throw new Error(parsed.message || response.statusText);
                    }
                    return parsed;
                })();
                promise.catch(() => inner.delete(nodeAlias));
                inner.set(nodeAlias, promise);
            }
            return inner.get(nodeAlias)!;
        }

        return { fetchTree };
    },
);
