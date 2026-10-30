import { defineStore } from "pinia";

import { generateArchesURL } from "@/arches_vue_components/application/generate-arches-url.ts";

import type { CardXNodeXWidgetData } from "@/arches_vue_components/types.ts";

async function requestNodegroupWidgetConfigs(
    graphSlug: string,
    nodegroupAlias: string,
): Promise<CardXNodeXWidgetData[]> {
    const response = await fetch(
        generateArchesURL(
            "arches_vue_components:api-card-x-node-x-widget-list-from-nodegroup",
            {
                graph_slug: graphSlug,
                nodegroup_alias: nodegroupAlias,
            },
        ),
    );

    const parsed = await response.json();

    if (!response.ok) {
        throw new Error(parsed.message ?? response.statusText);
    }

    return parsed;
}

export const useNodegroupWidgetConfigStore = defineStore(
    "arches_vue_components:nodegroupWidgetConfig",
    () => {
        const cache = new Map<
            string,
            Map<string, Promise<CardXNodeXWidgetData[]>>
        >();

        function fetchNodegroupWidgetConfigs(
            graphSlug: string,
            nodegroupAlias: string,
        ): Promise<CardXNodeXWidgetData[]> {
            if (!cache.has(graphSlug)) {
                cache.set(graphSlug, new Map());
            }

            const inner = cache.get(graphSlug)!;

            if (!inner.has(nodegroupAlias)) {
                const promise = requestNodegroupWidgetConfigs(
                    graphSlug,
                    nodegroupAlias,
                );
                promise.catch(() => inner.delete(nodegroupAlias));
                inner.set(nodegroupAlias, promise);
            }

            return inner.get(nodegroupAlias)!;
        }

        return { fetchNodegroupWidgetConfigs };
    },
);
