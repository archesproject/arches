import { defineStore } from "pinia";

import { generateArchesURL } from "@/arches_vue_components/application/generate-arches-url.ts";

import type { CardXNodeXWidgetData } from "@/arches_vue_components/types.ts";

async function requestWidgetConfig(
    graphSlug: string,
    nodeAlias: string,
): Promise<CardXNodeXWidgetData> {
    const response = await fetch(
        generateArchesURL("arches_vue_components:api-card-x-node-x-widget", {
            graph_slug: graphSlug,
            node_alias: nodeAlias,
        }),
    );

    const parsed = await response.json();

    if (!response.ok) {
        throw new Error(parsed.message ?? response.statusText);
    }

    return parsed;
}

export const useWidgetConfigStore = defineStore(
    "arches_vue_components:widgetConfig",
    () => {
        const cache = new Map<
            string,
            Map<string, Promise<CardXNodeXWidgetData>>
        >();

        function nodeCache(
            graphSlug: string,
        ): Map<string, Promise<CardXNodeXWidgetData>> {
            if (!cache.has(graphSlug)) {
                cache.set(graphSlug, new Map());
            }

            return cache.get(graphSlug)!;
        }

        function fetchWidgetConfig(
            graphSlug: string,
            nodeAlias: string,
        ): Promise<CardXNodeXWidgetData> {
            const inner = nodeCache(graphSlug);

            if (!inner.has(nodeAlias)) {
                const promise = requestWidgetConfig(graphSlug, nodeAlias);
                promise.catch(() => inner.delete(nodeAlias));
                inner.set(nodeAlias, promise);
            }

            return inner.get(nodeAlias)!;
        }

        function cacheWidgetConfigs(
            graphSlug: string,
            cardXNodeXWidgets: CardXNodeXWidgetData[],
        ): void {
            const inner = nodeCache(graphSlug);

            for (const cardXNodeXWidget of cardXNodeXWidgets) {
                if (!inner.has(cardXNodeXWidget.node.alias)) {
                    inner.set(
                        cardXNodeXWidget.node.alias,
                        Promise.resolve(cardXNodeXWidget),
                    );
                }
            }
        }

        return { fetchWidgetConfig, cacheWidgetConfigs };
    },
);
