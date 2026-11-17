import { computed, ref, watch } from "vue";

import {
    BUFFER_LAYER_ID,
    COMPONENT_LAYER_ID_PREFIX,
    DRAW_LAYER_ID_PREFIX,
} from "@/arches_vue_components/components/MapComponent/constants.ts";
import {
    buildScaledOpacityPaint,
    getOverlayOpacityPercent,
} from "@/arches_vue_components/components/MapComponent/utils/overlay-opacity.ts";

import type { ComputedRef, Ref, ShallowRef } from "vue";
import type {
    AddLayerObject,
    Map as MaplibreMap,
    SourceSpecification,
} from "maplibre-gl";

import type {
    LayerDefinition,
    MapContext,
    MapLayer,
    MapSource,
} from "@/arches_vue_components/components/MapComponent/types.ts";

export interface UseOverlayLayersReturn
    extends Pick<
        MapContext,
        "overlayOpacities" | "setOverlayOpacity" | "moveOverlay"
    > {
    overlayLayerIds: ComputedRef<string[]>;
    updateMapOverlays: (overlaysToUpdate: MapLayer[]) => void;
}

export function useOverlayLayers(
    map: ShallowRef<MaplibreMap | null>,
    overlays: Ref<MapLayer[]>,
    mapSources: Ref<MapSource[]>,
): UseOverlayLayersReturn {
    const overlayOpacities = ref<Record<string, number>>({});

    const overlayLayerIds = computed(() =>
        overlays.value
            .filter((overlay) => overlay.addtomap)
            .flatMap((overlay) =>
                overlay.layerdefinitions.map((layerDef) => layerDef.id),
            ),
    );

    watch(
        overlays,
        (updatedOverlays) => {
            if (map.value?.isStyleLoaded()) {
                updateMapOverlays(updatedOverlays);
            }
        },
        { deep: true },
    );

    function findOverlayAnchorLayerId(): string | undefined {
        const styleLayers = map.value!.getStyle()?.layers ?? [];
        return styleLayers.find(
            (layer) =>
                layer.id === BUFFER_LAYER_ID ||
                layer.id.startsWith(DRAW_LAYER_ID_PREFIX) ||
                layer.id.startsWith(COMPONENT_LAYER_ID_PREFIX),
        )?.id;
    }

    function addOverlayToMap(overlay: MapLayer, beforeLayerId?: string): void {
        for (const layerDef of overlay.layerdefinitions) {
            try {
                if (layerDef.source && !map.value!.getSource(layerDef.source)) {
                    const sourceSpec = mapSources.value.find(
                        (mapSource) => mapSource.name === layerDef.source,
                    );
                    if (sourceSpec) {
                        map.value!.addSource(
                            layerDef.source,
                            sourceSpec.source as SourceSpecification,
                        );
                    }
                }
                if (!map.value!.getLayer(layerDef.id)) {
                    map.value!.addLayer(
                        layerDef as AddLayerObject,
                        beforeLayerId,
                    );
                }
            } catch (error) {
                console.error(error);
            }
        }
        applyOverlayOpacity(overlay);
    }

    function removeOverlayFromMap(overlay: MapLayer): void {
        const sourcesToRemove: Record<string, boolean> = {};

        for (const layerDef of overlay.layerdefinitions) {
            if (map.value!.getLayer(layerDef.id)) {
                map.value!.removeLayer(layerDef.id);
                if (layerDef.source) {
                    sourcesToRemove[layerDef.source] = true;
                }
            }
        }

        for (const layer of (map.value!.getStyle()?.layers ??
            []) as LayerDefinition[]) {
            const layerSource = layer.source;
            if (layerSource && sourcesToRemove[layerSource]) {
                delete sourcesToRemove[layerSource];
            }
        }

        for (const source of Object.keys(sourcesToRemove)) {
            if (map.value!.getSource(source)) {
                map.value!.removeSource(source);
            }
        }
    }

    function updateMapOverlays(overlaysToUpdate: MapLayer[]): void {
        for (const overlay of overlaysToUpdate) {
            for (const layerDef of overlay.layerdefinitions) {
                if (map.value!.getLayer(layerDef.id)) {
                    map.value!.removeLayer(layerDef.id);
                }
            }
        }

        const anchorLayerId = findOverlayAnchorLayerId();
        for (const overlay of [...overlaysToUpdate].reverse()) {
            if (overlay.addtomap) {
                addOverlayToMap(overlay, anchorLayerId);
            } else {
                removeOverlayFromMap(overlay);
            }
        }
    }

    function applyOverlayOpacity(overlay: MapLayer): void {
        const opacityPercent = getOverlayOpacityPercent(
            overlayOpacities.value,
            overlay,
        );

        for (const layerDef of overlay.layerdefinitions) {
            if (!map.value!.getLayer(layerDef.id)) {
                continue;
            }
            for (const [property, value] of buildScaledOpacityPaint(
                layerDef,
                opacityPercent,
            )) {
                map.value!.setPaintProperty(layerDef.id, property, value);
            }
        }
    }

    function setOverlayOpacity(
        overlay: MapLayer,
        opacityPercent: number,
    ): void {
        overlayOpacities.value[overlay.maplayerid] = opacityPercent;
        if (map.value) {
            applyOverlayOpacity(overlay);
        }
    }

    function moveOverlay(overlay: MapLayer, toIndex: number): void {
        const reorderedOverlays = overlays.value.filter(
            (candidate) => candidate !== overlay,
        );
        reorderedOverlays.splice(toIndex, 0, overlay);
        overlays.value = reorderedOverlays;
    }

    return {
        overlayOpacities,
        overlayLayerIds,
        updateMapOverlays,
        setOverlayOpacity,
        moveOverlay,
    };
}
