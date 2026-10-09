import { watch } from "vue";

import MaplibreGeocoder from "@maplibre/maplibre-gl-geocoder";
import "@maplibre/maplibre-gl-geocoder/dist/maplibre-gl-geocoder.css";
import * as maplibregl from "maplibre-gl";

import { useGettext } from "vue3-gettext";

import { nominatimGeocoderApi } from "@/arches_vue_components/components/MapComponent/utils/geocoder-api.ts";

import type { Ref, ShallowRef } from "vue";
import type { IControl, Map as MaplibreMap } from "maplibre-gl";

import type { MapSettings } from "@/arches_vue_components/components/MapComponent/types.ts";

const CONTROL_POSITION = "top-right";
const DEFAULT_MAX_PITCH = 60;
const CAMERA_RESET_DURATION_MILLISECONDS = 300;

export function useMapControls(
    map: ShallowRef<MaplibreMap | null>,
    settings: Ref<MapSettings>,
    fullscreenContainer: Readonly<Ref<HTMLElement | null>>,
): void {
    const { $gettext } = useGettext();

    let orderedControls: { control: IControl; isVisible: () => boolean }[] = [];

    watch(
        map,
        (createdMap) => {
            if (!createdMap) {
                return;
            }

            orderedControls = [
                {
                    control: new MaplibreGeocoder(nominatimGeocoderApi, {
                        maplibregl,
                        placeholder:
                            settings.value.geocoderPlaceholder ??
                            $gettext("Search for a place"),
                    }),
                    isVisible: () => settings.value.geocoderVisible,
                },
                {
                    control: new maplibregl.NavigationControl(),
                    isVisible: () => settings.value.showNavigationControl,
                },
                {
                    control: new maplibregl.FullscreenControl({
                        container: fullscreenContainer.value ?? undefined,
                    }),
                    isVisible: () => settings.value.showFullscreenControl,
                },
            ];
            syncControls();
            applyScrollZoomRequiresKey();
            applyAllow3d();
        },
        { once: true },
    );

    watch(
        () => settings.value.scrollZoomRequiresKey,
        applyScrollZoomRequiresKey,
    );
    watch(() => settings.value.allow3d, applyAllow3d);
    watch(
        () => [
            settings.value.geocoderVisible,
            settings.value.showNavigationControl,
            settings.value.showFullscreenControl,
        ],
        syncControls,
    );

    function syncControls(): void {
        for (const { control } of orderedControls) {
            if (map.value!.hasControl(control)) {
                map.value!.removeControl(control);
            }
        }
        for (const { control, isVisible } of orderedControls) {
            if (isVisible()) {
                map.value!.addControl(control, CONTROL_POSITION);
            }
        }
    }

    function applyScrollZoomRequiresKey(): void {
        if (!map.value) {
            return;
        }

        if (settings.value.scrollZoomRequiresKey) {
            map.value.cooperativeGestures.enable();
        } else {
            map.value.cooperativeGestures.disable();
        }
    }

    function applyAllow3d(): void {
        if (!map.value) {
            return;
        }

        if (settings.value.allow3d) {
            map.value.setMaxPitch(DEFAULT_MAX_PITCH);
            map.value.dragRotate.enable();
            map.value.touchPitch.enable();
            map.value.touchZoomRotate.enableRotation();
        } else {
            map.value.dragRotate.disable();
            map.value.touchPitch.disable();
            map.value.touchZoomRotate.disableRotation();
            map.value.setMaxPitch(0);
            map.value.resetNorthPitch({
                duration: CAMERA_RESET_DURATION_MILLISECONDS,
            });
        }
    }
}
