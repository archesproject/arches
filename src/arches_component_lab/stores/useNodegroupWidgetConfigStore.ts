import { defineStore } from "pinia";

import arches from "arches";

import type { CardXNodeXWidgetData } from "@/arches_component_lab/types.ts";

async function requestNodegroupWidgetConfigs(
    graphSlug: string,
    nodegroupAlias: string,
): Promise<CardXNodeXWidgetData[]> {
    const response = await fetch(
        arches.urls.api_card_x_node_x_widget_list_from_nodegroup(
            graphSlug,
            nodegroupAlias,
        ),
    );

    const parsed = await response.json();

    if (!response.ok) {
        throw new Error(parsed.message ?? response.statusText);
    }

    return parsed;
}

export const useNodegroupWidgetConfigStore = defineStore(
    "arches_component_lab:nodegroupWidgetConfig",
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
