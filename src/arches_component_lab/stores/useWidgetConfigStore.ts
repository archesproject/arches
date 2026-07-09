import { defineStore } from "pinia";

import arches from "arches";

import type { CardXNodeXWidgetData } from "@/arches_component_lab/types.ts";

async function requestWidgetConfig(
    graphSlug: string,
    nodeAlias: string,
): Promise<CardXNodeXWidgetData> {
    const response = await fetch(
        arches.urls.api_card_x_node_x_widget(graphSlug, nodeAlias),
    );

    const parsed = await response.json();

    if (!response.ok) {
        throw new Error(parsed.message ?? response.statusText);
    }

    return parsed;
}

export const useWidgetConfigStore = defineStore(
    "arches_component_lab:widgetConfig",
    () => {
        const cache = new Map<
            string,
            Map<string, Promise<CardXNodeXWidgetData>>
        >();

        function fetchWidgetConfig(
            graphSlug: string,
            nodeAlias: string,
        ): Promise<CardXNodeXWidgetData> {
            if (!cache.has(graphSlug)) {
                cache.set(graphSlug, new Map());
            }

            const inner = cache.get(graphSlug)!;

            if (!inner.has(nodeAlias)) {
                const promise = requestWidgetConfig(graphSlug, nodeAlias);
                promise.catch(() => inner.delete(nodeAlias));
                inner.set(nodeAlias, promise);
            }

            return inner.get(nodeAlias)!;
        }

        return { fetchWidgetConfig };
    },
);
