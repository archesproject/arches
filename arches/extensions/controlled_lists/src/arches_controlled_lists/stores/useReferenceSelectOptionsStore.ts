import { defineStore } from "pinia";

import { fetchControlledListOptions } from "@/arches_controlled_lists/datatypes/reference-select/api.ts";

import type { ReferenceSelectTreeNode } from "@/arches_controlled_lists/datatypes/reference-select/types.ts";

export const useReferenceSelectOptionsStore = defineStore(
    "arches_controlled_lists:referenceSelectOptions",
    () => {
        const inflightFetches = new Map<
            string,
            Map<string, Promise<ReferenceSelectTreeNode[]>>
        >();

        function getNodeAliasCache(
            graphSlug: string,
        ): Map<string, Promise<ReferenceSelectTreeNode[]>> {
            if (!inflightFetches.has(graphSlug)) {
                inflightFetches.set(graphSlug, new Map());
            }
            return inflightFetches.get(graphSlug)!;
        }

        function fetchWidgetOptions(
            graphSlug: string,
            nodeAlias: string,
        ): Promise<ReferenceSelectTreeNode[]> {
            const nodeAliasCache = getNodeAliasCache(graphSlug);
            if (!nodeAliasCache.has(nodeAlias)) {
                nodeAliasCache.set(
                    nodeAlias,
                    fetchControlledListOptions(graphSlug, nodeAlias),
                );
            }
            return nodeAliasCache.get(nodeAlias)!;
        }

        return { fetchWidgetOptions };
    },
);
