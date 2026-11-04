import type { MapSettings } from "@/arches_vue_components/components/MapComponent/types.ts";
import type { MapCardXNodeXWidgetData } from "@/arches_vue_components/widgets/MapWidget/types.ts";

export function buildMapSettings(
    config: MapCardXNodeXWidgetData["config"] | undefined,
): Partial<MapSettings> {
    const hasCameraTilt =
        (config?.pitch ?? 0) !== 0 || (config?.bearing ?? 0) !== 0;

    return {
        showCursorCoordinates: config?.showCursorCoordinates,
        coordinateReadoutSrid: config?.coordinateReadoutSrid,
        coordinateReadoutFormat: config?.coordinateReadoutFormat,
        showMapScale: config?.showMapScale,
        mapScaleUnit: config?.mapScaleUnit,
        showZoomLevel: config?.showZoomLevel,
        geocoderVisible: config?.geocoderVisible,
        geocoderPlaceholder: config?.geocodePlaceholder,
        scrollZoomRequiresKey: config?.scrollZoomRequiresKey,
        showNavigationControl: config?.showNavigationControl,
        showFullscreenControl: config?.showFullscreenControl,
        allow3d: config?.allow3d ?? hasCameraTilt,
    };
}
