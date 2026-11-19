import MaplibreGeocoder from "@maplibre/maplibre-gl-geocoder";

import type {
    MaplibreGeocoderApi,
    MaplibreGeocoderOptions,
} from "@maplibre/maplibre-gl-geocoder";
import type { Map as MaplibreMap } from "maplibre-gl";

import type { GeocoderHosts } from "@/arches_vue_components/components/MapComponent/types.ts";

export class AccessibleGeocoder extends MaplibreGeocoder {
    private readonly onHostsChange: (hosts: GeocoderHosts | null) => void;

    constructor(
        geocoderApi: MaplibreGeocoderApi,
        options: MaplibreGeocoderOptions,
        onHostsChange: (hosts: GeocoderHosts | null) => void,
    ) {
        super(geocoderApi, options);
        this.onHostsChange = onHostsChange;
    }

    onAdd(map?: MaplibreMap): HTMLElement {
        const container = super.onAdd(map);
        const input = container.querySelector<HTMLInputElement>(
            ".maplibregl-ctrl-geocoder--input",
        )!;

        const field = document.createElement("div");
        field.className = "map-geocoder-field";
        field.append(...container.childNodes);
        field.querySelector(".maplibregl-ctrl-geocoder--button")?.remove();

        const clearHost = document.createElement("div");
        clearHost.className = "map-geocoder-clear-host";
        field.append(clearHost);

        const searchHost = document.createElement("div");
        searchHost.className = "map-geocoder-search-host";

        const suggestions = field.querySelector(".suggestions-wrapper");

        input.addEventListener(
            "keydown",
            (event) => {
                if (event.key === "Enter" && hasActiveSuggestion(container)) {
                    event.stopImmediatePropagation();
                }
            },
            { capture: true },
        );

        container.classList.add("map-geocoder");
        container.append(field, searchHost);
        if (suggestions) {
            container.append(suggestions);
        }

        this.onHostsChange({ input, clearHost, searchHost });
        return container;
    }

    onRemove(): this {
        this.onHostsChange(null);
        return super.onRemove();
    }
}

export function searchFrom(input: HTMLInputElement): void {
    if (!input.value.trim()) {
        input.focus();
        return;
    }
    input.dispatchEvent(
        new KeyboardEvent("keydown", { key: "Enter", bubbles: true }),
    );
}

function hasActiveSuggestion(container: HTMLElement): boolean {
    const activeSuggestion = container.querySelector<HTMLElement>(
        ".suggestions > li.active",
    );
    return activeSuggestion !== null && activeSuggestion.offsetParent !== null;
}
