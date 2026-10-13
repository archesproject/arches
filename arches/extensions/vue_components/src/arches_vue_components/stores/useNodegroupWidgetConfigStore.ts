import { defineStore } from "pinia";

import { generateArchesURL } from "@/arches_vue_components/application/generate-arches-url.ts";

import type {
    CardXNodeXWidgetData,
    NodegroupWidgetConfig,
} from "@/arches_vue_components/types.ts";

async function requestJson<T>(url: string): Promise<T> {
    const response = await fetch(url);

    const parsed = await response.json();

    if (!response.ok) {
        throw new Error(parsed.message ?? response.statusText);
    }

    return parsed;
}

function requestNodegroupWidgetConfigs(
    graphSlug: string,
    nodegroupAlias: string,
): Promise<CardXNodeXWidgetData[]> {
    return requestJson(
        generateArchesURL(
            "arches_vue_components:api-card-x-node-x-widget-list-from-nodegroup",
            {
                graph_slug: graphSlug,
                nodegroup_alias: nodegroupAlias,
            },
        ),
    );
}

function requestGraphWidgetConfigs(
    graphSlug: string,
): Promise<Record<string, NodegroupWidgetConfig>> {
    return requestJson(
        generateArchesURL(
            "arches_vue_components:api-card-x-node-x-widget-list-from-graph",
            { graph_slug: graphSlug },
        ),
    );
}

export const useNodegroupWidgetConfigStore = defineStore(
    "arches_vue_components:nodegroupWidgetConfig",
    () => {
        const cache = new Map<
            string,
            Map<string, Promise<CardXNodeXWidgetData[]>>
        >();
        const graphCache = new Map<
            string,
            Promise<Record<string, NodegroupWidgetConfig>>
        >();

        function nodegroupCache(
            graphSlug: string,
        ): Map<string, Promise<CardXNodeXWidgetData[]>> {
            if (!cache.has(graphSlug)) {
                cache.set(graphSlug, new Map());
            }

            return cache.get(graphSlug)!;
        }

        function fetchNodegroupWidgetConfigs(
            graphSlug: string,
            nodegroupAlias: string,
        ): Promise<CardXNodeXWidgetData[]> {
            const inner = nodegroupCache(graphSlug);

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

        function fetchGraphWidgetConfigs(
            graphSlug: string,
        ): Promise<Record<string, NodegroupWidgetConfig>> {
            if (!graphCache.has(graphSlug)) {
                const promise = requestGraphWidgetConfigs(graphSlug).then(
                    (nodegroupWidgetConfigs) => {
                        const inner = nodegroupCache(graphSlug);
                        for (const [
                            nodegroupAlias,
                            nodegroupWidgetConfig,
                        ] of Object.entries(nodegroupWidgetConfigs)) {
                            if (!inner.has(nodegroupAlias)) {
                                inner.set(
                                    nodegroupAlias,
                                    Promise.resolve(
                                        nodegroupWidgetConfig.card_x_node_x_widgets,
                                    ),
                                );
                            }
                        }
                        return nodegroupWidgetConfigs;
                    },
                );
                promise.catch(() => graphCache.delete(graphSlug));
                graphCache.set(graphSlug, promise);
            }

            return graphCache.get(graphSlug)!;
        }

        return { fetchNodegroupWidgetConfigs, fetchGraphWidgetConfigs };
    },
);
