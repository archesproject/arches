import arches from "arches";

import type { CardXNodeXWidgetData } from "@/arches_component_lab/types.ts";

// Promise-based cache: graph config is static for the lifetime of the SPA.
// Keyed by "graphSlug:nodeAlias". Caching the Promise (not the result)
// also deduplicates concurrent in-flight requests.
const cardXNodeXWidgetCache = new Map<string, Promise<CardXNodeXWidgetData>>();

async function fetchCardXNodeXWidgetDataFromServer(
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

export function fetchCardXNodeXWidgetData(
    graphSlug: string,
    nodeAlias: string,
): Promise<CardXNodeXWidgetData> {
    const cacheKey = `${graphSlug}:${nodeAlias}`;

    if (!cardXNodeXWidgetCache.has(cacheKey)) {
        const fetchRequest = fetchCardXNodeXWidgetDataFromServer(
            graphSlug,
            nodeAlias,
        );

        // On failure, evict so a retry can re-fetch.
        fetchRequest.catch(() => cardXNodeXWidgetCache.delete(cacheKey));
        cardXNodeXWidgetCache.set(cacheKey, fetchRequest);
    }

    return cardXNodeXWidgetCache.get(cacheKey)!;
}
