import { ref, shallowRef, useId, watch } from "vue";

import "@maplibre/maplibre-gl-geocoder/dist/maplibre-gl-geocoder.css";
import * as maplibregl from "maplibre-gl";

import { useGettext } from "vue3-gettext";

import { AccessibleGeocoder } from "@/arches_vue_components/components/MapComponent/utils/accessible-geocoder.ts";
import { geocoderApi } from "@/arches_vue_components/components/MapComponent/utils/geocoder-api.ts";

import type { Ref, ShallowRef } from "vue";
import type { IControl, Map as MaplibreMap } from "maplibre-gl";

import type {
    GeocoderControls,
    GeocoderHosts,
    MapSettings,
} from "@/arches_vue_components/components/MapComponent/types.ts";

const CONTROL_POSITION = "top-right";
const DEFAULT_MAX_PITCH = 60;
const CAMERA_RESET_DURATION_MILLISECONDS = 300;

export function useMapControls(
    map: ShallowRef<MaplibreMap | null>,
    settings: Ref<MapSettings>,
    fullscreenContainer: Readonly<Ref<HTMLElement | null>>,
): GeocoderControls {
    const { $gettext, $ngettext } = useGettext();
    const geocoderHintId = useId();

    const geocoderHosts = shallowRef<GeocoderHosts | null>(null);
    const geocoderInputText = ref("");
    const isGeocoderSearching = ref(false);
    const geocoderStatusMessage = ref("");

    let orderedControls: { control: IControl; isVisible: () => boolean }[] = [];
    let geocoder: AccessibleGeocoder | null = null;

    watch(
        map,
        (createdMap) => {
            if (!createdMap) {
                return;
            }

            geocoder = createGeocoder();
            orderedControls = [
                {
                    control: geocoder,
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

    function createGeocoder(): AccessibleGeocoder {
        const createdGeocoder = new AccessibleGeocoder(
            geocoderApi,
            {
                maplibregl,
                placeholder:
                    settings.value.geocoderPlaceholder ??
                    $gettext("Search for a place"),
            },
            setGeocoderHosts,
        );

        createdGeocoder.on("loading", () => {
            isGeocoderSearching.value = true;
            geocoderStatusMessage.value = $gettext("Searching for places…");
        });
        createdGeocoder.on("results", (results) => {
            isGeocoderSearching.value = false;
            const placeCount = results.features?.length ?? 0;
            if (placeCount > 0) {
                geocoderStatusMessage.value = $ngettext(
                    "%{count} place found. Use the arrow keys to choose it.",
                    "%{count} places found. Use the arrow keys to choose one.",
                    placeCount,
                    { count: String(placeCount) },
                );
            } else {
                geocoderStatusMessage.value = $gettext("No places found.");
            }
        });
        createdGeocoder.on("error", () => {
            geocoderStatusMessage.value = $gettext(
                "The place search failed. Try again later.",
            );
        });
        createdGeocoder.on("result", ({ result }) => {
            syncGeocoderInputText();
            geocoderStatusMessage.value = $gettext(
                "Showing %{placeName}.",
                { placeName: result.place_name },
                true,
            );
        });
        createdGeocoder.on("clear", () => {
            syncGeocoderInputText();
            geocoderStatusMessage.value = "";
        });

        return createdGeocoder;
    }

    function setGeocoderHosts(hosts: GeocoderHosts | null): void {
        geocoderHosts.value = hosts;
        if (hosts) {
            hosts.input.setAttribute("aria-describedby", geocoderHintId);
            hosts.input.addEventListener("input", syncGeocoderInputText);
        }
        syncGeocoderInputText();
    }

    function syncGeocoderInputText(): void {
        geocoderInputText.value = geocoderHosts.value?.input.value ?? "";
    }

    function clearGeocoder(): void {
        geocoder?.clear();
    }

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

    return {
        hosts: geocoderHosts,
        hintId: geocoderHintId,
        inputText: geocoderInputText,
        isSearching: isGeocoderSearching,
        statusMessage: geocoderStatusMessage,
        clear: clearGeocoder,
    };
}
