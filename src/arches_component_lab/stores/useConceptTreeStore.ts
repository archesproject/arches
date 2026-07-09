import { defineStore } from "pinia";

import arches from "arches";

import type { ConceptFetchResult } from "@/arches_component_lab/datatypes/concept/types.ts";

export const useConceptTreeStore = defineStore(
    "arches_component_lab:conceptTree",
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
                        arches.urls.api_concepts_tree(graphSlug, nodeAlias),
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
