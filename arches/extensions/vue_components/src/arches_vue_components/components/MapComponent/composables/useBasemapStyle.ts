import { watch } from "vue";

import type { Ref, ShallowRef } from "vue";
import type { Map as MaplibreMap, StyleSpecification } from "maplibre-gl";

import type { Basemap } from "@/arches_vue_components/components/MapComponent/types.ts";

export function useBasemapStyle(
    map: ShallowRef<MaplibreMap | null>,
    basemaps: Ref<Basemap[]>,
): void {
    let activeBasemapUrl: string | null = null;
    let basemapSourceIds = new Set<string>();

    watch(
        basemaps,
        (updatedBasemaps) => {
            const activeBasemap = updatedBasemaps.find(
                (basemap) => basemap.active,
            );

            if (
                !activeBasemap ||
                !map.value ||
                activeBasemap.url === activeBasemapUrl
            ) {
                return;
            }

            activeBasemapUrl = activeBasemap.url;
            map.value.setStyle(activeBasemap.url, {
                diff: false,
                transformStyle: carryOverComponentLayers,
            });
        },
        { deep: true },
    );

    function carryOverComponentLayers(
        previousStyle: StyleSpecification | undefined,
        nextStyle: StyleSpecification,
    ): StyleSpecification {
        const outgoingBasemapSourceIds = basemapSourceIds;
        basemapSourceIds = new Set(Object.keys(nextStyle.sources));

        if (!previousStyle) {
            return nextStyle;
        }

        const carriedSources = Object.fromEntries(
            Object.entries(previousStyle.sources).filter(
                ([sourceId]) => !outgoingBasemapSourceIds.has(sourceId),
            ),
        );
        const carriedLayers = previousStyle.layers.filter(
            (layer) => "source" in layer && layer.source in carriedSources,
        );

        return {
            ...nextStyle,
            sources: { ...nextStyle.sources, ...carriedSources },
            layers: [...nextStyle.layers, ...carriedLayers],
        };
    }
}
